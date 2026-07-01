from __future__ import annotations

import pytest

from building_model_v2.pipeline.dwg_knowledge import (
    DwgMetadata,
    DwgReference,
    KnowledgeRepository,
    RetrievalEngine,
    SimilarityQuery,
)


def make_reference(reference_id: str, **overrides):
    metadata = DwgMetadata(
        file_path=f"/tmp/{reference_id}.dwg",
        project_type=overrides.get("project_type", "residential"),
        plot_width=overrides.get("plot_width", 10.0),
        plot_depth=overrides.get("plot_depth", 20.0),
        floors=overrides.get("floors", 2),
        bedrooms=overrides.get("bedrooms", 3),
        bathrooms=overrides.get("bathrooms", 2),
        orientation=overrides.get("orientation", "north"),
        tags=overrides.get("tags", ["garden", "parking"]),
    )
    return DwgReference(
        id=reference_id,
        metadata=metadata,
        source_file=f"{reference_id}.dwg",
        extracted_features={},
    )


def test_empty_repository_returns_no_results() -> None:
    repository = KnowledgeRepository()
    engine = RetrievalEngine(repository)

    query = SimilarityQuery()
    assert engine.retrieve(query) == []
    assert engine.best_match(query) is None


def test_single_reference_is_returned() -> None:
    repository = KnowledgeRepository()
    reference = make_reference("ref1")
    repository.add(reference)
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(project_type="residential")
    results = engine.retrieve(query)

    assert len(results) == 1
    assert results[0].reference == reference
    assert results[0].score > 0.0


def test_multiple_references_ranked_by_score() -> None:
    repository = KnowledgeRepository()
    repository.add_many([
        make_reference("low", bedrooms=1, bathrooms=1, tags=["x"]),
        make_reference("high", bedrooms=3, bathrooms=2, tags=["garden", "parking"]),
        make_reference("medium", bedrooms=2, bathrooms=2, tags=["garden"]),
    ])
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(
        project_type="residential",
        bedrooms=3,
        bathrooms=2,
        tags=["garden", "parking"],
    )
    results = engine.retrieve(query)

    assert [result.reference.id for result in results] == ["high", "medium", "low"]


def test_best_match_returns_top_result() -> None:
    repository = KnowledgeRepository()
    repository.add_many([
        make_reference("a", bedrooms=3),
        make_reference("b", bedrooms=4),
    ])
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(bedrooms=3)
    best = engine.best_match(query)

    assert best is not None
    assert best.reference.id == "a"


def test_top_matches_limits_results() -> None:
    repository = KnowledgeRepository()
    repository.add_many([
        make_reference("one", bedrooms=3),
        make_reference("two", bedrooms=3),
        make_reference("three", bedrooms=3),
    ])
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(bedrooms=3)
    matches = engine.top_matches(query, limit=2)

    assert len(matches) == 2


def test_max_results_is_respected() -> None:
    repository = KnowledgeRepository()
    repository.add_many([
        make_reference("r1", bedrooms=3),
        make_reference("r2", bedrooms=3),
        make_reference("r3", bedrooms=3),
    ])
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(bedrooms=3, max_results=1)
    results = engine.retrieve(query)

    assert len(results) == 1


def test_zero_score_references_are_filtered() -> None:
    repository = KnowledgeRepository()
    repository.add_many([
        make_reference("good", bedrooms=3),
        make_reference("bad", bedrooms=1),
    ])
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(bedrooms=3)
    results = engine.retrieve(query)

    assert all(result.score > 0.0 for result in results)
    assert [result.reference.id for result in results] == ["good"]


def test_deterministic_ordering_for_equal_scores() -> None:
    repository = KnowledgeRepository()
    repository.add_many([
        make_reference("first", bedrooms=3, bathrooms=2),
        make_reference("second", bedrooms=3, bathrooms=2),
    ])
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(bedrooms=3, bathrooms=2)
    results = engine.retrieve(query)

    assert len(results) == 2
    assert results[0].reference.id == "first"
    assert results[1].reference.id == "second"


def test_top_matches_with_zero_limit_returns_empty_list() -> None:
    repository = KnowledgeRepository()
    repository.add(make_reference("one", bedrooms=3))
    engine = RetrievalEngine(repository)

    query = SimilarityQuery(bedrooms=3)
    matches = engine.top_matches(query, limit=0)

    assert matches == []


def test_top_matches_negative_limit_raises_value_error() -> None:
    repository = KnowledgeRepository()
    engine = RetrievalEngine(repository)
    query = SimilarityQuery()

    with pytest.raises(ValueError, match="limit must be non-negative"):
        engine.top_matches(query, limit=-1)
