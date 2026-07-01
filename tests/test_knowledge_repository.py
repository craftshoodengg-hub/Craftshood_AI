from __future__ import annotations

from building_model_v2.pipeline.dwg_knowledge import (
    DwgMetadata,
    DwgReference,
    KnowledgeRepository,
)


def _make_reference(reference_id: str, bedrooms: int, floors: int, project_type: str, tags: list[str]) -> DwgReference:
    metadata = DwgMetadata(
        file_path=f"/tmp/{reference_id}.dwg",
        project_type=project_type,
        plot_width=10.0,
        plot_depth=20.0,
        floors=floors,
        bedrooms=bedrooms,
        bathrooms=1,
        room_count=4,
        total_area=800.0,
        orientation="north",
        tags=tags,
    )
    return DwgReference(
        id=reference_id,
        metadata=metadata,
        source_file=f"{reference_id}.dwg",
        extracted_features={"example": True},
    )


def test_repository_add_and_count() -> None:
    repo = KnowledgeRepository()
    reference = _make_reference("ref1", bedrooms=3, floors=1, project_type="residential", tags=["test"])
    repo.add(reference)

    assert repo.count() == 1
    assert repo.all() == [reference]


def test_repository_add_many_preserves_insertion_order() -> None:
    repo = KnowledgeRepository()
    references = [
        _make_reference("ref1", bedrooms=2, floors=1, project_type="residential", tags=["alpha"]),
        _make_reference("ref2", bedrooms=3, floors=2, project_type="commercial", tags=["beta"]),
        _make_reference("ref3", bedrooms=4, floors=1, project_type="residential", tags=["alpha", "beta"]),
    ]
    repo.add_many(references)

    assert repo.all() == references


def test_repository_duplicate_ids_raise_value_error() -> None:
    repo = KnowledgeRepository()
    reference = _make_reference("ref1", bedrooms=3, floors=1, project_type="residential", tags=["test"])
    repo.add(reference)

    try:
        repo.add(reference)
    except ValueError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("Expected ValueError for duplicate ID")


def test_repository_remove_nonexistent_does_nothing() -> None:
    repo = KnowledgeRepository()
    repo.add(_make_reference("ref1", bedrooms=1, floors=1, project_type="residential", tags=["test"]))
    repo.remove("missing")
    assert repo.count() == 1


def test_repository_remove_removes_item() -> None:
    repo = KnowledgeRepository()
    reference = _make_reference("ref1", bedrooms=1, floors=1, project_type="residential", tags=["test"])
    repo.add(reference)
    repo.remove(reference.id)

    assert repo.count() == 0
    assert repo.find_by_id(reference.id) is None


def test_repository_clear() -> None:
    repo = KnowledgeRepository()
    repo.add_many([
        _make_reference("ref1", bedrooms=1, floors=1, project_type="residential", tags=["test"]),
        _make_reference("ref2", bedrooms=2, floors=2, project_type="commercial", tags=["demo"]),
    ])
    repo.clear()

    assert repo.count() == 0
    assert repo.all() == []


def test_repository_find_by_id() -> None:
    repo = KnowledgeRepository()
    reference = _make_reference("ref1", bedrooms=2, floors=1, project_type="residential", tags=["search"])
    repo.add(reference)

    assert repo.find_by_id("ref1") == reference
    assert repo.find_by_id("missing") is None


def test_repository_find_by_project_type() -> None:
    repo = KnowledgeRepository()
    repo.add_many([
        _make_reference("ref1", bedrooms=2, floors=1, project_type="residential", tags=["search"]),
        _make_reference("ref2", bedrooms=3, floors=2, project_type="commercial", tags=["search"]),
    ])

    assert repo.find_by_project_type("residential") == [repo.find_by_id("ref1")]
    assert repo.find_by_project_type("commercial") == [repo.find_by_id("ref2")]


def test_repository_find_by_bedrooms() -> None:
    repo = KnowledgeRepository()
    repo.add_many([
        _make_reference("ref1", bedrooms=2, floors=1, project_type="residential", tags=["search"]),
        _make_reference("ref2", bedrooms=3, floors=2, project_type="commercial", tags=["search"]),
    ])

    assert repo.find_by_bedrooms(2) == [repo.find_by_id("ref1")]
    assert repo.find_by_bedrooms(5) == []


def test_repository_find_by_floors() -> None:
    repo = KnowledgeRepository()
    repo.add_many([
        _make_reference("ref1", bedrooms=2, floors=1, project_type="residential", tags=["search"]),
        _make_reference("ref2", bedrooms=3, floors=2, project_type="commercial", tags=["search"]),
    ])

    assert repo.find_by_floors(1) == [repo.find_by_id("ref1")]
    assert repo.find_by_floors(2) == [repo.find_by_id("ref2")]


def test_repository_find_by_tag() -> None:
    repo = KnowledgeRepository()
    repo.add_many([
        _make_reference("ref1", bedrooms=2, floors=1, project_type="residential", tags=["alpha"]),
        _make_reference("ref2", bedrooms=3, floors=2, project_type="commercial", tags=["beta"]),
        _make_reference("ref3", bedrooms=4, floors=1, project_type="residential", tags=["alpha", "beta"]),
    ])

    assert repo.find_by_tag("alpha") == [repo.find_by_id("ref1"), repo.find_by_id("ref3")]
    assert repo.find_by_tag("beta") == [repo.find_by_id("ref2"), repo.find_by_id("ref3")]
