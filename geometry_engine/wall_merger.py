"""Logical wall merging."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger
from shapely.geometry import LineString

from .line_reader import LineEntity
from .wall_classifier import WallSegment, WallType


@dataclass(frozen=True, slots=True)
class WallMergerConfig:
    """Configuration for merging connected wall segments."""

    connection_tolerance: float = 0.01


@dataclass(frozen=True, slots=True)
class LogicalWall:
    """A connected set of classified wall segments.

    The logical wall preserves original line geometries as source geometry
    records rather than generating modified endpoints or centerlines.
    """

    id: str
    wall_type: WallType
    width: float
    segment_ids: tuple[str, ...]
    line_ids: tuple[str, ...]
    source_lines: tuple[LineEntity, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "wall_type": self.wall_type.value,
            "width": self.width,
            "segment_ids": list(self.segment_ids),
            "line_ids": list(self.line_ids),
            "source_lines": [line.to_dict() for line in self.source_lines],
        }


class WallMerger:
    """Merge connected wall segments into logical walls."""

    def __init__(self, config: WallMergerConfig | None = None) -> None:
        self.config = config or WallMergerConfig()
        if self.config.connection_tolerance < 0:
            raise ValueError("connection_tolerance must be non-negative")

    def merge(self, segments: list[WallSegment]) -> list[LogicalWall]:
        """Group connected wall segments with the same wall type and width."""

        groups = _connected_components(segments, self._are_connected)
        walls = [self._build_wall(index, group) for index, group in enumerate(groups, start=1)]
        logger.info("Merged {} wall segments into {} logical walls", len(segments), len(walls))
        return walls

    def _are_connected(self, first: WallSegment, second: WallSegment) -> bool:
        if first.wall_type != second.wall_type or first.width != second.width:
            return False

        first_lines = (first.source_pair.line_a, first.source_pair.line_b)
        second_lines = (second.source_pair.line_a, second.source_pair.line_b)
        return any(
            _line_string(line_a).distance(_line_string(line_b)) <= self.config.connection_tolerance
            for line_a in first_lines
            for line_b in second_lines
        )

    def _build_wall(self, index: int, segments: list[WallSegment]) -> LogicalWall:
        source_lines_by_id: dict[str, LineEntity] = {}
        segment_ids: list[str] = []
        for segment in segments:
            segment_ids.append(segment.id)
            source_lines_by_id[segment.source_pair.line_a.id] = segment.source_pair.line_a
            source_lines_by_id[segment.source_pair.line_b.id] = segment.source_pair.line_b

        first = segments[0]
        return LogicalWall(
            id=f"logical-wall-{index}",
            wall_type=first.wall_type,
            width=first.width,
            segment_ids=tuple(segment_ids),
            line_ids=tuple(source_lines_by_id),
            source_lines=tuple(source_lines_by_id.values()),
        )


def _connected_components(
    segments: list[WallSegment],
    are_connected: Any,
) -> list[list[WallSegment]]:
    seen: set[int] = set()
    groups: list[list[WallSegment]] = []

    for start_index in range(len(segments)):
        if start_index in seen:
            continue

        stack = [start_index]
        seen.add(start_index)
        group: list[WallSegment] = []
        while stack:
            current_index = stack.pop()
            current = segments[current_index]
            group.append(current)
            for candidate_index, candidate in enumerate(segments):
                if candidate_index in seen:
                    continue
                if are_connected(current, candidate):
                    seen.add(candidate_index)
                    stack.append(candidate_index)
        groups.append(group)

    return groups


def _line_string(line: LineEntity) -> LineString:
    return LineString([(line.start.x, line.start.y), (line.end.x, line.end.y)])
