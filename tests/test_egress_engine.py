"""Unit tests for Egress Engine."""
from __future__ import annotations
import pytest
from building_model_v2.layout.egress_engine import (
    EgressEngine,
    _is_exit_room,
    EGRESS_UNREACHABLE_EXIT,
    EGRESS_EXCESSIVE_TRAVEL_DISTANCE,
    EGRESS_DEAD_END_CORRIDOR,
    EGRESS_SINGLE_ESCAPE_ROUTE,
    EGRESS_STAIR_NOT_REACHABLE,
    EGRESS_NO_EXIT,
)
from building_model_v2.layout.adjacency_engine import AdjacencyEngine
from building_model_v2.layout.room_graph import RoomGraph
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel


def _build(room_configs):
    b = Building.create(name="T", floor_ids=("f1",))
    f = Floor.create(name="F1", level=0, room_ids=frozenset(r[0] for r in room_configs))
    rooms = {}
    for n, rt, verts in room_configs:
        rooms[n] = Room.create(vertices=verts, room_type=rt, metadata={"name": n})
    return BuildingModel(building=b, floors={"f1": f}, rooms=rooms, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])


class TestIsExitRoom:
    def test_exit_by_metadata(self):
        r = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], metadata={"is_exit": True})
        assert _is_exit_room(r)

    def test_exit_by_name(self):
        r = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], metadata={"name": "Main Entrance"})
        assert _is_exit_room(r)

    def test_exit_by_type(self):
        r = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.CORRIDOR, metadata={"name": "Entry"})
        assert _is_exit_room(r)

    def test_not_exit(self):
        r = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], metadata={"name": "Bedroom"})
        assert not _is_exit_room(r)


class TestEgressEngine:
    def test_empty_model(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        e = EgressEngine()
        r = e.evaluate(m)
        assert r.is_optimal

    def test_single_room_no_exit(self):
        m = _build([("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)])])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_NO_EXIT in codes

    def test_single_room_with_exit(self):
        m = _build([("Entrance", RoomType.CORRIDOR, [(0,0),(10,0),(10,10),(0,10)])])
        e = EgressEngine()
        r = e.evaluate(m)
        assert r.is_optimal

    def test_unreachable_exit(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Exit", RoomType.CORRIDOR, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_UNREACHABLE_EXIT in codes

    def test_reachable_exit(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("RoomB", RoomType.BEDROOM, [(10,0),(20,0),(20,10),(10,10)]),
            ("RoomC", RoomType.BATHROOM, [(20,0),(30,0),(30,10),(20,10)]),
            ("Exit", RoomType.CORRIDOR, [(30,0),(40,0),(40,10),(30,10)]),
        ])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_UNREACHABLE_EXIT not in codes

    def test_excessive_travel(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
            ("C", RoomType.BEDROOM, [(20,0),(30,0),(30,10),(20,10)]),
            ("D", RoomType.BATHROOM, [(30,0),(40,0),(40,10),(30,10)]),
            ("E", RoomType.KITCHEN, [(40,0),(50,0),(50,10),(40,10)]),
            ("F", RoomType.STORAGE, [(50,0),(60,0),(60,10),(50,10)]),
            ("Exit", RoomType.CORRIDOR, [(60,0),(70,0),(70,10),(60,10)]),
        ])
        e = EgressEngine(max_exit_distance=3)
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_EXCESSIVE_TRAVEL_DISTANCE in codes

    def test_dead_end_corridor(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
            ("Exit", RoomType.CORRIDOR, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_DEAD_END_CORRIDOR in codes

    def test_no_exit_issue(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_NO_EXIT in codes

    def test_egress_score_perfect(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = EgressEngine()
        metrics = e.analyze(m)
        assert metrics.egress_score == 1.0

    def test_egress_score_with_unreachable(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("RoomB", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = EgressEngine()
        metrics = e.analyze(m)
        assert metrics.egress_score < 1.0


    def test_multiple_exits(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Exit1", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
            ("Exit2", RoomType.CORRIDOR, [(0,10),(10,10),(10,20),(0,20)]),
        ])
        e = EgressEngine()
        r = e.evaluate(m)
        assert r.is_optimal

    def test_single_escape_route(self):
        m = _build([
            ("A", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("B", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_SINGLE_ESCAPE_ROUTE in codes

    def test_stair_not_reachable(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Stair", RoomType.STAIRCASE, [(100,0),(110,0),(110,10),(100,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_STAIR_NOT_REACHABLE in codes

    def test_room_graph_reuse(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        ae = AdjacencyEngine()
        graph = ae.build_graph(m)
        e = EgressEngine()
        metrics1 = e.analyze(m)
        metrics2 = e.analyze(m, room_graph=graph)
        assert metrics1.egress_score == metrics2.egress_score

    def test_serialization(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = EgressEngine()
        metrics = e.analyze(m)
        d = metrics.to_dict()
        assert d["egress_score"] == 1.0

    def test_deterministic(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = EgressEngine()
        r1 = e.evaluate(m)
        r2 = e.evaluate(m)
        assert r1.issue_count == r2.issue_count

    def test_integration_with_adjacency_engine(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("RoomB", RoomType.BEDROOM, [(10,0),(20,0),(20,10),(10,10)]),
            ("Exit", RoomType.CORRIDOR, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        ae = AdjacencyEngine()
        graph = ae.build_graph(m)
        assert graph.edge_count >= 1
        e = EgressEngine()
        metrics = e.analyze(m, room_graph=graph)
        assert len(metrics.reachable_rooms) >= 1

    def test_integration_with_circulation_engine(self):
        from building_model_v2.layout.circulation_engine import CirculationEngine
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("RoomB", RoomType.BEDROOM, [(10,0),(20,0),(20,10),(10,10)]),
            ("Exit", RoomType.CORRIDOR, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        ce = CirculationEngine()
        circ_metrics = ce.analyze(m)
        e = EgressEngine()
        egress_metrics = e.analyze(m)
        assert egress_metrics.egress_score >= 0

    def test_no_mutation(self):
        m = _build([
            ("RoomA", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Exit", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = EgressEngine()
        orig = dict(m.rooms)
        e.evaluate(m)
        assert dict(m.rooms) == orig

    def test_exit_by_is_exit_metadata(self):
        b = Building.create(name="T", floor_ids=("f1",))
        f = Floor.create(name="F1", level=0, room_ids=frozenset({"RoomA", "RoomB", "MainDoor"}))
        rooms = {
            "RoomA": Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING),
            "RoomB": Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], room_type=RoomType.BEDROOM),
            "MainDoor": Room.create(vertices=[(20,0),(30,0),(30,10),(20,10)], room_type=RoomType.CORRIDOR, metadata={"is_exit": True, "name": "Main Door"}),
        }
        m = BuildingModel(building=b, floors={"f1": f}, rooms=rooms, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        e = EgressEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert EGRESS_NO_EXIT not in codes
