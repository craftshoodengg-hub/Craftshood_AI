"""Tests for dataset room statistics integration."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import DatasetAnalyzer, DatasetReportExporter


def _create_dxf_with_text(path: Path, texts: list[tuple[str, tuple[float, float], str]]) -> None:
    document = ezdxf.new()
    modelspace = document.modelspace()
    for text, insert, layer in texts:
        modelspace.add_text(text, dxfattribs={"insert": insert, "layer": layer})
    document.saveas(path)


def test_empty_dataset_has_zero_room_totals(tmp_path: Path) -> None:
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))

    assert summary["total_rooms"] == 0
    assert summary["room_totals"] == {
        "Bedroom": 0,
        "Kitchen": 0,
        "Living": 0,
        "Dining": 0,
        "Toilet": 0,
        "Balcony": 0,
        "Parking": 0,
        "Utility": 0,
        "Pooja": 0,
        "Stair": 0,
        "Store": 0,
    }


def test_one_drawing_room_statistics(tmp_path: Path) -> None:
    path = tmp_path / "room.dxf"
    _create_dxf_with_text(
        path,
        [
            ("Bed room", (1, 1), "A-ROOM"),
            ("Kitchen", (2, 2), "A-ROOM"),
            ("Living/Dining", (3, 3), "A-ROOM"),
        ],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))

    assert summary["total_rooms"] == 3
    assert summary["room_totals"]["Bedroom"] == 1
    assert summary["room_totals"]["Kitchen"] == 1
    assert summary["room_totals"]["Living"] == 1
    assert summary["room_totals"]["Dining"] == 0
    assert summary["file_summaries"][0]["room_count"] == 3
    assert len(summary["file_summaries"][0]["rooms"]) == 3


def test_multiple_drawings_room_totals(tmp_path: Path) -> None:
    _create_dxf_with_text(
        tmp_path / "a.dxf",
        [("Pooja", (1, 1), "A-ROOM"), ("Covered Balcony", (2, 2), "A-BALCONY")],
    )
    _create_dxf_with_text(
        tmp_path / "b.dxf",
        [("Wash", (3, 3), "A-UTILITY"), ("Portico", (4, 4), "A-PARKING")],
    )
    analyzer = DatasetAnalyzer()

    summary = analyzer.analyze_directory(str(tmp_path))

    assert summary["total_rooms"] == 4
    assert summary["room_totals"]["Pooja"] == 1
    assert summary["room_totals"]["Balcony"] == 1
    assert summary["room_totals"]["Utility"] == 1
    assert summary["room_totals"]["Parking"] == 1


def test_room_statistics_markdown_section(tmp_path: Path) -> None:
    path = tmp_path / "room.dxf"
    _create_dxf_with_text(path, [("Bed room", (1, 1), "A-ROOM")])
    analyzer = DatasetAnalyzer()
    exporter = DatasetReportExporter()

    summary = analyzer.analyze_directory(str(tmp_path))
    markdown = exporter.to_markdown(summary)

    assert "## Room Statistics" in markdown
    assert "- **Total Rooms:** 1" in markdown
    assert "- **Bedroom**: 1" in markdown
    assert "- **Kitchen**: 0" in markdown
    assert "- **Living**: 0" in markdown
