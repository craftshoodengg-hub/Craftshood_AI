from __future__ import annotations

from building_model_v2.pipeline.dwg_knowledge import RoomOpeningAssigner


def _make_room(polygon: list[tuple[float, float]], room_type: str = "Bedroom") -> dict:
    return {
        "room_type": room_type,
        "raw_label": room_type,
        "polygon": polygon,
        "centroid": (0.0, 0.0),
        "area": 0.0,
        "perimeter": 0.0,
        "layer": "Rooms",
    }


def _opening(name: str, position: tuple[float, float], object_type: str, layer: str = "Openings") -> dict:
    return {
        "type": object_type,
        "name": name,
        "position": position,
        "layer": layer,
        "entity_type": "INSERT",
    }


def test_assigns_one_door_to_one_room() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]
    openings = {
        "doors": [_opening("door1", (2.0, 2.0), "Door")],
        "windows": [],
        "door_count": 1,
        "window_count": 0,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert len(result) == 1
    assert result[0]["doors"] == openings["doors"]
    assert result[0]["door_count"] == 1
    assert result[0]["windows"] == []
    assert result[0]["window_count"] == 0


def test_assigns_two_windows_to_one_room() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]
    openings = {
        "doors": [],
        "windows": [
            _opening("window1", (1.0, 1.0), "Window"),
            _opening("window2", (9.0, 9.0), "Window"),
        ],
        "door_count": 0,
        "window_count": 2,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert result[0]["windows"] == openings["windows"]
    assert result[0]["window_count"] == 2


def test_assigns_openings_to_multiple_rooms() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)], "Bedroom"),
        _make_room([(10.0, 0.0), (20.0, 0.0), (20.0, 10.0), (10.0, 10.0)], "Living"),
    ]
    openings = {
        "doors": [
            _opening("door1", (5.0, 5.0), "Door"),
            _opening("door2", (15.0, 5.0), "Door"),
        ],
        "windows": [],
        "door_count": 2,
        "window_count": 0,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert [room["room_type"] for room in result] == ["Bedroom", "Living"]
    assert len(result[0]["doors"]) == 1
    assert len(result[1]["doors"]) == 1
    assert result[0]["doors"][0]["name"] == "door1"
    assert result[1]["doors"][0]["name"] == "door2"


def test_ignores_openings_outside_all_rooms() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]
    openings = {
        "doors": [_opening("door1", (20.0, 20.0), "Door")],
        "windows": [_opening("window1", (-5.0, -5.0), "Window")],
        "door_count": 1,
        "window_count": 1,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert result[0]["doors"] == []
    assert result[0]["windows"] == []
    assert result[0]["door_count"] == 0
    assert result[0]["window_count"] == 0


def test_assigns_opening_exactly_on_boundary() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]
    openings = {
        "doors": [_opening("door1", (10.0, 5.0), "Door")],
        "windows": [],
        "door_count": 1,
        "window_count": 0,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert len(result[0]["doors"]) == 1


def test_handles_tolerance_for_boundary_proximity() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]
    openings = {
        "doors": [_opening("door1", (9.6, 5.0), "Door")],
        "windows": [],
        "door_count": 1,
        "window_count": 0,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert len(result[0]["doors"]) == 1


def test_keeps_empty_rooms_empty() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]
    openings = {
        "doors": [],
        "windows": [],
        "door_count": 0,
        "window_count": 0,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert result[0]["doors"] == []
    assert result[0]["windows"] == []
    assert result[0]["door_count"] == 0
    assert result[0]["window_count"] == 0


def test_handles_empty_openings_payload() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]

    result = RoomOpeningAssigner.assign(rooms, {})

    assert result[0]["doors"] == []
    assert result[0]["windows"] == []
    assert result[0]["door_count"] == 0
    assert result[0]["window_count"] == 0


def test_assigns_multiple_doors_and_windows() -> None:
    rooms = [
        _make_room([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
    ]
    openings = {
        "doors": [
            _opening("door1", (2.0, 2.0), "Door"),
            _opening("door2", (8.0, 8.0), "Door"),
        ],
        "windows": [
            _opening("window1", (2.0, 8.0), "Window"),
            _opening("window2", (8.0, 2.0), "Window"),
        ],
        "door_count": 2,
        "window_count": 2,
    }

    result = RoomOpeningAssigner.assign(rooms, openings)

    assert len(result[0]["doors"]) == 2
    assert len(result[0]["windows"]) == 2
    assert result[0]["door_count"] == 2
    assert result[0]["window_count"] == 2
