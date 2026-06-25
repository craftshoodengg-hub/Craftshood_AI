"""Rule-based room and plan-label detection for DXF text."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from loguru import logger

from .text_extractor import TextEntity


ROOM_PATTERNS: dict[str, re.Pattern[str]] = {
    "Living": re.compile(r"\bLIVING(?:\s+ROOM)?\b", re.IGNORECASE),
    "Kitchen": re.compile(r"\bKITCHEN\b", re.IGNORECASE),
    "Dining": re.compile(r"\bDINING\b", re.IGNORECASE),
    "M.bed room": re.compile(r"\bM\.?\s*BED\s*ROOM\b|\bMASTER\s+BED\s*ROOM\b", re.IGNORECASE),
    "Bed room": re.compile(r"\bBED\s*ROOM\b|\bBEDROOM\b", re.IGNORECASE),
    "Toilet": re.compile(r"\bTOILET\b|\bWC\b", re.IGNORECASE),
    "Sitout": re.compile(r"\bSIT\s*OUT\b|\bSITOUT\b", re.IGNORECASE),
    "Portico": re.compile(r"\bPORTICO\b", re.IGNORECASE),
    "Lounge": re.compile(r"\bLOUNGE\b", re.IGNORECASE),
}

FLOOR_TITLE_PATTERN = re.compile(
    r"\b(?:GROUND|FIRST|SECOND|THIRD|FOURTH|FIFTH|TYPICAL)\s+FLOOR\s+PLAN\b",
    re.IGNORECASE,
)
BUILT_UP_AREA_PATTERN = re.compile(
    r"\b(?:BUILT\s*[- ]?\s*UP|BUILTUP)\s+AREA\b|"
    r"\bAREA\s*[:=-]?\s*\d+(?:\.\d+)?\s*(?:SQ\.?\s*FT|SFT|SQFT|M2|SQ\.?\s*M)?\b",
    re.IGNORECASE,
)
ROAD_PATTERN = re.compile(r"\bROAD\b", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Detection:
    """A text-based detection with source entity metadata."""

    label: str
    text: str
    category: str
    x: float
    y: float
    layer: str
    space: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_rooms(text_entities: Iterable[TextEntity]) -> list[Detection]:
    """Detect known room labels from extracted DXF text."""

    detections: list[Detection] = []
    for entity in text_entities:
        normalized = _normalize(entity.text)
        for room_name, pattern in ROOM_PATTERNS.items():
            if pattern.search(normalized):
                detections.append(_build_detection(room_name, "room", entity))
                break

    logger.info("Detected {} room labels", len(detections))
    return detections


def detect_floor_titles(text_entities: Iterable[TextEntity]) -> list[Detection]:
    """Detect floor-plan title labels such as GROUND FLOOR PLAN."""

    detections = [
        _build_detection(_normalize(match.group(0)).title(), "floor_title", entity)
        for entity in text_entities
        if (match := FLOOR_TITLE_PATTERN.search(_normalize(entity.text)))
    ]
    logger.info("Detected {} floor title labels", len(detections))
    return detections


def detect_built_up_areas(text_entities: Iterable[TextEntity]) -> list[Detection]:
    """Detect built-up area notes from extracted text."""

    detections = [
        _build_detection(entity.text, "built_up_area", entity)
        for entity in text_entities
        if BUILT_UP_AREA_PATTERN.search(_normalize(entity.text))
    ]
    logger.info("Detected {} built-up area labels", len(detections))
    return detections


def detect_road_labels(text_entities: Iterable[TextEntity]) -> list[Detection]:
    """Detect ROAD labels from extracted text."""

    detections = [
        _build_detection("ROAD", "road", entity)
        for entity in text_entities
        if ROAD_PATTERN.search(_normalize(entity.text))
    ]
    logger.info("Detected {} road labels", len(detections))
    return detections


def _build_detection(label: str, category: str, entity: TextEntity) -> Detection:
    return Detection(
        label=label,
        text=entity.text,
        category=category,
        x=entity.position.x,
        y=entity.position.y,
        layer=entity.layer,
        space=entity.space,
    )


def _normalize(value: str) -> str:
    return " ".join(value.replace("\\P", " ").split()).strip()
