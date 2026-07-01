"""Tests for the DWG dataset analyzer."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import DatasetAnalyzer


def _create_dxf_file(path: Path, entities: list[dict]) -> None:
    document = ezdxf.new()
    modelspace = document.modelspace()
    for entity in entities:
        dxftype = entity["type"]
        attribs = entity.get("attribs", {})
        if dxftype == "LINE":
            modelspace.add_line(entity["start"], entity["end"], dxfattribs=attribs)
        elif dxftype == "LWPOLYLINE":
            modelspace.add_lwpolyline(entity["points"], dxfattribs=attribs)
        elif dxftype == "POLYLINE":
            modelspace.add_polyline2d(entity["points"], dxfattribs=attribs)
        elif dxftype == "TEXT":
            modelspace.add_text(entity["text"], dxfattribs={"insert": entity["insert"], **attribs})
        elif dxftype == "MTEXT":
            modelspace.add_mtext(entity["text"], dxfattribs={"insert": entity["insert"], **attribs})
        elif dxftype == "INSERT":
            block = document.blocks.new(entity["name"])
            block.add_line((0, 0), (1, 0))
            modelspace.add_blockref(entity["name"], insert=entity["insert"], dxfattribs=attribs)
    document.saveas(path)


def test_analyze_directory_empty(tmp_path: Path) -> None:
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))

    assert summary["files_scanned"] == 0
    assert summary["files_failed"] == 0
    assert summary["entity_totals"] == {}
    assert summary["layer_names"] == {}
    assert summary["block_names"] == {}
    assert summary["text_values"] == {}
    assert summary["file_summaries"] == []


def test_analyze_directory_single_file(tmp_path: Path) -> None:
    path = tmp_path / "single.dxf"
    _create_dxf_file(
        path,
        [
            {"type": "LINE", "start": (0, 0), "end": (10, 0), "attribs": {"layer": "A-WALL"}},
            {"type": "TEXT", "text": "Door", "insert": (1, 1), "attribs": {"layer": "A-WALL"}},
        ],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))

    assert summary["files_scanned"] == 1
    assert summary["files_failed"] == 0
    assert summary["entity_totals"] == {"entity_count": 2}
    assert summary["layer_names"] == {"A-WALL": 2}
    assert summary["text_values"] == {"Door": 1}
    assert summary["file_summaries"][0]["file_path"].endswith("single.dxf")
    assert summary["file_summaries"][0]["entity_count"] == 2
    assert summary["file_summaries"][0]["layers"] == ["A-WALL"]
    assert summary["file_summaries"][0]["texts"] == ["Door"]


def test_analyze_directory_multiple_files_and_limit(tmp_path: Path) -> None:
    _create_dxf_file(
        tmp_path / "a.dxf",
        [{"type": "LINE", "start": (0, 0), "end": (5, 0), "attribs": {"layer": "A-WALL"}}],
    )
    _create_dxf_file(
        tmp_path / "b.dxf",
        [
            {"type": "LWPOLYLINE", "points": [(0, 0), (0, 5)], "attribs": {"layer": "A-WALL"}},
            {"type": "TEXT", "text": "Window", "insert": (1, 1), "attribs": {"layer": "A-WALL"}},
        ],
    )
    _create_dxf_file(
        tmp_path / "c.dxf",
        [{"type": "MTEXT", "text": "Kitchen", "insert": (2, 2), "attribs": {"layer": "A-ROOM"}}],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False, limit=2)

    assert summary["files_scanned"] == 2
    assert summary["files_failed"] == 0
    assert summary["entity_totals"] == {"entity_count": 3}
    assert summary["layer_names"] == {"A-WALL": 3}
    assert summary["text_values"] == {"Window": 1}
    assert len(summary["file_summaries"]) == 2
    assert summary["file_summaries"][0]["file_path"].endswith("a.dxf")
    assert summary["file_summaries"][1]["file_path"].endswith("b.dxf")


def test_analyze_directory_recursive_scanning(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    _create_dxf_file(
        tmp_path / "root.dxf",
        [{"type": "LINE", "start": (0, 0), "end": (1, 0), "attribs": {"layer": "ROOT"}}],
    )
    _create_dxf_file(
        nested / "child.dxf",
        [{"type": "LINE", "start": (0, 0), "end": (1, 0), "attribs": {"layer": "NESTED"}}],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=True)

    assert summary["files_scanned"] == 2
    assert summary["layer_names"] == {"NESTED": 1, "ROOT": 1}
    assert sorted(file["file_path"].endswith(name) for file, name in zip(summary["file_summaries"], ["child.dxf", "root.dxf"]))


def test_analyze_directory_invalid_files_skipped(tmp_path: Path) -> None:
    valid_path = tmp_path / "valid.dxf"
    _create_dxf_file(
        valid_path,
        [{"type": "LINE", "start": (0, 0), "end": (1, 0), "attribs": {"layer": "A-WALL"}}],
    )
    invalid_path = tmp_path / "invalid.dxf"
    invalid_path.write_text("not a dxf", encoding="utf-8")
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False)

    assert summary["files_scanned"] == 1
    assert summary["files_failed"] == 1
    assert summary["entity_totals"] == {"entity_count": 1}
    assert summary["layer_names"] == {"A-WALL": 1}
    assert summary["file_summaries"][0]["file_path"].endswith("valid.dxf")


def test_analyze_directory_block_name_counting(tmp_path: Path) -> None:
    path = tmp_path / "blocks.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    block = document.blocks.new("DOOR_BLOCK")
    block.add_line((0, 0), (1, 0))
    modelspace.add_blockref("DOOR_BLOCK", insert=(0, 0), dxfattribs={"layer": "A-WALL"})
    modelspace.add_blockref("WINDOW_BLOCK", insert=(1, 0), dxfattribs={"layer": "A-WALL"})
    document.blocks.new("WINDOW_BLOCK").add_line((0, 0), (1, 0))
    modelspace.add_blockref("DOOR_BLOCK", insert=(2, 0), dxfattribs={"layer": "A-WALL"})
    document.saveas(path)
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False)

    assert summary["files_scanned"] == 1
    assert summary["block_names"] == {"DOOR_BLOCK": 2, "WINDOW_BLOCK": 1}
    assert summary["file_summaries"][0]["blocks"] == ["DOOR_BLOCK", "WINDOW_BLOCK"]


def test_analyze_directory_text_value_counting(tmp_path: Path) -> None:
    path = tmp_path / "text_values.dxf"
    _create_dxf_file(
        path,
        [
            {"type": "TEXT", "text": "Door", "insert": (0, 0), "attribs": {"layer": "A-WALL"}},
            {"type": "MTEXT", "text": "Door", "insert": (1, 0), "attribs": {"layer": "A-WALL"}},
            {"type": "TEXT", "text": "Window", "insert": (2, 0), "attribs": {"layer": "A-WALL"}},
        ],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False)

    assert summary["files_scanned"] == 1
    assert summary["text_values"] == {"Door": 2, "Window": 1}
    assert summary["file_summaries"][0]["texts"] == ["Door", "Door", "Window"]
