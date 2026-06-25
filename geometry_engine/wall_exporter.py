"""JSON export for geometry-engine results."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from .line_reader import LineEntity, LineReader
from .parallel_detector import ParallelDetector, ParallelDetectorConfig, ParallelPair
from .wall_classifier import WallClassifier, WallClassifierConfig, WallSegment
from .wall_merger import LogicalWall, WallMerger, WallMergerConfig


@dataclass(frozen=True, slots=True)
class WallExport:
    """Complete export payload for a DXF geometry-engine run."""

    lines: tuple[LineEntity, ...]
    parallel_pairs: tuple[ParallelPair, ...]
    wall_segments: tuple[WallSegment, ...]
    logical_walls: tuple[LogicalWall, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "lines": [line.to_dict() for line in self.lines],
            "parallel_pairs": [pair.to_dict() for pair in self.parallel_pairs],
            "wall_segments": [segment.to_dict() for segment in self.wall_segments],
            "logical_walls": [wall.to_dict() for wall in self.logical_walls],
        }


class WallExporter:
    """Run the LINE wall pipeline and export JSON."""

    def __init__(
        self,
        *,
        line_reader: LineReader | None = None,
        parallel_config: ParallelDetectorConfig | None = None,
        classifier_config: WallClassifierConfig | None = None,
        merger_config: WallMergerConfig | None = None,
    ) -> None:
        self.line_reader = line_reader or LineReader()
        self.parallel_detector = ParallelDetector(parallel_config)
        self.wall_classifier = WallClassifier(classifier_config)
        self.wall_merger = WallMerger(merger_config)

    def build_export(self, dxf_path: str | Path) -> WallExport:
        """Run all pipeline steps and return a serializable export model."""

        lines = self.line_reader.read(dxf_path)
        parallel_pairs = self.parallel_detector.find_pairs(lines)
        wall_segments = self.wall_classifier.classify(parallel_pairs)
        logical_walls = self.wall_merger.merge(wall_segments)
        return WallExport(
            lines=tuple(lines),
            parallel_pairs=tuple(parallel_pairs),
            wall_segments=tuple(wall_segments),
            logical_walls=tuple(logical_walls),
        )

    def export_json(
        self,
        dxf_path: str | Path,
        output_path: str | Path | None = None,
        *,
        indent: int = 2,
    ) -> str:
        """Export pipeline results as JSON and optionally write them to disk."""

        payload = self.build_export(dxf_path).to_dict()
        json_text = json.dumps(payload, indent=indent, sort_keys=True)

        if output_path is not None:
            target = Path(output_path).expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json_text, encoding="utf-8")
            logger.info("Wrote wall export JSON to {}", target)

        return json_text
