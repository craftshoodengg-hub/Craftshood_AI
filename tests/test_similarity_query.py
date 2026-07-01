from __future__ import annotations

import pytest

from building_model_v2.pipeline.dwg_knowledge import (
    DwgMetadata,
    DwgReference,
    SimilarityQuery,
    SimilarityResult,
)


def test_similarity_query_creation_and_serialization() -> None:
    query = SimilarityQuery(
        project_type="residential",
        plot_width=15.0,
        plot_depth=20.0,
        floors=2,
        bedrooms=3,
        bathrooms=2,
        orientation="north",
        tags=["garden", "parking"],
        max_results=5,
    )

    assert query.project_type == "residential"
    assert query.area() == 300.0
    assert query.max_results == 5

    restored = SimilarityQuery.from_dict(query.to_dict())
    assert restored == query


def test_similarity_query_default_max_results() -> None:
    query = SimilarityQuery()
    assert query.max_results == 10


def test_similarity_query_max_results_validation() -> None:
    with pytest.raises(ValueError, match="max_results must be between 1 and 100"):
        SimilarityQuery(max_results=0)

    with pytest.raises(ValueError, match="max_results must be between 1 and 100"):
        SimilarityQuery(max_results=101)


def test_similarity_result_creation_and_serialization() -> None:
    metadata = DwgMetadata(
        file_path="/tmp/project.dwg",
        project_type="commercial",
        tags=["example"],
    )
    reference = DwgReference(
        id="ref1",
        metadata=metadata,
        source_file="project.dwg",
        extracted_features={"room_count": 5},
    )
    result = SimilarityResult(reference=reference, score=0.75)

    assert result.reference == reference
    assert result.score == 0.75

    restored = SimilarityResult.from_dict(result.to_dict())
    assert restored == result


def test_similarity_result_score_validation() -> None:
    metadata = DwgMetadata(
        file_path="/tmp/project.dwg",
        project_type="commercial",
        tags=["example"],
    )
    reference = DwgReference(
        id="ref1",
        metadata=metadata,
        source_file="project.dwg",
        extracted_features={"room_count": 5},
    )

    with pytest.raises(ValueError, match="score must be between 0 and 1"):
        SimilarityResult(reference=reference, score=-0.1)

    with pytest.raises(ValueError, match="score must be between 0 and 1"):
        SimilarityResult(reference=reference, score=1.1)
