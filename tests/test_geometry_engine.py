from __future__ import annotations

import json
from pathlib import Path

import ezdxf

from geometry_engine import (
    LineReader,
    ParallelDetector,
    ParallelDetectorConfig,
    WallClassifier,
    WallClassifierConfig,
    WallExporter,
    WallMerger,
    WallType,
)


def test_line_reader_reads_line_entities_with_required_fields(tmp_path: Path) -> None:
    dxf_path = _write_sample_dxf(tmp_path)

    lines = LineReader(include_blocks=False).read(dxf_path)

    assert len(lines) == 5
    first = lines[0]
    assert first.id
    assert first.start.x == 0
    assert first.start.y == 0
    assert first.end.x == 10
    assert first.end.y == 0
    assert first.length == 10
    assert first.angle == 0
    assert first.layer == "A-WALL"


def test_parallel_detector_uses_angle_and_distance_configuration(tmp_path: Path) -> None:
    dxf_path = _write_sample_dxf(tmp_path)
    lines = LineReader(include_blocks=False).read(dxf_path)
    detector = ParallelDetector(
        ParallelDetectorConfig(
            angle_tolerance_degrees=1.0,
            max_perpendicular_distance=0.8,
        )
    )

    pairs = detector.find_pairs(lines)

    distances = sorted(round(pair.perpendicular_distance, 3) for pair in pairs)
    assert distances == [0.375, 0.75]


def test_wall_classifier_supports_brick_wall_widths(tmp_path: Path) -> None:
    dxf_path = _write_sample_dxf(tmp_path)
    lines = LineReader(include_blocks=False).read(dxf_path)
    pairs = ParallelDetector(
        ParallelDetectorConfig(max_perpendicular_distance=0.8)
    ).find_pairs(lines)

    segments = WallClassifier(WallClassifierConfig(width_tolerance=0.01)).classify(pairs)

    assert [segment.wall_type for segment in segments] == [
        WallType.NINE_INCH_BRICK,
        WallType.FOUR_HALF_INCH_BRICK,
    ]


def test_wall_merger_merges_connected_segments_only(tmp_path: Path) -> None:
    dxf_path = _write_connected_wall_dxf(tmp_path)
    lines = LineReader(include_blocks=False).read(dxf_path)
    pairs = ParallelDetector(
        ParallelDetectorConfig(max_perpendicular_distance=0.8)
    ).find_pairs(lines)
    segments = WallClassifier(WallClassifierConfig(width_tolerance=0.01)).classify(pairs)

    walls = WallMerger().merge(segments)

    assert len(walls) == 1
    assert walls[0].wall_type == WallType.NINE_INCH_BRICK
    assert len(walls[0].segment_ids) == 2
    assert len(walls[0].source_lines) == 4


def test_wall_exporter_returns_and_writes_json(tmp_path: Path) -> None:
    dxf_path = _write_sample_dxf(tmp_path)
    output_path = tmp_path / "walls.json"

    json_text = WallExporter(
        line_reader=LineReader(include_blocks=False),
        parallel_config=ParallelDetectorConfig(max_perpendicular_distance=0.8),
        classifier_config=WallClassifierConfig(width_tolerance=0.01),
    ).export_json(dxf_path, output_path)

    payload = json.loads(json_text)
    assert output_path.read_text(encoding="utf-8") == json_text
    assert len(payload["lines"]) == 5
    assert len(payload["wall_segments"]) == 2
    assert payload["logical_walls"][0]["wall_type"] == "9 inch brick wall"


def _write_sample_dxf(tmp_path: Path) -> Path:
    path = tmp_path / "sample.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    modelspace.add_line((0, 0), (10, 0), dxfattribs={"layer": "A-WALL"})
    modelspace.add_line((0, 0.75), (10, 0.75), dxfattribs={"layer": "A-WALL"})
    modelspace.add_line((20, 0), (30, 0), dxfattribs={"layer": "A-WALL"})
    modelspace.add_line((20, 0.375), (30, 0.375), dxfattribs={"layer": "A-WALL"})
    modelspace.add_line((0, 5), (0, 10), dxfattribs={"layer": "A-COLUMN"})
    document.saveas(path)
    return path


def _write_connected_wall_dxf(tmp_path: Path) -> Path:
    path = tmp_path / "connected.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    modelspace.add_line((0, 0), (10, 0), dxfattribs={"layer": "A-WALL"})
    modelspace.add_line((0, 0.75), (10, 0.75), dxfattribs={"layer": "A-WALL"})
    modelspace.add_line((10, 0), (20, 0), dxfattribs={"layer": "A-WALL"})
    modelspace.add_line((10, 0.75), (20, 0.75), dxfattribs={"layer": "A-WALL"})
    document.saveas(path)
    return path
