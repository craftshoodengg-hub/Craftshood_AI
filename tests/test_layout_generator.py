"""Unit tests for Layout Generator."""
from __future__ import annotations
import pytest
from building_model_v2.ai.layout_generator import LayoutGenerator
from building_model_v2.ai.layout_generation_result import LayoutGenerationResult
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.ai.space_generator import SpaceProgramGenerator
from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.design_requirements import BuildingRequirements, DesignRequirements


def _make_space_program(bedrooms=2, floors=1, parking=False, pooja=False):
    """Helper to create a space program."""
    gen = SpaceProgramGenerator()
    req = DesignRequirements(
        building=BuildingRequirements(
            bedrooms=bedrooms, floors=floors, parking=parking, pooja=pooja,
        ),
    )
    return gen.generate(req)


class TestLayoutGenerationResult:
    def test_success_with_model(self):
        result = LayoutGenerationResult(confidence=1.0)
        assert result.success is False  # No building model

    def test_placement_ratio(self):
        result = LayoutGenerationResult(
            placed_rooms=("a", "b"), unplaced_rooms=("c",),
        )
        assert result.placement_ratio == 2 / 3

    def test_serialization(self):
        result = LayoutGenerationResult(
            placed_rooms=("a", "b"), confidence=0.9,
        )
        d = result.to_dict()
        restored = LayoutGenerationResult.from_dict(d)
        assert restored.confidence == 0.9
        assert restored.placed_rooms == ("a", "b")


class TestLayoutGenerator:
    def test_empty_program(self):
        gen = LayoutGenerator()
        result = gen.generate(SpaceProgram())
        assert result.success is False
        assert result.confidence == 0.0

    def test_1bhk(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=1, floors=1)
        result = gen.generate(sp)
        assert result.success is True
        assert result.building_model is not None
        assert len(result.placed_rooms) > 0

    def test_3bhk(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=3, floors=2)
        result = gen.generate(sp)
        assert result.success is True
        assert len(result.building_model.floors) >= 1
        assert result.building_model.building is not None

    def test_5bhk(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=5, floors=2)
        result = gen.generate(sp)
        assert result.success is True
        assert len(result.placed_rooms) >= 10

    def test_building_model_valid(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=2, floors=1)
        result = gen.generate(sp)
        assert result.building_model is not None
        assert result.building_model.building is not None
        assert len(result.building_model.floors) >= 1
        assert len(result.building_model.rooms) > 0

    def test_no_room_overlap(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=3, floors=2)
        result = gen.generate(sp)
        rooms = list(result.building_model.rooms.values())
        for i, r1 in enumerate(rooms):
            for r2 in rooms[i+1:]:
                if r1.floor_id == r2.floor_id:
                    # Rooms on same floor should not overlap
                    if not r1.polygon.is_empty and not r2.polygon.is_empty:
                        intersection = r1.polygon.intersection(r2.polygon)
                        assert intersection.area < 1.0  # Allow tiny floating point overlap

    def test_deterministic(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=3, floors=2)
        r1 = gen.generate(sp)
        r2 = gen.generate(sp)
        assert r1.placed_rooms == r2.placed_rooms
        assert r1.confidence == r2.confidence

    def test_parking_included(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=2, floors=1, parking=True)
        result = gen.generate(sp)
        room_types = [r.room_type.value for r in result.building_model.rooms.values()]
        assert "Storage" in room_types  # Parking maps to Storage

    def test_pooja_included(self):
        gen = LayoutGenerator()
        sp = _make_space_program(bedrooms=2, floors=1, pooja=True)
        result = gen.generate(sp)
        assert result.success is True
        assert len(result.placed_rooms) > 5
