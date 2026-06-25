"""Text normalization for room labels and extracted drawing text."""

from __future__ import annotations

import re
from collections.abc import Mapping
from enum import StrEnum


class RoomName(StrEnum):
    """Supported standard room names."""

    LIVING = "Living"
    MASTER_BED_ROOM = "M.bed room"
    BED_ROOM = "Bed room"
    KITCHEN = "Kitchen"
    DINING = "Dining"
    TOILET = "Toilet"
    SITOUT = "Sitout"
    PORTICO = "Portico"


DEFAULT_ROOM_MAPPINGS: dict[RoomName, tuple[str, ...]] = {
    RoomName.LIVING: ("living", "living room", "liv", "hall"),
    RoomName.MASTER_BED_ROOM: (
        "m bed room",
        "m.bed room",
        "master bed room",
        "master bedroom",
        "mbr",
    ),
    RoomName.BED_ROOM: ("bed room", "bedroom", "br"),
    RoomName.KITCHEN: ("kitchen", "kit"),
    RoomName.DINING: ("dining", "dining room", "din"),
    RoomName.TOILET: ("toilet", "wc", "bath", "bathroom", "restroom"),
    RoomName.SITOUT: ("sitout", "sit out", "sitting out"),
    RoomName.PORTICO: ("portico", "porch", "car porch"),
}


class TextNormalizer:
    """Normalize extracted text values without performing detection."""

    def __init__(
        self,
        room_mappings: Mapping[RoomName | str, tuple[str, ...] | list[str]] | None = None,
    ) -> None:
        self._room_aliases = _compile_room_aliases(room_mappings or DEFAULT_ROOM_MAPPINGS)

    def clean(self, value: str | None) -> str:
        """Return whitespace-normalized drawing text."""

        if value is None:
            return ""
        text = str(value).replace("\\P", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def normalize_room_name(self, value: str | None) -> RoomName | None:
        """Return a standard room name when ``value`` is a known room label."""

        normalized = _room_key(self.clean(value))
        if not normalized:
            return None

        for room_name, aliases in self._room_aliases.items():
            if normalized in aliases:
                return room_name
        return None


def _compile_room_aliases(
    mappings: Mapping[RoomName | str, tuple[str, ...] | list[str]],
) -> dict[RoomName, set[str]]:
    compiled: dict[RoomName, set[str]] = {}
    for raw_room, aliases in mappings.items():
        room_name = _coerce_room(raw_room)
        compiled[room_name] = {_room_key(alias) for alias in aliases if _room_key(alias)}
    return compiled


def _coerce_room(value: RoomName | str) -> RoomName:
    if isinstance(value, RoomName):
        return value
    for room_name in RoomName:
        if value == room_name.value or value.upper() == room_name.name:
            return room_name
    raise ValueError(f"Unsupported room name: {value!r}")


def _room_key(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[_./\\-]+", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())
