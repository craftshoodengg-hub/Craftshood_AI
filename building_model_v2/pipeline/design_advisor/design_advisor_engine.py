"""Engine for executing design advisor rules and aggregating advice."""
from __future__ import annotations

from typing import Any, List

from .advice_result import AdviceResult
from .advisor_rule import BaseAdvisorRule
from .basic_advisor_rule import BasicAdvisorRule
from ..design_request import DesignRequest


class DesignAdvisorEngine:
    """Executes advisor rules and aggregates their advice results."""

    def __init__(self) -> None:
        self._rules: list[BaseAdvisorRule] = []
        self.register_rule(BasicAdvisorRule())

    def register_rule(self, rule: BaseAdvisorRule) -> None:
        if rule not in self._rules:
            self._rules.append(rule)

    def unregister_rule(self, rule: BaseAdvisorRule) -> None:
        if rule in self._rules:
            self._rules.remove(rule)

    def analyze(
        self,
        design_request: DesignRequest,
        building_model: Any = None,
        pipeline_result: Any = None,
    ) -> list[AdviceResult]:
        results: list[AdviceResult] = []
        for rule in self._rules:
            results.append(rule.analyze(design_request, building_model, pipeline_result))
        return results

    @staticmethod
    def overall_score(results: list[AdviceResult]) -> float:
        if not results:
            return 0.0
        return sum(result.score for result in results) / len(results)

    @staticmethod
    def strengths(results: list[AdviceResult]) -> list[str]:
        return [strength for result in results for strength in result.strengths]

    @staticmethod
    def weaknesses(results: list[AdviceResult]) -> list[str]:
        return [weakness for result in results for weakness in result.weaknesses]

    @staticmethod
    def advice(results: list[AdviceResult]) -> list["DesignAdvice"]:
        return [item for result in results for item in result.advice]
