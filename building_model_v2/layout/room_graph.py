"""Room Graph for Building Model v2.

Immutable graph representation of room connectivity.
No AI. No randomness. Pure deterministic graph operations.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from .adjacency_rules import ConnectionType


@dataclass(frozen=True, slots=True)
class RoomConnection:
    source_room_id: str
    target_room_id: str
    connection_type: ConnectionType
    door_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_room_id": self.source_room_id,
            "target_room_id": self.target_room_id,
            "connection_type": self.connection_type.value,
            "door_id": self.door_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RoomConnection:
        return cls(
            source_room_id=data["source_room_id"],
            target_room_id=data["target_room_id"],
            connection_type=ConnectionType(data["connection_type"]),
            door_id=data.get("door_id"),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoomConnection):
            return NotImplemented
        return (self.source_room_id == other.source_room_id and
                self.target_room_id == other.target_room_id and
                self.connection_type == other.connection_type)

    def __hash__(self) -> int:
        return hash((self.source_room_id, self.target_room_id, self.connection_type))


class RoomGraph:
    """Undirected graph of room connectivity."""

    def __init__(self) -> None:
        self._adjacency: Dict[str, Set[str]] = {}
        self._connections: List[RoomConnection] = []

    def add_connection(self, connection: RoomConnection) -> None:
        src = connection.source_room_id
        tgt = connection.target_room_id
        self._adjacency.setdefault(src, set()).add(tgt)
        self._adjacency.setdefault(tgt, set()).add(src)
        self._connections.append(connection)

    def neighbors(self, room_id: str) -> Set[str]:
        return set(self._adjacency.get(room_id, set()))

    def connected(self, room_a: str, room_b: str) -> bool:
        return room_b in self._adjacency.get(room_a, set())

    def shortest_path(self, room_a: str, room_b: str) -> Optional[List[str]]:
        if room_a == room_b:
            return [room_a]
        visited: Set[str] = {room_a}
        queue: deque[Tuple[str, List[str]]] = deque([(room_a, [room_a])])
        while queue:
            current, path = queue.popleft()
            for neighbor in self._adjacency.get(current, set()):
                if neighbor == room_b:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def degree(self, room_id: str) -> int:
        return len(self._adjacency.get(room_id, set()))

    @property
    def room_count(self) -> int:
        return len(self._adjacency)

    @property
    def edge_count(self) -> int:
        return len(self._connections)

    @property
    def rooms(self) -> Set[str]:
        return set(self._adjacency.keys())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_count": self.room_count,
            "edge_count": self.edge_count,
            "rooms": sorted(self.rooms),
            "connections": [c.to_dict() for c in self._connections],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RoomGraph:
        graph = cls()
        for conn_data in data.get("connections", []):
            graph.add_connection(RoomConnection.from_dict(conn_data))
        return graph

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoomGraph):
            return NotImplemented
        return self._adjacency == other._adjacency

    def __hash__(self) -> int:
        return hash(frozenset((k, frozenset(v)) for k, v in self._adjacency.items()))
