"""Detect plot information from DXF text entities."""
from __future__ import annotations

import re
from typing import Any

TEXT_ENTITY_TYPES = {"TEXT", "MTEXT"}

ORIENTATION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("North", re.compile(r"\bNORTH\b", re.IGNORECASE)),
    ("South", re.compile(r"\bSOUTH\b", re.IGNORECASE)),
    ("East", re.compile(r"\bEAST\b", re.IGNORECASE)),
    ("West", re.compile(r"\bWEST\b", re.IGNORECASE)),
    ("North", re.compile(r"\bN\b", re.IGNORECASE)),
    ("South", re.compile(r"\bS\b", re.IGNORECASE)),
    ("East", re.compile(r"\bE\b", re.IGNORECASE)),
    ("West", re.compile(r"\bW\b", re.IGNORECASE)),
]

_PLOT_DIMENSION = r"\d+(?:\.\d+)?(?:'\d*(?:\.\d+)?\"?)?"
PLOT_SIZE_PATTERN = re.compile(
    rf"(?<!\S)(?P<side1>{_PLOT_DIMENSION})\s*[xX×]\s*(?P<side2>{_PLOT_DIMENSION})(?!\S)"
)

IGNORE_PHRASES = [
    "Bedroom",
    "Kitchen",
    "Dining",
    "Living",
    "Hall",
    "Toilet",
    "Bath",
    "Road",
    "Road Width",
    "Scale",
    "North Arrow",
    "Architect",
    "Company Name",
    "Drawing Number",
    "Phone Numbers",
    "Dimensions",
    "Furniture Labels",
]

IGNORE_PATTERNS = [
    re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
    for phrase in IGNORE_PHRASES
]


class PlotInformationDetector:
    """Detect plot orientation and size from DXF text annotations."""

    def detect(self, document: Any) -> dict[str, float | None]:
        """Detect plot metadata from a DXF document."""
        orientation = self.detect_orientation(document)
        width, depth = self.detect_plot_size(document)
        area = self.detect_plot_area(width, depth)

        return {
            "plot_width": width,
            "plot_depth": depth,
            "plot_area": area,
            "orientation": orientation,
        }

    def detect_orientation(self, document: Any) -> str | None:
        """Detect the plot orientation from TEXT and MTEXT entities."""
        for entity in document.modelspace():
            if entity.dxftype() not in TEXT_ENTITY_TYPES:
                continue

            text = _extract_entity_text(entity)
            if not text or _is_ignored_text(text):
                continue

            for orientation, pattern in ORIENTATION_PATTERNS:
                if pattern.search(text):
                    return orientation

        return None

    def detect_plot_size(self, document: Any) -> tuple[float | None, float | None]:
        """Detect the plot width and depth from TEXT and MTEXT entities."""
        for entity in document.modelspace():
            if entity.dxftype() not in TEXT_ENTITY_TYPES:
                continue

            text = _extract_entity_text(entity)
            if not text or _is_ignored_text(text):
                continue

            match = PLOT_SIZE_PATTERN.search(text)
            if not match:
                continue

            width = _parse_plot_dimension(match.group("side1"))
            depth = _parse_plot_dimension(match.group("side2"))
            if width is not None and depth is not None:
                return width, depth

        return None, None

    def detect_plot_area(
        self, width: float | None, depth: float | None
    ) -> float | None:
        """Calculate the plot area from width and depth."""
        if width is None or depth is None:
            return None
        return width * depth


def _extract_entity_text(entity: Any) -> str:
    if entity.dxftype() == "TEXT":
        return _clean_text(str(getattr(entity.dxf, "text", "")))

    if entity.dxftype() == "MTEXT":
        plain_text = getattr(entity, "plain_text", None)
        if callable(plain_text):
            return _clean_text(str(plain_text()))
        return _clean_text(str(getattr(entity, "text", "")))

    return ""


def _clean_text(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split())


def _is_ignored_text(value: str) -> bool:
    cleaned = _clean_text(value)
    return any(pattern.search(cleaned) for pattern in IGNORE_PATTERNS)


def _parse_plot_dimension(value: str) -> float | None:
    cleaned = value.replace(" ", "").rstrip('"')

    if cleaned.endswith("'"):
        cleaned = cleaned[:-1]

    match = re.match(r"^(?P<feet>\d+(?:\.\d+)?)(?:'(?P<inches>\d+(?:\.\d+)?))?$", cleaned)
    if match:
        feet = float(match.group("feet"))
        inches_text = match.group("inches")
        inches = float(inches_text) if inches_text else 0.0
        return feet + inches / 12.0

    try:
        return float(cleaned)
    except ValueError:
        return None
