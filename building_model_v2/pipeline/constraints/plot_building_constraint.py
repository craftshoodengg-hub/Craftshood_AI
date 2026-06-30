"""Plot and building constraint for pipeline design requests."""
from __future__ import annotations

from .base_constraint import BaseConstraint
from .constraint_result import ConstraintResult
from ..design_request import DesignRequest


class PlotBuildingConstraint(BaseConstraint):
    """Constraint that validates plot dimensions and building coverage."""

    @property
    def name(self) -> str:
        return "PlotBuildingConstraint"

    def validate(self, design_request: DesignRequest) -> ConstraintResult:
        warnings: list[str] = []
        errors: list[str] = []

        plot_width = design_request.plot_width
        plot_depth = design_request.plot_depth
        plot_area = plot_width * plot_depth

        if plot_width < 10:
            errors.append("Plot width must be at least 10 ft")

        if plot_depth < 10:
            errors.append("Plot depth must be at least 10 ft")

        if plot_area < 300:
            errors.append("Plot area must be at least 300 sq ft")

        if plot_width < 20:
            warnings.append("Plot width under 20 ft may limit side setbacks")

        if plot_depth < 30:
            warnings.append("Plot depth under 30 ft may limit front/rear setbacks")

        required_footprint = 0.0
        required_footprint += design_request.bedrooms * 100
        required_footprint += design_request.bathrooms * 35
        required_footprint += 80  # kitchen

        if design_request.living_room:
            required_footprint += 120

        if design_request.dining_room:
            required_footprint += 80

        if design_request.pooja_room:
            required_footprint += 40

        if design_request.staircase:
            required_footprint += 60

        if design_request.parking > 0:
            required_footprint += design_request.parking * 120

        footprint_per_floor = required_footprint / max(design_request.floors, 1)
        max_coverage = plot_area * 0.7
        warning_threshold = plot_area * 0.6

        if footprint_per_floor > max_coverage:
            errors.append(
                "Estimated ground footprint exceeds 70% of plot coverage"
            )
        elif footprint_per_floor > warning_threshold:
            warnings.append(
                "Estimated ground footprint exceeds 60% of plot coverage"
            )

        if design_request.floors > 10:
            errors.append("Floor count must be 10 or less")

        if (
            design_request.project_type.lower() == "residential"
            and design_request.floors > 3
        ):
            warnings.append("Residential designs with more than 3 floors may be challenging")

        if design_request.parking > 0 and plot_width < 18:
            warnings.append(
                "Car parking may be difficult on a plot narrower than 18 ft"
            )

        if design_request.parking > 0 and plot_depth < 25:
            warnings.append(
                "Parking depth may be difficult on a plot shallower than 25 ft"
            )

        passed = len(errors) == 0
        return ConstraintResult(
            passed=passed,
            warnings=tuple(warnings),
            errors=tuple(errors),
            constraint_name=self.name,
        )
