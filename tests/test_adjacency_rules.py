"""Unit tests for Adjacency Rules."""
from __future__ import annotations
import pytest
from building_model_v2.layout.adjacency_rules import (
    AdjacencyRule,
    AdjacencyRuleSet,
    ConnectionType,
    create_default_rules,
)


class TestConnectionType:
    def test_values(self):
        assert ConnectionType.DIRECT.value == "direct"
        assert ConnectionType.VIA_DOOR.value == "via_door"
        assert ConnectionType.NONE.value == "none"


class TestAdjacencyRule:
    def test_create(self):
        r = AdjacencyRule("Kitchen", frozenset({"Dining"}), frozenset({"Master Bedroom"}), frozenset(), 0.8)
        assert r.room_type == "Kitchen" and r.weight == 0.8

    def test_to_dict(self):
        r = AdjacencyRule("Kitchen", frozenset({"Dining"}), frozenset({"Master Bedroom"}), frozenset(), 0.8)
        d = r.to_dict()
        assert d["room_type"] == "Kitchen" and "Dining" in d["preferred_adjacent"]

    def test_from_dict(self):
        r = AdjacencyRule.from_dict({"room_type": "Kitchen", "preferred_adjacent": ["Dining"], "weight": 0.8})
        assert r.room_type == "Kitchen" and "Dining" in r.preferred_adjacent

    def test_frozen(self):
        r = AdjacencyRule("Kitchen")
        with pytest.raises(AttributeError):
            r.weight = 0.5


class TestAdjacencyRuleSet:
    def test_get_rule(self):
        rules = create_default_rules()
        r = rules.get_rule("Kitchen")
        assert r is not None and r.room_type == "Kitchen"

    def test_get_rule_case_insensitive(self):
        rules = create_default_rules()
        r = rules.get_rule("kitchen")
        assert r is not None

    def test_get_rule_missing(self):
        rules = create_default_rules()
        assert rules.get_rule("NonExistent") is None

    def test_serialization(self):
        rules = create_default_rules()
        d = rules.to_dict()
        assert len(d["rules"]) == 13
        rules2 = AdjacencyRuleSet.from_dict(d)
        assert len(rules2.rules) == 13


class TestDefaultRules:
    def test_living_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Living")
        assert r is not None
        assert "Entrance" in r.preferred_adjacent
        assert "Dining" in r.preferred_adjacent

    def test_kitchen_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Kitchen")
        assert r is not None
        assert "Dining" in r.preferred_adjacent
        assert "Utility" in r.preferred_adjacent
        assert "Bedroom" in r.discouraged_adjacent

    def test_master_bedroom_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Bedroom")
        assert r is not None
        assert "Bathroom" in r.required_adjacent
        assert "Garage" in r.discouraged_adjacent

    def test_bathroom_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Bathroom")
        assert r is not None
        assert "Kitchen" in r.discouraged_adjacent
        assert "Dining" in r.discouraged_adjacent

    def test_pooja_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Pooja")
        assert r is not None
        assert "Toilet" in r.discouraged_adjacent
        assert "Common Toilet" in r.discouraged_adjacent

    def test_stair_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Stair")
        assert r is not None
        assert "Corridor" in r.required_adjacent

    def test_garage_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Garage")
        assert r is not None
        assert "Entrance" in r.preferred_adjacent

    def test_utility_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Utility")
        assert r is not None
        assert "Kitchen" in r.preferred_adjacent

    def test_bedroom_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Bedroom")
        assert r is not None
        assert "Bathroom" in r.preferred_adjacent

    def test_toilet_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Toilet")
        assert r is not None
        assert "Kitchen" in r.discouraged_adjacent

    def test_common_toilet_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Common Toilet")
        assert r is not None
        assert "Pooja" in r.discouraged_adjacent

    def test_balcony_rules(self):
        rules = create_default_rules()
        r = rules.get_rule("Balcony")
        assert r is not None
        assert "Living" in r.preferred_adjacent

    def test_all_rules_present(self):
        rules = create_default_rules()
        assert len(rules.rules) == 13

    def test_deterministic(self):
        r1 = create_default_rules()
        r2 = create_default_rules()
        assert r1.rules == r2.rules
