"""Road-facing wall and front-room detection.

This module consumes provided ROAD text location and exterior wall geometry. It
does not detect road text, does not infer doors/windows, and does not modify
room or wall geometry.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from shapely.geometry import GeometryCollection, LineString, MultiLineString, Point, Polygon

from adjacency import RoomPolygon


class RoadSide(StrEnum):
    """Supported road-side labels."""

    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ExteriorWall:
    """Provided exterior wall geometry."""

    wall_id: str
    geometry: LineString


@dataclass(frozen=True, slots=True)
class FacingConfig:
    """Configuration for matching rooms to the front wall."""

    wall_tolerance: float = 1e-6
    minimum_touch_length: float = 1e-6


@dataclass(frozen=True, slots=True)
class FacingResult:
    """Road-facing analysis result."""

    road_side: RoadSide
    front_wall_id: str | None
    front_rooms: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "road_side": self.road_side.value,
            "front_wall_id": self.front_wall_id,
            "front_rooms": list(self.front_rooms),
        }


class FacingDetector:
    """Detect the front wall and rooms touching it from provided geometry."""

    def __init__(self, config: FacingConfig | None = None) -> None:
        self.config = config or FacingConfig()
        if self.config.wall_tolerance < 0:
            raise ValueError("wall_tolerance must be non-negative")
        if self.config.minimum_touch_length < 0:
            raise ValueError("minimum_touch_length must be non-negative")

    def detect(
        self,
        rooms: Sequence[RoomPolygon],
        exterior_walls: Sequence[ExteriorWall],
        road_location: Point,
    ) -> dict[str, Any]:
        """Return the road-facing result as a JSON-friendly dictionary."""

        return self.detect_result(rooms, exterior_walls, road_location).to_dict()

    def detect_result(
        self,
        rooms: Sequence[RoomPolygon],
        exterior_walls: Sequence[ExteriorWall],
        road_location: Point,
    ) -> FacingResult:
        """Return typed road-facing result."""

        _validate_rooms(rooms)
        _validate_walls(exterior_walls)
        if road_location.is_empty:
            raise ValueError("road_location cannot be empty")

        front_wall = nearest_exterior_wall(exterior_walls, road_location)
        if front_wall is None:
            return FacingResult(
                road_side=RoadSide.UNKNOWN,
                front_wall_id=None,
                front_rooms=(),
            )

        front_rooms = tuple(
            room.room_id
            for room in rooms
            if self._room_touches_front_wall(room.polygon, front_wall.geometry)
        )
        return FacingResult(
            road_side=road_side_from_wall(front_wall.geometry, road_location),
            front_wall_id=front_wall.wall_id,
            front_rooms=front_rooms,
        )

    def _room_touches_front_wall(self, room: Polygon, wall: LineString) -> bool:
        shared_length = _linear_length(room.boundary.intersection(wall))
        if shared_length >= self.config.minimum_touch_length:
            return True

        if self.config.wall_tolerance == 0:
            return False

        if room.boundary.distance(wall) > self.config.wall_tolerance:
            return False

        buffered_wall = wall.buffer(self.config.wall_tolerance, cap_style="flat")
        touch_length = _linear_length(room.boundary.intersection(buffered_wall))
        return touch_length >= self.config.minimum_touch_length


def detect_facing(
    rooms: Sequence[RoomPolygon],
    exterior_walls: Sequence[ExteriorWall],
    road_location: Point,
    *,
    wall_tolerance: float = 1e-6,
    minimum_touch_length: float = 1e-6,
) -> dict[str, Any]:
    """Convenience wrapper for road-facing detection."""

    return FacingDetector(
        FacingConfig(
            wall_tolerance=wall_tolerance,
            minimum_touch_length=minimum_touch_length,
        )
    ).detect(rooms, exterior_walls, road_location)


def nearest_exterior_wall(
    exterior_walls: Sequence[ExteriorWall],
    road_location: Point,
) -> ExteriorWall | None:
    """Return the exterior wall nearest to the provided ROAD text location."""

    if not exterior_walls:
        return None
    return min(exterior_walls, key=lambda wall: wall.geometry.distance(road_location))


def road_side_from_wall(wall: LineString, road_location: Point) -> RoadSide:
    """Infer cardinal road side from wall midpoint to ROAD text point."""

    coordinates = list(wall.coords)
    if len(coordinates) < 2:
        return RoadSide.UNKNOWN

    start = coordinates[0]
    end = coordinates[-1]
    wall_dx = float(end[0] - start[0])
    wall_dy = float(end[1] - start[1])
    midpoint = wall.interpolate(0.5, normalized=True)
    dx = float(road_location.x - midpoint.x)
    dy = float(road_location.y - midpoint.y)

    if abs(dx) <= 1e-12 and abs(dy) <= 1e-12:
        return RoadSide.UNKNOWN
    if abs(wall_dy) > abs(wall_dx):
        return RoadSide.EAST if dx > 0 else RoadSide.WEST
    if abs(wall_dx) > abs(wall_dy):
        return RoadSide.NORTH if dy > 0 else RoadSide.SOUTH
    if abs(dy) >= abs(dx):
        return RoadSide.NORTH if dy > 0 else RoadSide.SOUTH
    return RoadSide.EAST if dx > 0 else RoadSide.WEST


def _validate_rooms(rooms: Sequence[RoomPolygon]) -> None:
    seen_ids: set[str] = set()
    for room in rooms:
        if not room.room_id:
            raise ValueError("room_id cannot be empty")
        if room.room_id in seen_ids:
            raise ValueError(f"Duplicate room_id: {room.room_id!r}")
        if room.polygon.is_empty:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is empty")
        if not room.polygon.is_valid:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is invalid")
        seen_ids.add(room.room_id)


def _validate_walls(exterior_walls: Sequence[ExteriorWall]) -> None:
    seen_ids: set[str] = set()
    for wall in exterior_walls:
        if not wall.wall_id:
            raise ValueError("wall_id cannot be empty")
        if wall.wall_id in seen_ids:
            raise ValueError(f"Duplicate wall_id: {wall.wall_id!r}")
        if wall.geometry.is_empty:
            raise ValueError(f"Geometry for wall_id {wall.wall_id!r} is empty")
        seen_ids.add(wall.wall_id)


def _linear_length(geometry: Any) -> float:
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(_linear_length(part) for part in geometry.geoms)
    return 0.0
