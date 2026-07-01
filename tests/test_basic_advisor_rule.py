from __future__ import annotations

from building_model_v2.pipeline.design_advisor import BasicAdvisorRule
from building_model_v2.pipeline.design_request import DesignRequest


def _make_request(**overrides) -> DesignRequest:
    data = {
        "project_type": "residential",
        "plot_width": 30.0,
        "plot_depth": 40.0,
        "floors": 1,
        "bedrooms": 2,
        "bathrooms": 2,
        "parking": 1,
        "kitchen_type": "open",
        "pooja_room": True,
        "living_room": True,
        "dining_room": True,
        "staircase": True,
        "orientation": "north",
    }
    data.update(overrides)
    return DesignRequest(**data)


def test_large_plot_strength() -> None:
    request = _make_request(plot_width=40.0, plot_depth=40.0)
    result = BasicAdvisorRule().analyze(request)

    assert any(advice.category == "plot" for advice in result.advice)
    assert "Large plot provides excellent design flexibility." in result.strengths
    assert result.score == 100.0


def test_small_plot_weakness() -> None:
    request = _make_request(plot_width=20.0, plot_depth=25.0)
    result = BasicAdvisorRule().analyze(request)

    assert any(advice.severity == "warning" for advice in result.advice)
    assert "Small plot limits planning flexibility." in result.weaknesses
    assert result.score == 95.0


def test_parking_strength() -> None:
    request = _make_request(parking=1)
    result = BasicAdvisorRule().analyze(request)

    assert "Dedicated parking improves convenience." in result.strengths
    assert any(advice.category == "parking" for advice in result.advice)


def test_missing_living_room_warning() -> None:
    request = _make_request(living_room=False)
    result = BasicAdvisorRule().analyze(request)

    assert any(advice.category == "living_room" for advice in result.advice)
    assert "Living room not requested." in result.weaknesses
    assert result.score == 95.0


def test_missing_pooja_room_recommendation() -> None:
    request = _make_request(pooja_room=False)
    result = BasicAdvisorRule().analyze(request)

    assert any(advice.category == "pooja_room" for advice in result.advice)
    assert any(advice.severity == "recommendation" for advice in result.advice)
    assert result.score == 97.0


def test_multi_floor_warning() -> None:
    request = _make_request(floors=3)
    result = BasicAdvisorRule().analyze(request)

    assert any(advice.category == "floors" for advice in result.advice)
    assert "Multi-storey designs require careful structural planning." in result.weaknesses
    assert result.score == 95.0


def test_score_calculation_combines_warnings_and_recommendations() -> None:
    request = _make_request(plot_width=20.0, plot_depth=25.0, bedrooms=1, pooja_room=False, floors=3, living_room=False)
    result = BasicAdvisorRule().analyze(request)

    expected_warnings = 3
    expected_recommendations = 2
    assert result.score == 100 - expected_warnings * 5 - expected_recommendations * 3
    assert result.score == 79.0
    assert result.advice_count() == expected_warnings + expected_recommendations + 1
