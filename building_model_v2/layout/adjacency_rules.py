"""Adjacency Rules for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional


class ConnectionType(Enum):
    DIRECT = "direct"
    VIA_DOOR = "via_door"
    VIA_HALL = "via_hall"
    ADJACENT_WALL = "adjacent_wall"
    FLOOR_CONNECT = "floor_connect"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class AdjacencyRule:
    room_type: str
    preferred_adjacent: FrozenSet[str] = field(default_factory=frozenset)
    discouraged_adjacent: FrozenSet[str] = field(default_factory=frozenset)
    required_adjacent: FrozenSet[str] = field(default_factory=frozenset)
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"room_type": self.room_type, "preferred_adjacent": sorted(self.preferred_adjacent), "discouraged_adjacent": sorted(self.discouraged_adjacent), "required_adjacent": sorted(self.required_adjacent), "weight": self.weight, "metadata": dict(self.metadata)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AdjacencyRule:
        return cls(room_type=data["room_type"], preferred_adjacent=frozenset(data.get("preferred_adjacent", [])), discouraged_adjacent=frozenset(data.get("discouraged_adjacent", [])), required_adjacent=frozenset(data.get("required_adjacent", [])), weight=data.get("weight", 1.0), metadata=dict(data.get("metadata", {})))


@dataclass(frozen=True, slots=True)
class AdjacencyRuleSet:
    rules: tuple[AdjacencyRule, ...]

    def get_rule(self, room_type: str) -> Optional[AdjacencyRule]:
        rt = room_type.lower()
        for rule in self.rules:
            if rule.room_type.lower() == rt:
                return rule
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {"rules": [r.to_dict() for r in self.rules]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AdjacencyRuleSet:
        return cls(rules=tuple(AdjacencyRule.from_dict(r) for r in data.get("rules", [])))


def create_default_rules() -> AdjacencyRuleSet:
    rules = [
        AdjacencyRule("Living", frozenset({"Entrance", "Dining"}), frozenset(), frozenset(), 1.0),
        AdjacencyRule("Dining", frozenset({"Kitchen", "Living"}), frozenset(), frozenset(), 0.9),
        AdjacencyRule("Kitchen", frozenset({"Dining", "Utility"}), frozenset({"Bedroom"}), frozenset(), 0.8),
        AdjacencyRule("Utility", frozenset({"Kitchen"}), frozenset(), frozenset(), 0.6),
        AdjacencyRule("Bedroom", frozenset({"Bathroom"}), frozenset({"Garage", "Common Toilet"}), frozenset({"Bathroom"}), 0.9),
        AdjacencyRule("Bedroom", frozenset({"Bathroom", "Corridor"}), frozenset({"Garage"}), frozenset(), 0.7),
        AdjacencyRule("Bathroom", frozenset({"Bedroom", "Bedroom", "Corridor"}), frozenset({"Kitchen", "Dining"}), frozenset(), 0.7),
        AdjacencyRule("Toilet", frozenset({"Bedroom", "Corridor"}), frozenset({"Kitchen", "Dining", "Pooja"}), frozenset(), 0.6),
        AdjacencyRule("Common Toilet", frozenset({"Corridor", "Stair"}), frozenset({"Kitchen", "Dining", "Pooja"}), frozenset(), 0.5),
        AdjacencyRule("Pooja", frozenset({"Entrance", "Living", "Corridor"}), frozenset({"Toilet", "Common Toilet", "Kitchen"}), frozenset(), 0.6),
        AdjacencyRule("Stair", frozenset({"Corridor", "Living", "Entrance"}), frozenset({"Bathroom", "Toilet"}), frozenset({"Corridor"}), 0.7),
        AdjacencyRule("Garage", frozenset({"Entrance", "Corridor"}), frozenset({"Bedroom", "Bedroom", "Pooja"}), frozenset(), 0.5),
        AdjacencyRule("Balcony", frozenset({"Living", "Bedroom", "Bedroom"}), frozenset(), frozenset(), 0.4),
    ]
    return AdjacencyRuleSet(rules=tuple(rules))
