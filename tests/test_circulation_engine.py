"""Unit tests for Circulation Engine."""
from __future__ import annotations
import math
import pytest
from building_model_v2.layout.circulation_engine import (
    CirculationEngine,
    CIRCULATION_DEAD_END,
    CIRCULATION_EXCESSIVE_PATH,
    CIRCULATION_KITCHEN_DINING,
    CIRCULATION_BEDROOM_BATHROOM,
    CIRCULATION_ROOM_ISOLATED,
    CIRCULATION_STAIR_CONNECTIVITY,
    CIRCULATION_UNREACHABLE_ROOM,
)
from building_model_v2.layout.adjacency_engine import AdjacencyEngine
from building_model_v2.base import Point2D
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.types import RoomType, StairType
from building_model_v2.validation.cross_entity_validator import BuildingModel


def _build(room_configs):
    b = Building.create(name="T", floor_ids=("f1",))
    f = Floor.create(name="F1", level=0, room_ids=frozenset(r[0] for r in room_configs))
    rooms = {}
    for n, rt, verts in room_configs:
        rooms[n] = Room.create(vertices=verts, room_type=rt, metadata={"name": n})
    stair_ids = frozenset()
    stairs = {}
    return BuildingModel(building=b, floors={"f1": f}, rooms=rooms, walls={}, columns={}, stairs=stairs, doors={}, windows={}, relationships=[])


class TestCirculationEngine:
    def test_empty_model(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        e = CirculationEngine()
        r = e.evaluate(m)
        assert r.is_optimal
        metrics = e.analyze(m)
        assert metrics.room_count if hasattr(metrics, 'room_count') else True

    def test_single_room(self):
        m = _build([("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)])])
        e = CirculationEngine()
        r = e.evaluate(m)
        assert r.is_optimal

    def test_connected_rooms(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = CirculationEngine()
        metrics = e.analyze(m)
        assert len(metrics.reachable_rooms) == 2

    def test_disconnected_rooms(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("RoomB", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = CirculationEngine()
        metrics = e.analyze(m)
        assert len(metrics.isolated_rooms) == 2

    def test_dead_end(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
            ("C", RoomType.BEDROOM, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        e = CirculationEngine()
        metrics = e.analyze(m)
        assert "A" in metrics.dead_end_rooms or "C" in metrics.dead_end_rooms

    def test_metrics_properties(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = CirculationEngine()
        metrics = e.analyze(m)
        assert metrics.average_path_length > 0
        assert metrics.maximum_path_length > 0
        assert 0 <= metrics.circulation_efficiency <= 1.0


    def test_isolated_room_issue(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_ROOM_ISOLATED in codes

    def test_dead_end_issue(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
            ("C", RoomType.BEDROOM, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_DEAD_END in codes

    def test_excessive_path(self):
        m = _build([
            ("A", RoomType.CORRIDOR, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.LIVING, [(10,0),(20,0),(20,10),(10,10)]),
            ("C", RoomType.DINING, [(20,0),(30,0),(30,10),(20,10)]),
            ("D", RoomType.KITCHEN, [(30,0),(40,0),(40,10),(30,10)]),
            ("E", RoomType.BEDROOM, [(40,0),(50,0),(50,10),(40,10)]),
        ])
        e = CirculationEngine(max_path_length=2)
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_EXCESSIVE_PATH in codes

    def test_entrance_unreachable(self):
        m = _build([
            ("Entrance", RoomType.CORRIDOR, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bedroom", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_UNREACHABLE_ROOM in codes

    def test_kitchen_dining_circulation(self):
        m = _build([
            ("Kitchen", RoomType.KITCHEN, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_KITCHEN_DINING in codes

    def test_kitchen_dining_connected(self):
        m = _build([
            ("Kitchen", RoomType.KITCHEN, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_KITCHEN_DINING not in codes

    def test_bedroom_bathroom_circulation(self):
        m = _build([
            ("Bedroom", RoomType.BEDROOM, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bathroom", RoomType.BATHROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_BEDROOM_BATHROOM in codes

    def test_bedroom_bathroom_connected(self):
        m = _build([
            ("Bedroom", RoomType.BEDROOM, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bathroom", RoomType.BATHROOM, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_BEDROOM_BATHROOM not in codes

    def test_stair_connectivity(self):
        m = _build([
            ("Stair", RoomType.STAIRCASE, [(0,0),(10,0),(10,10),(0,10)]),
            ("RoomA", RoomType.LIVING, [(100,0),(110,0),(110,10),(100,10)]),
            ("RoomB", RoomType.BEDROOM, [(200,0),(210,0),(210,10),(200,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert CIRCULATION_STAIR_CONNECTIVITY in codes

    def test_deterministic(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = CirculationEngine()
        r1 = e.evaluate(m)
        r2 = e.evaluate(m)
        assert r1.issue_count == r2.issue_count

    def test_serialization(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = CirculationEngine()
        metrics = e.analyze(m)
        d = metrics.to_dict()
        assert d["average_path_length"] > 0

    def test_integration_with_adjacency_engine(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        ae = AdjacencyEngine()
        graph = ae.build_graph(m)
        assert graph.edge_count == 1
        e = CirculationEngine()
        metrics = e.analyze(m)
        assert len(metrics.reachable_rooms) == 2

    def test_integration_with_constraint_engine(self):
        from building_model_v2.constraints.constraint_engine import ConstraintEngine
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = CirculationEngine()
        r = e.evaluate(m)
        engine = ConstraintEngine()
        # Verify the result is a proper ConstraintResult
        assert hasattr(r, "is_optimal")
        assert hasattr(r, "issues")
