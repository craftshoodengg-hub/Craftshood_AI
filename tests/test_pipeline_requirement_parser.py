"""Tests for the pipeline natural language requirement parser."""
from __future__ import annotations

from building_model_v2.pipeline.requirement_parser import RequirementParser


class TestPipelineRequirementParser:
    def test_parse_1_bhk(self) -> None:
        request = RequirementParser.parse("I need a 1 BHK apartment with open kitchen and north facing plot.")

        assert request.bedrooms == 1
        assert request.bathrooms == 1
        assert request.kitchen_type == "open"
        assert request.orientation == "north"
        assert request.project_type == "residential"

    def test_parse_2_bhk(self) -> None:
        request = RequirementParser.parse("Looking for a 2 BHK home with 2 bathrooms and a dining room.")

        assert request.bedrooms == 2
        assert request.bathrooms == 2
        assert request.dining_room is True

    def test_parse_duplex(self) -> None:
        request = RequirementParser.parse("Duplex residence with 3 bedrooms and 3 bathrooms on a 40x30 plot.")

        assert request.floors == 2
        assert request.plot_width == 40.0
        assert request.plot_depth == 30.0
        assert request.project_type == "residential"

    def test_parse_g_plus_one(self) -> None:
        request = RequirementParser.parse("G+1 villa with 4 bedrooms, modern interiors, and a closed kitchen.")

        assert request.floors == 2
        assert request.bedrooms == 4
        assert request.kitchen_type == "closed"
        assert "modern" in request.special_requirements

    def test_parse_plot_size_variants(self) -> None:
        request = RequirementParser.parse("A 30 by 40 plot with luxury feel and east orientation.")

        assert request.plot_width == 30.0
        assert request.plot_depth == 40.0
        assert request.orientation == "east"
        assert "luxury" in request.special_requirements

    def test_parse_orientation(self) -> None:
        request = RequirementParser.parse("South facing bungalow with 3 bedrooms.")

        assert request.orientation == "south"

    def test_parse_parking(self) -> None:
        request = RequirementParser.parse("3 car parking, 2 BHK with a pooja room.")

        assert request.parking == 3
        assert request.pooja_room is True

    def test_parse_pooja_room(self) -> None:
        request = RequirementParser.parse("Residential plan must include a pooja room and a dining area.")

        assert request.pooja_room is True
        assert request.dining_room is True

    def test_parse_kitchen_type(self) -> None:
        request = RequirementParser.parse("I want a closed kitchen in a 2 BHK house.")

        assert request.kitchen_type == "closed"

    def test_parse_descriptive_keywords(self) -> None:
        request = RequirementParser.parse("Minimalist and contemporary home design with a balcony.")

        assert request.special_requirements == ("minimalist", "contemporary")

    def test_parse_incomplete_prompt_defaults(self) -> None:
        request = RequirementParser.parse("Need a small home.")

        assert request.plot_width == 10.0
        assert request.plot_depth == 10.0
        assert request.bedrooms == 1
        assert request.bathrooms == 1
        assert request.floors == 1
        assert request.kitchen_type == "open"
        assert request.orientation == "north"
        assert request.project_type == "residential"
