"""Door-based room connectivity graph construction.

This module does not detect doors. It consumes provided door point geometry,
room polygons, and an existing adjacency graph, then marks rooms as connected
only when a door lies on their shared boundary.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from shapely.geometry import Point, Polygon

from adjacency import RoomPolygon
from geometry_utils import linear_length


@dataclass(frozen=True, slots=True)
class DoorPoint:
    """A provided door location."""

    door_id: str
    point: Point


@dataclass(frozen=True, slots=True)
class ConnectivityConfig:
    """Configuration for door-to-boundary matching."""

    door_distance_tolerance: float = 1e-6


@dataclass(frozen=True, slots=True)
class ConnectedRoom:
    """One connected room edge and the door that connects it."""

    room_id: str
    door_id: str

    def to_dict(self) -> dict[str, str]:
        return {"room_id": self.room_id, "door_id": self.door_id}


@dataclass(frozen=True, slots=True)
class RoomConnectivity:
    """Connectivity record for one room."""

    room_id: str
    connected_rooms: tuple[ConnectedRoom, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "connected_rooms": [room.to_dict() for room in self.connected_rooms],
        }


class ConnectivityBuilder:
    """Build a connectivity graph from adjacent rooms and provided doors."""

    def __init__(self, config: ConnectivityConfig | None = None) -> None:
        self.config = config or ConnectivityConfig()
        if self.config.door_distance_tolerance < 0:
            raise ValueError("door_distance_tolerance must be non-negative")

    def build(
        self,
        rooms: Sequence[RoomPolygon],
        adjacency_graph: Sequence[Mapping[str, Any]],
        doors: Sequence[DoorPoint],
    ) -> list[dict[str, Any]]:
        """Return JSON-friendly room connectivity records."""

        return [
            record.to_dict()
            for record in self.build_records(rooms, adjacency_graph, doors)
        ]

    def build_records(
        self,
        rooms: Sequence[RoomPolygon],
        adjacency_graph: Sequence[Mapping[str, Any]],
        doors: Sequence[DoorPoint],
    ) -> list[RoomConnectivity]:
        """Return typed room connectivity records."""

        room_by_id = _room_index(rooms)
        adjacency_by_id = _adjacency_index(adjacency_graph)
        _validate_doors(doors)

        connectivity: dict[str, list[ConnectedRoom]] = {
            room.room_id: [] for room in rooms
        }
        seen_edges: set[tuple[str, str]] = set()

        for room_id, adjacent_room_ids in adjacency_by_id.items():
            if room_id not in room_by_id:
                raise ValueError(f"Adjacency graph references unknown room_id: {room_id!r}")

            for adjacent_room_id in adjacent_room_ids:
                if adjacent_room_id not in room_by_id:
                    raise ValueError(
                        f"Adjacency graph references unknown room_id: {adjacent_room_id!r}"
                    )

                edge_key = tuple(sorted((room_id, adjacent_room_id)))
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)

                door = self._door_on_shared_boundary(
                    room_by_id[room_id].polygon,
                    room_by_id[adjacent_room_id].polygon,
                    doors,
                )
                if door is None:
                    continue

                connectivity[room_id].append(
                    ConnectedRoom(room_id=adjacent_room_id, door_id=door.door_id)
                )
                connectivity[adjacent_room_id].append(
                    ConnectedRoom(room_id=room_id, door_id=door.door_id)
                )

        return [
            RoomConnectivity(room_id=room.room_id, connected_rooms=tuple(connectivity[room.room_id]))
            for room in rooms
        ]

    def _door_on_shared_boundary(
        self,
        first: Polygon,
        second: Polygon,
        doors: Sequence[DoorPoint],
    ) -> DoorPoint | None:
        shared_boundary = first.boundary.intersection(second.boundary)
        if linear_length(shared_boundary) <= 0:
            return None

        for door in doors:
            if shared_boundary.distance(door.point) <= self.config.door_distance_tolerance:
                return door
        return None


def build_connectivity_graph(
    rooms: Sequence[RoomPolygon],
    adjacency_graph: Sequence[Mapping[str, Any]],
    doors: Sequence[DoorPoint],
    *,
    door_distance_tolerance: float = 1e-6,
) -> list[dict[str, Any]]:
    """Build a connectivity graph with default dataclass configuration."""

    return ConnectivityBuilder(
        ConnectivityConfig(door_distance_tolerance=door_distance_tolerance)
    ).build(rooms, adjacency_graph, doors)


def _room_index(rooms: Sequence[RoomPolygon]) -> dict[str, RoomPolygon]:
    room_by_id: dict[str, RoomPolygon] = {}
    for room in rooms:
        if not room.room_id:
            raise ValueError("room_id cannot be empty")
        if room.room_id in room_by_id:
            raise ValueError(f"Duplicate room_id: {room.room_id!r}")
        if room.polygon.is_empty:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is empty")
        if not room.polygon.is_valid:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is invalid")
        room_by_id[room.room_id] = room
    return room_by_id


def _adjacency_index(adjacency_graph: Sequence[Mapping[str, Any]]) -> dict[str, tuple[str, ...]]:
    indexed: dict[str, tuple[str, ...]] = {}
    for entry in adjacency_graph:
        room_id = str(entry.get("room_id", ""))
        if not room_id:
            raise ValueError("Adjacency entry is missing room_id")
        if room_id in indexed:
            raise ValueError(f"Duplicate adjacency room_id: {room_id!r}")
        adjacent_rooms = entry.get("adjacent_rooms", ())
        indexed[room_id] = tuple(str(adjacent_room) for adjacent_room in adjacent_rooms)
    return indexed


def _validate_doors(doors: Sequence[DoorPoint]) -> None:
    seen_ids: set[str] = set()
    for door in doors:
        if not door.door_id:
            raise ValueError("door_id cannot be empty")
        if door.door_id in seen_ids:
            raise ValueError(f"Duplicate door_id: {door.door_id!r}")
        if door.point.is_empty:
            raise ValueError(f"Door point for door_id {door.door_id!r} is empty")
        seen_ids.add(door.door_id)



