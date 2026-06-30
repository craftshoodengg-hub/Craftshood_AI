"""Space and size constraint for pipeline design requests."""
from __future__ import annotations

from .base_constraint import BaseConstraint
from .constraint_result import ConstraintResult
from ..design_request import DesignRequest


class SpaceSizeConstraint(BaseConstraint):
    """Constraint that validates plot and program size feasibility."""

    @property
    def name(self) -> str:
        return "SpaceSizeConstraint"

    def validate(self, design_request: DesignRequest) -> ConstraintResult:
        area = design_request.plot_width * design_request.plot_depth
        warnings: list[str] = []
        errors: list[str] = []

        if area < 300:
            errors.append("Plot area must be at least 300 square units")

        required_area = 0.0
        required_area += design_request.bedrooms * 100
        required_area += design_request.bathrooms * 35

        if design_request.living_room:
            required_area += 120

        if design_request.kitchen_type:
            required_area += 80

        if design_request.parking > 0:
            required_area += design_request.parking * 120

        buffer_area = required_area * 0.2
        estimated_area = required_area + buffer_area

        if area < design_request.bedrooms * 100:
            errors.append("Too many bedrooms for the available plot size")

        if estimated_area > area:
            errors.append(
                "Estimated required area exceeds available plot area"
            )
        elif estimated_area > area * 0.9:
            warnings.append("Layout is tight for available plot area")

        if design_request.floors > 3 and area < 500:
            warnings.append("High floor count on a small plot may be challenging")

        if design_request.parking > 0 and area < design_request.parking * 120:
            warnings.append("Parking requirement may be difficult to accommodate on this plot")

        passed = len(errors) == 0
        return ConstraintResult(
            passed=passed,
            warnings=tuple(warnings),
            errors=tuple(errors),
            constraint_name=self.name,
        )
