"""Wall-width classification from parallel LINE pairs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from loguru import logger

from .parallel_detector import ParallelPair


class WallType(StrEnum):
    """Supported wall classifications."""

    NINE_INCH_BRICK = "9 inch brick wall"
    FOUR_HALF_INCH_BRICK = "4.5 inch brick wall"


DEFAULT_WALL_WIDTHS: dict[WallType, float] = {
    WallType.NINE_INCH_BRICK: 9.0 / 12.0,
    WallType.FOUR_HALF_INCH_BRICK: 4.5 / 12.0,
}


@dataclass(frozen=True, slots=True)
class WallClassifierConfig:
    """Configuration for wall classification."""

    wall_widths: dict[WallType, float] = field(default_factory=lambda: DEFAULT_WALL_WIDTHS.copy())
    width_tolerance: float = 0.05


@dataclass(frozen=True, slots=True)
class WallSegment:
    """A classified wall segment represented by two original LINE entities."""

    id: str
    wall_type: WallType
    width: float
    measured_width: float
    source_pair: ParallelPair

    @property
    def line_ids(self) -> tuple[str, str]:
        return (self.source_pair.line_a.id, self.source_pair.line_b.id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "wall_type": self.wall_type.value,
            "width": self.width,
            "measured_width": self.measured_width,
            "line_ids": list(self.line_ids),
            "source_pair": self.source_pair.to_dict(),
        }


class WallClassifier:
    """Classify parallel pairs as supported brick-wall widths."""

    def __init__(self, config: WallClassifierConfig | None = None) -> None:
        self.config = config or WallClassifierConfig()
        if self.config.width_tolerance < 0:
            raise ValueError("width_tolerance must be non-negative")

    def classify(self, pairs: list[ParallelPair]) -> list[WallSegment]:
        """Return classified wall segments from parallel pairs."""

        segments: list[WallSegment] = []
        for pair in pairs:
            match = self._match_width(pair.perpendicular_distance)
            if match is None:
                continue
            wall_type, expected_width = match
            segments.append(
                WallSegment(
                    id=f"wall-segment-{len(segments) + 1}",
                    wall_type=wall_type,
                    width=expected_width,
                    measured_width=pair.perpendicular_distance,
                    source_pair=pair,
                )
            )

        logger.info("Classified {} wall segments", len(segments))
        return segments

    def _match_width(self, measured_width: float) -> tuple[WallType, float] | None:
        candidates = sorted(
            self.config.wall_widths.items(),
            key=lambda item: abs(measured_width - item[1]),
        )
        for wall_type, expected_width in candidates:
            if abs(measured_width - expected_width) <= self.config.width_tolerance:
                return wall_type, expected_width
        return None
