"""Tests for the room label detector helper."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import RoomLabelDetector, normalize_label


def _create_dxf_with_labels(path: Path, labels: list[tuple[str, str, tuple[float, float], str]]) -> None:
    document = ezdxf.new()
    modelspace = document.modelspace()
    for text, entity_type, insert, layer in labels:
        if entity_type == "TEXT":
            modelspace.add_text(text, dxfattribs={"insert": insert, "layer": layer})
        else:
            modelspace.add_mtext(text, dxfattribs={"insert": insert, "layer": layer})
    document.saveas(path)


def test_normalize_label_known_room_types() -> None:
    assert normalize_label("Bed") == "Bedroom"
    assert normalize_label("M.Bed room") == "Bedroom"
    assert normalize_label("Kitchen / Dining") == "Kitchen"
    assert normalize_label("Living/Dining") == "Living"
    assert normalize_label("Hall") == "Living"
    assert normalize_label("Dining") == "Dining"
    assert normalize_label("W.C") == "Toilet"
    assert normalize_label("Pooja Shelf") == "Pooja"
    assert normalize_label("Covered Balcony") == "Balcony"
    assert normalize_label("Wash") == "Utility"
    assert normalize_label("Portico") == "Parking"
    assert normalize_label("DN") == "Stair"
    assert normalize_label("Shelf") == "Store"


def test_detect_labels_from_dxf_text_and_mtext(tmp_path: Path) -> None:
    path = tmp_path / "labels.dxf"
    labels = [
        ("Bed room", "TEXT", (1, 1), "A-ROOM"),
        ("Kitchen", "MTEXT", (2, 2), "A-ROOM"),
        ("Living/Dining", "TEXT", (3, 3), "A-ROOM"),
        ("Toilet", "TEXT", (4, 4), "A-TOILET"),
        ("Pooja", "MTEXT", (5, 5), "A-ROOM"),
        ("Covered Balcony", "TEXT", (6, 6), "A-BALCONY"),
        ("Wash", "TEXT", (7, 7), "A-UTILITY"),
        ("Car Parking", "MTEXT", (8, 8), "A-PARKING"),
        ("Staircase", "TEXT", (9, 9), "A-STAIR"),
    ]
    _create_dxf_with_labels(path, labels)

    document = ezdxf.readfile(str(path))
    detections = RoomLabelDetector.detect(document)

    assert len(detections) == 9
    expected = {
        "Bed room": "Bedroom",
        "Kitchen": "Kitchen",
        "Living/Dining": "Living",
        "Toilet": "Toilet",
        "Pooja": "Pooja",
        "Covered Balcony": "Balcony",
        "Wash": "Utility",
        "Car Parking": "Parking",
        "Staircase": "Stair",
    }
    for detection in detections:
        assert detection["raw_label"] in expected
        assert detection["room_type"] == expected[detection["raw_label"]]
        assert detection["position"] in {(1.0, 1.0), (2.0, 2.0), (3.0, 3.0), (4.0, 4.0), (5.0, 5.0), (6.0, 6.0), (7.0, 7.0), (8.0, 8.0), (9.0, 9.0)}
        assert detection["layer"].startswith("A-")
        assert detection["entity_type"] in {"TEXT", "MTEXT"}


def test_detect_ignores_dimensions_and_title_text(tmp_path: Path) -> None:
    path = tmp_path / "ignored.dxf"
    labels = [
        ("10'0\"x10'0\"", "TEXT", (1, 1), "A-DIM"),
        ("ROAD", "TEXT", (2, 2), "A-ANNO"),
        ("PROJECT: Demo", "MTEXT", (3, 3), "A-TITLE"),
        ("Company Name", "TEXT", (4, 4), "A-TITLE"),
        ("", "TEXT", (5, 5), "A-EMPTY"),
        ("Bedroom", "TEXT", (6, 6), "A-ROOM"),
    ]
    _create_dxf_with_labels(path, labels)

    document = ezdxf.readfile(str(path))
    detections = RoomLabelDetector.detect(document)

    assert len(detections) == 1
    assert detections[0]["raw_label"] == "Bedroom"
    assert detections[0]["room_type"] == "Bedroom"
    assert detections[0]["layer"] == "A-ROOM"
    assert detections[0]["position"] == (6.0, 6.0)
