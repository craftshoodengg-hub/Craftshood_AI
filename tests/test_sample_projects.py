"""Tests for deterministic sample projects."""
from __future__ import annotations

from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.examples.sample_projects import SampleProjects
from building_model_v2.pipeline.pipeline_engine import PipelineEngine
from building_model_v2.pipeline.pipeline_result import PipelineResult
from building_model_v2.types import RoomType


class TestSampleProjects:
    def test_sample_projects_return_space_program(self) -> None:
        samples = (
            SampleProjects.one_bhk(),
            SampleProjects.two_bhk(),
            SampleProjects.three_bhk(),
            SampleProjects.duplex(),
            SampleProjects.small_office(),
            SampleProjects.retail_shop(),
        )

        for sample in samples:
            assert isinstance(sample, SpaceProgram)
            assert sample.rooms

    def test_sample_projects_room_counts(self) -> None:
        assert SampleProjects.one_bhk().room_count == 4
        assert SampleProjects.two_bhk().room_count == 6
        assert SampleProjects.three_bhk().room_count == 8
        assert SampleProjects.duplex().room_count == 9
        assert SampleProjects.small_office().room_count == 5
        assert SampleProjects.retail_shop().room_count == 4

    def test_sample_projects_required_rooms_exist(self) -> None:
        one = SampleProjects.one_bhk()
        assert any(room.id == "living" for room in one.rooms)
        assert any(room.id == "kitchen" for room in one.rooms)
        assert any(room.id == "bedroom" for room in one.rooms)
        assert any(room.id == "bathroom" for room in one.rooms)

        two = SampleProjects.two_bhk()
        assert any(room.id == "master_bedroom" for room in two.rooms)
        assert any(room.id == "bedroom" for room in two.rooms)
        assert any(room.room_type == RoomType.DINING for room in two.rooms)

        three = SampleProjects.three_bhk()
        assert any(room.id == "utility" for room in three.rooms)
        assert sum(1 for room in three.rooms if room.room_type == RoomType.BEDROOM) == 3

        duplex = SampleProjects.duplex()
        assert any(room.id == "guest_bedroom" for room in duplex.rooms)
        assert any(room.id == "family_lounge" for room in duplex.rooms)
        assert duplex.floor_count == 2

        office = SampleProjects.small_office()
        assert any(room.id == "reception" for room in office.rooms)
        assert any(room.id == "meeting" for room in office.rooms)

        retail = SampleProjects.retail_shop()
        assert any(room.id == "shop" for room in retail.rooms)
        assert any(room.id == "storage" for room in retail.rooms)

    def test_sample_projects_deterministic_generation(self) -> None:
        first = SampleProjects.three_bhk()
        second = SampleProjects.three_bhk()
        assert first.to_dict() == second.to_dict()
        assert first.rooms == second.rooms

    def test_sample_projects_serialization(self) -> None:
        sample = SampleProjects.duplex()
        data = sample.to_dict()
        restored = SpaceProgram.from_dict(data)
        assert restored.floor_count == sample.floor_count
        assert restored.room_count == sample.room_count
        assert restored.to_dict() == sample.to_dict()

    def test_sample_projects_pipeline_compatibility(self) -> None:
        engine = PipelineEngine()
        for sample in (
            SampleProjects.one_bhk(),
            SampleProjects.two_bhk(),
            SampleProjects.three_bhk(),
            SampleProjects.duplex(),
            SampleProjects.small_office(),
            SampleProjects.retail_shop(),
        ):
            result = engine.run(sample)
            assert isinstance(result, PipelineResult)
            assert result.room_count == len(result.building.room_ids)
            assert result.floor_count == len(result.building.floor_ids)
            assert result.room_count >= 1
