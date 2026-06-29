"""Privacy Metrics for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional


@dataclass(frozen=True, slots=True)
class PrivacyConflict:
    room_a: str
    room_b: str
    issue_code: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {"room_a": self.room_a, "room_b": self.room_b, "issue_code": self.issue_code, "description": self.description}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PrivacyConflict:
        return cls(room_a=data["room_a"], room_b=data["room_b"], issue_code=data["issue_code"], description=data["description"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PrivacyConflict): return NotImplemented
        return self.room_a == other.room_a and self.room_b == other.room_b and self.issue_code == other.issue_code

    def __hash__(self) -> int:
        return hash((self.room_a, self.room_b, self.issue_code))


@dataclass(frozen=True, slots=True)
class PrivacyMetrics:
    public_rooms: FrozenSet[str]
    semi_private_rooms: FrozenSet[str]
    private_rooms: FrozenSet[str]
    privacy_score: float
    privacy_conflicts: tuple[PrivacyConflict, ...]
    circulation_crossings: int

    def to_dict(self) -> Dict[str, Any]:
        return {"public_rooms": sorted(self.public_rooms), "semi_private_rooms": sorted(self.semi_private_rooms), "private_rooms": sorted(self.private_rooms), "privacy_score": self.privacy_score, "privacy_conflicts": [c.to_dict() for c in self.privacy_conflicts], "circulation_crossings": self.circulation_crossings}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PrivacyMetrics:
        return cls(public_rooms=frozenset(data.get("public_rooms", [])), semi_private_rooms=frozenset(data.get("semi_private_rooms", [])), private_rooms=frozenset(data.get("private_rooms", [])), privacy_score=data["privacy_score"], privacy_conflicts=tuple(PrivacyConflict.from_dict(c) for c in data.get("privacy_conflicts", [])), circulation_crossings=data.get("circulation_crossings", 0))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PrivacyMetrics): return NotImplemented
        return self.privacy_score == other.privacy_score and self.privacy_conflicts == other.privacy_conflicts

    def __hash__(self) -> int:
        return hash((self.privacy_score, self.privacy_conflicts))
