"""Rule-based plot information detection from DXF text."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from loguru import logger

from .text_extractor import TextEntity


PLOT_DIMENSION_PATTERN = re.compile(
    r"\b(?P<feet>\d+(?:\.\d+)?)\s*'\s*(?P<inches>\d+(?:\.\d+)?)?\s*(?:\"|''|in)?\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class PlotDimension:
    """Detected plot dimension with parsed feet and inch components."""

    value: str
    feet: float
    inches: float
    text: str
    x: float
    y: float
    layer: str
    space: str

    @property
    def total_inches(self) -> float:
        return (self.feet * 12.0) + self.inches

    @property
    def total_feet(self) -> float:
        return self.feet + (self.inches / 12.0)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["total_inches"] = self.total_inches
        payload["total_feet"] = self.total_feet
        return payload


def detect_plot_dimensions(text_entities: Iterable[TextEntity]) -> list[PlotDimension]:
    """Detect plot dimension strings like 30'0" and 50'0"."""

    dimensions: list[PlotDimension] = []
    for entity in text_entities:
        for match in PLOT_DIMENSION_PATTERN.finditer(entity.text):
            feet = float(match.group("feet"))
            inches = float(match.group("inches") or 0)
            dimensions.append(
                PlotDimension(
                    value=_normalize_dimension(match.group(0), feet, inches),
                    feet=feet,
                    inches=inches,
                    text=entity.text,
                    x=entity.position.x,
                    y=entity.position.y,
                    layer=entity.layer,
                    space=entity.space,
                )
            )

    logger.info("Detected {} plot dimensions", len(dimensions))
    return dimensions


def _normalize_dimension(raw_value: str, feet: float, inches: float) -> str:
    if feet.is_integer() and inches.is_integer():
        return f"{int(feet)}'{int(inches)}\""
    return raw_value.strip()
