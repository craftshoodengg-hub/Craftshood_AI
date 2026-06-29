"""Vastu Geometry helpers for Building Model v2."""
from __future__ import annotations
import math
from typing import Optional
from shapely.geometry import Polygon, Point
from ..base import BoundingBox, Point2D
from ..geometry.polygon import centroid as poly_centroid, bounding_box
from .vastu_direction import VastuDirection
from .vastu_zone import VastuZone


def calculate_building_center(polygon: Polygon) -> Optional[Point2D]:
    return poly_centroid(polygon)


def calculate_room_centroid(polygon: Polygon) -> Optional[Point2D]:
    return poly_centroid(polygon)


def calculate_room_direction(center: Point2D, reference: Point2D) -> VastuDirection:
    dx = center.x - reference.x
    dy = center.y - reference.y
    angle = math.degrees(math.atan2(dx, -dy)) % 360.0
    return VastuDirection.from_angle(angle)


def calculate_plot_rotation(north_direction_degrees: float) -> float:
    return north_direction_degrees % 360.0


def rotate_point(point: Point2D, angle_degrees: float, origin: Point2D | None = None) -> Point2D:
    if origin is None:
        origin = Point2D(x=0.0, y=0.0)
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dx = point.x - origin.x
    dy = point.y - origin.y
    new_x = origin.x + dx * cos_a - dy * sin_a
    new_y = origin.y + dx * sin_a + dy * cos_a
    return Point2D(x=new_x, y=new_y)


def determine_zone(center: Point2D, building_center: Point2D) -> VastuDirection:
    dx = center.x - building_center.x
    dy = center.y - building_center.y
    angle = math.degrees(math.atan2(dx, -dy)) % 360.0
    return VastuDirection.from_angle(angle)


def zone_to_vastu_zone(direction: VastuDirection) -> VastuZone:
    mapping = {
        VastuDirection.NORTH: VastuZone.NORTH,
        VastuDirection.NORTH_EAST: VastuZone.ISHANYA,
        VastuDirection.EAST: VastuZone.EAST,
        VastuDirection.SOUTH_EAST: VastuZone.AGNEYA,
        VastuDirection.SOUTH: VastuZone.SOUTH,
        VastuDirection.SOUTH_WEST: VastuZone.NAIRUTYA,
        VastuDirection.WEST: VastuZone.WEST,
        VastuDirection.NORTH_WEST: VastuZone.VAYAVYA,
        VastuDirection.CENTER: VastuZone.BRAHMASTHAN,
    }
    return mapping.get(direction, VastuZone.BRAHMASTHAN)


__all__ = [
    "calculate_building_center",
    "calculate_room_centroid",
    "calculate_room_direction",
    "calculate_plot_rotation",
    "rotate_point",
    "determine_zone",
    "zone_to_vastu_zone",
]
