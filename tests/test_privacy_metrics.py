"""Unit tests for Privacy Metrics."""
from __future__ import annotations
import pytest
from building_model_v2.layout.privacy_metrics import PrivacyConflict, PrivacyMetrics


class TestPrivacyConflict:
    def test_create(self):
        c = PrivacyConflict("a", "b", "CODE", "desc")
        assert c.room_a == "a" and c.issue_code == "CODE"

    def test_to_dict(self):
        c = PrivacyConflict("a", "b", "CODE", "desc")
        d = c.to_dict()
        assert d["room_a"] == "a" and d["issue_code"] == "CODE"

    def test_from_dict(self):
        c = PrivacyConflict.from_dict({"room_a": "a", "room_b": "b", "issue_code": "CODE", "description": "desc"})
        assert c.room_a == "a" and c.issue_code == "CODE"

    def test_equality(self):
        c1 = PrivacyConflict("a", "b", "CODE", "desc")
        c2 = PrivacyConflict("a", "b", "CODE", "desc")
        assert c1 == c2

    def test_hash(self):
        c1 = PrivacyConflict("a", "b", "CODE", "desc")
        c2 = PrivacyConflict("a", "b", "CODE", "desc")
        assert hash(c1) == hash(c2)


class TestPrivacyMetrics:
    def test_create(self):
        m = PrivacyMetrics(frozenset({"a"}), frozenset({"b"}), frozenset({"c"}), 0.8, (), 2)
        assert m.privacy_score == 0.8 and m.circulation_crossings == 2

    def test_to_dict(self):
        m = PrivacyMetrics(frozenset({"a"}), frozenset({"b"}), frozenset({"c"}), 0.8, (), 2)
        d = m.to_dict()
        assert d["privacy_score"] == 0.8 and d["circulation_crossings"] == 2

    def test_from_dict(self):
        m = PrivacyMetrics.from_dict({"public_rooms": ["a"], "semi_private_rooms": ["b"], "private_rooms": ["c"], "privacy_score": 0.8, "privacy_conflicts": [], "circulation_crossings": 2})
        assert m.privacy_score == 0.8

    def test_empty_metrics(self):
        m = PrivacyMetrics(frozenset(), frozenset(), frozenset(), 1.0, (), 0)
        assert m.privacy_score == 1.0

    def test_equality(self):
        m1 = PrivacyMetrics(frozenset(), frozenset(), frozenset(), 1.0, (), 0)
        m2 = PrivacyMetrics(frozenset(), frozenset(), frozenset(), 1.0, (), 0)
        assert m1 == m2

    def test_deterministic(self):
        m1 = PrivacyMetrics(frozenset(), frozenset(), frozenset(), 1.0, (), 0)
        m2 = PrivacyMetrics.from_dict(m1.to_dict())
        assert m1 == m2
