"""Engine for executing Vastu rules and aggregating results."""
from __future__ import annotations

from typing import List

from .vastu_result import VastuResult
from .vastu_rule import BaseVastuRule
from .basic_vastu_rule import BasicVastuRule
from ..design_request import DesignRequest


class VastuEngine:
    """Executes Vastu rules against a design request."""

    def __init__(self) -> None:
        self._rules: list[BaseVastuRule] = []
        self.register_rule(BasicVastuRule())

    def register_rule(self, rule: BaseVastuRule) -> None:
        if rule not in self._rules:
            self._rules.append(rule)

    def unregister_rule(self, rule: BaseVastuRule) -> None:
        if rule in self._rules:
            self._rules.remove(rule)

    def analyze(self, design_request: DesignRequest) -> list[VastuResult]:
        results: list[VastuResult] = []
        for rule in self._rules:
            results.append(rule.analyze(design_request))
        return results

    @staticmethod
    def overall_score(results: list[VastuResult]) -> float:
        if not results:
            return 0.0
        return sum(result.score for result in results) / len(results)

    @staticmethod
    def warnings(results: list[VastuResult]) -> list[str]:
        return [warning for result in results for warning in result.warnings]

    @staticmethod
    def suggestions(results: list[VastuResult]) -> list[str]:
        return [suggestion for result in results for suggestion in result.suggestions]
