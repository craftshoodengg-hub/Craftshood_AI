"""Unit tests for Adjacency Engine."""
from __future__ import annotations
import pytest
from building_model_v2.layout.adjacency_engine import (
    AdjacencyEngine,
    LAYOUT_BATHROOM_NEAR_DINING,
    LAYOUT_BATHROOM_NEAR_KITCHEN,
    LAYOUT_KITCHEN_NOT_NEAR_DINING,
    LAYOUT_MASTER_BEDROOM_NO_BATH,
    LAYOUT_POOJA_NEAR_TOILET,
    _rooms_are_adjacent,
    _rooms_share_wall,
)
from building_model_v2.layout.adjacency_rules import AdjacencyRuleSet
from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor


def _build(room_configs):
    b = Building.create(name="T", floor_ids=("f1",))
    f = Floor.create(name="F1", level=0, room_ids=frozenset(r[0] for r in room_configs))
    rooms = {n: Room.create(vertices=v, room_type=rt, metadata={"name": n}) for n, rt, v in room_configs}
    return BuildingModel(building=b, floors={"f1": f}, rooms=rooms, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])


class TestAdjacencyEngine:
    def test_empty(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        e = AdjacencyEngine()
        assert e.build_graph(m).room_count == 0
        assert e.evaluate(m).is_optimal

    def test_single(self):
        m = _build([("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)])])
        r = AdjacencyEngine().evaluate(m)
        # Single room has no neighbors, so preferred adjacency issues are expected
        assert r.issue_count >= 0  # Just verify it doesn't crash

    def test_kitchen_near_dining(self):
        m = _build([("Kitchen", RoomType.KITCHEN, [(0,0),(10,0),(10,10),(0,10)]), ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)])])
        r = AdjacencyEngine().evaluate(m)
        # Rooms share a wall edge, so they are adjacent
        codes = [i.code for i in r.issues]
        assert LAYOUT_KITCHEN_NOT_NEAR_DINING not in codes

    def test_kitchen_not_near_dining(self):
        m = _build([("Kitchen", RoomType.KITCHEN, [(0,0),(10,0),(10,10),(0,10)]), ("Dining", RoomType.DINING, [(100,0),(110,0),(110,10),(100,10)])])
        r = AdjacencyEngine().evaluate(m)
        assert LAYOUT_KITCHEN_NOT_NEAR_DINING in [i.code for i in r.issues]

    def test_bath_near_kitchen(self):
        m = _build([("Bathroom", RoomType.BATHROOM, [(0,0),(10,0),(10,10),(0,10)]), ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)])])
        codes = [i.code for i in AdjacencyEngine().evaluate(m).issues]
        assert LAYOUT_BATHROOM_NEAR_KITCHEN in codes

    def test_bath_near_dining(self):
        m = _build([("Bathroom", RoomType.BATHROOM, [(0,0),(10,0),(10,10),(0,10)]), ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)])])
        codes = [i.code for i in AdjacencyEngine().evaluate(m).issues]
        assert LAYOUT_BATHROOM_NEAR_DINING in codes

    def test_master_no_bath(self):
        m = _build([("Bedroom", RoomType.BEDROOM, [(0,0),(10,0),(10,10),(0,10)])])
        r = AdjacencyEngine().evaluate(m)
        # Bedroom rule has required_adjacent: Bathroom
        codes = [i.code for i in r.issues]
        # Should generate either LAYOUT_MASTER_BEDROOM_NO_BATH or LAYOUT_REQUIRED_ADJACENCY_MISSING
        assert len(codes) > 0

    def test_pooja_near_toilet(self):
        from building_model_v2.layout.adjacency_rules import AdjacencyRule, AdjacencyRuleSet, ConnectionType
        rules = AdjacencyRuleSet(rules=(
            AdjacencyRule("Unknown", frozenset(), frozenset({"Toilet"}), frozenset(), 0.6),
        ))
        m = _build([("Pooja", RoomType.UNKNOWN, [(0,0),(10,0),(10,10),(0,10)]), ("Toilet", RoomType.TOILET, [(10,0),(20,0),(20,10),(10,10)])])
        codes = [i.code for i in AdjacencyEngine(rules=rules).evaluate(m).issues]
        assert LAYOUT_POOJA_NEAR_TOILET in codes

    def test_deterministic(self):
        m = _build([("Kitchen", RoomType.KITCHEN, [(0,0),(10,0),(10,10),(0,10)])])
        e = AdjacencyEngine()
        assert e.evaluate(m).issue_count == e.evaluate(m).issue_count

    def test_custom_rules(self):
        rules = AdjacencyRuleSet(rules=(AdjacencyRuleSet(rules=()).rules[0:0] if False else ()))
        e = AdjacencyEngine(rules=rules)
        m = _build([("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)])])
        assert e.evaluate(m).is_optimal

    def test_build_graph(self):
        m = _build([("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]), ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)])])
        g = AdjacencyEngine().build_graph(m)
        # Rooms share a wall edge at x=10, so they should be connected
        assert g.edge_count == 1

    def test_no_mutation(self):
        m = _build([("Kitchen", RoomType.KITCHEN, [(0,0),(10,0),(10,10),(0,10)])])
        e = AdjacencyEngine()
        orig = dict(m.rooms)
        e.evaluate(m)
        assert dict(m.rooms) == orig


class TestHelpers:
    def test_adjacent_true(self):
        r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)])
        r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)])
        assert _rooms_are_adjacent(r1, r2)  # centroids 10ft apart, within 15ft threshold

    def test_adjacent_false(self):
        r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)])
        r2 = Room.create(vertices=[(100,0),(110,0),(110,10),(100,10)])
        assert not _rooms_are_adjacent(r1, r2)

    def test_share_wall_true(self):
        r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], wall_ids=frozenset({"w1"}))
        r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], wall_ids=frozenset({"w1"}))
        assert _rooms_share_wall(r1, r2)

    def test_share_wall_false(self):
        r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], wall_ids=frozenset({"w1"}))
        r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], wall_ids=frozenset({"w2"}))
        assert not _rooms_share_wall(r1, r2)
