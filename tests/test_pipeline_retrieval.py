"""Pipeline retrieval integration tests."""
from __future__ import annotations

from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.pipeline.design_request import DesignRequest
from building_model_v2.pipeline.dwg_knowledge import DwgMetadata, DwgReference, RetrievalService
from building_model_v2.pipeline.pipeline_engine import PipelineEngine
from building_model_v2.pipeline.pipeline_result import PipelineResult
from building_model_v2.types import RoomType


def _make_program(*rooms: RoomProgram) -> SpaceProgram:
    return SpaceProgram(rooms=rooms, floor_count=1)


def _make_room(
    room_id: str,
    room_type: str,
    target_area: float = 4.0,
    required: bool = True,
) -> RoomProgram:
    return RoomProgram(
        room_id=room_id,
        room_type=room_type,
        target_area=target_area,
        required=required,
        privacy_level=PrivacyLevel.PRIVATE,
        floor_preference=FloorPreference.ANY,
    )


def _make_request() -> DesignRequest:
    return DesignRequest(
        project_type="residential",
        plot_width=10.0,
        plot_depth=20.0,
        floors=1,
        bedrooms=2,
        bathrooms=1,
        parking=1,
        kitchen_type="open",
        pooja_room=False,
        living_room=True,
        dining_room=True,
        staircase=True,
        orientation="north",
        special_requirements=("garden",),
    )


def _make_reference(reference_id: str, bedrooms: int = 2) -> DwgReference:
    return DwgReference(
        id=reference_id,
        metadata=DwgMetadata(
            file_path=f"/tmp/{reference_id}.dwg",
            project_type="residential",
            plot_width=10.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=bedrooms,
            bathrooms=1,
            orientation="north",
            tags=["garden"],
        ),
        source_file=f"{reference_id}.dwg",
        extracted_features={},
    )


class TestPipelineRetrieval:
    def test_pipeline_without_retrieval_service_still_succeeds(self) -> None:
        program = _make_program(_make_room("living", RoomType.LIVING, target_area=16.0))
        request = _make_request()
        engine = PipelineEngine()

        result = engine.run(program, design_request=request)

        assert result.success
        assert result.retrieval_count == 0
        assert result.retrieval_score == 0.0
        assert result.reference_designs == []

    def test_pipeline_with_empty_retrieval_repository_returns_zero_metadata(self) -> None:
        program = _make_program(_make_room("living", RoomType.LIVING, target_area=16.0))
        request = _make_request()
        retrieval_service = RetrievalService()
        engine = PipelineEngine(retrieval_service=retrieval_service)

        result = engine.run(program, design_request=request)

        assert result.success
        assert result.retrieval_count == 0
        assert result.retrieval_score == 0.0
        assert result.reference_designs == []

    def test_pipeline_with_single_reference_populates_retrieval_metadata(self) -> None:
        program = _make_program(_make_room("living", RoomType.LIVING, target_area=16.0))
        request = _make_request()
        retrieval_service = RetrievalService()
        retrieval_service.add_reference(_make_reference("ref-1", bedrooms=2))
        engine = PipelineEngine(retrieval_service=retrieval_service)

        result = engine.run(program, design_request=request)

        assert result.success
        assert result.retrieval_count == 1
        assert result.retrieval_score > 0.0
        assert len(result.reference_designs) == 1
        assert result.reference_designs[0].id == "ref-1"

    def test_pipeline_with_multiple_references_returns_multiple_matches(self) -> None:
        program = _make_program(_make_room("living", RoomType.LIVING, target_area=16.0))
        request = _make_request()
        retrieval_service = RetrievalService()
        retrieval_service.add_reference(_make_reference("ref-1", bedrooms=2))
        retrieval_service.add_reference(_make_reference("ref-2", bedrooms=2))
        engine = PipelineEngine(retrieval_service=retrieval_service)

        result = engine.run(program, design_request=request)

        assert result.success
        assert result.retrieval_count == 2
        assert result.retrieval_score > 0.0
        assert len(result.reference_designs) == 2
        assert {reference.id for reference in result.reference_designs} == {"ref-1", "ref-2"}

    def test_serialization_preserves_retrieval_metadata(self) -> None:
        program = _make_program(_make_room("living", RoomType.LIVING, target_area=16.0))
        request = _make_request()
        retrieval_service = RetrievalService()
        retrieval_service.add_reference(_make_reference("ref-1", bedrooms=2))
        engine = PipelineEngine(retrieval_service=retrieval_service)

        result = engine.run(program, design_request=request)
        restored = PipelineResult.from_dict(result.to_dict())

        assert restored.success == result.success
        assert restored.retrieval_count == result.retrieval_count
        assert restored.retrieval_score == result.retrieval_score
        assert [reference.id for reference in restored.reference_designs] == [reference.id for reference in result.reference_designs]
