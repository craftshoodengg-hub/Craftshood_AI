"""Parallel LINE pair detection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from loguru import logger

from .line_reader import LineEntity, Point2D


@dataclass(frozen=True, slots=True)
class ParallelDetectorConfig:
    """Configuration for parallel line detection."""

    angle_tolerance_degrees: float = 1.0
    max_perpendicular_distance: float = 1.0
    min_perpendicular_distance: float = 1e-6
    min_overlap_length: float = 1e-6


@dataclass(frozen=True, slots=True)
class ParallelPair:
    """Two parallel lines separated by a configurable perpendicular distance."""

    id: str
    line_a: LineEntity
    line_b: LineEntity
    angle_difference: float
    perpendicular_distance: float

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["line_a"] = self.line_a.to_dict()
        payload["line_b"] = self.line_b.to_dict()
        return payload


class ParallelDetector:
    """Find candidate parallel line pairs."""

    def __init__(self, config: ParallelDetectorConfig | None = None) -> None:
        self.config = config or ParallelDetectorConfig()
        if self.config.angle_tolerance_degrees < 0:
            raise ValueError("angle_tolerance_degrees must be non-negative")
        if self.config.max_perpendicular_distance < 0:
            raise ValueError("max_perpendicular_distance must be non-negative")
        if self.config.min_perpendicular_distance < 0:
            raise ValueError("min_perpendicular_distance must be non-negative")
        if self.config.min_overlap_length < 0:
            raise ValueError("min_overlap_length must be non-negative")

    def find_pairs(self, lines: list[LineEntity]) -> list[ParallelPair]:
        """Return all line pairs matching the configured parallel conditions."""

        pairs: list[ParallelPair] = []
        for first_index, line_a in enumerate(lines):
            for second_index in range(first_index + 1, len(lines)):
                line_b = lines[second_index]
                angle_difference = angle_difference_degrees(line_a.angle, line_b.angle)
                if angle_difference > self.config.angle_tolerance_degrees:
                    continue

                distance = perpendicular_distance(line_a, line_b)
                if distance > self.config.max_perpendicular_distance:
                    continue
                if distance < self.config.min_perpendicular_distance:
                    continue
                if projection_overlap_length(line_a, line_b) < self.config.min_overlap_length:
                    continue

                pairs.append(
                    ParallelPair(
                        id=f"{line_a.id}|{line_b.id}",
                        line_a=line_a,
                        line_b=line_b,
                        angle_difference=angle_difference,
                        perpendicular_distance=distance,
                    )
                )

        logger.info("Detected {} parallel line pairs", len(pairs))
        return pairs


def angle_difference_degrees(angle_a: float, angle_b: float) -> float:
    """Return the smallest directionless angle difference in degrees."""

    difference = abs((angle_a % 180.0) - (angle_b % 180.0))
    return min(difference, 180.0 - difference)


def perpendicular_distance(line_a: LineEntity, line_b: LineEntity) -> float:
    """Return perpendicular distance between two parallel line carriers."""

    start = line_a.start.to_array()
    end = line_a.end.to_array()
    point = _midpoint(line_b.start, line_b.end)
    base = end - start
    denominator = np.linalg.norm(base)
    if denominator == 0:
        return float("inf")
    delta = point - start
    numerator = abs((base[0] * delta[1]) - (base[1] * delta[0]))
    return float(numerator / denominator)


def projection_overlap_length(line_a: LineEntity, line_b: LineEntity) -> float:
    """Return overlap length of ``line_b`` projected onto ``line_a``."""

    start = line_a.start.to_array()
    end = line_a.end.to_array()
    base = end - start
    base_length = np.linalg.norm(base)
    if base_length == 0:
        return 0.0

    direction = base / base_length
    interval_a = (0.0, float(base_length))
    projected = [
        float(np.dot(line_b.start.to_array() - start, direction)),
        float(np.dot(line_b.end.to_array() - start, direction)),
    ]
    interval_b = (min(projected), max(projected))
    return max(0.0, min(interval_a[1], interval_b[1]) - max(interval_a[0], interval_b[0]))


def _midpoint(start: Point2D, end: Point2D) -> np.ndarray:
    return (start.to_array() + end.to_array()) / 2.0
