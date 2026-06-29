"""Circulation Metrics for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass(frozen=True, slots=True)
class CirculationPath:
    source_room_id: str
    target_room_id: str
    room_sequence: tuple[str, ...]
    door_count: int
    path_length: float

    @property
    def room_count(self) -> int:
        return len(self.room_sequence)

    @property
    def is_direct(self) -> bool:
        return self.room_count <= 2

    def to_dict(self) -> Dict[str, Any]:
        return {"source_room_id": self.source_room_id, "target_room_id": self.target_room_id, "room_sequence": list(self.room_sequence), "door_count": self.door_count, "path_length": self.path_length}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CirculationPath:
        return cls(source_room_id=data["source_room_id"], target_room_id=data["target_room_id"], room_sequence=tuple(data["room_sequence"]), door_count=data["door_count"], path_length=data["path_length"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CirculationPath): return NotImplemented
        return self.source_room_id == other.source_room_id and self.target_room_id == other.target_room_id and self.room_sequence == other.room_sequence

    def __hash__(self) -> int:
        return hash((self.source_room_id, self.target_room_id, self.room_sequence))


@dataclass(frozen=True, slots=True)
class CirculationMetrics:
    average_path_length: float
    maximum_path_length: float
    isolated_rooms: frozenset[str]
    dead_end_rooms: frozenset[str]
    circulation_efficiency: float
    reachable_rooms: frozenset[str]
    unreachable_rooms: frozenset[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"average_path_length": self.average_path_length, "maximum_path_length": self.maximum_path_length, "isolated_rooms": sorted(self.isolated_rooms), "dead_end_rooms": sorted(self.dead_end_rooms), "circulation_efficiency": self.circulation_efficiency, "reachable_rooms": sorted(self.reachable_rooms), "unreachable_rooms": sorted(self.unreachable_rooms)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CirculationMetrics:
        return cls(average_path_length=data["average_path_length"], maximum_path_length=data["maximum_path_length"], isolated_rooms=frozenset(data.get("isolated_rooms", [])), dead_end_rooms=frozenset(data.get("dead_end_rooms", [])), circulation_efficiency=data["circulation_efficiency"], reachable_rooms=frozenset(data.get("reachable_rooms", [])), unreachable_rooms=frozenset(data.get("unreachable_rooms", [])))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CirculationMetrics): return NotImplemented
        return self.average_path_length == other.average_path_length and self.maximum_path_length == other.maximum_path_length and self.isolated_rooms == other.isolated_rooms

    def __hash__(self) -> int:
        return hash((self.average_path_length, self.maximum_path_length, self.isolated_rooms))
