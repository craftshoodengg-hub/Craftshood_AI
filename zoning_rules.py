"""Configurable zoning rules for room classification."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ZoningRule:
    """A rule describing zoning requirements for a room type."""

    room_name: str
    zone: str
    privacy: str
    preferred_neighbors: tuple[str, ...] = ()
    avoid_neighbors: tuple[str, ...] = ()
    requires_exterior_wall: bool = False
    requires_ventilation: bool = False
    minimum_area: float | None = None
    maximum_area: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["preferred_neighbors"] = list(self.preferred_neighbors)
        payload["avoid_neighbors"] = list(self.avoid_neighbors)
        return payload


DEFAULT_UNKNOWN_RULE = ZoningRule(
    room_name="Unknown",
    zone="Unknown",
    privacy="Unknown",
    preferred_neighbors=(),
    avoid_neighbors=(),
    requires_exterior_wall=False,
    requires_ventilation=False,
    minimum_area=None,
    maximum_area=None,
)


DEFAULT_ZONING_RULES: dict[str, ZoningRule] = {
    "Living": ZoningRule(
        room_name="Living",
        zone="Public",
        privacy="Public",
        preferred_neighbors=("Dining", "Sitout"),
        avoid_neighbors=("Toilet",),
        requires_exterior_wall=True,
        requires_ventilation=True,
        minimum_area=120,
        maximum_area=350,
    ),
    "M.bed room": ZoningRule(
        room_name="M.bed room",
        zone="Private",
        privacy="Private",
        preferred_neighbors=("Toilet",),
        avoid_neighbors=("Kitchen", "Portico"),
        requires_exterior_wall=True,
        requires_ventilation=True,
        minimum_area=120,
        maximum_area=260,
    ),
    "Bed room": ZoningRule(
        room_name="Bed room",
        zone="Private",
        privacy="Private",
        preferred_neighbors=("Toilet",),
        avoid_neighbors=("Kitchen", "Portico"),
        requires_exterior_wall=True,
        requires_ventilation=True,
        minimum_area=100,
        maximum_area=220,
    ),
    "Kitchen": ZoningRule(
        room_name="Kitchen",
        zone="Service",
        privacy="Semi-Private",
        preferred_neighbors=("Dining", "Utility"),
        avoid_neighbors=("Bedroom",),
        requires_exterior_wall=True,
        requires_ventilation=True,
        minimum_area=60,
        maximum_area=180,
    ),
    "Dining": ZoningRule(
        room_name="Dining",
        zone="Public",
        privacy="Semi-Private",
        preferred_neighbors=("Kitchen", "Living"),
        avoid_neighbors=("Toilet",),
        requires_exterior_wall=False,
        requires_ventilation=False,
        minimum_area=80,
        maximum_area=220,
    ),
    "Toilet": ZoningRule(
        room_name="Toilet",
        zone="Service",
        privacy="Private",
        preferred_neighbors=("Bed room", "M.bed room"),
        avoid_neighbors=("Kitchen", "Dining"),
        requires_exterior_wall=True,
        requires_ventilation=True,
        minimum_area=25,
        maximum_area=80,
    ),
    "Sitout": ZoningRule(
        room_name="Sitout",
        zone="Public",
        privacy="Public",
        preferred_neighbors=("Living", "Portico"),
        avoid_neighbors=("Toilet",),
        requires_exterior_wall=True,
        requires_ventilation=True,
        minimum_area=40,
        maximum_area=160,
    ),
    "Portico": ZoningRule(
        room_name="Portico",
        zone="Public",
        privacy="Public",
        preferred_neighbors=("Sitout", "Living"),
        avoid_neighbors=("Toilet", "Kitchen"),
        requires_exterior_wall=True,
        requires_ventilation=True,
        minimum_area=80,
        maximum_area=300,
    ),
}


DEFAULT_ALIASES: dict[str, str] = {
    "bedroom": "Bed room",
    "bed room": "Bed room",
    "br": "Bed room",
    "master bedroom": "M.bed room",
    "master bed room": "M.bed room",
    "m bed room": "M.bed room",
    "m.bed room": "M.bed room",
    "living room": "Living",
    "hall": "Living",
    "dining room": "Dining",
    "wc": "Toilet",
    "bath": "Toilet",
    "bathroom": "Toilet",
    "sit out": "Sitout",
    "sitout": "Sitout",
    "porch": "Portico",
}


@dataclass(frozen=True, slots=True)
class ZoningRulesConfig:
    """Rule dictionary configuration."""

    rules: Mapping[str, ZoningRule] = field(default_factory=lambda: DEFAULT_ZONING_RULES.copy())
    aliases: Mapping[str, str] = field(default_factory=lambda: DEFAULT_ALIASES.copy())
    unknown_rule: ZoningRule = DEFAULT_UNKNOWN_RULE


class ZoningRuleBook:
    """Lookup service for zoning rules."""

    def __init__(self, config: ZoningRulesConfig | None = None) -> None:
        self.config = config or ZoningRulesConfig()
        self._rules = dict(self.config.rules)
        self._aliases = {
            normalize_room_key(alias): canonical
            for alias, canonical in self.config.aliases.items()
        }
        for room_name in self._rules:
            self._aliases.setdefault(normalize_room_key(room_name), room_name)

    def lookup(self, room_name: str | None) -> ZoningRule:
        """Return a matching zoning rule or the configured unknown fallback."""

        key = normalize_room_key(room_name)
        canonical_name = self._aliases.get(key)
        if canonical_name is None:
            return self.config.unknown_rule
        return self._rules.get(canonical_name, self.config.unknown_rule)


def normalize_room_key(value: str | None) -> str:
    """Normalize room names and aliases into comparable keys."""

    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[_./\\-]+", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())
