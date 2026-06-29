"""Room adjacency graph construction.

The module accepts already detected room polygons and calculates room-to-room
adjacency using Shapely boundary operations. It ignores corner-only touching by
requiring a positive shared boundary length.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from shapely.geometry import Polygon

from geometry_utils import linear_length
from validation import validate_room_polygons_iterable


@dataclass(frozen=True, slots=True)
class RoomPolygon:
    """A detected room polygon with identifying metadata."""

    room_id: str
    room_name: str
    polygon: Polygon


@dataclass(frozen=True, slots=True)
class AdjacencyConfig:
    """Configuration for room adjacency detection."""

    minimum_shared_wall_length: float = 1e-6
    length_precision: int | None = 6


@dataclass(frozen=True, slots=True)
class RoomAdjacency:
    """Adjacency record for one room."""

    room_id: str
    room_name: str
    adjacent_rooms: tuple[str, ...]
    shared_boundary_length: Mapping[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "adjacent_rooms": list(self.adjacent_rooms),
            "shared_boundary_length": dict(self.shared_boundary_length),
        }


class AdjacencyBuilder:
    """Build an adjacency graph for detected room polygons."""

    def __init__(self, config: AdjacencyConfig | None = None) -> None:
        self.config = config or AdjacencyConfig()
        if self.config.minimum_shared_wall_length < 0:
            raise ValueError("minimum_shared_wall_length must be non-negative")
        if self.config.length_precision is not None and self.config.length_precision < 0:
            raise ValueError("length_precision must be non-negative or None")

    def build(self, rooms: Sequence[RoomPolygon]) -> list[dict[str, Any]]:
        """Return the adjacency graph as JSON-friendly dictionaries."""

        records = self.build_records(rooms)
        return [record.to_dict() for record in records]

    def build_records(self, rooms: Sequence[RoomPolygon]) -> list[RoomAdjacency]:
        """Return typed adjacency records for ``rooms``."""

        validate_room_polygons_iterable(rooms)
        adjacency: dict[str, dict[str, float]] = {room.room_id: {} for room in rooms}

        for first_index, first in enumerate(rooms):
            for second in rooms[first_index + 1 :]:
                shared_length = shared_boundary_length(first.polygon, second.polygon)
                if shared_length < self.config.minimum_shared_wall_length:
                    continue

                length = self._format_length(shared_length)
                adjacency[first.room_id][second.room_id] = length
                adjacency[second.room_id][first.room_id] = length

        return [
            RoomAdjacency(
                room_id=room.room_id,
                room_name=room.room_name,
                adjacent_rooms=tuple(adjacency[room.room_id]),
                shared_boundary_length=adjacency[room.room_id],
            )
            for room in rooms
        ]

    def _format_length(self, value: float) -> float:
        if self.config.length_precision is None:
            return float(value)
        return round(float(value), self.config.length_precision)


def build_adjacency_graph(
    rooms: Sequence[RoomPolygon],
    *,
    minimum_shared_wall_length: float = 1e-6,
    length_precision: int | None = 6,
) -> list[dict[str, Any]]:
    """Build a room adjacency graph using default dataclass configuration."""

    return AdjacencyBuilder(
        AdjacencyConfig(
            minimum_shared_wall_length=minimum_shared_wall_length,
            length_precision=length_precision,
        )
    ).build(rooms)


def build_adjacency_graph_from_values(
    room_ids: Sequence[str],
    room_names: Sequence[str],
    polygons: Sequence[Polygon],
    *,
    minimum_shared_wall_length: float = 1e-6,
    length_precision: int | None = 6,
) -> list[dict[str, Any]]:
    """Build a graph from parallel room-id, room-name, and polygon sequences."""

    if not (len(room_ids) == len(room_names) == len(polygons)):
        raise ValueError("room_ids, room_names, and polygons must have the same length")

    rooms = [
        RoomPolygon(room_id=room_id, room_name=room_name, polygon=polygon)
        for room_id, room_name, polygon in zip(room_ids, room_names, polygons, strict=True)
    ]
    return build_adjacency_graph(
        rooms,
        minimum_shared_wall_length=minimum_shared_wall_length,
        length_precision=length_precision,
    )


def shared_boundary_length(first: Polygon, second: Polygon) -> float:
    """Return the length of shared polygon boundary, ignoring area overlap."""

    intersection = first.boundary.intersection(second.boundary)
    return linear_length(intersection)
