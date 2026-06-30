"""Unit tests for design request domain model."""
from __future__ import annotations

import pytest

from building_model_v2.pipeline.design_request import DesignRequest


class TestDesignRequest:
    def test_valid_design_request_creation(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=12.5,
            plot_depth=18.0,
            floors=2,
            bedrooms=3,
            bathrooms=2,
            parking=1,
            kitchen_type="open",
            pooja_room=True,
            living_room=True,
            dining_room=True,
            staircase=True,
            orientation="north",
            special_requirements=("garden", "solar"),
        )

        assert request.project_type == "residential"
        assert request.floors == 2
        assert request.bedrooms == 3
        assert request.area() == pytest.approx(225.0)
        assert request.special_requirements == ("garden", "solar")

    @pytest.mark.parametrize(
        "plot_width, plot_depth, floors, bedrooms, bathrooms, expected_message",
        [
            (0.0, 18.0, 1, 0, 0, "plot_width must be positive"),
            (12.0, 0.0, 1, 0, 0, "plot_depth must be positive"),
            (12.0, 18.0, 0, 0, 0, "floors must be at least 1"),
            (12.0, 18.0, 1, -1, 0, "bedrooms must be non-negative"),
            (12.0, 18.0, 1, 0, -1, "bathrooms must be non-negative"),
        ],
    )
    def test_invalid_design_request_validation(
        self,
        plot_width: float,
        plot_depth: float,
        floors: int,
        bedrooms: int,
        bathrooms: int,
        expected_message: str,
    ) -> None:
        with pytest.raises(ValueError, match=expected_message):
            DesignRequest(
                project_type="residential",
                plot_width=plot_width,
                plot_depth=plot_depth,
                floors=floors,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                parking=1,
                kitchen_type="open",
                pooja_room=False,
                living_room=False,
                dining_room=False,
                staircase=False,
                orientation="east",
                special_requirements=(),
            )

    def test_design_request_serialization(self) -> None:
        request = DesignRequest(
            project_type="residential",
            plot_width=10.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=2,
            bathrooms=1,
            parking=1,
            kitchen_type="closed",
            pooja_room=False,
            living_room=True,
            dining_room=False,
            staircase=True,
            orientation="south",
            special_requirements=("balcony",),
        )

        payload = request.to_dict()

        assert payload["project_type"] == "residential"
        assert payload["plot_width"] == 10.0
        assert payload["plot_depth"] == 20.0
        assert payload["special_requirements"] == ["balcony"]

    def test_design_request_deserialization(self) -> None:
        payload = {
            "project_type": "residential",
            "plot_width": 10.0,
            "plot_depth": 20.0,
            "floors": 1,
            "bedrooms": 2,
            "bathrooms": 1,
            "parking": 1,
            "kitchen_type": "closed",
            "pooja_room": False,
            "living_room": True,
            "dining_room": False,
            "staircase": True,
            "orientation": "south",
            "special_requirements": ["balcony"],
        }

        request = DesignRequest.from_dict(payload)

        assert request.project_type == "residential"
        assert request.plot_width == 10.0
        assert request.plot_depth == 20.0
        assert request.special_requirements == ("balcony",)
        assert request.area() == pytest.approx(200.0)

    def test_design_request_area_calculation(self) -> None:
        request = DesignRequest(
            project_type="commercial",
            plot_width=15.0,
            plot_depth=30.0,
            floors=1,
            bedrooms=0,
            bathrooms=2,
            parking=2,
            kitchen_type="pantry",
            pooja_room=False,
            living_room=False,
            dining_room=False,
            staircase=True,
            orientation="west",
            special_requirements=(),
        )

        assert request.area() == pytest.approx(450.0)
