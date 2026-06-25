"""Polygon construction from boundary points."""

from __future__ import annotations

import math
from dataclasses import dataclass

from loguru import logger
from shapely.geometry import Polygon

from .boundary_finder import BoundaryIntersection, RoomCenter


@dataclass(frozen=True, slots=True)
class PolygonBuilderConfig:
    """Configuration for boundary polygon building."""

    point_precision: int = 6
    minimum_points: int = 3


class PolygonBuilder:
    """Sort boundary points clockwise and build a Shapely polygon."""

    def __init__(self, config: PolygonBuilderConfig | None = None) -> None:
        self.config = config or PolygonBuilderConfig()
        if self.config.point_precision < 0:
            raise ValueError("point_precision must be non-negative")
        if self.config.minimum_points < 3:
            raise ValueError("minimum_points must be at least 3")

    def build_polygon(
        self,
        center: RoomCenter,
        intersections: list[BoundaryIntersection],
    ) -> Polygon:
        """Build a valid polygon from collected intersection points."""

        points = self.sort_clockwise(center, intersections)
        if len(points) < self.config.minimum_points:
            raise ValueError("At least three unique boundary points are required")

        polygon = Polygon(points)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty or not isinstance(polygon, Polygon):
            raise ValueError("Boundary points could not produce a valid polygon")

        logger.info("Built room polygon with {} exterior points", len(points))
        return polygon

    def sort_clockwise(
        self,
        center: RoomCenter,
        intersections: list[BoundaryIntersection],
    ) -> list[tuple[float, float]]:
        """Return unique boundary coordinates sorted clockwise around ``center``."""

        unique: dict[tuple[float, float], tuple[float, float]] = {}
        for intersection in intersections:
            key = (
                round(intersection.point.x, self.config.point_precision),
                round(intersection.point.y, self.config.point_precision),
            )
            unique[key] = (intersection.point.x, intersection.point.y)

        return sorted(
            unique.values(),
            key=lambda point: _clockwise_angle(center, point),
        )


def _clockwise_angle(center: RoomCenter, point: tuple[float, float]) -> float:
    dx = point[0] - center.x
    dy = point[1] - center.y
    return (2.0 * math.pi - math.atan2(dy, dx)) % (2.0 * math.pi)
