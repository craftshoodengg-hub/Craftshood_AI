"""Tests for plot information detection from DXF text."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import PlotInformationDetector


def _create_dxf_with_text(path: Path, texts: list[tuple[str, tuple[float, float], str]]) -> None:
    document = ezdxf.new()
    modelspace = document.modelspace()
    for text, insert, layer in texts:
        modelspace.add_text(text, dxfattribs={"insert": insert, "layer": layer})
    document.saveas(path)


def test_detect_orientation_north() -> None:
    document = ezdxf.new()
    document.modelspace().add_text("North", dxfattribs={"insert": (0, 0), "layer": "A-ANNO"})

    detector = PlotInformationDetector()
    assert detector.detect_orientation(document) == "North"


def test_detect_orientation_short_form() -> None:
    document = ezdxf.new()
    document.modelspace().add_text("E", dxfattribs={"insert": (0, 0), "layer": "A-ANNO"})

    detector = PlotInformationDetector()
    assert detector.detect_orientation(document) == "East"


def test_detect_orientation_facing() -> None:
    document = ezdxf.new()
    document.modelspace().add_text("Facing South", dxfattribs={"insert": (0, 0), "layer": "A-ANNO"})

    detector = PlotInformationDetector()
    assert detector.detect_orientation(document) == "South"


def test_detect_plot_size_simple_formats(tmp_path: Path) -> None:
    path = tmp_path / "plot.dxf"
    _create_dxf_with_text(path, [("40x60", (0, 0), "A-ANNO")])

    detector = PlotInformationDetector()
    document = ezdxf.readfile(str(path))
    assert detector.detect_plot_size(document) == (40.0, 60.0)


def test_detect_plot_size_with_spaces_and_apostrophes(tmp_path: Path) -> None:
    path = tmp_path / "plot.dxf"
    _create_dxf_with_text(path, [("106'x117'6\"", (0, 0), "A-ANNO")])

    detector = PlotInformationDetector()
    document = ezdxf.readfile(str(path))
    width, depth = detector.detect_plot_size(document)

    assert width == 106.0
    assert depth == 117.5


def test_detect_plot_size_decimal_values(tmp_path: Path) -> None:
    path = tmp_path / "plot.dxf"
    _create_dxf_with_text(path, [("40.0 x 60.0", (0, 0), "A-ANNO")])

    detector = PlotInformationDetector()
    document = ezdxf.readfile(str(path))
    assert detector.detect_plot_size(document) == (40.0, 60.0)


def test_detect_plot_area_calculation() -> None:
    detector = PlotInformationDetector()
    assert detector.detect_plot_area(40.0, 60.0) == 2400.0
    assert detector.detect_plot_area(None, 60.0) is None


def test_detect_ignores_invalid_labels(tmp_path: Path) -> None:
    path = tmp_path / "plot.dxf"
    _create_dxf_with_text(
        path,
        [
            ("Bedroom", (0, 0), "A-ROOM"),
            ("Kitchen", (1, 1), "A-ROOM"),
            ("Road Width", (2, 2), "A-ANNO"),
        ],
    )

    detector = PlotInformationDetector()
    document = ezdxf.readfile(str(path))
    assert detector.detect_plot_size(document) == (None, None)
    assert detector.detect_orientation(document) is None


def test_detect_document_returns_complete_plot_information(tmp_path: Path) -> None:
    path = tmp_path / "full.dxf"
    _create_dxf_with_text(
        path,
        [
            ("Facing West", (0, 0), "A-ANNO"),
            ("115'x580'", (1, 1), "A-ANNO"),
        ],
    )

    detector = PlotInformationDetector()
    document = ezdxf.readfile(str(path))
    info = detector.detect(document)

    assert info == {
        "plot_width": 115.0,
        "plot_depth": 580.0,
        "plot_area": 66700.0,
        "orientation": "West",
    }
