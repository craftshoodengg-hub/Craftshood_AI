"""Requirement Parser for Craftshood AI.

Deterministic natural language parser for architectural design requirements.
No AI. No LLM. Pure regex-based extraction.
"""
from __future__ import annotations
from .design_requirements import (
    BuildingRequirements,
    DesignRequirements,
    PlotRequirements,
)
from .parser_result import ParserResult
from .parser_rules import (
    extract_bathrooms,
    extract_bedrooms,
    extract_bhk,
    extract_boolean_features,
    extract_budget,
    extract_building_type,
    extract_facing,
    extract_floors,
    extract_parking_count,
    extract_plot_size,
    extract_priorities,
    extract_style,
)


class RequirementParser:
    """Deterministic parser for architectural design requirements."""

    def parse(self, text: str) -> ParserResult:
        """Parse natural language text into structured design requirements.

        Args:
            text: User's natural language design request.

        Returns:
            ParserResult with extracted requirements and metadata.
        """
        warnings: list[str] = []
        extracted: list[str] = []

        # Extract plot requirements
        width, length, area_value = extract_plot_size(text)
        facing = extract_facing(text)
        # If width is None but area_value is set, it's an area-only plot
        if width is None and area_value is not None:
            plot = PlotRequirements(area=area_value, facing=facing)
            extracted.append("plot.area")
        else:
            plot = PlotRequirements(width=width, length=length, facing=facing)
            if width is not None:
                extracted.append("plot.width")
            if length is not None:
                extracted.append("plot.length")
        if facing is not None:
            extracted.append("plot.facing")

        # Extract building requirements
        bhk = extract_bhk(text)
        bedrooms = extract_bedrooms(text) or bhk
        bathrooms = extract_bathrooms(text)
        floors = extract_floors(text)
        building_type = extract_building_type(text)
        style = extract_style(text)
        parking_count = extract_parking_count(text)
        budget, budget_unit = extract_budget(text)
        bool_features = extract_boolean_features(text)
        priorities = extract_priorities(text)

        # Check for duplex/villa/apartment
        duplex = bool_features.get("duplex", False) or building_type == "duplex"
        apartment = building_type == "apartment"
        villa = building_type == "villa"

        # Validate BHK vs bedrooms consistency
        if bhk is not None and bedrooms is not None and bhk != bedrooms:
            warnings.append(
                f"BHK count ({bhk}) differs from bedroom count ({bedrooms}). "
                f"Using BHK value."
            )
            bedrooms = bhk

        # Default bathrooms to bedrooms if not specified
        if bathrooms is None and bedrooms is not None:
            bathrooms = max(1, bedrooms - 1)

        # Default floors
        if floors is None:
            if duplex:
                floors = 2
            else:
                floors = 1

        building = BuildingRequirements(
            building_type=building_type,
            floors=floors,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking=bool_features.get("parking", False) or parking_count is not None,
            parking_count=parking_count,
            pooja=bool_features.get("pooja", False),
            office=bool_features.get("office", False),
            balcony=bool_features.get("balcony", False),
            utility=bool_features.get("utility", False),
            vastu_required=bool_features.get("vastu", False),
            accessibility_required=bool_features.get("accessibility", False),
            duplex=duplex,
            apartment=apartment,
            villa=villa,
        )

        if bedrooms is not None:
            extracted.append("building.bedrooms")
        if bathrooms is not None:
            extracted.append("building.bathrooms")
        if floors is not None:
            extracted.append("building.floors")
        if building_type is not None:
            extracted.append("building.building_type")
        if bool_features.get("parking"):
            extracted.append("building.parking")
        if bool_features.get("pooja"):
            extracted.append("building.pooja")
        if bool_features.get("vastu"):
            extracted.append("building.vastu_required")

        # Build requirements object
        requirements = DesignRequirements(
            plot=plot,
            building=building,
            budget=budget,
            budget_unit=budget_unit,
            style=style,
            priorities=tuple(priorities),
        )

        # Determine missing fields
        missing: list[str] = []
        if plot.width is None and plot.length is None and plot.area is None:
            missing.append("plot dimensions")
        if building.bedrooms is None:
            missing.append("building.bedrooms")

        # Calculate confidence
        total_fields = len(extracted) + len(missing)
        confidence = len(extracted) / total_fields if total_fields > 0 else 0.0

        # Add warnings for missing critical fields
        if not building.vastu_required and "vastu" in text.lower():
            warnings.append("Vastu mentioned but could not determine specific requirements")

        return ParserResult(
            requirements=requirements,
            confidence=round(confidence, 2),
            extracted_fields=tuple(extracted),
            missing_fields=tuple(missing),
            warnings=tuple(warnings),
        )
