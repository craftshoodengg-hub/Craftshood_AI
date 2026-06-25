from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from adjacency import (
    AdjacencyBuilder,
    AdjacencyConfig,
    RoomPolygon,
    build_adjacency_graph_from_values,
    shared_boundary_length,
)


def test_adjacent_rooms_share_boundary_length() -> None:
    rooms = [
        RoomPolygon("living", "Living", _box(0, 0, 10, 10)),
        RoomPolygon("kitchen", "Kitchen", _box(10, 0, 20, 10)),
        RoomPolygon("toilet", "Toilet", _box(20, 0, 25, 5)),
    ]

    graph = AdjacencyBuilder().build(rooms)

    living = graph[0]
    kitchen = graph[1]
    assert living["adjacent_rooms"] == ["kitchen"]
    assert living["shared_boundary_length"] == {"kitchen": 10.0}
    assert set(kitchen["adjacent_rooms"]) == {"living", "toilet"}
    assert kitchen["shared_boundary_length"]["living"] == 10.0
    assert kitchen["shared_boundary_length"]["toilet"] == 5.0


def test_corner_only_touching_is_ignored() -> None:
    rooms = [
        RoomPolygon("living", "Living", _box(0, 0, 10, 10)),
        RoomPolygon("bed", "Bed room", _box(10, 10, 20, 20)),
    ]

    graph = AdjacencyBuilder().build(rooms)

    assert graph[0]["adjacent_rooms"] == []
    assert graph[1]["shared_boundary_length"] == {}


def test_minimum_shared_wall_length_filters_short_boundaries() -> None:
    rooms = [
        RoomPolygon("kitchen", "Kitchen", _box(0, 0, 10, 10)),
        RoomPolygon("toilet", "Toilet", _box(10, 0, 15, 4)),
    ]

    graph = AdjacencyBuilder(
        AdjacencyConfig(minimum_shared_wall_length=5.0)
    ).build(rooms)

    assert graph == [
        {
            "room_id": "kitchen",
            "room_name": "Kitchen",
            "adjacent_rooms": [],
            "shared_boundary_length": {},
        },
        {
            "room_id": "toilet",
            "room_name": "Toilet",
            "adjacent_rooms": [],
            "shared_boundary_length": {},
        },
    ]


def test_parallel_value_inputs_are_supported() -> None:
    graph = build_adjacency_graph_from_values(
        ["living", "dining"],
        ["Living", "Dining"],
        [_box(0, 0, 10, 10), _box(0, 10, 10, 20)],
    )

    assert graph[0]["room_id"] == "living"
    assert graph[0]["adjacent_rooms"] == ["dining"]
    assert graph[0]["shared_boundary_length"]["dining"] == 10.0


def test_shared_boundary_length_uses_only_linear_intersection() -> None:
    assert shared_boundary_length(_box(0, 0, 10, 10), _box(10, 10, 20, 20)) == 0
    assert shared_boundary_length(_box(0, 0, 10, 10), _box(10, 0, 20, 10)) == 10


def test_duplicate_room_ids_are_rejected() -> None:
    rooms = [
        RoomPolygon("living", "Living", _box(0, 0, 10, 10)),
        RoomPolygon("living", "Kitchen", _box(10, 0, 20, 10)),
    ]

    with pytest.raises(ValueError, match="Duplicate room_id"):
        AdjacencyBuilder().build(rooms)


def _box(min_x: float, min_y: float, max_x: float, max_y: float) -> Polygon:
    return Polygon(
        [
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
            (min_x, min_y),
        ]
    )
