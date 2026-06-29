"""Unit tests for structural constraints."""
from __future__ import annotations
import pytest, math
from building_model_v2.constraints.constraint_result import ConstraintResult
from building_model_v2.constraints.constraint_engine import ConstraintEngine
from building_model_v2.constraints.structural_constraints import (
    ColumnAlignmentConstraint, ColumnAlignmentConfig,
    ColumnSpacingConstraint, ColumnSpacingConfig,
    LargeUnsupportedRoomConstraint, LargeUnsupportedRoomConfig,
    MaximumWallSpanConstraint, MaximumWallSpanConfig,
    StairSupportConstraint, StairSupportConfig,
    StructuralConstraint, StructuralSymmetryConstraint, StructuralSymmetryConfig,
    WallContinuityConstraint, WallContinuityConfig,
    STRUCTURAL_COLUMN_ALIGNMENT, STRUCTURAL_COLUMN_SPACING,
    STRUCTURAL_STAIR_SUPPORT, STRUCTURAL_SYMMETRY,
    STRUCTURAL_UNSUPPORTED_ROOM, STRUCTURAL_WALL_CONTINUITY, STRUCTURAL_WALL_SPAN,
)
from building_model_v2.constraints.constraint_severity import ConstraintSeverity
from building_model_v2.entities_building import Building
from building_model_v2.entities_column import Column
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.entities_wall import Wall
from building_model_v2.types import RoomType, WallType
from building_model_v2.validation.cross_entity_validator import BuildingModel


def _walls(length, bearing=True):
    b = Building.create(name="T", floor_ids=())
    w = Wall.create(start=(0,0), end=(length,0), wall_type=WallType.BEARING, is_load_bearing=bearing)
    return BuildingModel(building=b, floors={}, rooms={}, walls={"w1": w}, columns={}, stairs={}, doors={}, windows={}, relationships=[])


def _room(area, rt=RoomType.LIVING):
    b = Building.create(name="T", floor_ids=())
    s = math.sqrt(area)
    r = Room.create(vertices=[(0,0),(s,0),(s,s),(0,s)], room_type=rt)
    return BuildingModel(building=b, floors={}, rooms={"r1": r}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])


def _cols(count, spacing):
    b = Building.create(name="T", floor_ids=())
    cols = {f"c{i}": Column.create(location=(i*spacing, 0), floor_id="f1") for i in range(count)}
    return BuildingModel(building=b, floors={}, rooms={}, walls={}, columns=cols, stairs={}, doors={}, windows={}, relationships=[])



class TestMaximumWallSpan:
    def test_valid(self): assert MaximumWallSpanConstraint().evaluate(_walls(15)).is_optimal
    def test_invalid(self):
        r = MaximumWallSpanConstraint().evaluate(_walls(25))
        assert not r.is_optimal and r.issues[0].code == STRUCTURAL_WALL_SPAN
    def test_boundary(self): assert MaximumWallSpanConstraint().evaluate(_walls(20)).is_optimal
    def test_exceeded(self): assert not MaximumWallSpanConstraint().evaluate(_walls(20.1)).is_optimal
    def test_custom(self):
        assert not MaximumWallSpanConstraint(config=MaximumWallSpanConfig(max_span_ft=10)).evaluate(_walls(15)).is_optimal
    def test_multi(self):
        b = Building.create(name="T", floor_ids=())
        w1, w2 = Wall.create(start=(0,0), end=(15,0)), Wall.create(start=(0,0), end=(30,0))
        m = BuildingModel(building=b, floors={}, rooms={}, walls={"w1":w1,"w2":w2}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert MaximumWallSpanConstraint().evaluate(m).issue_count == 1
    def test_severity(self):
        assert MaximumWallSpanConstraint().evaluate(_walls(30)).issues[0].severity == ConstraintSeverity.WARNING
    def test_deterministic(self):
        c = MaximumWallSpanConstraint()
        assert c.evaluate(_walls(25)) == c.evaluate(_walls(25))
    def test_no_mutation(self):
        m = _walls(30); orig = dict(m.walls)
        MaximumWallSpanConstraint().evaluate(m)
        assert dict(m.walls) == orig


class TestColumnSpacing:
    def test_valid(self): assert ColumnSpacingConstraint().evaluate(_cols(3, 9)).is_optimal
    def test_invalid(self):
        r = ColumnSpacingConstraint().evaluate(_cols(3, 20))
        assert not r.is_optimal and r.issues[0].code == STRUCTURAL_COLUMN_SPACING
    def test_boundary(self): assert ColumnSpacingConstraint().evaluate(_cols(2, 18)).is_optimal
    def test_insufficient(self): assert ColumnSpacingConstraint().evaluate(_cols(1, 50)).is_optimal
    def test_severity(self):
        assert ColumnSpacingConstraint().evaluate(_cols(3, 25)).issues[0].severity == ConstraintSeverity.WARNING
    def test_custom(self):
        assert not ColumnSpacingConstraint(config=ColumnSpacingConfig(max_spacing_ft=10)).evaluate(_cols(3, 15)).is_optimal
    def test_deterministic(self):
        c = ColumnSpacingConstraint()
        r1 = c.evaluate(_cols(3, 25))
        r2 = c.evaluate(_cols(3, 25))
        assert r1.issue_count == r2.issue_count and r1.is_optimal == r2.is_optimal


class TestLargeUnsupportedRoom:
    def test_valid(self): assert LargeUnsupportedRoomConstraint().evaluate(_room(300)).is_optimal
    def test_invalid(self):
        r = LargeUnsupportedRoomConstraint().evaluate(_room(500))
        assert not r.is_optimal and r.issues[0].code == STRUCTURAL_UNSUPPORTED_ROOM
    def test_boundary(self): assert LargeUnsupportedRoomConstraint().evaluate(_room(400)).is_optimal
    def test_exceeded(self): assert not LargeUnsupportedRoomConstraint().evaluate(_room(401)).is_optimal
    def test_custom(self):
        assert not LargeUnsupportedRoomConstraint(config=LargeUnsupportedRoomConfig(max_area_sqft=200)).evaluate(_room(300)).is_optimal
    def test_severity(self):
        assert LargeUnsupportedRoomConstraint().evaluate(_room(600)).issues[0].severity == ConstraintSeverity.WARNING
    def test_deterministic(self):
        c = LargeUnsupportedRoomConstraint()
        assert c.evaluate(_room(500)) == c.evaluate(_room(500))



class TestWallContinuity:
    def test_valid(self):
        b = Building.create(name="T", floor_ids=("f1",))
        f = Floor.create(name="F", level=0, room_ids=frozenset())
        w = Wall.create(start=(0,0), end=(10,0), floor_id="f1", metadata={"is_load_bearing": True, "has_support": True})
        m = BuildingModel(building=b, floors={"f1": f}, rooms={}, walls={"w1": w}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert WallContinuityConstraint().evaluate(m).is_optimal
    def test_missing_floor(self):
        b = Building.create(name="T", floor_ids=())
        w = Wall.create(start=(0,0), end=(10,0), is_load_bearing=True)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={"w1": w}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        r = WallContinuityConstraint().evaluate(m)
        assert not r.is_optimal and r.issues[0].code == STRUCTURAL_WALL_CONTINUITY
    def test_no_load_bearing(self):
        assert WallContinuityConstraint().evaluate(_walls(10, bearing=False)).is_optimal
    def test_severity(self):
        b = Building.create(name="T", floor_ids=())
        w = Wall.create(start=(0,0), end=(10,0), is_load_bearing=True)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={"w1": w}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert WallContinuityConstraint().evaluate(m).issues[0].severity == ConstraintSeverity.WARNING
    def test_deterministic(self):
        c = WallContinuityConstraint()
        assert c.evaluate(_walls(10, bearing=False)) == c.evaluate(_walls(10, bearing=False))


class TestColumnAlignment:
    def test_single_floor(self):
        assert ColumnAlignmentConstraint().evaluate(_cols(3, 10)).is_optimal
    def test_empty(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert ColumnAlignmentConstraint().evaluate(m).is_optimal
    def test_severity(self):
        assert ColumnAlignmentConstraint().default_severity == ConstraintSeverity.WARNING


class TestStairSupport:
    def test_valid(self):
        b = Building.create(name="T", floor_ids=())
        s = Stair.create(start=(0,0), end=(10,0), width=3.0, floor_id="f1", metadata={"has_landing": True})
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={"s1": s}, doors={}, windows={}, relationships=[])
        assert StairSupportConstraint().evaluate(m).is_optimal
    def test_missing_floor(self):
        b = Building.create(name="T", floor_ids=())
        s = Stair.create(start=(0,0), end=(10,0), width=3.0)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={"s1": s}, doors={}, windows={}, relationships=[])
        r = StairSupportConstraint().evaluate(m)
        assert not r.is_optimal and r.issues[0].code == STRUCTURAL_STAIR_SUPPORT
    def test_severity(self):
        b = Building.create(name="T", floor_ids=())
        s = Stair.create(start=(0,0), end=(10,0), width=3.0)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={"s1": s}, doors={}, windows={}, relationships=[])
        assert StairSupportConstraint().evaluate(m).issues[0].severity == ConstraintSeverity.WARNING
    def test_deterministic(self):
        c = StairSupportConstraint()
        b = Building.create(name="T", floor_ids=())
        s = Stair.create(start=(0,0), end=(10,0), width=3.0)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={"s1": s}, doors={}, windows={}, relationships=[])
        assert c.evaluate(m) == c.evaluate(m)



class TestStructuralSymmetry:
    def test_symmetric(self):
        b = Building.create(name="T", floor_ids=())
        w1 = Wall.create(start=(-5,0), end=(5,0))
        m = BuildingModel(building=b, floors={}, rooms={}, walls={"w1": w1}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert StructuralSymmetryConstraint().evaluate(m).is_optimal
    def test_empty(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert StructuralSymmetryConstraint().evaluate(m).is_optimal
    def test_severity(self):
        assert StructuralSymmetryConstraint().default_severity == ConstraintSeverity.WARNING
    def test_deterministic(self):
        c = StructuralSymmetryConstraint()
        assert c.evaluate(_walls(10)) == c.evaluate(_walls(10))


class TestBaseClass:
    def test_category(self):
        assert MaximumWallSpanConstraint().category.value == "structural"
    def test_severity(self):
        assert MaximumWallSpanConstraint().default_severity == ConstraintSeverity.WARNING


class TestEngineIntegration:
    def test_engine_registration(self):
        engine = ConstraintEngine()
        engine.register(MaximumWallSpanConstraint())
        engine.register(ColumnSpacingConstraint())
        engine.register(LargeUnsupportedRoomConstraint())
        engine.register(WallContinuityConstraint())
        engine.register(StairSupportConstraint())
        engine.register(StructuralSymmetryConstraint())
        assert engine.constraint_count == 6
    def test_engine_evaluate(self):
        engine = ConstraintEngine()
        engine.register(MaximumWallSpanConstraint())
        r = engine.evaluate(_walls(25))
        assert not r.is_optimal and r.issue_count == 1
    def test_pipeline_integration(self):
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
        pipeline = EvaluationPipeline()
        report = pipeline.evaluate(_walls(25))
        codes = [i.code for i in report.constraint_issues]
        assert STRUCTURAL_WALL_SPAN in codes
    def test_repeated_deterministic(self):
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
        pipeline = EvaluationPipeline()
        r1 = pipeline.evaluate(_walls(25))
        r2 = pipeline.evaluate(_walls(25))
        assert len(r1.constraint_issues) == len(r2.constraint_issues)
        codes1 = sorted(i.code for i in r1.constraint_issues)
        codes2 = sorted(i.code for i in r2.constraint_issues)
        assert codes1 == codes2
    def test_empty_model(self):
        engine = ConstraintEngine()
        engine.register(MaximumWallSpanConstraint())
        engine.register(ColumnSpacingConstraint())
        engine.register(LargeUnsupportedRoomConstraint())
        engine.register(WallContinuityConstraint())
        engine.register(StairSupportConstraint())
        engine.register(StructuralSymmetryConstraint())
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        r = engine.evaluate(m)
        assert isinstance(r, ConstraintResult)
    def test_serialization(self):
        r = MaximumWallSpanConstraint().evaluate(_walls(25))
        d = r.to_dict()
        assert d["issue_count"] == 1 and len(d["issues"]) == 1
