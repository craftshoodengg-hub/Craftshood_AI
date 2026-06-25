from __future__ import annotations

import json
from pathlib import Path

import pytest

from zoning import ZoningClassifier, classify_room_zone
from zoning_exporter import ZoningExporter
from zoning_rules import ZoningRule, ZoningRulesConfig


def test_kitchen_uses_expected_default_rule() -> None:
    result = classify_room_zone("room-1", "Kitchen")

    assert result == {
        "room_id": "room-1",
        "room_name": "Kitchen",
        "zone": "Service",
        "privacy": "Semi-Private",
        "preferred_neighbors": ["Dining", "Utility"],
        "avoid_neighbors": ["Bedroom"],
        "requires_exterior_wall": True,
        "requires_ventilation": True,
        "minimum_area": 60,
        "maximum_area": 180,
    }


def test_alias_and_case_normalization_are_supported() -> None:
    result = classify_room_zone("room-2", "MASTER-BEDROOM")

    assert result["room_name"] == "M.bed room"
    assert result["zone"] == "Private"
    assert result["privacy"] == "Private"


def test_unknown_room_fallback_preserves_input_name() -> None:
    result = classify_room_zone("room-3", "Prayer")

    assert result == {
        "room_id": "room-3",
        "room_name": "Prayer",
        "zone": "Unknown",
        "privacy": "Unknown",
        "preferred_neighbors": [],
        "avoid_neighbors": [],
        "requires_exterior_wall": False,
        "requires_ventilation": False,
        "minimum_area": None,
        "maximum_area": None,
    }


def test_rule_dictionaries_are_configurable() -> None:
    classifier = ZoningClassifier(
        ZoningRulesConfig(
            rules={
                "Utility": ZoningRule(
                    room_name="Utility",
                    zone="Service",
                    privacy="Private",
                    preferred_neighbors=("Kitchen",),
                    avoid_neighbors=("Living",),
                    requires_exterior_wall=True,
                    requires_ventilation=True,
                    minimum_area=30,
                    maximum_area=100,
                )
            },
            aliases={"work area": "Utility"},
        )
    )

    result = classifier.classify("room-4", "Work Area")

    assert result["room_name"] == "Utility"
    assert result["preferred_neighbors"] == ["Kitchen"]
    assert result["minimum_area"] == 30


def test_exporter_writes_single_room_json(tmp_path: Path) -> None:
    output_path = tmp_path / "kitchen-zoning.json"

    json_text = ZoningExporter().export_room("room-1", "Kitchen", output_path)

    payload = json.loads(json_text)
    assert output_path.read_text(encoding="utf-8") == json_text
    assert payload["room_id"] == "room-1"
    assert payload["zone"] == "Service"


def test_exporter_writes_multiple_room_json(tmp_path: Path) -> None:
    output_path = tmp_path / "zoning.json"

    json_text = ZoningExporter().export_rooms(
        [
            {"room_id": "room-1", "room_name": "Kitchen"},
            {"room_id": "room-2", "room_name": "Dining"},
        ],
        output_path,
    )

    payload = json.loads(json_text)
    assert len(payload) == 2
    assert payload[0]["zone"] == "Service"
    assert payload[1]["zone"] == "Public"


def test_empty_room_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="room_id cannot be empty"):
        classify_room_zone("", "Kitchen")
