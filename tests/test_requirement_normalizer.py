"""Tests for RequirementNormalizer normalization and validation."""
from __future__ import annotations

import pytest

from building_model_v2.pipeline.design_request import DesignRequest
from building_model_v2.pipeline.requirement_normalizer import RequirementNormalizer


def _make_invalid_design_request(**payload) -> DesignRequest:
    request = object.__new__(DesignRequest)
    for key, value in payload.items():
        object.__setattr__(request, key, value)
    return request


class TestRequirementNormalizer:
    def test_project_type_normalization_apartment(self) -> None:
        request = DesignRequest(
            project_type="apartment",
            plot_width=30.0,
            plot_depth=40.0,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.project_type == "residential"

    def test_project_type_normalization_office(self) -> None:
        request = DesignRequest(
            project_type="office",
            plot_width=20.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=0,
            bathrooms=1,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=False,
            dining_room=False,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.project_type == "commercial"

    def test_kitchen_type_normalization_modular(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=25.0,
            plot_depth=25.0,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=0,
            kitchen_type="modular kitchen",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.kitchen_type == "modular"

    def test_orientation_normalization(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north-east",
            special_requirements=(),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.orientation == "north"

    def test_inferred_bathrooms_from_zero(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=3,
            bathrooms=0,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.bathrooms == 3

    def test_duplex_floor_normalization(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=30.0,
            plot_depth=40.0,
            floors=1,
            bedrooms=3,
            bathrooms=3,
            parking=1,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=("duplex",),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.floors == 2

    def test_g_plus_two_floor_normalization(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=30.0,
            plot_depth=40.0,
            floors=1,
            bedrooms=3,
            bathrooms=3,
            parking=1,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=("g+2",),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.floors == 3

    def test_parking_keyword_normalization(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=("garage",),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.parking == 1

    def test_invalid_plot_dimensions(self) -> None:
        request = _make_invalid_design_request(
            project_type="residential",
            plot_width=0.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        with pytest.raises(ValueError, match="plot dimensions must be greater than 0"):
            RequirementNormalizer.normalize(request)

    def test_invalid_bedrooms_too_many(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=21,
            bathrooms=2,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        with pytest.raises(ValueError, match="bedrooms must be 20 or fewer"):
            RequirementNormalizer.normalize(request)

    def test_invalid_bathrooms_too_many(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=2,
            bathrooms=6,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        with pytest.raises(ValueError, match="bathrooms must be at most bedrooms \\+ 3"):
            RequirementNormalizer.normalize(request)

    def test_invalid_floors_too_many(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=11,
            bedrooms=2,
            bathrooms=2,
            parking=0,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

        with pytest.raises(ValueError, match="floors must be 10 or fewer"):
            RequirementNormalizer.normalize(request)

    def test_boundary_values(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=10,
            bedrooms=20,
            bathrooms=23,
            parking=2,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=True,
            orientation="west",
            special_requirements=(),
        )

        normalized = RequirementNormalizer.normalize(request)
        assert normalized.floors == 10
        assert normalized.bedrooms == 20
        assert normalized.bathrooms == 23
