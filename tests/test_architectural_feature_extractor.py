"""Tests for the architectural wall extractor."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import ArchitecturalFeatureExtractor


def _make_dxf_with_wall_entities(tmp_path: Path) -> Path:
    path = tmp_path / "walls.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    modelspace.add_line((0, 0), (10, 0), dxfattribs={"layer": "A-WALL"})
    modelspace.add_lwpolyline(
        [(10, 0), (10, 10), (0, 10)], dxfattribs={"layer": "A-WALL"}
    )
    modelspace.add_polyline2d(
        [(0, 0), (0, 5), (5, 5)], dxfattribs={"layer": "A-WALL"}
    )
    modelspace.add_circle((20, 20), radius=2)
    modelspace.add_line((1, 1), (1, 1), dxfattribs={"layer": "A-WALL"})
    document.saveas(path)
    return path


def test_extract_walls_from_document(tmp_path: Path) -> None:
    path = _make_dxf_with_wall_entities(tmp_path)
    document = ezdxf.readfile(path)
    extractor = ArchitecturalFeatureExtractor()

    walls = extractor.extract_walls(document)

    assert len(walls) == 3
    assert walls[0]["type"] == "LINE"
    assert walls[1]["type"] == "LWPOLYLINE"
    assert walls[2]["type"] == "POLYLINE"
    assert walls[0]["points"] == [(0.0, 0.0), (10.0, 0.0)]
    assert walls[1]["points"] == [(10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert walls[2]["points"] == [(0.0, 0.0), (0.0, 5.0), (5.0, 5.0)]


def test_wall_count_ignores_non_wall_and_zero_length_entities(tmp_path: Path) -> None:
    path = _make_dxf_with_wall_entities(tmp_path)
    document = ezdxf.readfile(path)
    extractor = ArchitecturalFeatureExtractor()

    assert extractor.wall_count(document) == 3
