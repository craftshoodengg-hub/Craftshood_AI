from __future__ import annotations

from building_model_v2.pipeline.design_advisor import (
    BasicAdvisorRule,
    DesignAdvisorEngine,
    DesignAdvice,
)
from building_model_v2.pipeline.design_request import DesignRequest


class DummyAdvisorRule(BasicAdvisorRule):
    @property
    def name(self) -> str:
        return "dummy-advisor"

    def analyze(self, design_request, building_model=None, pipeline_result=None):
        return super().analyze(design_request, building_model, pipeline_result)


def _make_request(**overrides) -> DesignRequest:
    data = {
        "project_type": "residential",
        "plot_width": 30.0,
        "plot_depth": 40.0,
        "floors": 1,
        "bedrooms": 2,
        "bathrooms": 2,
        "parking": 1,
        "kitchen_type": "open",
        "pooja_room": True,
        "living_room": True,
        "dining_room": True,
        "staircase": True,
        "orientation": "north",
    }
    data.update(overrides)
    return DesignRequest(**data)


def test_default_rule_registration() -> None:
    engine = DesignAdvisorEngine()
    results = engine.analyze(_make_request())

    assert len(results) == 1
    assert results[0].score == 100.0


def test_register_and_unregister_rule() -> None:
    engine = DesignAdvisorEngine()
    extra_rule = DummyAdvisorRule()

    engine.register_rule(extra_rule)
    assert len(engine.analyze(_make_request())) == 2

    engine.unregister_rule(extra_rule)
    assert len(engine.analyze(_make_request())) == 1


def test_execution_order_is_preserved() -> None:
    engine = DesignAdvisorEngine()
    rule_one = DummyAdvisorRule()
    rule_two = BasicAdvisorRule()

    engine.register_rule(rule_one)
    engine.register_rule(rule_two)

    results = engine.analyze(_make_request())
    assert len(results) == 3
    assert results[0].score == 100.0
    assert results[1].score == 100.0
    assert results[2].score == 100.0


def test_multiple_rules_aggregate_results() -> None:
    engine = DesignAdvisorEngine()
    extra_rule = DummyAdvisorRule()
    engine.register_rule(extra_rule)

    results = engine.analyze(_make_request(pooja_room=False, living_room=False))
    assert len(results) == 2
    assert all(result.advice_count() >= 1 for result in results)


def test_overall_score_averages_results() -> None:
    engine = DesignAdvisorEngine()
    results = engine.analyze(_make_request())
    assert engine.overall_score(results) == 100.0

    empty_results: list = []
    assert engine.overall_score(empty_results) == 0.0


def test_strengths_and_weaknesses_aggregation() -> None:
    engine = DesignAdvisorEngine()
    results = engine.analyze(_make_request(pooja_room=False, living_room=False, floors=3))

    strengths = engine.strengths(results)
    weaknesses = engine.weaknesses(results)

    assert "Dedicated parking improves convenience." in strengths
    assert "Living room not requested." in weaknesses
    assert "Multi-storey designs require careful structural planning." in weaknesses


def test_advice_aggregation() -> None:
    engine = DesignAdvisorEngine()
    results = engine.analyze(_make_request(pooja_room=False, living_room=False, floors=3))
    all_advice = engine.advice(results)

    assert any(isinstance(item, DesignAdvice) for item in all_advice)
    assert any(item.category == "pooja_room" for item in all_advice)


def test_empty_engine_behavior() -> None:
    engine = DesignAdvisorEngine()
    engine.unregister_rule(next(iter(engine._rules)))
    assert engine.analyze(_make_request()) == []
    assert engine.overall_score([]) == 0.0
    assert engine.strengths([]) == []
    assert engine.weaknesses([]) == []
    assert engine.advice([]) == []
