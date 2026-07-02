"""Build adjacency graph between semantic rooms using Shapely geometry."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Any

from shapely.geometry import Polygon as ShapelyPolygon

from .semantic_room_builder import SemanticRoom


@dataclass
class RoomAdjacency:
    """Represents an adjacency relationship between two rooms."""

    source_room_id: str
    target_room_id: str
    relationship: str = "adjacent"
    distance: float = 0.0
    shared_boundary_length: float = 0.0
    door_connected: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return {
            "source_room_id": self.source_room_id,
            "target_room_id": self.target_room_id,
            "relationship": self.relationship,
            "distance": self.distance,
            "shared_boundary_length": self.shared_boundary_length,
            "door_connected": self.door_connected,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RoomAdjacency":
        """Restore from a dictionary payload."""
        return cls(
            source_room_id=str(payload.get("source_room_id", "")),
            target_room_id=str(payload.get("target_room_id", "")),
            relationship=str(payload.get("relationship", "adjacent")),
            distance=float(payload.get("distance", 0.0)),
            shared_boundary_length=float(payload.get("shared_boundary_length", 0.0)),
            door_connected=bool(payload.get("door_connected", False)),
        )


def _build_shapely_polygon(polygon: list[Any]) -> ShapelyPolygon:
    """Convert a polygon coordinate list to a Shapely Polygon."""
    coords = [(float(p[0]), float(p[1])) for p in polygon]
    return ShapelyPolygon(coords)


def _door_positions(room: SemanticRoom) -> list[tuple[float, float]]:
    """Extract door centroid positions from a room's door list."""
    positions: list[tuple[float, float]] = []
    for door in room.doors:
        # Try centroid first, then fall back to position/x,y keys
        centroid = door.get("centroid")
        if centroid and isinstance(centroid, (list, tuple)) and len(centroid) >= 2:
            positions.append((float(centroid[0]), float(centroid[1])))
            continue
        pos = door.get("position")
        if pos and isinstance(pos, (list, tuple)) and len(pos) >= 2:
            positions.append((float(pos[0]), float(pos[1])))
            continue
        x = door.get("x")
        y = door.get("y")
        if x is not None and y is not None:
            positions.append((float(x), float(y)))
    return positions


def _positions_close(
    pos_a: tuple[float, float],
    pos_b: tuple[float, float],
    tolerance: float = 0.5,
) -> bool:
    """Check if two positions are within tolerance distance."""
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return sqrt(dx * dx + dy * dy) <= tolerance


def _doors_connect(
    room_a: SemanticRoom,
    room_b: SemanticRoom,
    tolerance: float = 0.5,
) -> bool:
    """Check if any door in room_a is close to any door in room_b."""
    doors_a = _door_positions(room_a)
    doors_b = _door_positions(room_b)
    if not doors_a or not doors_b:
        return False
    for da in doors_a:
        for db in doors_b:
            if _positions_close(da, db, tolerance):
                return True
    return False


class RoomAdjacencyGraphBuilder:
    """Build adjacency relationships between semantic rooms."""

    def __init__(self, tolerance: float = 0.5) -> None:
        self.tolerance = tolerance

    def build(self, rooms: list[SemanticRoom]) -> list[RoomAdjacency]:
        """Build a list of unique adjacency relationships between rooms.

        Rooms are considered adjacent if their polygon boundaries touch
        or the minimum distance between them is <= tolerance.
        """
        adjacencies: list[RoomAdjacency] = []
        seen_pairs: set[tuple[str, str]] = set()

        for i in range(len(rooms)):
            for j in range(i + 1, len(rooms)):
                room_a = rooms[i]
                room_b = rooms[j]

                # Build Shapely polygons
                poly_a = _build_shapely_polygon(room_a.polygon)
                poly_b = _build_shapely_polygon(room_b.polygon)

                # Check adjacency via boundary touch or distance
                if poly_a.touches(poly_b):
                    distance = 0.0
                    shared = poly_a.intersection(poly_b).length
                else:
                    distance = poly_a.distance(poly_b)
                    if distance > self.tolerance:
                        continue
                    shared = 0.0

                # Check door connection
                door_connected = _doors_connect(room_a, room_b, self.tolerance)
                relationship = "door_connected" if door_connected else "adjacent"

                # Create unique pair key (sorted alphabetically)
                pair_key = tuple(sorted([room_a.room_id, room_b.room_id]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                adjacencies.append(
                    RoomAdjacency(
                        source_room_id=room_a.room_id,
                        target_room_id=room_b.room_id,
                        relationship=relationship,
                        distance=distance,
                        shared_boundary_length=shared,
                        door_connected=door_connected,
                    )
                )

        return adjacencies