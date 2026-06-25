from __future__ import annotations

import pytest
from shapely.geometry import Point, Polygon

from adjacency import AdjacencyBuilder, RoomPolygon
from connectivity import (
    ConnectivityBuilder,
    ConnectivityConfig,
    DoorPoint,
    build_connectivity_graph,
)


def test_rooms_connect_only_when_adjacent_and_door_lies_on_shared_boundary() -> None:
    rooms = _rooms()
    adjacency_graph = AdjacencyBuilder().build(rooms)
    doors = [DoorPoint("door-1", Point(10, 5))]

    graph = ConnectivityBuilder().build(rooms, adjacency_graph, doors)

    assert graph == [
        {
            "room_id": "living",
            "connected_rooms": [{"room_id": "kitchen", "door_id": "door-1"}],
        },
        {
            "room_id": "kitchen",
            "connected_rooms": [{"room_id": "living", "door_id": "door-1"}],
        },
        {"room_id": "bed", "connected_rooms": []},
    ]


def test_adjacent_rooms_without_door_are_not_connected() -> None:
    rooms = _rooms()[:2]
    adjacency_graph = AdjacencyBuilder().build(rooms)

    graph = ConnectivityBuilder().build(rooms, adjacency_graph, [])

    assert graph == [
        {"room_id": "living", "connected_rooms": []},
        {"room_id": "kitchen", "connected_rooms": []},
    ]


def test_door_distance_tolerance_is_configurable() -> None:
    rooms = _rooms()[:2]
    adjacency_graph = AdjacencyBuilder().build(rooms)
    doors = [DoorPoint("door-offset", Point(10.02, 5))]

    strict_graph = ConnectivityBuilder(
        ConnectivityConfig(door_distance_tolerance=0.01)
    ).build(rooms, adjacency_graph, doors)
    tolerant_graph = ConnectivityBuilder(
        ConnectivityConfig(door_distance_tolerance=0.03)
    ).build(rooms, adjacency_graph, doors)

    assert strict_graph[0]["connected_rooms"] == []
    assert tolerant_graph[0]["connected_rooms"] == [
        {"room_id": "kitchen", "door_id": "door-offset"}
    ]


def test_non_adjacent_rooms_do_not_connect_even_when_door_point_touches_a_room() -> None:
    rooms = _rooms()
    adjacency_graph = [
        {"room_id": "living", "adjacent_rooms": []},
        {"room_id": "kitchen", "adjacent_rooms": []},
        {"room_id": "bed", "adjacent_rooms": []},
    ]
    doors = [DoorPoint("door-1", Point(10, 5))]

    graph = build_connectivity_graph(rooms, adjacency_graph, doors)

    assert all(record["connected_rooms"] == [] for record in graph)


def test_unknown_adjacency_room_id_is_rejected() -> None:
    rooms = _rooms()[:1]
    adjacency_graph = [{"room_id": "living", "adjacent_rooms": ["missing"]}]

    with pytest.raises(ValueError, match="unknown room_id"):
        ConnectivityBuilder().build(rooms, adjacency_graph, [])


def test_duplicate_door_ids_are_rejected() -> None:
    rooms = _rooms()[:2]
    adjacency_graph = AdjacencyBuilder().build(rooms)
    doors = [DoorPoint("door-1", Point(10, 5)), DoorPoint("door-1", Point(10, 6))]

    with pytest.raises(ValueError, match="Duplicate door_id"):
        ConnectivityBuilder().build(rooms, adjacency_graph, doors)


def _rooms() -> list[RoomPolygon]:
    return [
        RoomPolygon("living", "Living", _box(0, 0, 10, 10)),
        RoomPolygon("kitchen", "Kitchen", _box(10, 0, 20, 10)),
        RoomPolygon("bed", "Bed room", _box(30, 0, 40, 10)),
    ]


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
