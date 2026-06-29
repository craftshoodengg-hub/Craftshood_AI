"""Unit tests for Egress Metrics."""
from __future__ import annotations
import pytest
from building_model_v2.layout.egress_metrics import ExitPath, EgressMetrics


class TestExitPath:
    def test_create(self):
        p = ExitPath("a", "exit", ("a", "b", "exit"), 3.0, 2)
        assert p.source_room_id == "a" and p.exit_room_id == "exit"

    def test_room_count(self):
        p = ExitPath("a", "exit", ("a", "b", "exit"), 3.0, 2)
        assert p.room_count == 3

    def test_is_direct(self):
        p1 = ExitPath("a", "exit", ("a", "exit"), 1.0, 1)
        assert p1.is_direct
        p2 = ExitPath("a", "exit", ("a", "b", "c", "exit"), 3.0, 3)
        assert not p2.is_direct

    def test_to_dict(self):
        p = ExitPath("a", "exit", ("a", "exit"), 1.0, 1)
        d = p.to_dict()
        assert d["source_room_id"] == "a" and d["door_count"] == 1

    def test_from_dict(self):
        p = ExitPath.from_dict({"source_room_id": "a", "exit_room_id": "exit", "room_sequence": ["a", "exit"], "path_length": 1.0, "door_count": 1})
        assert p.source_room_id == "a"

    def test_equality(self):
        p1 = ExitPath("a", "exit", ("a", "exit"), 1.0, 1)
        p2 = ExitPath("a", "exit", ("a", "exit"), 1.0, 1)
        assert p1 == p2

    def test_hash(self):
        p1 = ExitPath("a", "exit", ("a", "exit"), 1.0, 1)
        p2 = ExitPath("a", "exit", ("a", "exit"), 1.0, 1)
        assert hash(p1) == hash(p2)


class TestEgressMetrics:
    def test_create(self):
        m = EgressMetrics(frozenset({"a"}), frozenset({"b"}), 5.0, 3.0, frozenset(), (), 0.8)
        assert m.egress_score == 0.8 and m.maximum_exit_distance == 5.0

    def test_to_dict(self):
        m = EgressMetrics(frozenset({"a"}), frozenset(), 5.0, 5.0, frozenset(), (), 1.0)
        d = m.to_dict()
        assert d["egress_score"] == 1.0

    def test_from_dict(self):
        m = EgressMetrics.from_dict({"reachable_rooms": ["a"], "unreachable_rooms": [], "maximum_exit_distance": 5.0, "average_exit_distance": 5.0, "dead_end_rooms": [], "exit_paths": [], "egress_score": 1.0})
        assert m.egress_score == 1.0

    def test_empty_metrics(self):
        m = EgressMetrics(frozenset(), frozenset(), 0.0, 0.0, frozenset(), (), 1.0)
        assert m.egress_score == 1.0

    def test_equality(self):
        m1 = EgressMetrics(frozenset(), frozenset(), 0.0, 0.0, frozenset(), (), 1.0)
        m2 = EgressMetrics(frozenset(), frozenset(), 0.0, 0.0, frozenset(), (), 1.0)
        assert m1 == m2

    def test_deterministic(self):
        m1 = EgressMetrics(frozenset(), frozenset(), 0.0, 0.0, frozenset(), (), 1.0)
        m2 = EgressMetrics.from_dict(m1.to_dict())
        assert m1 == m2
