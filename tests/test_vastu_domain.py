"""Tests for the basic Vastu domain model."""
from __future__ import annotations

from building_model_v2.pipeline.design_request import DesignRequest
from building_model_v2.pipeline.vastu.vastu_result import VastuResult
from building_model_v2.pipeline.vastu.vastu_rule import BaseVastuRule


class DummyVastuRule(BaseVastuRule):
    @property
    def name(self) -> str:
        return "DummyVastuRule"

    def analyze(self, design_request: DesignRequest) -> VastuResult:
        return VastuResult(
            passed=True,
            score=8.5,
            warnings=["Minor directional warning"],
            suggestions=["Consider placing the bedroom in the southwest."],
            rule_name=self.name,
        )


class TestVastuDomain:
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

    def test_vastu_result_creation(self) -> None:
        result = VastuResult(
            passed=False,
            score=4.0,
            warnings=["Test warning"],
            suggestions=["Test suggestion"],
            rule_name="TestRule",
        )

        assert result.passed is False
        assert result.score == 4.0
        assert result.warnings == ["Test warning"]
        assert result.suggestions == ["Test suggestion"]
        assert result.rule_name == "TestRule"

    def test_warnings_helper(self) -> None:
        result = VastuResult(
            passed=True,
            score=9.0,
            warnings=["Warning present"],
            suggestions=[],
            rule_name="TestRule",
        )

        assert result.has_warnings() is True
        assert result.has_suggestions() is False

    def test_suggestions_helper(self) -> None:
        result = VastuResult(
            passed=True,
            score=9.0,
            warnings=[],
            suggestions=["Suggestion present"],
            rule_name="TestRule",
        )

        assert result.has_warnings() is False
        assert result.has_suggestions() is True

    def test_dummy_rule_analyze_returns_vastu_result(self) -> None:
        rule = DummyVastuRule()
        result = rule.analyze(self._make_request())

        assert isinstance(result, VastuResult)
        assert result.rule_name == "DummyVastuRule"
        assert result.passed is True
        assert result.score == 8.5
        assert result.has_warnings() is True
        assert result.has_suggestions() is True
