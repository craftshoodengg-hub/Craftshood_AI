"""Unit tests for Circulation Metrics."""
from __future__ import annotations
import pytest
from building_model_v2.layout.circulation_metrics import CirculationPath, CirculationMetrics


class TestCirculationPath:
    def test_create(self):
        p = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        assert p.source_room_id == "a" and p.target_room_id == "b"

    def test_room_count(self):
        p = CirculationPath("a", "b", ("a", "c", "b"), 2, 20.0)
        assert p.room_count == 3

    def test_is_direct(self):
        p1 = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        assert p1.is_direct
        p2 = CirculationPath("a", "b", ("a", "c", "b"), 2, 20.0)
        assert not p2.is_direct

    def test_to_dict(self):
        p = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        d = p.to_dict()
        assert d["source_room_id"] == "a" and d["door_count"] == 1

    def test_from_dict(self):
        p = CirculationPath.from_dict({"source_room_id": "a", "target_room_id": "b", "room_sequence": ["a", "b"], "door_count": 1, "path_length": 10.0})
        assert p.source_room_id == "a" and p.room_sequence == ("a", "b")

    def test_equality(self):
        p1 = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        p2 = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        assert p1 == p2

    def test_hash(self):
        p1 = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        p2 = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        assert hash(p1) == hash(p2)

    def test_deterministic(self):
        p1 = CirculationPath("a", "b", ("a", "b"), 1, 10.0)
        p2 = CirculationPath.from_dict(p1.to_dict())
        assert p1 == p2


class TestCirculationMetrics:
    def test_create(self):
        m = CirculationMetrics(5.0, 10.0, frozenset({"a"}), frozenset({"b"}), 0.8, frozenset({"a", "b"}), frozenset())
        assert m.average_path_length == 5.0 and m.maximum_path_length == 10.0

    def test_isolated_rooms(self):
        m = CirculationMetrics(0.0, 0.0, frozenset({"a"}), frozenset(), 1.0, frozenset(), frozenset({"a"}))
        assert "a" in m.isolated_rooms

    def test_dead_end_rooms(self):
        m = CirculationMetrics(0.0, 0.0, frozenset(), frozenset({"a"}), 1.0, frozenset(), frozenset())
        assert "a" in m.dead_end_rooms

    def test_serialization(self):
        m = CirculationMetrics(5.0, 10.0, frozenset({"a"}), frozenset({"b"}), 0.8, frozenset({"a", "b"}), frozenset())
        d = m.to_dict()
        assert d["average_path_length"] == 5.0
        m2 = CirculationMetrics.from_dict(d)
        assert m.average_path_length == m2.average_path_length

    def test_empty_metrics(self):
        m = CirculationMetrics(0.0, 0.0, frozenset(), frozenset(), 1.0, frozenset(), frozenset())
        assert m.circulation_efficiency == 1.0

    def test_efficiency_high(self):
        m = CirculationMetrics(1.0, 1.0, frozenset(), frozenset(), 0.95, frozenset({"a", "b"}), frozenset())
        assert m.circulation_efficiency == 0.95

    def test_equality(self):
        m1 = CirculationMetrics(5.0, 10.0, frozenset(), frozenset(), 0.8, frozenset(), frozenset())
        m2 = CirculationMetrics(5.0, 10.0, frozenset(), frozenset(), 0.8, frozenset(), frozenset())
        assert m1 == m2

    def test_deterministic(self):
        m1 = CirculationMetrics(5.0, 10.0, frozenset(), frozenset(), 0.8, frozenset(), frozenset())
        m2 = CirculationMetrics.from_dict(m1.to_dict())
        assert m1 == m2
