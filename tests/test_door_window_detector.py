"""Tests for the DoorWindowDetector DXF-based detection helper."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import DoorWindowDetector


def _create_dxf_with_entities(path: Path) -> ezdxf.DXFDocument:
    document = ezdxf.new()
    document.saveas(path)
    return document


def test_detect_single_and_double_doors_by_block_and_layer(tmp_path: Path) -> None:
    path = tmp_path / "doors.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    document.blocks.new("DOOR_SINGLE")
    document.blocks.new("DOOR_DOUBLE")
    modelspace.add_blockref("DOOR_SINGLE", insert=(1, 1), dxfattribs={"layer": "A-DOOR"})
    modelspace.add_blockref("DOOR_DOUBLE", insert=(2, 2), dxfattribs={"layer": "A-DOUBLE_DOOR"})
    modelspace.add_blockref("UNKNOWN", insert=(3, 3), dxfattribs={"layer": "A-FURNITURE"})
    document.saveas(path)

    detector = DoorWindowDetector()
    results = detector.detect(document)

    assert results["door_count"] == 2
    assert results["window_count"] == 0
    names = {door["name"] for door in results["doors"]}
    assert "DOOR_SINGLE" in names
    assert "DOOR_DOUBLE" in names
    assert results["doors"][0]["position"] in {(1.0, 1.0), (2.0, 2.0)}


def test_detect_main_door_and_entrance_by_text(tmp_path: Path) -> None:
    path = tmp_path / "entrances.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    modelspace.add_text("Main Door", dxfattribs={"insert": (5, 5), "layer": "A-ANNO"})
    modelspace.add_text("Entrance", dxfattribs={"insert": (6, 6), "layer": "A-ANNO"})
    document.saveas(path)

    detector = DoorWindowDetector()
    results = detector.detect(document)

    assert results["door_count"] == 2
    assert {door["name"] for door in results["doors"]} == {"Main Door", "Entrance"}
    assert all(door["entity_type"] == "TEXT" for door in results["doors"])


def test_detect_windows_and_ventilators_by_block_layer_and_text(tmp_path: Path) -> None:
    path = tmp_path / "windows.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    document.blocks.new("W1")
    document.blocks.new("VENTILATOR")
    modelspace.add_blockref("W1", insert=(10, 10), dxfattribs={"layer": "A-WINDOW"})
    modelspace.add_blockref("VENTILATOR", insert=(11, 11), dxfattribs={"layer": "A-VENT"})
    modelspace.add_text("Window", dxfattribs={"insert": (12, 12), "layer": "A-ANNO"})
    document.saveas(path)

    detector = DoorWindowDetector()
    results = detector.detect(document)

    assert results["window_count"] == 3
    assert {window["name"] for window in results["windows"]} == {"W1", "VENTILATOR", "Window"}
    assert results["windows"][0]["position"] in {(10.0, 10.0), (11.0, 11.0), (12.0, 12.0)}


def test_detect_ignores_unrelated_blocks_and_room_labels(tmp_path: Path) -> None:
    path = tmp_path / "ignored.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    document.blocks.new("SOFA")
    modelspace.add_blockref("SOFA", insert=(15, 15), dxfattribs={"layer": "A-FURNITURE"})
    modelspace.add_text("Bedroom", dxfattribs={"insert": (16, 16), "layer": "A-ROOM"})
    modelspace.add_text("Doorbell", dxfattribs={"insert": (17, 17), "layer": "A-ANNO"})
    document.saveas(path)

    detector = DoorWindowDetector()
    results = detector.detect(document)

    assert results["door_count"] == 0
    assert results["window_count"] == 0


def test_detect_by_layer_name(tmp_path: Path) -> None:
    path = tmp_path / "layer.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    document.blocks.new("TABLE")
    modelspace.add_blockref("TABLE", insert=(20, 20), dxfattribs={"layer": "DOOR_LAYER"})
    modelspace.add_blockref("TABLE", insert=(21, 21), dxfattribs={"layer": "WINDOW_LAYER"})
    document.saveas(path)

    detector = DoorWindowDetector()
    results = detector.detect(document)

    assert results["door_count"] == 1
    assert results["window_count"] == 1
    assert any(door["layer"] == "DOOR_LAYER" for door in results["doors"])
    assert any(window["layer"] == "WINDOW_LAYER" for window in results["windows"])


def test_detect_by_block_name_and_position(tmp_path: Path) -> None:
    path = tmp_path / "position.dxf"
    document = ezdxf.new()
    modelspace = document.modelspace()
    document.blocks.new("D2")
    modelspace.add_blockref("D2", insert=(30, 30), dxfattribs={"layer": "A-DOOR"})
    document.saveas(path)

    detector = DoorWindowDetector()
    results = detector.detect(document)

    assert results["door_count"] == 1
    assert results["doors"][0]["position"] == (30.0, 30.0)
    assert results["doors"][0]["name"] == "D2"
    assert results["doors"][0]["entity_type"] == "INSERT"
