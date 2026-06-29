"""Unit tests for Requirement Parser."""
from __future__ import annotations
import pytest
from building_model_v2.ai.requirement_parser import RequirementParser
from building_model_v2.ai.design_requirements import (
    BuildingRequirements,
    DesignRequirements,
    PlotRequirements,
)
from building_model_v2.ai.parser_result import ParserResult
from building_model_v2.ai.parser_rules import (
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


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def parser() -> RequirementParser:
    return RequirementParser()


# ============================================================================
# Plot Extraction Tests
# ============================================================================


class TestPlotExtraction:
    def test_40x60(self):
        w, l, u = extract_plot_size("40x60")
        assert w == 40.0 and l == 60.0

    def test_30_x_50_feet(self):
        w, l, u = extract_plot_size("30 x 50 feet")
        assert w == 30.0 and l == 50.0

    def test_40_by_60(self):
        w, l, u = extract_plot_size("40 by 60")
        assert w == 40.0 and l == 60.0

    def test_sqrtft(self):
        w, l, area = extract_plot_size("2000 sqft plot")
        assert area == 2000.0 and w is None and l is None

    def test_sqm(self):
        w, l, area = extract_plot_size("250 sqm")
        assert area == 250.0 and w is None and l is None

    def test_no_plot(self):
        w, l, u = extract_plot_size("3BHK house")
        assert w is None and l is None


# ============================================================================
# Facing Extraction Tests
# ============================================================================


class TestFacingExtraction:
    def test_east_facing(self):
        assert extract_facing("east-facing plot") == "east"

    def test_west_face(self):
        assert extract_facing("west face") == "west"

    def test_north_facing(self):
        assert extract_facing("north facing") == "north"

    def test_south(self):
        assert extract_facing("south direction") == "south"

    def test_north_east(self):
        assert extract_facing("north-east corner") == "north-east"

    def test_no_facing(self):
        assert extract_facing("3BHK house") is None


# ============================================================================
# BHK Extraction Tests
# ============================================================================


class TestBHKExtraction:
    def test_1bhk(self):
        assert extract_bhk("1BHK") == 1

    def test_2bhk(self):
        assert extract_bhk("2bhk house") == 2

    def test_3bhk(self):
        assert extract_bhk("3BHK duplex") == 3

    def test_10bhk(self):
        assert extract_bhk("10BHK villa") == 10

    def test_no_bhk(self):
        assert extract_bhk("house with garden") is None


# ============================================================================
# Bedroom Extraction Tests
# ============================================================================


class TestBedroomExtraction:
    def test_3_bedrooms(self):
        assert extract_bedrooms("3 bedrooms") == 3

    def test_three_bedroom(self):
        assert extract_bedrooms("three bedroom house") == 3

    def test_1_bedroom(self):
        assert extract_bedrooms("1 bedroom") == 1

    def test_no_bedrooms(self):
        assert extract_bedrooms("studio apartment") is None


# ============================================================================
# Bathroom Extraction Tests
# ============================================================================


class TestBathroomExtraction:
    def test_2_bathrooms(self):
        assert extract_bathrooms("2 bathrooms") == 2

    def test_1_bathroom(self):
        assert extract_bathrooms("1 bathroom") == 1

    def test_no_bathrooms(self):
        assert extract_bathrooms("3BHK house") is None


# ============================================================================
# Floor Extraction Tests
# ============================================================================


class TestFloorExtraction:
    def test_2_floors(self):
        assert extract_floors("2 floors") == 2

    def test_g_plus_2(self):
        assert extract_floors("G+2 building") == 3

    def test_duplex_implies_2(self):
        assert extract_floors("duplex house") == 2

    def test_single_floor(self):
        assert extract_floors("single floor") == 1

    def test_no_floors(self):
        assert extract_floors("3BHK house") is None



# ============================================================================
# Building Type Extraction Tests
# ============================================================================


class TestBuildingTypeExtraction:
    def test_duplex(self):
        assert extract_building_type("duplex house") == "duplex"

    def test_villa(self):
        assert extract_building_type("luxury villa") == "villa"

    def test_apartment(self):
        assert extract_building_type("2BHK apartment") == "apartment"

    def test_flat(self):
        assert extract_building_type("3BHK flat") == "apartment"

    def test_commercial(self):
        assert extract_building_type("commercial office") == "commercial"

    def test_residential(self):
        assert extract_building_type("residential house") == "residential"

    def test_no_type(self):
        assert extract_building_type("building") is None


# ============================================================================
# Style Extraction Tests
# ============================================================================


class TestStyleExtraction:
    def test_modern(self):
        assert extract_style("modern house") == "modern"

    def test_contemporary(self):
        assert extract_style("contemporary design") == "contemporary"

    def test_traditional(self):
        assert extract_style("traditional home") == "traditional"

    def test_minimalist(self):
        assert extract_style("minimalist apartment") == "minimalist"

    def test_no_style(self):
        assert extract_style("3BHK house") is None


# ============================================================================
# Boolean Features Tests
# ============================================================================


class TestBooleanFeatures:
    def test_parking(self):
        f = extract_boolean_features("with parking")
        assert f.get("parking") is True

    def test_pooja(self):
        f = extract_boolean_features("pooja room")
        assert f.get("pooja") is True

    def test_office(self):
        f = extract_boolean_features("office room")
        assert f.get("office") is True

    def test_balcony(self):
        f = extract_boolean_features("with balcony")
        assert f.get("balcony") is True

    def test_utility(self):
        f = extract_boolean_features("utility room")
        assert f.get("utility") is True

    def test_vastu(self):
        f = extract_boolean_features("vastu compliant")
        assert f.get("vastu") is True

    def test_accessibility(self):
        f = extract_boolean_features("wheelchair accessible")
        assert f.get("accessibility") is True

    def test_no_features(self):
        f = extract_boolean_features("simple house")
        assert len(f) == 0


# ============================================================================
# Budget Extraction Tests
# ============================================================================


class TestBudgetExtraction:
    def test_lakhs(self):
        amount, unit = extract_budget("50 lakhs")
        assert amount == 5000000.0 and unit == "INR"

    def test_crore(self):
        amount, unit = extract_budget("1.5 crore")
        assert amount == 15000000.0 and unit == "INR"

    def test_usd(self):
        amount, unit = extract_budget("$500000")
        assert amount == 500000.0 and unit == "USD"

    def test_no_budget(self):
        amount, unit = extract_budget("3BHK house")
        assert amount is None


# ============================================================================
# Parking Count Tests
# ============================================================================


class TestParkingCount:
    def test_2_cars(self):
        assert extract_parking_count("2 car parking") == 2

    def test_no_parking(self):
        assert extract_parking_count("3BHK house") is None


# ============================================================================
# Priorities Tests
# ============================================================================


class TestPriorities:
    def test_spacious(self):
        assert "spacious" in extract_priorities("spacious living room")

    def test_ventilated(self):
        assert "ventilated" in extract_priorities("well ventilated")

    def test_natural_light(self):
        assert "natural light" in extract_priorities("good natural light")

    def test_no_priorities(self):
        assert extract_priorities("simple house") == []



# ============================================================================
# RequirementParser Integration Tests
# ============================================================================


class TestRequirementParser:
    def test_full_modern_duplex(self, parser):
        text = "Design a modern east-facing 3BHK duplex on a 40x60 plot with parking and pooja room."
        result = parser.parse(text)

        assert isinstance(result, ParserResult)
        assert isinstance(result.requirements, DesignRequirements)
        assert result.requirements.plot.width == 40.0
        assert result.requirements.plot.length == 60.0
        assert result.requirements.plot.facing == "east"
        assert result.requirements.building.bedrooms == 3
        assert result.requirements.building.duplex is True
        assert result.requirements.building.floors == 2
        assert result.requirements.building.parking is True
        assert result.requirements.building.pooja is True
        assert result.requirements.style == "modern"
        assert result.is_complete is True
        assert result.confidence >= 0.5

    def test_apartment(self, parser):
        text = "2BHK apartment with parking"
        result = parser.parse(text)

        assert result.requirements.building.bedrooms == 2
        assert result.requirements.building.apartment is True
        assert result.requirements.building.floors == 1
        assert result.requirements.building.parking is True

    def test_villa(self, parser):
        text = "5BHK luxury villa with 3 bathrooms and parking for 2 cars"
        result = parser.parse(text)

        assert result.requirements.building.bedrooms == 5
        assert result.requirements.building.villa is True
        assert result.requirements.building.bathrooms == 3
        assert result.requirements.building.parking_count == 2

    def test_vastu_required(self, parser):
        text = "4BHK vastu compliant house with pooja room"
        result = parser.parse(text)

        assert result.requirements.building.vastu_required is True
        assert result.requirements.building.pooja is True
        assert result.requirements.building.bedrooms == 4

    def test_accessibility(self, parser):
        text = "wheelchair accessible 2BHK house"
        result = parser.parse(text)

        assert result.requirements.building.accessibility_required is True
        assert result.requirements.building.bedrooms == 2

    def test_budget_lakhs(self, parser):
        text = "3BHK house budget 50 lakhs"
        result = parser.parse(text)

        assert result.requirements.budget == 5000000.0
        assert result.requirements.budget_unit == "INR"

    def test_budget_crore(self, parser):
        text = "4BHK villa budget 2 crore"
        result = parser.parse(text)

        assert result.requirements.budget == 20000000.0
        assert result.requirements.budget_unit == "INR"

    def test_sqm_plot(self, parser):
        result = parser.parse("250 sqm plot 3BHK house")
        assert result.requirements.plot.area == 250.0

        assert result.requirements.plot.area == 250.0

    def test_sqft_plot(self, parser):
        result = parser.parse("2000 sqft 2BHK house")
        assert result.requirements.plot.area == 2000.0

        assert result.requirements.plot.area == 2000.0

    def test_no_plot_dimensions(self, parser):
        text = "3BHK house"
        result = parser.parse(text)

        assert result.requirements.plot.width is None
        assert result.requirements.plot.length is None

    def test_no_bedrooms(self, parser):
        text = "modern house with parking"
        result = parser.parse(text)

        assert result.requirements.building.bedrooms is None
        assert "building.bedrooms" in result.missing_fields

    def test_bhk_bedroom_mismatch(self, parser):
        text = "3BHK 4 bedroom house"
        result = parser.parse(text)

        assert len(result.warnings) > 0
        assert any("BHK" in w for w in result.warnings)

    def test_default_bathrooms(self, parser):
        text = "3BHK house"
        result = parser.parse(text)

        assert result.requirements.building.bathrooms == 2

    def test_default_floors_house(self, parser):
        text = "3BHK house"
        result = parser.parse(text)

        assert result.requirements.building.floors == 1

    def test_priorities(self, parser):
        text = "spacious ventilated house with natural light"
        result = parser.parse(text)

        assert "spacious" in result.requirements.priorities
        assert "ventilated" in result.requirements.priorities
        assert "natural light" in result.requirements.priorities

    def test_minimalist_style(self, parser):
        text = "minimalist 2BHK apartment"
        result = parser.parse(text)

        assert result.requirements.style == "minimalist"

    def test_contemporary_style(self, parser):
        text = "contemporary 3BHK duplex"
        result = parser.parse(text)

        assert result.requirements.style == "contemporary"

    def test_duplex_floors(self, parser):
        text = "4BHK duplex"
        result = parser.parse(text)

        assert result.requirements.building.duplex is True
        assert result.requirements.building.floors == 2



# ============================================================================
# Serialization Tests
# ============================================================================


class TestSerialization:
    def test_design_requirements_roundtrip(self):
        req = DesignRequirements(
            plot=PlotRequirements(width=40.0, length=60.0, facing="east"),
            building=BuildingRequirements(
                building_type="duplex",
                floors=2,
                bedrooms=3,
                bathrooms=2,
                parking=True,
                pooja=True,
                vastu_required=True,
            ),
            budget=5000000.0,
            budget_unit="INR",
            style="modern",
            priorities=("spacious", "ventilated"),
        )
        d = req.to_dict()
        restored = DesignRequirements.from_dict(d)
        assert restored.plot.width == 40.0
        assert restored.building.bedrooms == 3
        assert restored.style == "modern"
        assert restored.priorities == ("spacious", "ventilated")

    def test_parser_result_roundtrip(self):
        req = DesignRequirements(
            plot=PlotRequirements(width=40.0, length=60.0),
            building=BuildingRequirements(bedrooms=3, floors=1),
        )
        result = ParserResult(
            requirements=req,
            confidence=0.8,
            extracted_fields=("plot.width", "plot.length", "building.bedrooms"),
            missing_fields=(),
            warnings=(),
        )
        d = result.to_dict()
        restored = ParserResult.from_dict(d)
        assert restored.confidence == 0.8
        assert restored.is_complete is True
        assert len(restored.extracted_fields) == 3

    def test_parser_result_incomplete(self):
        req = DesignRequirements()
        result = ParserResult(
            requirements=req,
            confidence=0.2,
            extracted_fields=(),
            missing_fields=("plot dimensions", "building.bedrooms"),
            warnings=("Could not parse plot size",),
        )
        assert result.is_complete is False
        assert len(result.missing_fields) == 2
        assert len(result.warnings) == 1


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    def test_empty_string(self, parser):
        result = parser.parse("")
        assert result.confidence >= 0.0
        assert len(result.missing_fields) > 0

    def test_malformed_input(self, parser):
        result = parser.parse("asdfghjkl")
        assert result.confidence >= 0.0
        assert result.requirements.building.bedrooms is None
        assert result.confidence >= 0.0

    def test_conflicting_facing(self, parser):
        text = "east facing west facing house"
        result = parser.parse(text)
        assert result.requirements.plot.facing is not None

    def test_multiple_bhk_formats(self, parser):
        text = "3 BHK 4 bhk house"
        result = parser.parse(text)
        assert result.requirements.building.bedrooms is not None

    def test_deterministic_repeated_parsing(self, parser):
        text = "3BHK modern duplex 40x60 east facing"
        r1 = parser.parse(text)
        r2 = parser.parse(text)
        assert r1 == r2

    def test_case_insensitivity(self, parser):
        r1 = parser.parse("3BHK MODERN DUPLEX")
        r2 = parser.parse("3bhk modern duplex")
        assert r1.requirements.building.bedrooms == r2.requirements.building.bedrooms
        assert r1.requirements.style == r2.requirements.style

    def test_special_characters(self, parser):
        text = "3BHK house, 40x60 plot, parking!"
        result = parser.parse(text)
        assert result.requirements.plot.width == 40.0
        assert result.requirements.building.parking is True

    def test_very_long_input(self, parser):
        text = " ".join(["3BHK", "modern", "duplex", "parking"] * 100)
        result = parser.parse(text)
        assert result.requirements.building.bedrooms == 3
        assert result.requirements.style == "modern"

    def test_numbers_only(self, parser):
        result = parser.parse("3 4 5")
        assert result.requirements.building.bedrooms is None

    def test_float_plot_dimensions(self, parser):
        text = "30.5 x 45.2 plot"
        result = parser.parse(text)
        assert result.requirements.plot.width == 30.5
        assert result.requirements.plot.length == 45.2

    def test_commercial_office(self, parser):
        result = parser.parse("commercial office space 5000 sqft")
        assert result.requirements.plot.area == 5000.0
        assert result.requirements.building.building_type == "commercial"
        assert result.requirements.plot.area == 5000.0

    def test_all_boolean_features(self, parser):
        text = "house with parking pooja office balcony utility vastu accessibility"
        result = parser.parse(text)
        b = result.requirements.building
        assert b.parking is True
        assert b.pooja is True
        assert b.office is True
        assert b.balcony is True
        assert b.utility is True
        assert b.vastu_required is True
        assert b.accessibility_required is True
