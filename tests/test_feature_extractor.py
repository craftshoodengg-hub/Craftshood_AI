from __future__ import annotations

import pytest

from building_model_v2.pipeline.dwg_knowledge import (
    BaseFeatureExtractor,
    DummyFeatureExtractor,
    DwgMetadata,
    DwgReference,
)


def test_dummy_feature_extractor_metadata_extraction() -> None:
    extractor = DummyFeatureExtractor()
    metadata = extractor.extract_metadata("sample_residential.dwg")

    assert isinstance(metadata, DwgMetadata)
    assert metadata.file_path == "sample_residential.dwg"
    assert metadata.project_type == "residential"
    assert metadata.plot_width == 20.0
    assert metadata.tags == ["dummy", "test", "residential"]


def test_dummy_feature_extractor_feature_extraction() -> None:
    extractor = DummyFeatureExtractor()
    features = extractor.extract_features("sample_commercial.dwg")

    assert isinstance(features, dict)
    assert features["file_path"] == "sample_commercial.dwg"
    assert features["room_count"] == 7
    assert features["has_parking"] is True
    assert "zones" in features


def test_dummy_feature_extractor_reference_extraction() -> None:
    extractor = DummyFeatureExtractor()
    reference = extractor.extract_reference("sample_residential.dwg")

    assert isinstance(reference, DwgReference)
    assert reference.id == "dummy-sample_residential.dwg"
    assert reference.source_file == "sample_residential.dwg"
    assert reference.metadata.file_path == "sample_residential.dwg"
    assert reference.extracted_features["main_orientation"] == "north"


def test_dummy_feature_extractor_serialization() -> None:
    extractor = DummyFeatureExtractor()
    reference = extractor.extract_reference("sample_residential.dwg")

    restored = DwgReference.from_dict(reference.to_dict())
    assert restored == reference


def test_base_feature_extractor_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseFeatureExtractor()
