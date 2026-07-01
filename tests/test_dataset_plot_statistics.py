"""Tests for dataset plot statistics integration."""
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
        if dxftype == "TEXT":
            modelspace.add_text(entity["text"], dxfattribs={"insert": entity["insert"], **attribs})
        elif dxftype == "MTEXT":
            modelspace.add_mtext(entity["text"], dxfattribs={"insert": entity["insert"], **attribs})
        elif dxftype == "LINE":
            modelspace.add_line(entity["start"], entity["end"], dxfattribs=attribs)
        elif dxftype == "LWPOLYLINE":
            modelspace.add_lwpolyline(entity["points"], dxfattribs=attribs)
    document.saveas(path)


def test_analyze_directory_empty_plot_statistics(tmp_path: Path) -> None:
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))

    assert summary["plot_statistics"]["total_detected"] == 0
    assert summary["plot_statistics"]["orientations"] == {"North": 0, "South": 0, "East": 0, "West": 0}
    assert summary["plot_statistics"]["average_width"] is None
    assert summary["plot_statistics"]["average_depth"] is None
    assert summary["plot_statistics"]["average_area"] is None
    assert summary["plot_statistics"]["largest_plot"] is None
    assert summary["plot_statistics"]["smallest_plot"] is None


def test_analyze_directory_single_plot_file(tmp_path: Path) -> None:
    path = tmp_path / "plot.dxf"
    _create_dxf_file(
        path,
        [
            {"type": "TEXT", "text": "115'x580'", "insert": (0, 0), "attribs": {"layer": "A-ANNO"}},
        ],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))
    plot_stats = summary["plot_statistics"]

    assert plot_stats["total_detected"] == 1
    assert plot_stats["orientations"] == {"North": 0, "South": 0, "East": 0, "West": 0}
    assert plot_stats["average_width"] == 115.0
    assert plot_stats["average_depth"] == 580.0
    assert plot_stats["average_area"] == 66700.0
    assert plot_stats["largest_plot"]["file"].endswith("plot.dxf")
    assert plot_stats["smallest_plot"]["file"].endswith("plot.dxf")


def test_analyze_directory_multiple_plots_and_orientations(tmp_path: Path) -> None:
    _create_dxf_file(
        tmp_path / "north.dxf",
        [{"type": "TEXT", "text": "North", "insert": (0, 0), "attribs": {"layer": "A-ANNO"}}, {"type": "TEXT", "text": "40x50", "insert": (1, 1), "attribs": {"layer": "A-ANNO"}}],
    )
    _create_dxf_file(
        tmp_path / "east.dxf",
        [{"type": "TEXT", "text": "Facing East", "insert": (0, 0), "attribs": {"layer": "A-ANNO"}}, {"type": "TEXT", "text": "30x20", "insert": (1, 1), "attribs": {"layer": "A-ANNO"}}],
    )
    _create_dxf_file(
        tmp_path / "west.dxf",
        [{"type": "TEXT", "text": "Facing West", "insert": (0, 0), "attribs": {"layer": "A-ANNO"}}, {"type": "TEXT", "text": "50x10", "insert": (1, 1), "attribs": {"layer": "A-ANNO"}}],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False)
    plot_stats = summary["plot_statistics"]

    assert plot_stats["total_detected"] == 3
    assert plot_stats["orientations"] == {"North": 1, "South": 0, "East": 1, "West": 1}
    assert plot_stats["average_width"] == (40.0 + 30.0 + 50.0) / 3
    assert plot_stats["average_depth"] == (50.0 + 20.0 + 10.0) / 3
    assert plot_stats["average_area"] == (2000.0 + 600.0 + 500.0) / 3
    assert plot_stats["largest_plot"]["file"].endswith("north.dxf")
    assert plot_stats["largest_plot"]["area"] == 2000.0
    assert plot_stats["smallest_plot"]["file"].endswith("west.dxf")
    assert plot_stats["smallest_plot"]["area"] == 500.0


def test_file_summaries_include_plot_information(tmp_path: Path) -> None:
    path = tmp_path / "plot.dxf"
    _create_dxf_file(
        path,
        [{"type": "TEXT", "text": "Facing South", "insert": (0, 0), "attribs": {"layer": "A-ANNO"}}, {"type": "TEXT", "text": "25x35", "insert": (1, 1), "attribs": {"layer": "A-ANNO"}}],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path), recursive=False)
    file_summary = summary["file_summaries"][0]

    assert file_summary["plot_information"]["plot_width"] == 25.0
    assert file_summary["plot_information"]["plot_depth"] == 35.0
    assert file_summary["plot_information"]["orientation"] == "South"


def test_report_exporter_includes_plot_statistics() -> None:
    exporter = DatasetReportExporter()
    summary = {
        "files_scanned": 1,
        "files_failed": 0,
        "entity_totals": {"entity_count": 1},
        "layer_names": {},
        "block_names": {},
        "text_values": {},
        "room_totals": {},
        "total_rooms": 0,
        "plot_statistics": {
            "total_detected": 1,
            "orientations": {"North": 0, "South": 1, "East": 0, "West": 0},
            "average_width": 25.0,
            "average_depth": 35.0,
            "average_area": 875.0,
            "largest_plot": {"width": 25.0, "depth": 35.0, "area": 875.0, "file": "plot.dxf"},
            "smallest_plot": {"width": 25.0, "depth": 35.0, "area": 875.0, "file": "plot.dxf"},
        },
        "failed_files": [],
        "file_summaries": [],
    }

    markdown = exporter.to_markdown(summary)

    assert "## Plot Statistics" in markdown
    assert "- **Detected Plots:** 1" in markdown
    assert "- **Average Width:** 25.0" in markdown
    assert "- **Average Depth:** 35.0" in markdown
    assert "- **Average Area:** 875.0" in markdown
    assert "- **South Facing:** 1" in markdown
    assert "- **Largest Plot:** 25.0 x 35.0 = 875.0 (plot.dxf)" in markdown
    assert "- **Smallest Plot:** 25.0 x 35.0 = 875.0 (plot.dxf)" in markdown
