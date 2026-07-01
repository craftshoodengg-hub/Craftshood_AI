"""Tests for door and window statistics in the DWG dataset analyzer."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import DatasetAnalyzer, DatasetReportExporter


def _create_dxf_file(path: Path, entities: list[dict]) -> None:
    document = ezdxf.new()
    modelspace = document.modelspace()
    for entity in entities:
        dxftype = entity["type"]
        attribs = entity.get("attribs", {})
        if dxftype == "LINE":
            modelspace.add_line(entity["start"], entity["end"], dxfattribs=attribs)
        elif dxftype == "TEXT":
            modelspace.add_text(entity["text"], dxfattribs={"insert": entity["insert"], **attribs})
        elif dxftype == "MTEXT":
            modelspace.add_mtext(entity["text"], dxfattribs={"insert": entity["insert"], **attribs})
        elif dxftype == "INSERT":
            block = document.blocks.new(entity["name"])
            block.add_line((0, 0), (1, 0))
            modelspace.add_blockref(entity["name"], insert=entity["insert"], dxfattribs=attribs)
    document.saveas(path)


def test_empty_dataset_reports_zero_statistics(tmp_path: Path) -> None:
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))

    assert summary["files_scanned"] == 0
    assert summary["door_window_statistics"] == {
        "total_doors": 0,
        "total_windows": 0,
        "files_with_doors": 0,
        "files_with_windows": 0,
        "average_doors_per_file": 0.0,
        "average_windows_per_file": 0.0,
    }


def test_one_drawing_counts_doors_and_windows(tmp_path: Path) -> None:
    path = tmp_path / "single.dxf"
    _create_dxf_file(
        path,
        [
            {"type": "TEXT", "text": "Door", "insert": (1, 1), "attribs": {"layer": "A-ANNO"}},
            {"type": "TEXT", "text": "Window", "insert": (2, 2), "attribs": {"layer": "A-ANNO"}},
        ],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False)

    assert summary["door_window_statistics"]["total_doors"] == 1
    assert summary["door_window_statistics"]["total_windows"] == 1
    assert summary["door_window_statistics"]["files_with_doors"] == 1
    assert summary["door_window_statistics"]["files_with_windows"] == 1
    assert summary["door_window_statistics"]["average_doors_per_file"] == 1.0
    assert summary["door_window_statistics"]["average_windows_per_file"] == 1.0


def test_multiple_drawings_accumulated_door_window_statistics(tmp_path: Path) -> None:
    _create_dxf_file(
        tmp_path / "a.dxf",
        [
            {"type": "TEXT", "text": "Door", "insert": (0, 0), "attribs": {"layer": "A-DOOR"}},
            {"type": "TEXT", "text": "Door", "insert": (1, 0), "attribs": {"layer": "A-DOOR"}},
        ],
    )
    _create_dxf_file(
        tmp_path / "b.dxf",
        [
            {"type": "TEXT", "text": "Window", "insert": (0, 0), "attribs": {"layer": "A-WINDOW"}},
        ],
    )
    _create_dxf_file(
        tmp_path / "c.dxf",
        [
            {"type": "TEXT", "text": "Bedroom", "insert": (0, 0), "attribs": {"layer": "A-ROOM"}},
        ],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False)

    assert summary["files_scanned"] == 3
    assert summary["door_window_statistics"]["total_doors"] == 2
    assert summary["door_window_statistics"]["total_windows"] == 1
    assert summary["door_window_statistics"]["files_with_doors"] == 1
    assert summary["door_window_statistics"]["files_with_windows"] == 1
    assert summary["door_window_statistics"]["average_doors_per_file"] == 2 / 3
    assert summary["door_window_statistics"]["average_windows_per_file"] == 1 / 3


def test_markdown_report_includes_door_window_statistics() -> None:
    exporter = DatasetReportExporter()
    summary = {
        "files_scanned": 2,
        "files_failed": 0,
        "entity_totals": {},
        "layer_names": {},
        "block_names": {},
        "text_values": {},
        "failed_files": [],
        "plot_statistics": {},
        "door_window_statistics": {
            "total_doors": 4,
            "total_windows": 5,
            "files_with_doors": 2,
            "files_with_windows": 1,
            "average_doors_per_file": 2.0,
            "average_windows_per_file": 2.5,
        },
        "file_summaries": [],
    }

    markdown = exporter.to_markdown(summary)

    assert "## Door & Window Statistics" in markdown
    assert "- **Total Doors:** 4" in markdown
    assert "- **Total Windows:** 5" in markdown
    assert "- **Files with Doors:** 2" in markdown
    assert "- **Files with Windows:** 1" in markdown
    assert "- **Average Doors per File:** 2.0" in markdown
    assert "- **Average Windows per File:** 2.5" in markdown
