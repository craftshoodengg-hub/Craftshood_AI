"""Unit tests for Generation Pipeline."""
from __future__ import annotations
import pytest
from building_model_v2.ai.generation_pipeline import GenerationPipeline
from building_model_v2.ai.generation_result import GenerationResult


class TestGenerationResult:
    def test_success_with_all_fields(self):
        result = GenerationResult(final_score=90.0)
        # success checks initial_layout which is None
        assert result.success is False

    def test_quality_excellent(self):
        result = GenerationResult(final_score=95.0)
        assert result.quality == "Excellent"

    def test_quality_good(self):
        result = GenerationResult(final_score=85.0)
        assert result.quality == "Good"

    def test_quality_fair(self):
        result = GenerationResult(final_score=70.0)
        assert result.quality == "Fair"

    def test_quality_poor(self):
        result = GenerationResult(final_score=50.0)
        assert result.quality == "Poor"

    def test_serialization(self):
        result = GenerationResult(
            prompt="test prompt", final_score=85.0,
            metadata={"warnings": ["test"]},
        )
        d = result.to_dict()
        restored = GenerationResult.from_dict(d)
        assert restored.prompt == "test prompt"
        assert restored.final_score == 85.0

    def test_iteration_count_none(self):
        result = GenerationResult()
        assert result.iteration_count == 0

    def test_layout_score_none(self):
        result = GenerationResult()
        assert result.layout_score == 0.0


class TestGenerationPipeline:
    def test_empty_prompt(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("")
        assert isinstance(result, GenerationResult)
        assert result.prompt == ""

    def test_minimal_prompt(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("2BHK house")
        assert isinstance(result, GenerationResult)
        assert result.parser_result is not None
        assert result.design_requirements is not None

    def test_full_prompt(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate(
            "Design a modern east-facing 3BHK duplex on a 40x60 plot "
            "with parking and pooja room."
        )
        assert isinstance(result, GenerationResult)
        assert result.success is True
        assert result.space_program is not None
        assert result.initial_layout is not None
        assert result.initial_layout.success is True

    def test_parser_result_present(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK modern duplex")
        assert result.parser_result is not None
        assert result.design_requirements is not None
        assert result.design_requirements.building.bedrooms == 3

    def test_space_program_present(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house")
        assert result.space_program is not None
        assert result.space_program.room_count > 0
        assert result.space_program.bedroom_count == 3

    def test_initial_layout_present(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("2BHK apartment")
        assert result.initial_layout is not None
        assert result.initial_layout.success is True
        assert result.initial_layout.building_model is not None

    def test_deterministic(self):
        pipeline = GenerationPipeline()
        r1 = pipeline.generate("3BHK modern duplex")
        r2 = pipeline.generate("3BHK modern duplex")
        assert r1.parser_result.requirements.building.bedrooms == r2.parser_result.requirements.building.bedrooms
        assert r1.space_program.room_count == r2.space_program.room_count
        assert r1.initial_layout.placed_rooms == r2.initial_layout.placed_rooms

    def test_duplex(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("4BHK duplex")
        assert result.success is True
        assert result.space_program.floor_count == 2

    def test_apartment(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("2BHK apartment")
        assert result.success is True
        assert result.space_program.floor_count == 1

    def test_villa(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("5BHK villa")
        assert result.success is True

    def test_parking(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house with parking")
        room_types = {r.room_type for r in result.space_program.rooms}
        assert "parking" in room_types

    def test_pooja(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house with pooja room")
        room_types = {r.room_type for r in result.space_program.rooms}
        assert "pooja" in room_types

    def test_office(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house with office")
        room_types = {r.room_type for r in result.space_program.rooms}
        assert "office" in room_types

    def test_warnings_stored(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("")
        assert "warnings" in result.metadata

    def test_pipeline_order(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house")
        assert result.parser_result is not None
        assert result.design_requirements is not None
        assert result.space_program is not None
        assert result.initial_layout is not None
