"""Unit tests for Vastu Shastra constraints.

Covers:
    - Preferred locations
    - Acceptable locations
    - Invalid locations
    - Missing metadata
    - Serialization
    - Deterministic evaluation
    - Engine integration
    - Multiple issues
    - Empty models
    - Repeated evaluation
"""
from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError

from building_model_v2.constraints.constraint_result import ConstraintResult
from building_model_v2.constraints.constraint_severity import ConstraintSeverity
from building_model_v2.constraints.constraint_engine import ConstraintEngine
from building_model_v2.constraints.vastu_constraints import (
    BrahmasthanConstraint,
    EntranceDirectionConstraint,
    KitchenPlacementConstraint,
    MasterBedroomConstraint,
    PoojaRoomConstraint,
    StaircaseConstraint,
    ToiletPlacementConstraint,
    VastuConstraint,
    VASTU_BRAHMASTHAN,
    VASTU_ENTRANCE_DIRECTION,
    VASTU_KITCHEN_PLACEMENT,
    VASTU_MASTER_BEDROOM,
    VASTU_POOJA_ROOM,
    VASTU_STAIRCASE,
    VASTU_TOILET,
)
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.entities_wall import Wall
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.vastu.vastu_direction import VastuDirection
from building_model_v2.vastu.vastu_metadata import VastuMetadata
from building_model_v2.vastu.vastu_zone import VastuZone


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def building_model():
    building = Building.create(name="Test Building", floor_ids=("floor_1",))
    floor = Floor.create(name="Ground Floor", level=0, room_ids=frozenset({"room_1"}))
    rooms = {
        "room_1": Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        ),
    }
    return BuildingModel(
        building=building,
        floors={"floor_1": floor},
        rooms=rooms,
        walls={},
        columns={},
        stairs={},
        doors={},
        windows={},
        relationships=[],
    )


@pytest.fixture
def building_model_with_kitchen():
    building = Building.create(name="Test", floor_ids=("f1",))
    floor = Floor.create(name="F1", level=0, room_ids=frozenset({"kitchen_1"}))
    kitchen = Room.create(
        vertices=[(0, 0), (8, 0), (8, 8), (0, 8)],
        room_type=RoomType.KITCHEN,
        metadata={"vastu_zone": "AGNEYA"},
    )
    return BuildingModel(
        building=building,
        floors={"f1": floor},
        rooms={"kitchen_1": kitchen},
        walls={},
        columns={},
        stairs={},
        doors={},
        windows={},
        relationships=[],
    )


@pytest.fixture
def building_model_vastu_metadata():
    building = Building.create(name="Test", floor_ids=("f1",))
    building.metadata["vastu"] = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
        pooja_direction=VastuDirection.NORTH_EAST,
        staircase_direction=VastuDirection.SOUTH,
        toilet_direction=VastuDirection.NORTH,
    )
    floor = Floor.create(name="F1", level=0, room_ids=frozenset())
    return BuildingModel(
        building=building,
        floors={"f1": floor},
        rooms={},
        walls={},
        columns={},
        stairs={},
        doors={},
        windows={},
        relationships=[],
    )


def _make_building(metadata_dict=None):
    building = Building.create(name="Test", floor_ids=())
    if metadata_dict:
        building.metadata["vastu"] = metadata_dict
    return BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])



# ============================================================================
# EntranceDirectionConstraint Tests
# ============================================================================


class TestEntranceDirectionConstraint:
    def test_preferred_north(self):
        meta = VastuMetadata(entrance_direction=VastuDirection.NORTH)
        model = _make_building(meta.to_dict())
        result = EntranceDirectionConstraint().evaluate(model)
        assert result.is_optimal

    def test_preferred_east(self):
        meta = VastuMetadata(entrance_direction=VastuDirection.EAST)
        model = _make_building(meta.to_dict())
        result = EntranceDirectionConstraint().evaluate(model)
        assert result.is_optimal

    def test_preferred_north_east(self):
        meta = VastuMetadata(entrance_direction=VastuDirection.NORTH_EAST)
        model = _make_building(meta.to_dict())
        result = EntranceDirectionConstraint().evaluate(model)
        assert result.is_optimal

    def test_invalid_south(self):
        meta = VastuMetadata(entrance_direction=VastuDirection.SOUTH)
        model = _make_building(meta.to_dict())
        result = EntranceDirectionConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_ENTRANCE_DIRECTION

    def test_invalid_south_west(self):
        meta = VastuMetadata(entrance_direction=VastuDirection.SOUTH_WEST)
        model = _make_building(meta.to_dict())
        result = EntranceDirectionConstraint().evaluate(model)
        assert not result.is_optimal

    def test_missing_metadata(self):
        model = _make_building()
        result = EntranceDirectionConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_ENTRANCE_DIRECTION

    def test_missing_entrance_direction(self):
        meta = VastuMetadata()
        model = _make_building(meta.to_dict())
        result = EntranceDirectionConstraint().evaluate(model)
        assert not result.is_optimal

    def test_deterministic(self):
        meta = VastuMetadata(entrance_direction=VastuDirection.SOUTH)
        model = _make_building(meta.to_dict())
        c = EntranceDirectionConstraint()
        r1 = c.evaluate(model)
        r2 = c.evaluate(model)
        assert r1 == r2

    def test_severity(self):
        meta = VastuMetadata(entrance_direction=VastuDirection.WEST)
        model = _make_building(meta.to_dict())
        result = EntranceDirectionConstraint().evaluate(model)
        assert result.issues[0].severity == ConstraintSeverity.RECOMMENDATION

    def test_no_mutation(self):
        building = Building.create(name="T", floor_ids=())
        building.metadata["vastu"] = VastuMetadata(entrance_direction=VastuDirection.NORTH)
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        original_id = id(building)
        EntranceDirectionConstraint().evaluate(model)
        assert id(model.building) == original_id



# ============================================================================
# KitchenPlacementConstraint Tests
# ============================================================================


class TestKitchenPlacementConstraint:
    def test_preferred_agneya_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "AGNEYA"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_acceptable_vayavya_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "VAYAVYA"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_KITCHEN_PLACEMENT

    def test_invalid_north_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "NORTH"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].score == 0.7

    def test_missing_metadata(self):
        model = _make_building()
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_metadata_direction_to_zone(self):
        meta = VastuMetadata(kitchen_direction=VastuDirection.SOUTH_EAST)
        model = _make_building(meta.to_dict())
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_kitchen_without_zone(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN)
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_KITCHEN_PLACEMENT

    def test_no_kitchen_rooms(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1"}))
        room = Room.create(vertices=[(0,0),(5,0),(5,5),(0,5)], room_type=RoomType.LIVING)
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"r1": room}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_deterministic(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "NORTH"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        c = KitchenPlacementConstraint()
        assert c.evaluate(model) == c.evaluate(model)



# ============================================================================
# MasterBedroomConstraint Tests
# ============================================================================


class TestMasterBedroomConstraint:
    def test_preferred_nairutya_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"b1"}))
        bedroom = Room.create(vertices=[(0,0),(7,0),(7,7),(0,7)], room_type=RoomType.BEDROOM, metadata={"vastu_zone": "NAIRUTYA"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"b1": bedroom}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = MasterBedroomConstraint().evaluate(model)
        assert result.is_optimal

    def test_invalid_north_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"b1"}))
        bedroom = Room.create(vertices=[(0,0),(7,0),(7,7),(0,7)], room_type=RoomType.BEDROOM, metadata={"vastu_zone": "NORTH"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"b1": bedroom}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = MasterBedroomConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_MASTER_BEDROOM

    def test_missing_metadata(self):
        model = _make_building()
        result = MasterBedroomConstraint().evaluate(model)
        assert result.is_optimal

    def test_metadata_direction(self):
        meta = VastuMetadata(master_bedroom_direction=VastuDirection.SOUTH_WEST)
        model = _make_building(meta.to_dict())
        result = MasterBedroomConstraint().evaluate(model)
        assert result.is_optimal

    def test_no_bedrooms(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1"}))
        room = Room.create(vertices=[(0,0),(5,0),(5,5),(0,5)], room_type=RoomType.LIVING)
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"r1": room}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = MasterBedroomConstraint().evaluate(model)
        assert result.is_optimal

    def test_deterministic(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"b1"}))
        bedroom = Room.create(vertices=[(0,0),(7,0),(7,7),(0,7)], room_type=RoomType.BEDROOM, metadata={"vastu_zone": "EAST"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"b1": bedroom}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        c = MasterBedroomConstraint()
        assert c.evaluate(model) == c.evaluate(model)


# ============================================================================
# PoojaRoomConstraint Tests
# ============================================================================


class TestPoojaRoomConstraint:
    def test_preferred_ishanya_metadata(self):
        meta = VastuMetadata(pooja_direction=VastuDirection.NORTH_EAST)
        model = _make_building(meta.to_dict())
        result = PoojaRoomConstraint().evaluate(model)
        assert result.is_optimal

    def test_invalid_metadata(self):
        meta = VastuMetadata(pooja_direction=VastuDirection.SOUTH)
        model = _make_building(meta.to_dict())
        result = PoojaRoomConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_POOJA_ROOM

    def test_missing_metadata(self):
        model = _make_building()
        result = PoojaRoomConstraint().evaluate(model)
        assert result.is_optimal

    def test_room_by_name(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1"}))
        room = Room.create(vertices=[(0,0),(5,0),(5,5),(0,5)], room_type=RoomType.UNKNOWN, metadata={"name": "Pooja Room", "vastu_zone": "ISHANYA"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"r1": room}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = PoojaRoomConstraint().evaluate(model)
        assert result.is_optimal

    def test_room_by_name_invalid(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1"}))
        room = Room.create(vertices=[(0,0),(5,0),(5,5),(0,5)], room_type=RoomType.UNKNOWN, metadata={"name": "Pooja Room", "vastu_zone": "SOUTH"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"r1": room}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = PoojaRoomConstraint().evaluate(model)
        assert not result.is_optimal

    def test_deterministic(self):
        meta = VastuMetadata(pooja_direction=VastuDirection.WEST)
        model = _make_building(meta.to_dict())
        c = PoojaRoomConstraint()
        assert c.evaluate(model) == c.evaluate(model)



# ============================================================================
# StaircaseConstraint Tests
# ============================================================================


class TestStaircaseConstraint:
    def test_preferred_south(self):
        meta = VastuMetadata(staircase_direction=VastuDirection.SOUTH)
        model = _make_building(meta.to_dict())
        result = StaircaseConstraint().evaluate(model)
        assert result.is_optimal

    def test_preferred_west(self):
        meta = VastuMetadata(staircase_direction=VastuDirection.WEST)
        model = _make_building(meta.to_dict())
        result = StaircaseConstraint().evaluate(model)
        assert result.is_optimal

    def test_preferred_south_west(self):
        meta = VastuMetadata(staircase_direction=VastuDirection.SOUTH_WEST)
        model = _make_building(meta.to_dict())
        result = StaircaseConstraint().evaluate(model)
        assert result.is_optimal

    def test_disallowed_center(self):
        meta = VastuMetadata(staircase_direction=VastuDirection.CENTER)
        model = _make_building(meta.to_dict())
        result = StaircaseConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_STAIRCASE

    def test_missing_metadata(self):
        model = _make_building()
        result = StaircaseConstraint().evaluate(model)
        assert result.is_optimal

    def test_deterministic(self):
        meta = VastuMetadata(staircase_direction=VastuDirection.NORTH)
        model = _make_building(meta.to_dict())
        c = StaircaseConstraint()
        assert c.evaluate(model) == c.evaluate(model)

    def test_severity(self):
        meta = VastuMetadata(staircase_direction=VastuDirection.CENTER)
        model = _make_building(meta.to_dict())
        result = StaircaseConstraint().evaluate(model)
        assert result.issues[0].severity == ConstraintSeverity.RECOMMENDATION


# ============================================================================
# ToiletPlacementConstraint Tests
# ============================================================================


class TestToiletPlacementConstraint:
    def test_disallowed_north_east_metadata(self):
        meta = VastuMetadata(toilet_direction=VastuDirection.NORTH_EAST)
        model = _make_building(meta.to_dict())
        result = ToiletPlacementConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_TOILET

    def test_disallowed_center_metadata(self):
        meta = VastuMetadata(toilet_direction=VastuDirection.CENTER)
        model = _make_building(meta.to_dict())
        result = ToiletPlacementConstraint().evaluate(model)
        assert not result.is_optimal

    def test_allowed_south_metadata(self):
        meta = VastuMetadata(toilet_direction=VastuDirection.SOUTH)
        model = _make_building(meta.to_dict())
        result = ToiletPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_missing_metadata(self):
        model = _make_building()
        result = ToiletPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_deterministic(self):
        meta = VastuMetadata(toilet_direction=VastuDirection.NORTH_EAST)
        model = _make_building(meta.to_dict())
        c = ToiletPlacementConstraint()
        assert c.evaluate(model) == c.evaluate(model)



# ============================================================================
# BrahmasthanConstraint Tests
# ============================================================================


class TestBrahmasthanConstraint:
    def test_column_in_brahmasthan(self):
        building = Building.create(name="T", floor_ids=())
        col = type("Col", (), {"id": "c1", "metadata": {"vastu_zone": "BRAHMASTHAN"}, "name": "C1"})()
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={"c1": col}, stairs={}, doors={}, windows={}, relationships=[])
        result = BrahmasthanConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_BRAHMASTHAN

    def test_stair_in_brahmasthan(self):
        building = Building.create(name="T", floor_ids=())
        stair = type("St", (), {"id": "s1", "metadata": {"vastu_zone": "BRAHMASTHAN"}, "name": "S1"})()
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={"s1": stair}, doors={}, windows={}, relationships=[])
        result = BrahmasthanConstraint().evaluate(model)
        assert not result.is_optimal

    def test_toilet_room_in_brahmasthan(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"t1"}))
        toilet = Room.create(vertices=[(0,0),(4,0),(4,4),(0,4)], room_type=RoomType.TOILET, metadata={"vastu_zone": "BRAHMASTHAN"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"t1": toilet}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = BrahmasthanConstraint().evaluate(model)
        assert not result.is_optimal

    def test_clear_center(self):
        building = Building.create(name="T", floor_ids=())
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = BrahmasthanConstraint().evaluate(model)
        assert result.is_optimal

    def test_deterministic(self):
        building = Building.create(name="T", floor_ids=())
        col = type("Col", (), {"id": "c1", "metadata": {"vastu_zone": "BRAHMASTHAN"}, "name": "C1"})()
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={"c1": col}, stairs={}, doors={}, windows={}, relationships=[])
        c = BrahmasthanConstraint()
        assert c.evaluate(model) == c.evaluate(model)



# ============================================================================
# Engine Integration Tests
# ============================================================================


class TestEngineIntegration:
    def test_all_vastu_constraints_registered(self):
        engine = ConstraintEngine()
        engine.register(EntranceDirectionConstraint())
        engine.register(KitchenPlacementConstraint())
        engine.register(MasterBedroomConstraint())
        engine.register(PoojaRoomConstraint())
        engine.register(StaircaseConstraint())
        engine.register(ToiletPlacementConstraint())
        engine.register(BrahmasthanConstraint())
        assert engine.constraint_count == 7

    def test_engine_evaluate_aggregates(self):
        engine = ConstraintEngine()
        engine.register(EntranceDirectionConstraint())
        engine.register(KitchenPlacementConstraint())
        building = Building.create(name="T", floor_ids=())
        building.metadata["vastu"] = VastuMetadata(
            entrance_direction=VastuDirection.SOUTH,
            kitchen_direction=VastuDirection.NORTH,
        )
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = engine.evaluate(model)
        assert not result.is_optimal
        assert result.issue_count >= 2

    def test_evaluation_pipeline_includes_vastu(self):
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
        pipeline = EvaluationPipeline()
        building = Building.create(name="T", floor_ids=())
        building.metadata["vastu"] = VastuMetadata(entrance_direction=VastuDirection.SOUTH)
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        report = pipeline.evaluate(model)
        codes = [issue.code for issue in report.constraint_issues]
        assert VASTU_ENTRANCE_DIRECTION in codes

    def test_repeated_evaluation_same_result(self):
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
        pipeline = EvaluationPipeline()
        building = Building.create(name="T", floor_ids=())
        building.metadata["vastu"] = VastuMetadata(entrance_direction=VastuDirection.WEST)
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        r1 = pipeline.evaluate(model)
        r2 = pipeline.evaluate(model)
        assert r1.constraint_issues == r2.constraint_issues

    def test_empty_model_no_crash(self):
        engine = ConstraintEngine()
        engine.register(EntranceDirectionConstraint())
        engine.register(KitchenPlacementConstraint())
        engine.register(MasterBedroomConstraint())
        engine.register(PoojaRoomConstraint())
        engine.register(StaircaseConstraint())
        engine.register(ToiletPlacementConstraint())
        engine.register(BrahmasthanConstraint())
        building = Building.create(name="T", floor_ids=())
        model = BuildingModel(building=building, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = engine.evaluate(model)
        assert isinstance(result, ConstraintResult)

    def test_multiple_kitchen_issues(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1", "k2"}))
        k1 = Room.create(vertices=[(0,0),(5,0),(5,5),(0,5)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "NORTH"})
        k2 = Room.create(vertices=[(5,0),(10,0),(10,5),(5,5)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "EAST"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": k1, "k2": k2}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.issue_count == 2

    def test_vastu_constraint_base_properties(self):
        c = EntranceDirectionConstraint()
        assert c.category.value == "vastu"
        assert c.default_severity == ConstraintSeverity.RECOMMENDATION



# ============================================================================
# KitchenPlacementConstraint Tests
# ============================================================================


class TestKitchenPlacementConstraint:
    def test_preferred_agneya_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "AGNEYA"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_acceptable_vayavya_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "VAYAVYA"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_KITCHEN_PLACEMENT

    def test_invalid_north_room(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "NORTH"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].score == 0.7

    def test_missing_metadata(self):
        model = _make_building()
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_metadata_direction_to_zone(self):
        meta = VastuMetadata(kitchen_direction=VastuDirection.SOUTH_EAST)
        model = _make_building(meta.to_dict())
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_kitchen_without_zone(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN)
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert not result.is_optimal
        assert result.issues[0].code == VASTU_KITCHEN_PLACEMENT

    def test_no_kitchen_rooms(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1"}))
        room = Room.create(vertices=[(0,0),(5,0),(5,5),(0,5)], room_type=RoomType.LIVING)
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"r1": room}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        result = KitchenPlacementConstraint().evaluate(model)
        assert result.is_optimal

    def test_deterministic(self):
        building = Building.create(name="T", floor_ids=("f1",))
        floor = Floor.create(name="F1", level=0, room_ids=frozenset({"k1"}))
        kitchen = Room.create(vertices=[(0,0),(6,0),(6,6),(0,6)], room_type=RoomType.KITCHEN, metadata={"vastu_zone": "NORTH"})
        model = BuildingModel(building=building, floors={"f1": floor}, rooms={"k1": kitchen}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        c = KitchenPlacementConstraint()
        assert c.evaluate(model) == c.evaluate(model)

