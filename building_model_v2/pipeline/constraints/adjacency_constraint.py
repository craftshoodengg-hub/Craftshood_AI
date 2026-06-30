"""Adjacency and relationship constraint for design requests."""
from __future__ import annotations

from .base_constraint import BaseConstraint
from .constraint_result import ConstraintResult
from ..design_request import DesignRequest


class AdjacencyConstraint(BaseConstraint):
    """Constraint that validates architectural adjacency relationships."""

    @property
    def name(self) -> str:
        return "AdjacencyConstraint"

    def validate(self, design_request: DesignRequest) -> ConstraintResult:
        warnings: list[str] = []
        errors: list[str] = []

        plot_area = design_request.plot_width * design_request.plot_depth

        if design_request.living_room is False and design_request.bedrooms >= 1:
            errors.append("Living room is required for residential designs with bedrooms")

        if design_request.bathrooms > design_request.bedrooms + 3:
            errors.append("Bathrooms must not exceed bedrooms + 3")

        if design_request.floors > 1 and not design_request.staircase:
            errors.append("Multi-floor designs require a staircase")

        if design_request.parking > 0 and plot_area < 500:
            warnings.append("Parking on a small plot may be difficult to accommodate")

        if design_request.bedrooms >= 3 and not design_request.pooja_room:
            warnings.append("A pooja room is recommended for larger residential designs")

        if not design_request.dining_room and design_request.kitchen_type:
            warnings.append("Dining room not requested; kitchen adjacency cannot be guaranteed.")

        passed = len(errors) == 0
        return ConstraintResult(
            passed=passed,
            warnings=tuple(warnings),
            errors=tuple(errors),
            constraint_name=self.name,
        )
