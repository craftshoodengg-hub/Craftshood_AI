"""Tests for the BasicVastuRule implementation."""
from __future__ import annotations

from building_model_v2.pipeline.design_request import DesignRequest
from building_model_v2.pipeline.vastu.basic_vastu_rule import BasicVastuRule
from building_model_v2.pipeline.vastu.vastu_result import VastuResult


class TestBasicVastuRule:
    def _make_request(
        self,
        orientation: str = "north",
        kitchen_type: str = "open",
        pooja_room: bool = False,
        bedrooms: int = 2,
        parking: int = 0,
        floors: int = 1,
    ) -> DesignRequest:
        return DesignRequest(
            project_type="residential",
            plot_width=30.0,
            plot_depth=40.0,
            floors=floors,
            bedrooms=bedrooms,
            bathrooms=2,
            parking=parking,
            kitchen_type=kitchen_type,
            pooja_room=pooja_room,
            living_room=True,
            dining_room=True,
            staircase=True,
            orientation=orientation,
            special_requirements=(),
        )

    def test_north_orientation(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(orientation="north"))

        assert isinstance(result, VastuResult)
        assert result.score >= 20.0
        assert result.rule_name == "BasicVastuRule"

    def test_east_orientation(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(orientation="east"))

        assert result.score >= 20.0

    def test_south_orientation(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(orientation="south"))

        assert result.score >= 10.0
        assert result.score <= 20.0

    def test_unknown_orientation(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(orientation="unknown"))

        assert result.has_warnings() is True
        assert any("unknown" in warning.lower() for warning in result.warnings)

    def test_pooja_room_suggestion(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(pooja_room=False, bedrooms=3))

        assert result.has_suggestions() is True
        assert any("pooja room" in suggestion.lower() for suggestion in result.suggestions)

    def test_multi_floor_warning(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(floors=3))

        assert result.has_warnings() is True
        assert any("more than two floors" in warning.lower() for warning in result.warnings)

    def test_score_bounds(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(
            orientation="north",
            kitchen_type="open",
            pooja_room=True,
            bedrooms=1,
            parking=1,
            floors=1,
        ))

        assert 0.0 <= result.score <= 100.0

    def test_warnings_and_suggestions_helpers(self) -> None:
        result = BasicVastuRule().analyze(self._make_request(orientation="unknown", pooja_room=False, bedrooms=3))

        assert result.has_warnings() is True
        assert result.has_suggestions() is True
