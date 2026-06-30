"""Integration tests for the end-to-end pipeline and export flow."""
from __future__ import annotations

from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.export.drawing_builder import build_drawing_model
from building_model_v2.export.dxf_exporter import DXFExporter
from building_model_v2.export.svg_exporter import export_svg_to_string
from building_model_v2.pipeline.pipeline_engine import PipelineEngine
from building_model_v2.pipeline.pipeline_result import PipelineResult
from building_model_v2.ai.requirement_parser import RequirementParser
from building_model_v2.ai.space_generator import SpaceProgramGenerator
from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel


def _make_room(
    room_id: str,
    room_type: str,
    target_area: float = 10.0,
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


def _make_program(*rooms: RoomProgram, floor_count: int = 1) -> SpaceProgram:
    return SpaceProgram(rooms=rooms, floor_count=floor_count)


class TestPipelineIntegration:
    def test_pipeline_end_to_end_with_export(self) -> None:
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=20.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=12.0),
            _make_room("bedroom", RoomType.BEDROOM, target_area=16.0),
            floor_count=1,
        )

        engine = PipelineEngine()
        result = engine.run(program)

        assert result.success
        assert result.room_count == len(result.building.room_ids)
        assert result.floor_count == len(result.building.floor_ids)
        assert result.room_count == 3
        assert result.floor_count == 1

        data = result.to_dict()
        restored = PipelineResult.from_dict(data)
        assert restored.success == result.success
        assert restored.room_count == result.room_count
        assert restored.floor_count == result.floor_count
        assert restored.building.room_ids == result.building.room_ids
        assert restored.building.floor_ids == result.building.floor_ids

        model = BuildingModel(building=restored.building)
        drawing = build_drawing_model(model)
        svg = export_svg_to_string(drawing)
        assert isinstance(svg, str)
        assert svg.startswith("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        assert "<svg" in svg
        assert "viewBox=" in svg

        exporter = DXFExporter()
        dxf = exporter.export_to_string(model)
        assert isinstance(dxf, str)
        assert "EOF" in dxf
        assert "SECTION" in dxf

    def test_pipeline_multi_floor_end_to_end(self) -> None:
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=20.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=12.0),
            _make_room("bedroom1", RoomType.BEDROOM, target_area=16.0),
            _make_room("bedroom2", RoomType.BEDROOM, target_area=16.0),
            floor_count=2,
        )

        engine = PipelineEngine()
        result = engine.run(program)

        assert result.success
        assert result.room_count == 4
        assert result.floor_count >= 1
        assert len(result.building.floor_ids) == result.floor_count
        assert len(result.building.room_ids) == result.room_count

    def test_1bhk_simple_layout(self) -> None:
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=20.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=14.0),
            _make_room("bedroom", RoomType.BEDROOM, target_area=16.0),
            _make_room("bathroom", RoomType.BATHROOM, target_area=8.0),
            floor_count=1,
        )

        engine = PipelineEngine()
        result1 = engine.run(program)
        result2 = engine.run(program)

        assert result1.success
        assert result1.room_count == 4
        assert result1.building.room_ids == result2.building.room_ids
        assert result1.building.floor_ids == result2.building.floor_ids

    def test_2bhk_residential_layout(self) -> None:
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=22.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=14.0),
            _make_room("bedroom1", RoomType.BEDROOM, target_area=16.0),
            _make_room("bedroom2", RoomType.BEDROOM, target_area=16.0),
            _make_room("bathroom", RoomType.BATHROOM, target_area=8.0),
            floor_count=1,
        )

        engine = PipelineEngine()
        result = engine.run(program)

        assert result.success
        assert result.room_count == 5
        assert result.floor_count == 1
        assert len(result.building.room_ids) == 5

    def test_3bhk_villa_layout(self) -> None:
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=12.0),
            _make_room("bedroom1", RoomType.BEDROOM, target_area=10.0),
            _make_room("bedroom2", RoomType.BEDROOM, target_area=10.0),
            _make_room("bedroom3", RoomType.BEDROOM, target_area=10.0),
            _make_room("bathroom1", RoomType.BATHROOM, target_area=6.0),
            _make_room("bathroom2", RoomType.BATHROOM, target_area=6.0),
            _make_room("balcony", RoomType.BALCONY, target_area=4.0, required=False),
            floor_count=1,
        )

        engine = PipelineEngine()
        result1 = engine.run(program)
        result2 = engine.run(program)

        assert result1.success
        assert result1.room_count == 8
        assert result1.floor_count == 1
        assert result1.building.room_ids == result2.building.room_ids
        assert result1.building.floor_ids == result2.building.floor_ids

    def test_duplex_multi_floor_layout(self) -> None:
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=16.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=12.0),
            _make_room("bedroom1", RoomType.BEDROOM, target_area=12.0),
            _make_room("bedroom2", RoomType.BEDROOM, target_area=12.0),
            _make_room("bathroom1", RoomType.BATHROOM, target_area=8.0),
            _make_room("bathroom2", RoomType.BATHROOM, target_area=8.0),
            _make_room("stair", RoomType.STAIRCASE, target_area=10.0),
            floor_count=2,
        )

        engine = PipelineEngine()
        result1 = engine.run(program)
        result2 = engine.run(program)

        assert result1.success
        assert program.floor_count == 2
        assert result1.room_count == 7
        assert result1.building.room_ids == result2.building.room_ids
        assert result1.building.floor_ids == result2.building.floor_ids
        assert len(result1.building.floor_ids) == result1.floor_count
        assert result1.floor_count >= 1

    def test_requirement_parser_to_space_program_pipeline(self) -> None:
        prompt = "3BHK duplex villa with parking and balcony"
        parser = RequirementParser()
        parse_result = parser.parse(prompt)

        assert parse_result.requirements.building.bedrooms == 3
        assert parse_result.requirements.building.duplex
        assert not parse_result.requirements.building.villa
        assert parse_result.requirements.building.parking

        generator = SpaceProgramGenerator()
        space_program = generator.generate(parse_result.requirements)

        assert space_program.floor_count == 2
        assert space_program.rooms

        engine = PipelineEngine()
        result = engine.run(space_program)

        assert isinstance(result, PipelineResult)
        assert result.floor_count == len(result.building.floor_ids)
        assert result.room_count == len(result.building.room_ids)
        assert result.room_count >= 1

    def test_evaluation_pipeline_can_evaluate_generated_building(self) -> None:
        program = _make_program(
            _make_room("living", RoomType.LIVING, target_area=22.0),
            _make_room("kitchen", RoomType.KITCHEN, target_area=14.0),
            _make_room("bedroom", RoomType.BEDROOM, target_area=16.0),
            _make_room("bathroom", RoomType.BATHROOM, target_area=8.0),
            floor_count=1,
        )

        engine = PipelineEngine()
        result = engine.run(program)
        building_model = BuildingModel(building=result.building)

        evaluation = EvaluationPipeline()
        report = evaluation.evaluate(building_model)

        assert report is not None
        assert getattr(report, 'summary', None) is not None
        assert getattr(report.summary, 'overall_score', None) is not None
