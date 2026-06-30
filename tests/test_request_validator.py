"""Tests for the RequestValidator."""
from __future__ import annotations

from building_model_v2.pipeline.request_validator import RequestValidator
from building_model_v2.pipeline.design_request import DesignRequest


class TestRequestValidator:
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

    def test_all_constraints_registered(self) -> None:
        validator = RequestValidator()

        results = validator.validate(self._make_request())
        names = {result.constraint_name for result in results}

        assert "SpaceSizeConstraint" in names
        assert "AdjacencyConstraint" in names
        assert "PlotBuildingConstraint" in names
        assert len(results) == 3

    def test_valid_request_has_no_errors(self) -> None:
        validator = RequestValidator()
        request = self._make_request(plot_width=30.0, plot_depth=40.0, bedrooms=2, bathrooms=2)

        results = validator.validate(request)

        assert validator.has_errors(results) is False
        assert validator.has_warnings(results) is False
        assert all(result.passed for result in results)

    def test_invalid_request_returns_errors(self) -> None:
        validator = RequestValidator()
        request = self._make_request(plot_width=8.0, plot_depth=9.0, bedrooms=3, bathrooms=6, staircase=False)

        results = validator.validate(request)

        assert validator.has_errors(results) is True
        assert any(result.errors for result in results)
        assert any("Plot width must be at least 10 ft" in error for error in validator.errors(results))

    def test_warning_request_returns_warnings(self) -> None:
        validator = RequestValidator()
        request = self._make_request(plot_width=18.0, plot_depth=28.0, bedrooms=1, bathrooms=1, parking=0, floors=2)

        results = validator.validate(request)

        assert validator.has_warnings(results) is True
        assert validator.has_errors(results) is False
        assert any("side setbacks" in warning for warning in validator.warnings(results))

    def test_helper_methods_work(self) -> None:
        validator = RequestValidator()
        request = self._make_request(plot_width=30.0, plot_depth=40.0, bedrooms=3, bathrooms=4, parking=1)

        results = validator.validate(request)

        assert isinstance(validator.errors(results), list)
        assert isinstance(validator.warnings(results), list)
        assert len(validator.errors(results)) >= 0
        assert len(validator.warnings(results)) >= 0

    def test_results_include_all_constraint_names(self) -> None:
        validator = RequestValidator()
        request = self._make_request(plot_width=30.0, plot_depth=40.0)

        results = validator.validate(request)
        names = [result.constraint_name for result in results]

        assert names == ["SpaceSizeConstraint", "AdjacencyConstraint", "PlotBuildingConstraint"]
