from __future__ import annotations

import pytest

from building_model_v2.pipeline.dwg_knowledge import DwgMetadata, DwgReference


def test_dwg_metadata_creation_and_serialization() -> None:
    metadata = DwgMetadata(
        file_path="/data/drawings/project1.dwg",
        project_type="residential",
        plot_width=18.0,
        plot_depth=24.0,
        floors=2,
        bedrooms=4,
        bathrooms=3,
        room_count=10,
        total_area=2200.0,
        orientation="north",
        tags=["villa", "garden", "parking"],
    )

    data = metadata.to_dict()
    assert data["file_path"] == "/data/drawings/project1.dwg"
    assert data["project_type"] == "residential"
    assert data["plot_width"] == 18.0
    assert data["plot_depth"] == 24.0
    assert data["floors"] == 2
    assert data["bedrooms"] == 4
    assert data["bathrooms"] == 3
    assert data["room_count"] == 10
    assert data["total_area"] == 2200.0
    assert data["orientation"] == "north"
    assert data["tags"] == ["villa", "garden", "parking"]

    restored = DwgMetadata.from_dict(data)
    assert restored == metadata


def test_dwg_reference_creation_and_serialization() -> None:
    metadata = DwgMetadata(
        file_path="/data/drawings/project2.dwg",
        project_type="commercial",
        plot_width=None,
        plot_depth=None,
        floors=None,
        bedrooms=None,
        bathrooms=None,
        room_count=None,
        total_area=None,
        orientation=None,
        tags=["office", "urban"],
    )
    reference = DwgReference(
        id="ref-123",
        metadata=metadata,
        source_file="project2.dwg",
        extracted_features={
            "room_count": 8,
            "has_parking": False,
            "main_orientation": "east",
        },
    )

    data = reference.to_dict()
    assert data["id"] == "ref-123"
    assert data["metadata"]["project_type"] == "commercial"
    assert data["source_file"] == "project2.dwg"
    assert data["extracted_features"]["room_count"] == 8
    assert data["extracted_features"]["main_orientation"] == "east"

    restored = DwgReference.from_dict(data)
    assert restored == reference


def test_dwg_metadata_optional_fields_and_tags() -> None:
    metadata = DwgMetadata(
        file_path="/data/drawings/project3.dwg",
        project_type="residential",
        tags=[],
    )

    data = metadata.to_dict()
    assert data["plot_width"] is None
    assert data["plot_depth"] is None
    assert data["floors"] is None
    assert data["bedrooms"] is None
    assert data["bathrooms"] is None
    assert data["room_count"] is None
    assert data["total_area"] is None
    assert data["orientation"] is None
    assert data["tags"] == []

    restored = DwgMetadata.from_dict(data)
    assert restored.file_path == metadata.file_path
    assert restored.project_type == metadata.project_type
    assert restored.tags == []


def test_dwg_reference_extracted_features_are_preserved() -> None:
    metadata = DwgMetadata(
        file_path="/data/drawings/project4.dwg",
        project_type="residential",
        tags=["test"],
    )
    features = {
        "zones": ["living", "kitchen", "bedroom"],
        "areas": {"living": 25.0, "kitchen": 12.0},
        "notes": "Accepted as useful example design.",
    }
    reference = DwgReference(
        id="ref-456",
        metadata=metadata,
        source_file="project4.dwg",
        extracted_features=features,
    )

    restored = DwgReference.from_dict(reference.to_dict())
    assert restored.extracted_features == features
    assert restored.metadata.tags == ["test"]
