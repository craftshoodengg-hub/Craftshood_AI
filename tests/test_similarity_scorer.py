from __future__ import annotations

from building_model_v2.pipeline.dwg_knowledge import (
    DwgMetadata,
    DwgReference,
    SimilarityQuery,
    SimilarityScorer,
)


def make_reference(**overrides):
    metadata = DwgMetadata(
        file_path="/tmp/sample.dwg",
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
        id=overrides.get("id", "ref1"),
        metadata=metadata,
        source_file="sample.dwg",
        extracted_features={},
    )


def test_exact_match_scores_maximum_for_nonzero_area() -> None:
    query = SimilarityQuery(
        project_type="residential",
        plot_width=10.0,
        plot_depth=20.0,
        floors=2,
        bedrooms=3,
        bathrooms=2,
        orientation="north",
        tags=["garden", "parking", "balcony", "terrace", "garage", "pool"],
    )
    reference = make_reference(tags=["garden", "parking", "balcony", "terrace", "garage", "pool"])

    assert SimilarityScorer.score(query, reference) == 1.0


def test_different_project_type_penalty() -> None:
    query = SimilarityQuery(project_type="commercial")
    reference = make_reference(project_type="residential")

    assert SimilarityScorer.score(query, reference) == 0.0


def test_bedroom_mismatch() -> None:
    query = SimilarityQuery(bedrooms=4)
    reference = make_reference(bedrooms=3)

    assert SimilarityScorer.score(query, reference) == 0.0


def test_bathroom_mismatch() -> None:
    query = SimilarityQuery(bathrooms=1)
    reference = make_reference(bathrooms=2)

    assert SimilarityScorer.score(query, reference) == 0.0


def test_floor_mismatch() -> None:
    query = SimilarityQuery(floors=1)
    reference = make_reference(floors=2)

    assert SimilarityScorer.score(query, reference) == 0.0


def test_orientation_mismatch() -> None:
    query = SimilarityQuery(orientation="south")
    reference = make_reference(orientation="north")

    assert SimilarityScorer.score(query, reference) == 0.0


def test_area_similarity_scoring() -> None:
    query = SimilarityQuery(plot_width=10.5, plot_depth=20.0)
    reference = make_reference(plot_width=10.0, plot_depth=20.0)

    assert SimilarityScorer.compare_area(query, reference) == 5.0
    assert SimilarityScorer.score(query, reference) == 0.20


def test_tag_scoring_limits_to_ten_percent() -> None:
    query = SimilarityQuery(tags=["a", "b", "c", "d", "e", "f"])
    reference = make_reference(tags=["a", "b", "c", "d", "e", "f"])

    assert SimilarityScorer.score(query, reference) == 0.10


def test_score_clamping_does_not_exceed_one() -> None:
    query = SimilarityQuery(
        project_type="residential",
        plot_width=10.0,
        plot_depth=20.0,
        floors=2,
        bedrooms=3,
        bathrooms=2,
        orientation="north",
        tags=["a", "b", "c", "d", "e", "f", "g", "h"],
    )
    reference = make_reference(
        project_type="residential",
        plot_width=10.0,
        plot_depth=20.0,
        floors=2,
        bedrooms=3,
        bathrooms=2,
        orientation="north",
        tags=["a", "b", "c", "d", "e", "f", "g", "h"],
    )

    assert SimilarityScorer.score(query, reference) == 1.0
