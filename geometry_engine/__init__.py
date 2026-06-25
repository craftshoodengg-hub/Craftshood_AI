"""Geometry engine for LINE-based wall extraction from DXF files.

The package reads existing LINE entities, finds parallel candidates, classifies
wall-width pairs, merges connected wall segments, and exports JSON. It does not
detect rooms, doors, or windows, and it does not modify source geometry.
"""

from .line_reader import LineEntity, LineReader, Point2D, read_line_entities
from .parallel_detector import ParallelDetector, ParallelDetectorConfig, ParallelPair
from .wall_classifier import WallClassifier, WallClassifierConfig, WallSegment, WallType
from .wall_exporter import WallExport, WallExporter
from .wall_merger import LogicalWall, WallMerger, WallMergerConfig

__all__ = [
    "LineEntity",
    "LineReader",
    "LogicalWall",
    "ParallelDetector",
    "ParallelDetectorConfig",
    "ParallelPair",
    "Point2D",
    "WallClassifier",
    "WallClassifierConfig",
    "WallExport",
    "WallExporter",
    "WallMerger",
    "WallMergerConfig",
    "WallSegment",
    "WallType",
    "read_line_entities",
]
