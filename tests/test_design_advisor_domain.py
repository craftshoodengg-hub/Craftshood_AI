from __future__ import annotations

import pytest

from building_model_v2.pipeline.design_advisor import (
    AdviceResult,
    BaseAdvisorRule,
    DesignAdvice,
)


class DummyAdvisor(BaseAdvisorRule):
    @property
    def name(self) -> str:
        return "dummy-advisor"

    def analyze(self, design_request, building_model, pipeline_result) -> AdviceResult:
        advice = [
            DesignAdvice(
                category="layout",
                title="Provide wider circulation",
                description="Circulation is currently tight around the entrance.",
                severity="warning",
                recommendation="Increase corridor width to at least 1.2 meters.",
            )
        ]
        return AdviceResult(
            advice=advice,
            score=0.75,
            strengths=["Efficient core plan"],
            weaknesses=["Narrow access corridor"],
        )


def test_design_advice_creation() -> None:
    advice = DesignAdvice(
        category="space-planning",
        title="Improve room adjacency",
        description="The kitchen and dining room are not directly connected.",
        severity="recommendation",
        recommendation="Place the dining room adjacent to the kitchen for better flow.",
    )

    assert advice.category == "space-planning"
    assert advice.title == "Improve room adjacency"
    assert advice.severity == "recommendation"
    assert advice.recommendation.startswith("Place the dining room")


def test_design_advice_invalid_severity_raises() -> None:
    with pytest.raises(ValueError, match="severity must be one of"):
        DesignAdvice(
            category="geometry",
            title="Invalid severity",
            description="This advice has a bad severity value.",
            severity="critical",
            recommendation="Use an allowed severity label.",
        )


def test_advice_result_helpers_for_empty_result() -> None:
    result = AdviceResult()

    assert result.score == 0.0
    assert result.advice_count() == 0
    assert not result.has_strengths()
    assert not result.has_weaknesses()


def test_advice_result_helpers_with_strengths_and_weaknesses() -> None:
    result = AdviceResult(
        advice=[
            DesignAdvice(
                category="efficiency",
                title="Optimize room layout",
                description="Room positions can be improved.",
                severity="info",
                recommendation="Review area allocation and circulation.",
            )
        ],
        score=0.9,
        strengths=["Good access to natural light"],
        weaknesses=["Small service zone"],
    )

    assert result.advice_count() == 1
    assert result.has_strengths()
    assert result.has_weaknesses()
    assert result.score == 0.9
    assert result.advice[0].severity == "info"


def test_dummy_advisor_analyze_returns_advice_result() -> None:
    advisor = DummyAdvisor()
    result = advisor.analyze(design_request=None, building_model=None, pipeline_result=None)

    assert isinstance(result, AdviceResult)
    assert result.advice_count() == 1
    assert result.has_strengths()
    assert result.has_weaknesses()
    assert result.advice[0].title == "Provide wider circulation"
    assert result.score == 0.75
