"""Request validation flow for pipeline design requests."""
from __future__ import annotations

from .constraints.constraint_engine import ConstraintEngine
from .constraints.adjacency_constraint import AdjacencyConstraint
from .constraints.plot_building_constraint import PlotBuildingConstraint
from .constraints.space_size_constraint import SpaceSizeConstraint
from .design_request import DesignRequest
from ..constraints.constraint_result import ConstraintResult


class RequestValidator:
    """Validates a design request against the Phase 15B constraint set."""

    def __init__(self) -> None:
        self.engine = ConstraintEngine()
        self.engine.register_constraint(SpaceSizeConstraint())
        self.engine.register_constraint(AdjacencyConstraint())
        self.engine.register_constraint(PlotBuildingConstraint())

    def validate(self, design_request: DesignRequest) -> list[ConstraintResult]:
        return self.engine.validate(design_request)

    @staticmethod
    def has_errors(results: list[ConstraintResult]) -> bool:
        return any(result.has_errors() for result in results)

    @staticmethod
    def has_warnings(results: list[ConstraintResult]) -> bool:
        return any(result.has_warnings() for result in results)

    @staticmethod
    def errors(results: list[ConstraintResult]) -> list[str]:
        return [error for result in results for error in result.errors]

    @staticmethod
    def warnings(results: list[ConstraintResult]) -> list[str]:
        return [warning for result in results for warning in result.warnings]
