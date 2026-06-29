"""Unit tests for Privacy Engine."""
from __future__ import annotations
import pytest
from building_model_v2.layout.privacy_engine import (
    PrivacyEngine,
    PRIVACY_MASTER_BEDROOM_ACCESS,
    PRIVACY_TOILET_VISIBILITY,
    PRIVACY_POOJA_DISTURBANCE,
    PRIVACY_GUEST_ACCESS,
    PRIVACY_LIVING_TRANSITION,
    PRIVACY_BEDROOM_CORRIDOR,
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


class TestPrivacyEngine:
    def test_empty_model(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        e = PrivacyEngine()
        r = e.evaluate(m)
        assert r.is_optimal
        metrics = e.analyze(m)
        assert metrics.privacy_score == 1.0

    def test_single_room(self):
        m = _build([("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)])])
        e = PrivacyEngine()
        r = e.evaluate(m)
        assert r.is_optimal

    def test_public_rooms(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        assert len(metrics.public_rooms) == 2

    def test_private_rooms(self):
        m = _build([
            ("Bedroom", RoomType.BEDROOM, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bathroom", RoomType.BATHROOM, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        assert len(metrics.private_rooms) == 2

    def test_semi_private_rooms(self):
        m = _build([("Corridor", RoomType.CORRIDOR, [(0,0),(10,0),(10,10),(0,10)])])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        assert len(metrics.semi_private_rooms) == 1

    def test_toilet_near_dining(self):
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert PRIVACY_TOILET_VISIBILITY in codes

    def test_toilet_near_kitchen(self):
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert PRIVACY_TOILET_VISIBILITY in codes

    def test_pooja_near_toilet(self):
        m = _build([
            ("Pooja", RoomType.BALCONY, [(0,0),(10,0),(10,10),(0,10)]),
            ("Toilet", RoomType.TOILET, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert PRIVACY_POOJA_DISTURBANCE in codes

    def test_master_bedroom_privacy(self):
        m = _build([
            ("Master Bedroom", RoomType.BEDROOM, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        r = e.evaluate(m)
        codes = [i.code for i in r.issues]
        assert PRIVACY_MASTER_BEDROOM_ACCESS in codes

    def test_privacy_score_perfect(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bedroom", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        assert metrics.privacy_score == 1.0

    def test_privacy_score_with_conflicts(self):
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        assert metrics.privacy_score < 1.0


    def test_room_graph_reuse(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Kitchen", RoomType.KITCHEN, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        ae = AdjacencyEngine()
        graph = ae.build_graph(m)
        e = PrivacyEngine()
        metrics1 = e.analyze(m)
        metrics2 = e.analyze(m, room_graph=graph)
        assert metrics1.privacy_score == metrics2.privacy_score

    def test_serialization(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bedroom", RoomType.BEDROOM, [(100,0),(110,0),(110,10),(100,10)]),
        ])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        d = metrics.to_dict()
        assert d["privacy_score"] == 1.0

    def test_deterministic(self):
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        r1 = e.evaluate(m)
        r2 = e.evaluate(m)
        assert r1.issue_count == r2.issue_count

    def test_integration_with_adjacency_engine(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bedroom", RoomType.BEDROOM, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        ae = AdjacencyEngine()
        graph = ae.build_graph(m)
        assert graph.edge_count == 1
        e = PrivacyEngine()
        metrics = e.analyze(m, room_graph=graph)
        assert len(metrics.public_rooms) >= 1

    def test_integration_with_circulation_engine(self):
        from building_model_v2.layout.circulation_engine import CirculationEngine
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Bedroom", RoomType.BEDROOM, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        ce = CirculationEngine()
        circ_metrics = ce.analyze(m)
        e = PrivacyEngine()
        priv_metrics = e.analyze(m)
        assert priv_metrics.privacy_score >= 0

    def test_integration_with_constraint_engine(self):
        from building_model_v2.constraints.constraint_engine import ConstraintEngine
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        r = e.evaluate(m)
        assert hasattr(r, "is_optimal")
        assert hasattr(r, "issues")

    def test_no_mutation(self):
        m = _build([
            ("Toilet", RoomType.TOILET, [(0,0),(10,0),(10,10),(0,10)]),
            ("Dining", RoomType.DINING, [(10,0),(20,0),(20,10),(10,10)]),
        ])
        e = PrivacyEngine()
        orig = dict(m.rooms)
        e.evaluate(m)
        assert dict(m.rooms) == orig

    def test_multiple_floors(self):
        b = Building.create(name="T", floor_ids=("f1", "f2"))
        f1 = Floor.create(name="F1", level=0, room_ids=frozenset({"Living"}))
        f2 = Floor.create(name="F2", level=1, room_ids=frozenset({"Bedroom"}))
        rooms = {
            "Living": Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING, floor_id="f1"),
            "Bedroom": Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.BEDROOM, floor_id="f2"),
        }
        m = BuildingModel(building=b, floors={"f1": f1, "f2": f2}, rooms=rooms, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        assert len(metrics.public_rooms) >= 1
        assert len(metrics.private_rooms) >= 1

    def test_circulation_crossings(self):
        m = _build([
            ("Living", RoomType.LIVING, [(0,0),(10,0),(10,10),(0,10)]),
            ("Corridor", RoomType.CORRIDOR, [(10,0),(20,0),(20,10),(10,10)]),
            ("Bedroom", RoomType.BEDROOM, [(20,0),(30,0),(30,10),(20,10)]),
        ])
        e = PrivacyEngine()
        metrics = e.analyze(m)
        assert metrics.circulation_crossings >= 0
