"""Tests for the VastuEngine."""
from __future__ import annotations

from building_model_v2.pipeline.design_request import DesignRequest
from building_model_v2.pipeline.vastu.basic_vastu_rule import BasicVastuRule
from building_model_v2.pipeline.vastu.vastu_engine import VastuEngine
from building_model_v2.pipeline.vastu.vastu_result import VastuResult
from building_model_v2.pipeline.vastu.vastu_rule import BaseVastuRule


class TestVastuEngine:
    def _make_request(self) -> DesignRequest:
        return DesignRequest(
            project_type="residential",
            plot_width=30.0,
            plot_depth=40.0,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=1,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=True,
            orientation="north",
            special_requirements=(),
        )

    def test_default_rule_registration(self) -> None:
        engine = VastuEngine()
        results = engine.analyze(self._make_request())

        assert len(results) == 1
        assert results[0].rule_name == "BasicVastuRule"

    def test_register_rule(self) -> None:
        engine = VastuEngine()

        class AdditionalRule(BaseVastuRule):
            @property
            def name(self) -> str:
                return "AdditionalRule"

            def analyze(self, design_request: DesignRequest) -> VastuResult:
                return VastuResult(
                    passed=True,
                    score=10.0,
                    warnings=["Extra warning"],
                    suggestions=["Extra suggestion"],
                    rule_name=self.name,
                )

        engine.register_rule(AdditionalRule())
        results = engine.analyze(self._make_request())

        assert len(results) == 2
        assert results[1].rule_name == "AdditionalRule"

    def test_unregister_rule(self) -> None:
        engine = VastuEngine()
        basic_rule = next(rule for rule in engine._rules if rule.name == "BasicVastuRule")

        engine.unregister_rule(basic_rule)
        results = engine.analyze(self._make_request())

        assert len(results) == 0

    def test_execution_order(self) -> None:
        engine = VastuEngine()

        class FirstRule(BaseVastuRule):
            @property
            def name(self) -> str:
                return "FirstRule"

            def analyze(self, design_request: DesignRequest) -> VastuResult:
                return VastuResult(
                    passed=True,
                    score=1.0,
                    warnings=["first"],
                    suggestions=["first"],
                    rule_name=self.name,
                )

        class SecondRule(BaseVastuRule):
            @property
            def name(self) -> str:
                return "SecondRule"

            def analyze(self, design_request: DesignRequest) -> VastuResult:
                return VastuResult(
                    passed=True,
                    score=2.0,
                    warnings=["second"],
                    suggestions=["second"],
                    rule_name=self.name,
                )

        engine.unregister_rule(next(rule for rule in engine._rules if rule.name == "BasicVastuRule"))
        engine.register_rule(FirstRule())
        engine.register_rule(SecondRule())

        results = engine.analyze(self._make_request())

        assert [result.rule_name for result in results] == ["FirstRule", "SecondRule"]

    def test_multiple_rules(self) -> None:
        engine = VastuEngine()

        class ExtraRule(BaseVastuRule):
            @property
            def name(self) -> str:
                return "ExtraRule"

            def analyze(self, design_request: DesignRequest) -> VastuResult:
                return VastuResult(
                    passed=True,
                    score=30.0,
                    warnings=["extra"],
                    suggestions=["extra"],
                    rule_name=self.name,
                )

        engine.register_rule(ExtraRule())
        results = engine.analyze(self._make_request())

        assert len(results) == 2
        assert any(result.rule_name == "BasicVastuRule" for result in results)
        assert any(result.rule_name == "ExtraRule" for result in results)

    def test_overall_score(self) -> None:
        engine = VastuEngine()

        class ScoreRule(BaseVastuRule):
            @property
            def name(self) -> str:
                return "ScoreRule"

            def analyze(self, design_request: DesignRequest) -> VastuResult:
                return VastuResult(
                    passed=True,
                    score=80.0,
                    warnings=[],
                    suggestions=[],
                    rule_name=self.name,
                )

        engine.unregister_rule(next(rule for rule in engine._rules if rule.name == "BasicVastuRule"))
        engine.register_rule(ScoreRule())
        engine.register_rule(ScoreRule())

        results = engine.analyze(self._make_request())
        assert VastuEngine.overall_score(results) == 80.0

    def test_warning_aggregation(self) -> None:
        engine = VastuEngine()

        class WarningRule(BaseVastuRule):
            @property
            def name(self) -> str:
                return "WarningRule"

            def analyze(self, design_request: DesignRequest) -> VastuResult:
                return VastuResult(
                    passed=True,
                    score=10.0,
                    warnings=["warning1"],
                    suggestions=[],
                    rule_name=self.name,
                )

        engine.unregister_rule(next(rule for rule in engine._rules if rule.name == "BasicVastuRule"))
        engine.register_rule(WarningRule())
        engine.register_rule(WarningRule())

        results = engine.analyze(self._make_request())
        assert VastuEngine.warnings(results) == ["warning1", "warning1"]

    def test_suggestion_aggregation(self) -> None:
        engine = VastuEngine()

        class SuggestionRule(BaseVastuRule):
            @property
            def name(self) -> str:
                return "SuggestionRule"

            def analyze(self, design_request: DesignRequest) -> VastuResult:
                return VastuResult(
                    passed=True,
                    score=10.0,
                    warnings=[],
                    suggestions=["suggestion1"],
                    rule_name=self.name,
                )

        engine.unregister_rule(next(rule for rule in engine._rules if rule.name == "BasicVastuRule"))
        engine.register_rule(SuggestionRule())
        engine.register_rule(SuggestionRule())

        results = engine.analyze(self._make_request())
        assert VastuEngine.suggestions(results) == ["suggestion1", "suggestion1"]

    def test_empty_engine_behavior(self) -> None:
        engine = VastuEngine()
        engine.unregister_rule(next(rule for rule in engine._rules if rule.name == "BasicVastuRule"))

        results = engine.analyze(self._make_request())

        assert results == []
        assert VastuEngine.overall_score(results) == 0.0
        assert VastuEngine.warnings(results) == []
        assert VastuEngine.suggestions(results) == []
