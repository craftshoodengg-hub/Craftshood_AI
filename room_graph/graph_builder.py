"""Room graph orchestration."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from shapely.geometry import Polygon

from geometry_engine import LogicalWall

from .area_calculator import AreaCalculator, RoomMetrics
from .boundary_finder import BoundaryFinder, BoundaryIntersection, BoundaryFinderConfig, RoomCenter
from .polygon_builder import PolygonBuilder, PolygonBuilderConfig


@dataclass(frozen=True, slots=True)
class RoomGraphResult:
    """Boundary polygon and metrics for one room."""

    room_name: str
    polygon: Polygon
    area: float
    perimeter: float
    centroid: RoomCenter
    boundary_wall_ids: tuple[str, ...]
    intersections: tuple[BoundaryIntersection, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_name": self.room_name,
            "polygon": _polygon_coordinates(self.polygon),
            "area": self.area,
            "perimeter": self.perimeter,
            "centroid": self.centroid.to_dict(),
            "boundary_wall_ids": list(self.boundary_wall_ids),
        }


class RoomGraphBuilder:
    """Build room boundary polygons from room center points and logical walls."""

    def __init__(
        self,
        *,
        boundary_config: BoundaryFinderConfig | None = None,
        polygon_config: PolygonBuilderConfig | None = None,
        boundary_finder: BoundaryFinder | None = None,
        polygon_builder: PolygonBuilder | None = None,
        area_calculator: AreaCalculator | None = None,
    ) -> None:
        self.boundary_finder = boundary_finder or BoundaryFinder(boundary_config)
        self.polygon_builder = polygon_builder or PolygonBuilder(polygon_config)
        self.area_calculator = area_calculator or AreaCalculator()

    def build_room(
        self,
        room_name: str,
        center: RoomCenter,
        logical_walls: Iterable[LogicalWall],
    ) -> RoomGraphResult:
        """Build a room boundary graph result."""

        walls = list(logical_walls)
        intersections = self.boundary_finder.find_boundary_points(center, walls)
        polygon = self.polygon_builder.build_polygon(center, intersections)
        metrics = self.area_calculator.calculate(polygon)
        return _result_from_metrics(room_name, polygon, intersections, metrics)


def _result_from_metrics(
    room_name: str,
    polygon: Polygon,
    intersections: list[BoundaryIntersection],
    metrics: RoomMetrics,
) -> RoomGraphResult:
    boundary_wall_ids = tuple(dict.fromkeys(item.wall_id for item in intersections))
    return RoomGraphResult(
        room_name=room_name,
        polygon=polygon,
        area=metrics.area,
        perimeter=metrics.perimeter,
        centroid=metrics.centroid,
        boundary_wall_ids=boundary_wall_ids,
        intersections=tuple(intersections),
    )


def _polygon_coordinates(polygon: Polygon) -> list[list[float]]:
    return [[float(x), float(y)] for x, y in polygon.exterior.coords]
