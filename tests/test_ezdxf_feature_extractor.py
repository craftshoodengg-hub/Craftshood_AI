"""Tests for the EZDXF DWG feature extractor."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import EzDXFFeatureExtractor, DwgReference


def _make_temp_dxf(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    document = ezdxf.new()
    document.saveas(path)
    return path


def _make_dxf_with_entities(tmp_path: Path) -> Path:
    path = tmp_path / "entities.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    modelspace.add_line((0, 0), (10, 0))
    modelspace.add_circle((5, 5), radius=2)
    modelspace.add_arc((10, 10), radius=3, start_angle=0, end_angle=180)
    document.saveas(path)
    return path


def _make_dxf_with_blocks(tmp_path: Path) -> Path:
    path = tmp_path / "blocks.dxf"
    document = ezdxf.new()
    block = document.blocks.new("TEST_BLOCK")
    block.add_line((0, 0), (1, 0))
    modelspace = document.modelspace()
    modelspace.add_blockref("TEST_BLOCK", insert=(0, 0))
    document.saveas(path)
    return path


def _make_dxf_with_text(tmp_path: Path) -> Path:
    path = tmp_path / "text.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    modelspace.add_text("hello", dxfattribs={"insert": (0, 0)})
    modelspace.add_mtext("hello world", dxfattribs={"insert": (1, 1)})
    document.saveas(path)
    return path


def test_extract_metadata_from_empty_dxf(tmp_path: Path) -> None:
    extractor = EzDXFFeatureExtractor()
    path = _make_temp_dxf(tmp_path, "empty.dxf")

    metadata = extractor.extract_metadata(str(path))

    assert metadata.file_path == str(path)
    assert metadata.project_type == "unknown"
    assert metadata.room_count is None
    assert metadata.plot_width is None
    assert metadata.plot_depth is None
    assert metadata.orientation is None
    assert metadata.tags == ["dwg"]


def test_extract_features_counts_entities(tmp_path: Path) -> None:
    extractor = EzDXFFeatureExtractor()
    path = _make_dxf_with_entities(tmp_path)

    features = extractor.extract_features(str(path))

    assert features["entity_count"] == 3
    assert features["lines"] == 1
    assert features["circles"] == 1
    assert features["arcs"] == 1
    assert features["lwpolylines"] == 0
    assert features["polylines"] == 0
    assert features["blocks"] == 0
    assert features["texts"] == 0
    assert features["mtexts"] == 0


def test_extract_features_counts_blocks(tmp_path: Path) -> None:
    extractor = EzDXFFeatureExtractor()
    path = _make_dxf_with_blocks(tmp_path)

    features = extractor.extract_features(str(path))

    assert features["entity_count"] == 1
    assert features["blocks"] == 1
    assert features["lines"] == 0
    assert features["circles"] == 0
    assert features["arcs"] == 0


def test_extract_features_counts_text_entities(tmp_path: Path) -> None:
    extractor = EzDXFFeatureExtractor()
    path = _make_dxf_with_text(tmp_path)

    features = extractor.extract_features(str(path))

    assert features["entity_count"] == 2
    assert features["texts"] == 1
    assert features["mtexts"] == 1


def test_extract_reference_returns_dwg_reference(tmp_path: Path) -> None:
    extractor = EzDXFFeatureExtractor()
    path = _make_dxf_with_entities(tmp_path)

    reference = extractor.extract_reference(str(path))

    assert isinstance(reference, DwgReference)
    assert reference.id == path.name
    assert reference.source_file == path.name
    assert reference.metadata.file_path == str(path)
    assert reference.extracted_features["entity_count"] == 3


def test_invalid_file_raises_value_error(tmp_path: Path) -> None:
    extractor = EzDXFFeatureExtractor()
    path = tmp_path / "invalid.dxf"
    path.write_text("not a dxf file", encoding="utf-8")

    try:
        extractor.extract_features(str(path))
        raise AssertionError("Expected ValueError for invalid DWG file")
    except ValueError:
        pass
