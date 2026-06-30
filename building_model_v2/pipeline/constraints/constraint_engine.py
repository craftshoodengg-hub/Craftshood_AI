"""Constraint engine for managing and executing architectural constraints."""
from __future__ import annotations

from typing import List

from ..design_request import DesignRequest
from .base_constraint import BaseConstraint
from .constraint_result import ConstraintResult


class ConstraintEngine:
    """Registry and executor for pipeline constraints."""

    def __init__(self) -> None:
        self._constraints: list[BaseConstraint] = []

    def register_constraint(self, constraint: BaseConstraint) -> None:
        if constraint not in self._constraints:
            self._constraints.append(constraint)

    def unregister_constraint(self, constraint: BaseConstraint) -> None:
        if constraint in self._constraints:
            self._constraints.remove(constraint)

    def validate(self, design_request: DesignRequest) -> list[ConstraintResult]:
        results: list[ConstraintResult] = []
        for constraint in self._constraints:
            result = constraint.validate(design_request)
            results.append(result)
        return results
