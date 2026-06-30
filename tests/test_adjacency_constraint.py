"""Tests for the AdjacencyConstraint."""
from __future__ import annotations

from building_model_v2.pipeline.constraints.adjacency_constraint import AdjacencyConstraint
from building_model_v2.pipeline.design_request import DesignRequest


class TestAdjacencyConstraint:
    def _make_request(
        self,
        plot_width: float = 30.0,
        plot_depth: float = 40.0,
        bedrooms: int = 2,
        bathrooms: int = 2,
        parking: int = 0,
        floors: int = 1,
        pooja_room: bool = False,
        dining_room: bool = True,
        living_room: bool = True,
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

    def test_valid_residential_request(self) -> None:
        request = self._make_request()
        result = AdjacencyConstraint().validate(request)

        assert result.passed is True
        assert not result.has_errors()

    def test_missing_living_room(self) -> None:
        request = self._make_request(living_room=False)
        result = AdjacencyConstraint().validate(request)

        assert result.passed is False
        assert any("Living room is required" in error for error in result.errors)

    def test_excessive_bathrooms(self) -> None:
        request = self._make_request(bedrooms=2, bathrooms=6)
        result = AdjacencyConstraint().validate(request)

        assert result.passed is False
        assert any("Bathrooms must not exceed" in error for error in result.errors)

    def test_multi_floor_without_staircase(self) -> None:
        request = self._make_request(floors=2, staircase=False)
        result = AdjacencyConstraint().validate(request)

        assert result.passed is False
        assert any("Multi-floor designs require" in error for error in result.errors)

    def test_parking_on_small_plot(self) -> None:
        request = self._make_request(plot_width=15.0, plot_depth=20.0, parking=1)
        result = AdjacencyConstraint().validate(request)

        assert result.passed is True
        assert result.has_warnings()
        assert any("Parking on a small plot" in warning for warning in result.warnings)

    def test_pooja_recommendation(self) -> None:
        request = self._make_request(bedrooms=3, pooja_room=False)
        result = AdjacencyConstraint().validate(request)

        assert result.passed is True
        assert any("pooja room is recommended" in warning for warning in result.warnings)

    def test_dining_room_warning(self) -> None:
        request = self._make_request(dining_room=False)
        result = AdjacencyConstraint().validate(request)

        assert result.passed is True
        assert any("Dining room not requested" in warning for warning in result.warnings)

    def test_passed_warning_error_behavior(self) -> None:
        request = self._make_request(bedrooms=3, bathrooms=7)
        result = AdjacencyConstraint().validate(request)

        assert result.passed is False
        assert result.has_errors() is True
        assert result.has_warnings() is True
