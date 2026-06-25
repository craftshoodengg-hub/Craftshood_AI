from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from confidence import (
    ConfidenceConfig,
    ConfidenceScorer,
    ConfidenceWeights,
    RoomMetadata,
    calculate_confidence,
    quality_for_score,
)


def test_confidence_scores_all_available_signals_as_excellent() -> None:
    result = calculate_confidence(
        _box(),
        {"room_id": "living", "adjacent_rooms": ["kitchen"], "shared_boundary_length": {"kitchen": 10}},
        {"room_id": "living", "connected_rooms": [{"room_id": "kitchen", "door_id": "door-1"}]},
        {"road_side": "North", "front_wall_id": "north-wall", "front_rooms": ["living"]},
        RoomMetadata(room_id="living", room_name="Living"),
    )

    assert result == {
        "room_id": "living",
        "confidence": 1.0,
        "quality": "Excellent",
        "breakdown": {
            "closed_polygon": True,
            "valid_geometry": True,
            "known_room_name": True,
            "adjacency_available": True,
            "connectivity_available": True,
            "facing_available": True,
        },
    }


def test_missing_context_lowers_confidence_and_quality() -> None:
    result = calculate_confidence(
        _box(),
        None,
        {"room_id": "bed", "connected_rooms": []},
        {"road_side": "Unknown", "front_wall_id": None, "front_rooms": []},
        {"room_id": "bed", "room_name": "Garage"},
    )

    assert result["confidence"] == 0.45
    assert result["quality"] == "Poor"
    assert result["breakdown"] == {
        "closed_polygon": True,
        "valid_geometry": True,
        "known_room_name": False,
        "adjacency_available": False,
        "connectivity_available": False,
        "facing_available": False,
    }


def test_invalid_geometry_is_reflected_in_breakdown() -> None:
    bowtie = Polygon([(0, 0), (10, 10), (10, 0), (0, 10), (0, 0)])

    result = calculate_confidence(
        bowtie,
        {"room_id": "living", "adjacent_rooms": ["kitchen"]},
        None,
        None,
        RoomMetadata("living", "Living"),
    )

    assert result["breakdown"]["closed_polygon"] is True
    assert result["breakdown"]["valid_geometry"] is False
    assert result["confidence"] == 0.5
    assert result["quality"] == "Fair"


def test_custom_weights_are_normalized() -> None:
    scorer = ConfidenceScorer(
        ConfidenceConfig(
            weights=ConfidenceWeights(
                closed_polygon=1,
                valid_geometry=1,
                known_room_name=0,
                adjacency_available=0,
                connectivity_available=0,
                facing_available=0,
            ),
            score_precision=3,
        )
    )

    result = scorer.score(
        _box(),
        None,
        None,
        None,
        RoomMetadata("living", "Unknown"),
    )

    assert result["confidence"] == 1.0
    assert result["breakdown"]["known_room_name"] is False


def test_empty_room_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="room_id cannot be empty"):
        calculate_confidence(_box(), None, None, None, {"room_id": "", "room_name": "Living"})


def test_quality_thresholds() -> None:
    assert quality_for_score(0.96).value == "Excellent"
    assert quality_for_score(0.80).value == "Good"
    assert quality_for_score(0.55).value == "Fair"
    assert quality_for_score(0.20).value == "Poor"


def _box() -> Polygon:
    return Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
