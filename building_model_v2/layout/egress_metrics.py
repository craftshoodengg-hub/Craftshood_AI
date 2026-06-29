"""Egress Metrics for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Tuple


@dataclass(frozen=True, slots=True)
class ExitPath:
    source_room_id: str
    exit_room_id: str
    room_sequence: tuple[str, ...]
    path_length: float
    door_count: int

    @property
    def room_count(self) -> int:
        return len(self.room_sequence)

    @property
    def is_direct(self) -> bool:
        return self.room_count <= 2

    def to_dict(self) -> Dict[str, Any]:
        return {"source_room_id": self.source_room_id, "exit_room_id": self.exit_room_id, "room_sequence": list(self.room_sequence), "path_length": self.path_length, "door_count": self.door_count}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExitPath:
        return cls(source_room_id=data["source_room_id"], exit_room_id=data["exit_room_id"], room_sequence=tuple(data["room_sequence"]), path_length=data["path_length"], door_count=data["door_count"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExitPath): return NotImplemented
        return self.source_room_id == other.source_room_id and self.exit_room_id == other.exit_room_id and self.room_sequence == other.room_sequence

    def __hash__(self) -> int:
        return hash((self.source_room_id, self.exit_room_id, self.room_sequence))


@dataclass(frozen=True, slots=True)
class EgressMetrics:
    reachable_rooms: FrozenSet[str]
    unreachable_rooms: FrozenSet[str]
    maximum_exit_distance: float
    average_exit_distance: float
    dead_end_rooms: FrozenSet[str]
    exit_paths: tuple[ExitPath, ...]
    egress_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {"reachable_rooms": sorted(self.reachable_rooms), "unreachable_rooms": sorted(self.unreachable_rooms), "maximum_exit_distance": self.maximum_exit_distance, "average_exit_distance": self.average_exit_distance, "dead_end_rooms": sorted(self.dead_end_rooms), "exit_paths": [p.to_dict() for p in self.exit_paths], "egress_score": self.egress_score}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EgressMetrics:
        return cls(reachable_rooms=frozenset(data.get("reachable_rooms", [])), unreachable_rooms=frozenset(data.get("unreachable_rooms", [])), maximum_exit_distance=data["maximum_exit_distance"], average_exit_distance=data["average_exit_distance"], dead_end_rooms=frozenset(data.get("dead_end_rooms", [])), exit_paths=tuple(ExitPath.from_dict(p) for p in data.get("exit_paths", [])), egress_score=data["egress_score"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EgressMetrics): return NotImplemented
        return self.egress_score == other.egress_score and self.reachable_rooms == other.reachable_rooms

    def __hash__(self) -> int:
        return hash((self.egress_score, self.reachable_rooms))
