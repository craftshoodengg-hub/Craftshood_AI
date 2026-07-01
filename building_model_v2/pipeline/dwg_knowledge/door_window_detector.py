"""Detect doors and windows from DXF drawings."""
from __future__ import annotations

import re
from typing import Any

INSERT_ENTITY_TYPE = "INSERT"
TEXT_ENTITY_TYPES = {"TEXT", "MTEXT"}

DOOR_PATTERN = re.compile(
    r"\b(?:door|single\s+door|double\s+door|main\s+door|entrance|dr(?:\d?\b)|d[12])\b",
    re.IGNORECASE,
)
WINDOW_PATTERN = re.compile(
    r"\b(?:window|win|w[12]|ventilator|vent)\b",
    re.IGNORECASE,
)

DETECTION_FIELDS = ("type", "name", "position", "layer", "entity_type")


class DoorWindowDetector:
    """Detect doors and windows from DXF documents."""

    def detect(self, document: Any) -> dict[str, Any]:
        """Detect all doors and windows from a DXF document."""
        doors = self.detect_doors(document)
        windows = self.detect_windows(document)

        return {
            "doors": doors,
            "windows": windows,
            "door_count": len(doors),
            "window_count": len(windows),
        }

    def detect_doors(self, document: Any) -> list[dict[str, Any]]:
        """Detect door entities from INSERT, TEXT, and MTEXT entities."""
        return [
            detection
            for detection in self._detect_all(document, DOOR_PATTERN, "Door")
        ]

    def detect_windows(self, document: Any) -> list[dict[str, Any]]:
        """Detect window entities from INSERT, TEXT, and MTEXT entities."""
        return [
            detection
            for detection in self._detect_all(document, WINDOW_PATTERN, "Window")
        ]

    def _detect_all(
        self, document: Any, pattern: re.Pattern[str], object_type: str
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for entity in document.modelspace():
            entity_type = entity.dxftype()
            if entity_type == INSERT_ENTITY_TYPE:
                detection = _detect_insert_entity(entity, pattern)
            elif entity_type in TEXT_ENTITY_TYPES:
                detection = _detect_text_entity(entity, pattern)
            else:
                detection = None

            if detection is not None:
                detection["type"] = object_type
                results.append(detection)

        return results


def _detect_insert_entity(entity: Any, pattern: re.Pattern[str]) -> dict[str, Any] | None:
    layer = _get_layer(entity)
    block_name = _get_block_name(entity)

    if _matches_pattern(block_name, pattern):
        return _build_detection(block_name, layer, entity)

    if _matches_pattern(layer, pattern):
        return _build_detection(layer, layer, entity)

    return None


def _detect_text_entity(entity: Any, pattern: re.Pattern[str]) -> dict[str, Any] | None:
    text = _extract_entity_text(entity)
    if not text:
        return None

    if _matches_pattern(text, pattern):
        layer = _get_layer(entity)
        return _build_detection(text, layer, entity)

    return None


def _build_detection(name: str, layer: str, entity: Any) -> dict[str, Any]:
    return {
        "name": name,
        "position": _entity_position(entity),
        "layer": layer,
        "entity_type": entity.dxftype(),
    }


def _matches_pattern(value: str, pattern: re.Pattern[str]) -> bool:
    return bool(pattern.search(_clean_text(value)))


def _get_layer(entity: Any) -> str:
    try:
        return str(entity.dxf.layer)
    except AttributeError:
        return ""


def _get_block_name(entity: Any) -> str:
    try:
        return str(entity.dxf.name)
    except AttributeError:
        return ""


def _extract_entity_text(entity: Any) -> str:
    if entity.dxftype() == "TEXT":
        return _clean_text(str(getattr(entity.dxf, "text", "")))

    if entity.dxftype() == "MTEXT":
        plain_text = getattr(entity, "plain_text", None)
        if callable(plain_text):
            return _clean_text(str(plain_text()))
        return _clean_text(str(getattr(entity.dxf, "text", "")))

    return ""


def _clean_text(value: str) -> str:
    normalized = value.replace("\r", " ").replace("\n", " ")
    normalized = re.sub(r"[^A-Za-z0-9]+", " ", normalized)
    return " ".join(normalized.split()).strip()


def _entity_position(entity: Any) -> tuple[float, float]:
    insert = getattr(entity.dxf, "insert", (0.0, 0.0, 0.0))
    try:
        x = float(insert[0])
        y = float(insert[1])
    except (TypeError, ValueError, IndexError):
        x = 0.0
        y = 0.0
    return x, y
