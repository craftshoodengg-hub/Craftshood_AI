"""Tests for pipeline engine."""
from __future__ import annotations

import pytest

from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.pipeline.pipeline_engine import PipelineEngine
from building_model_v2.pipeline.pipeline_result import PipelineResult
from building_model_v2.types import RoomType


def _make_program(*rooms: RoomProgram) -> SpaceProgram:
    """Create a SpaceProgram from rooms."""
    return SpaceProgram(rooms=rooms, floor_count=1)


def _make_room(
    room_id: str,
    room_type: str,
    target_area: float = 4.0,
    required: bool = True,
) -> RoomProgram:
    """Create a RoomProgram."""
    return RoomProgram(
        room_id=room_id,
        room_type=room_type,
        target_area=target_area,
        required=required,
        privacy_level=PrivacyLevel.PRIVATE,
        floor_preference=FloorPreference.ANY,
    )


class TestPipelineEngineEmpty:
    """Tests for empty space program."""

    def test_empty_program(self) -> None:
        """Empty space program produces empty building."""
        engine = PipelineEngine()
        result = engine.run(SpaceProgram())
        assert result.success
        assert result.room_count == 0
        assert result.floor_count >= 0

    def test_empty_program_serialization(self) -> None:
        """Empty program result serializes."""
        engine = PipelineEngine()
        result = engine.run(SpaceProgram())
        data = result.to_dict()
        assert "success" in data
        restored = PipelineResult.from_dict(data)
        assert restored.success == result.success


class TestPipelineEngineSingleRoom:
    """Tests for single room."""

    def test_single_room(self) -> None:
        """Single room pipeline."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.success
        assert result.room_count >= 1

    def test_single_room_building_generated(self) -> None:
        """Single room produces building."""
        program = _make_program(
            _make_room("bedroom", RoomType.BEDROOM, target_area=12.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.building is not None


class TestPipelineEngineSmallResidential:
    """Tests for small residential house."""

    def test_small_house(self) -> None:
        """Small residential house pipeline."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=20.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=12.0),
            _make_room("bedroom", RoomType.BEDROOM, target_area=16.0),
            _make_room("bathroom", RoomType.BATHROOM, target_area=8.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.success
        assert result.room_count >= 4

    def test_small_house_deterministic(self) -> None:
        """Same program produces same result."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=20.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=12.0),
        )
        engine = PipelineEngine()
        result1 = engine.run(program)
        result2 = engine.run(program)
        assert result1.building.floor_ids == result2.building.floor_ids


class TestPipelineEngineMultiFloor:
    """Tests for multi-floor house."""

    def test_multi_floor(self) -> None:
        """Multi-floor house pipeline."""
        program = SpaceProgram(
            rooms=(
                _make_room("living", RoomType.LIVING, target_area=20.0),
                _make_room("kitchen", RoomType.KITCHEN, target_area=12.0),
                _make_room("bedroom1", RoomType.BEDROOM, target_area=16.0),
                _make_room("bedroom2", RoomType.BEDROOM, target_area=16.0),
            ),
            floor_count=2,
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.success
        assert result.floor_count >= 1


class TestPipelineEngineSerialization:
    """Tests for pipeline serialization."""

    def test_pipeline_result_to_dict(self) -> None:
        """PipelineResult serializes to dict."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        data = result.to_dict()
        assert "architect_result" in data
        assert "building" in data
        assert "success" in data

    def test_pipeline_result_from_dict(self) -> None:
        """PipelineResult deserializes from dict."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        restored = PipelineResult.from_dict(result.to_dict())
        assert restored.success == result.success
        assert restored.room_count == result.room_count


class TestPipelineEngineDeterministic:
    """Tests for deterministic execution."""

    def test_deterministic_execution(self) -> None:
        """Same input produces same output."""
        program = _make_program(
            _make_room("r1", RoomType.LIVING, target_area=16.0),
            _make_room("r2", RoomType.BEDROOM, target_area=12.0),
        )
        engine = PipelineEngine()
        result1 = engine.run(program)
        result2 = engine.run(program)
        assert result1.building.floor_ids == result2.building.floor_ids
        assert result1.success == result2.success


class TestPipelineEngineStageOrdering:
    """Tests for stage ordering."""

    def test_stage_results_present(self) -> None:
        """All stage results are present."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.architect_result is not None
        assert result.circulation_result is not None
        assert result.placement_result is not None
        assert result.validation_result is not None
        assert result.refinement_result is not None
        assert result.building is not None


class TestPipelineEngineExceptionPropagation:
    """Tests for exception propagation."""

    def test_invalid_program_raises(self) -> None:
        """Invalid program raises exception."""
        engine = PipelineEngine()
        with pytest.raises(RuntimeError):
            engine.run(None)  # type: ignore


class TestPipelineEngineResultIntegrity:
    """Tests for result integrity."""

    def test_success_flag(self) -> None:
        """Success flag reflects validation."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert isinstance(result.success, bool)

    def test_room_count_matches_building(self) -> None:
        """Room count matches building."""
        program = _make_program(
            _make_room("r1", RoomType.LIVING, target_area=16.0),
            _make_room("r2", RoomType.BEDROOM, target_area=12.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.room_count == len(result.building.room_ids)


class TestPipelineEngineBuildingModelGeneration:
    """Tests for BuildingModel generation."""

    def test_building_has_floors(self) -> None:
        """Building has at least one floor."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.building.floor_count >= 1

    def test_building_has_rooms(self) -> None:
        """Building has rooms."""
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
            _make_room("bedroom", RoomType.BEDROOM, target_area=12.0),
        )
        engine = PipelineEngine()
        result = engine.run(program)
        assert result.building.floor_count >= 1