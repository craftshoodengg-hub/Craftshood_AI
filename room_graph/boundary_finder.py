"""Radial ray casting against logical walls."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from loguru import logger
from shapely.geometry import GeometryCollection, LineString, MultiPoint, Point

from geometry_engine import LogicalWall


@dataclass(frozen=True, slots=True)
class RoomCenter:
    """Known center point for a room label."""

    x: float
    y: float

    def to_point(self) -> Point:
        return Point(self.x, self.y)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BoundaryFinderConfig:
    """Configuration for radial boundary search."""

    radial_ray_count: int = 360
    max_ray_length: float = 10000.0
    min_intersection_distance: float = 1e-6
    point_precision: int = 6


@dataclass(frozen=True, slots=True)
class BoundaryIntersection:
    """Nearest wall intersection found for a single radial ray."""

    angle_degrees: float
    point: RoomCenter
    distance: float
    wall_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "angle_degrees": self.angle_degrees,
            "point": self.point.to_dict(),
            "distance": self.distance,
            "wall_id": self.wall_id,
        }


class BoundaryFinder:
    """Find nearest wall intersections from a room center."""

    def __init__(self, config: BoundaryFinderConfig | None = None) -> None:
        self.config = config or BoundaryFinderConfig()
        if self.config.radial_ray_count < 3:
            raise ValueError("radial_ray_count must be at least 3")
        if self.config.max_ray_length <= 0:
            raise ValueError("max_ray_length must be greater than zero")
        if self.config.min_intersection_distance < 0:
            raise ValueError("min_intersection_distance must be non-negative")
        if self.config.point_precision < 0:
            raise ValueError("point_precision must be non-negative")

    def find_boundary_points(
        self,
        center: RoomCenter,
        logical_walls: Iterable[LogicalWall],
    ) -> list[BoundaryIntersection]:
        """Cast radial rays and return nearest valid wall intersections."""

        wall_lines = list(_iter_wall_lines(logical_walls))
        intersections: list[BoundaryIntersection] = []
        seen_points: set[tuple[float, float]] = set()

        for index in range(self.config.radial_ray_count):
            angle = (360.0 * index) / self.config.radial_ray_count
            ray = self._ray(center, angle)
            nearest = self._nearest_intersection(center, angle, ray, wall_lines)
            if nearest is None:
                continue

            key = (
                round(nearest.point.x, self.config.point_precision),
                round(nearest.point.y, self.config.point_precision),
            )
            if key in seen_points:
                continue
            seen_points.add(key)
            intersections.append(nearest)

        logger.info(
            "Found {} boundary intersections from {} radial rays",
            len(intersections),
            self.config.radial_ray_count,
        )
        return intersections

    def _ray(self, center: RoomCenter, angle_degrees: float) -> LineString:
        radians = math.radians(angle_degrees)
        direction = np.array([math.cos(radians), math.sin(radians)], dtype=float)
        end = center.to_array() + (direction * self.config.max_ray_length)
        return LineString([(center.x, center.y), (float(end[0]), float(end[1]))])

    def _nearest_intersection(
        self,
        center: RoomCenter,
        angle_degrees: float,
        ray: LineString,
        wall_lines: list[tuple[str, LineString]],
    ) -> BoundaryIntersection | None:
        center_point = center.to_point()
        nearest: BoundaryIntersection | None = None

        for wall_id, wall_line in wall_lines:
            points = _intersection_points(ray.intersection(wall_line), center_point)
            for point in points:
                distance = center_point.distance(point)
                if distance < self.config.min_intersection_distance:
                    continue
                if nearest is not None and distance >= nearest.distance:
                    continue
                nearest = BoundaryIntersection(
                    angle_degrees=angle_degrees,
                    point=RoomCenter(x=float(point.x), y=float(point.y)),
                    distance=float(distance),
                    wall_id=wall_id,
                )

        return nearest


def _iter_wall_lines(logical_walls: Iterable[LogicalWall]) -> Iterable[tuple[str, LineString]]:
    for wall in logical_walls:
        for line in wall.source_lines:
            yield (
                wall.id,
                LineString([(line.start.x, line.start.y), (line.end.x, line.end.y)]),
            )


def _intersection_points(geometry: Any, center: Point) -> list[Point]:
    if geometry.is_empty:
        return []
    if isinstance(geometry, Point):
        return [geometry]
    if isinstance(geometry, MultiPoint):
        return list(geometry.geoms)
    if isinstance(geometry, LineString):
        return _line_endpoints_by_distance(geometry, center)
    if isinstance(geometry, GeometryCollection):
        points: list[Point] = []
        for part in geometry.geoms:
            points.extend(_intersection_points(part, center))
        return points
    return []


def _line_endpoints_by_distance(line: LineString, center: Point) -> list[Point]:
    coordinates = list(line.coords)
    if not coordinates:
        return []
    points = [Point(coordinates[0]), Point(coordinates[-1])]
    return sorted(points, key=center.distance)
