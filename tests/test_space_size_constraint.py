"""Tests for the SpaceSizeConstraint."""
from __future__ import annotations

from building_model_v2.pipeline.constraints.space_size_constraint import SpaceSizeConstraint
from building_model_v2.pipeline.design_request import DesignRequest


class TestSpaceSizeConstraint:
    def _make_request(
        self,
        plot_width: float = 30.0,
        plot_depth: float = 40.0,
        bedrooms: int = 2,
        bathrooms: int = 2,
        parking: int = 0,
        floors: int = 1,
        living_room: bool = True,
        kitchen_type: str = "open",
    ) -> DesignRequest:
        return DesignRequest(
            project_type="residential",
            plot_width=plot_width,
            plot_depth=plot_depth,
            floors=floors,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking=parking,
            kitchen_type=kitchen_type,
            pooja_room=False,
            living_room=living_room,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

    def test_valid_2bhk_30x40_plot(self) -> None:
        request = self._make_request(plot_width=30.0, plot_depth=40.0, bedrooms=2, bathrooms=2)
        result = SpaceSizeConstraint().validate(request)

        assert result.passed is True
        assert result.has_errors() is False

    def test_plot_too_small(self) -> None:
        request = self._make_request(plot_width=10.0, plot_depth=10.0)
        result = SpaceSizeConstraint().validate(request)

        assert result.passed is False
        assert "Plot area must be at least 300 square units" in result.errors

    def test_too_many_bedrooms_for_plot(self) -> None:
        request = self._make_request(plot_width=15.0, plot_depth=20.0, bedrooms=4, bathrooms=2)
        result = SpaceSizeConstraint().validate(request)

        assert result.passed is False
        assert any("Too many bedrooms" in error for error in result.errors)

    def test_parking_warning_tight_layout(self) -> None:
        request = self._make_request(plot_width=25.0, plot_depth=30.0, bedrooms=2, bathrooms=2, parking=1)
        result = SpaceSizeConstraint().validate(request)

        assert result.passed is True
        assert result.has_warnings() is True
        assert any("Parking requirement" in warning or "tight" in warning for warning in result.warnings)

    def test_bathroom_area_estimation(self) -> None:
        request = self._make_request(plot_width=18.0, plot_depth=20.0, bedrooms=2, bathrooms=3)
        result = SpaceSizeConstraint().validate(request)

        assert result.passed is False
        assert any("Estimated required area exceeds" in error for error in result.errors)

    def test_passed_flag_behavior(self) -> None:
        request = self._make_request(plot_width=30.0, plot_depth=40.0, bedrooms=2, bathrooms=2)
        result = SpaceSizeConstraint().validate(request)

        assert result.passed is True
        assert result.has_errors() is False

        request = self._make_request(plot_width=10.0, plot_depth=10.0)
        result = SpaceSizeConstraint().validate(request)

        assert result.passed is False
        assert result.has_errors() is True

    def test_warnings_vs_errors(self) -> None:
        request = self._make_request(plot_width=25.0, plot_depth=30.0, bedrooms=2, bathrooms=2, parking=1)
        result = SpaceSizeConstraint().validate(request)

        assert result.has_errors() is False
        assert result.has_warnings() is True
