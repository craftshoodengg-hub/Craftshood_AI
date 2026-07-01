from __future__ import annotations

from building_model_v2.pipeline.dwg_knowledge import (
    DwgMetadata,
    DwgReference,
    KnowledgeRepository,
    RetrievalService,
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


def test_empty_repository_behavior() -> None:
    service = RetrievalService()
    query = SimilarityQuery()

    assert service.count() == 0
    assert service.retrieve(query) == []
    assert service.best_match(query) is None
    assert service.top_matches(query, limit=1) == []


def test_add_reference_increases_count() -> None:
    service = RetrievalService()
    service.add_reference(make_reference("ref1"))

    assert service.count() == 1


def test_add_references_appends_multiple() -> None:
    service = RetrievalService()
    service.add_references([make_reference("ref1"), make_reference("ref2")])

    assert service.count() == 2


def test_clear_resets_repository() -> None:
    service = RetrievalService()
    service.add_reference(make_reference("ref1"))
    service.clear()

    assert service.count() == 0
    assert service.retrieve(SimilarityQuery()) == []


def test_repository_passthrough_returns_underlying_repository() -> None:
    repository = KnowledgeRepository()
    service = RetrievalService(repository=repository)

    assert service.repository() is repository


def test_retrieve_delegates_to_engine() -> None:
    service = RetrievalService()
    service.add_reference(make_reference("high", bedrooms=3))
    service.add_reference(make_reference("low", bedrooms=1))

    results = service.retrieve(SimilarityQuery(bedrooms=3))

    assert len(results) == 1
    assert results[0].reference.id == "high"


def test_best_match_returns_highest_score() -> None:
    service = RetrievalService()
    service.add_reference(make_reference("a", bedrooms=3))
    service.add_reference(make_reference("b", bedrooms=4))

    best = service.best_match(SimilarityQuery(bedrooms=3))

    assert best is not None
    assert best.reference.id == "a"


def test_top_matches_respects_limit() -> None:
    service = RetrievalService()
    service.add_references(
        [
            make_reference("one", bedrooms=3),
            make_reference("two", bedrooms=3),
            make_reference("three", bedrooms=3),
        ]
    )

    matches = service.top_matches(SimilarityQuery(bedrooms=3), limit=2)

    assert len(matches) == 2


def test_deterministic_behavior_for_equal_scores() -> None:
    service = RetrievalService()
    service.add_reference(make_reference("first", bedrooms=3, bathrooms=2))
    service.add_reference(make_reference("second", bedrooms=3, bathrooms=2))

    results = service.retrieve(SimilarityQuery(bedrooms=3, bathrooms=2))

    assert [result.reference.id for result in results] == ["first", "second"]
