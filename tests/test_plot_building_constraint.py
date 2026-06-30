"""Tests for the PlotBuildingConstraint."""
from __future__ import annotations

from building_model_v2.pipeline.constraints.plot_building_constraint import PlotBuildingConstraint
from building_model_v2.pipeline.design_request import DesignRequest


class TestPlotBuildingConstraint:
    def _make_request(
        self,
        plot_width: float = 30.0,
        plot_depth: float = 40.0,
        bedrooms: int = 2,
        bathrooms: int = 2,
        parking: int = 0,
        floors: int = 1,
        pooja_room: bool = False,
        living_room: bool = True,
        dining_room: bool = True,
        staircase: bool = True,
    ) -> DesignRequest:
        return DesignRequest(
            project_type="residential",
            plot_width=plot_width,
            plot_depth=plot_depth,
            floors=floors,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking=parking,
            kitchen_type="open",
            pooja_room=pooja_room,
            living_room=living_room,
            dining_room=dining_room,
            staircase=staircase,
            orientation="north",
            special_requirements=(),
        )

    def test_valid_30x40_residential_request(self) -> None:
        request = self._make_request(plot_width=30.0, plot_depth=40.0, bedrooms=2, bathrooms=2)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is True
        assert result.has_errors() is False

    def test_plot_width_too_small(self) -> None:
        request = self._make_request(plot_width=9.0, plot_depth=40.0)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is False
        assert any("Plot width must be at least 10 ft" in error for error in result.errors)

    def test_plot_depth_too_small(self) -> None:
        request = self._make_request(plot_width=30.0, plot_depth=9.0)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is False
        assert any("Plot depth must be at least 10 ft" in error for error in result.errors)

    def test_plot_area_too_small(self) -> None:
        request = self._make_request(plot_width=15.0, plot_depth=19.0)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is False
        assert any("Plot area must be at least 300 sq ft" in error for error in result.errors)

    def test_setback_warnings(self) -> None:
        request = self._make_request(plot_width=18.0, plot_depth=28.0, floors=2, bedrooms=1, bathrooms=1)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is True
        assert result.has_warnings() is True
        assert any("limit side setbacks" in warning for warning in result.warnings)
        assert any("limit front/rear setbacks" in warning for warning in result.warnings)

    def test_coverage_warning(self) -> None:
        request = self._make_request(
            plot_width=20.0,
            plot_depth=40.0,
            bedrooms=4,
            bathrooms=3,
            parking=1,
            floors=2,
        )
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is True
        assert result.has_warnings() is True
        assert any("exceeds 60% of plot coverage" in warning for warning in result.warnings)

    def test_coverage_error(self) -> None:
        request = self._make_request(
            plot_width=20.0,
            plot_depth=30.0,
            bedrooms=4,
            bathrooms=4,
            parking=1,
            floors=1,
        )
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is False
        assert any("exceeds 70% of plot coverage" in error for error in result.errors)

    def test_residential_high_floor_warning(self) -> None:
        request = self._make_request(plot_width=30.0, plot_depth=40.0, floors=4)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is True
        assert any("Residential designs with more than 3 floors" in warning for warning in result.warnings)

    def test_parking_width_depth_warnings(self) -> None:
        request = self._make_request(plot_width=17.0, plot_depth=24.0, parking=1, floors=3)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is True
        assert any("narrower than 18 ft" in warning for warning in result.warnings)
        assert any("shallower than 25 ft" in warning for warning in result.warnings)

    def test_passed_flag_behavior(self) -> None:
        request = self._make_request(plot_width=30.0, plot_depth=40.0, bedrooms=1, bathrooms=1)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is True
        assert result.has_errors() is False

        request = self._make_request(plot_width=9.0, plot_depth=9.0)
        result = PlotBuildingConstraint().validate(request)

        assert result.passed is False
        assert result.has_errors() is True
