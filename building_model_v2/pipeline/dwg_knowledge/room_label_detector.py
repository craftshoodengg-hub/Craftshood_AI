"""Detect architectural room labels from DXF TEXT and MTEXT entities."""
from __future__ import annotations

import re
from typing import Any

TEXT_ENTITY_TYPES = {"TEXT", "MTEXT"}

LABEL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Bedroom", re.compile(r"\bM\.?\s*BED(?:\s*ROOM)?\b|\bBED\s*ROOM\b|\bBEDROOM\b|\bBED\b", re.IGNORECASE)),
    ("Kitchen", re.compile(r"\bKITCHEN\b|\bKITCHEN\s*/\s*DINING\b", re.IGNORECASE)),
    ("Living", re.compile(r"\bLIVING\b|\bLIVING\s*/\s*DINING\b|\bHALL\b|\bLOUNGE\b", re.IGNORECASE)),
    ("Dining", re.compile(r"\bDINING\b|\bKITCHEN\s*/\s*DINING\b", re.IGNORECASE)),
    ("Toilet", re.compile(r"\bTOILET\b|\bA\.?TOILET\b|\bC\.?TOILET\b|\bBATH\b|\bW\.?C\b|\bWC\b", re.IGNORECASE)),
    ("Pooja", re.compile(r"\bPOOJA\b|\bPOOJA\s*SHELF\b", re.IGNORECASE)),
    ("Balcony", re.compile(r"\bCOVERED\s+BALCONY\b|\bBALCONY\b", re.IGNORECASE)),
    ("Utility", re.compile(r"\bUTILITY\b|\bWASH\b", re.IGNORECASE)),
    ("Parking", re.compile(r"\bCAR\s+PARKING\b|\bPARKING\b|\bPORTICO\b", re.IGNORECASE)),
    ("Stair", re.compile(r"\bSTAIR(?:CASE)?\b|\bUP\b|\bDN\b", re.IGNORECASE)),
    ("Store", re.compile(r"\bSTORE\b|\bSHELF\b", re.IGNORECASE)),
]

IGNORE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bROAD\b", re.IGNORECASE),
    re.compile(r"\b(?:PROJECT|COMPANY|TITLE|DRAWING|SHEET|CLIENT|DATE|ADDRESS)\b", re.IGNORECASE),
    re.compile(r"\d+\s*['’]\s*\d*(?:\"|”)?\s*[xX×]\s*\d+\s*['’]\s*\d*(?:\"|”)?", re.IGNORECASE),
]


class RoomLabelDetector:
    """Detect room labels from TEXT and MTEXT entities."""

    @classmethod
    def detect(cls, document: Any) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for entity in document.modelspace():
            if entity.dxftype() not in TEXT_ENTITY_TYPES:
                continue

            raw_label = _extract_entity_text(entity)
            if not raw_label:
                continue

            normalized_type = normalize_label(raw_label)
            if normalized_type is None:
                continue

            position = _entity_position(entity)
            layer = str(entity.dxf.layer) if hasattr(entity.dxf, "layer") else ""

            results.append(
                {
                    "raw_label": raw_label,
                    "room_type": normalized_type,
                    "position": position,
                    "layer": layer,
                    "entity_type": entity.dxftype(),
                }
            )

        return results


def normalize_label(text: str) -> str | None:
    """Normalize a room label text value into a known room type."""
    cleaned = _clean_text(text)
    if not cleaned:
        return None

    if any(pattern.search(cleaned) for pattern in IGNORE_PATTERNS):
        return None

    for room_type, pattern in LABEL_PATTERNS:
        if pattern.search(cleaned):
            return room_type

    return None


def _clean_text(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split()).strip()


def _extract_entity_text(entity: Any) -> str:
    if entity.dxftype() == "TEXT":
        return _clean_text(str(getattr(entity.dxf, "text", "")))

    if entity.dxftype() == "MTEXT":
        plain_text = getattr(entity, "plain_text", None)
        if callable(plain_text):
            return _clean_text(str(plain_text()))
        return _clean_text(str(getattr(entity, "text", "")))

    return ""


def _entity_position(entity: Any) -> tuple[float, float]:
    insert = getattr(entity.dxf, "insert", (0.0, 0.0, 0.0))
    try:
        x = float(insert[0])
        y = float(insert[1])
    except (TypeError, ValueError, IndexError):
        x = 0.0
        y = 0.0
    return x, y
