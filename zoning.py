"""Room zoning classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zoning_rules import ZoningRule, ZoningRuleBook, ZoningRulesConfig


@dataclass(frozen=True, slots=True)
class RoomZoning:
    """Zoning result for one room."""

    room_id: str
    room_name: str
    zone: str
    privacy: str
    preferred_neighbors: tuple[str, ...]
    avoid_neighbors: tuple[str, ...]
    requires_exterior_wall: bool
    requires_ventilation: bool
    minimum_area: float | None
    maximum_area: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "zone": self.zone,
            "privacy": self.privacy,
            "preferred_neighbors": list(self.preferred_neighbors),
            "avoid_neighbors": list(self.avoid_neighbors),
            "requires_exterior_wall": self.requires_exterior_wall,
            "requires_ventilation": self.requires_ventilation,
            "minimum_area": self.minimum_area,
            "maximum_area": self.maximum_area,
        }


class ZoningClassifier:
    """Classify rooms into functional zoning metadata."""

    def __init__(self, config: ZoningRulesConfig | None = None) -> None:
        self.rule_book = ZoningRuleBook(config)

    def classify(self, room_id: str, room_name: str | None) -> dict[str, Any]:
        """Return zoning data as a JSON-friendly dictionary."""

        return self.classify_result(room_id, room_name).to_dict()

    def classify_result(self, room_id: str, room_name: str | None) -> RoomZoning:
        """Return a typed zoning result."""

        if not str(room_id).strip():
            raise ValueError("room_id cannot be empty")

        rule = self.rule_book.lookup(room_name)
        output_name = rule.room_name if rule is not self.rule_book.config.unknown_rule else str(room_name or "Unknown")
        if not output_name.strip():
            output_name = "Unknown"
        return _result_from_rule(str(room_id), output_name, rule)


def classify_room_zone(
    room_id: str,
    room_name: str | None,
    *,
    config: ZoningRulesConfig | None = None,
) -> dict[str, Any]:
    """Convenience wrapper around :class:`ZoningClassifier`."""

    return ZoningClassifier(config).classify(room_id, room_name)


def _result_from_rule(room_id: str, room_name: str, rule: ZoningRule) -> RoomZoning:
    return RoomZoning(
        room_id=room_id,
        room_name=room_name,
        zone=rule.zone,
        privacy=rule.privacy,
        preferred_neighbors=rule.preferred_neighbors,
        avoid_neighbors=rule.avoid_neighbors,
        requires_exterior_wall=rule.requires_exterior_wall,
        requires_ventilation=rule.requires_ventilation,
        minimum_area=rule.minimum_area,
        maximum_area=rule.maximum_area,
    )
