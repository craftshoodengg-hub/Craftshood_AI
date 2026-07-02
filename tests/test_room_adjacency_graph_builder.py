"""Tests for the RoomAdjacencyGraphBuilder."""
from __future__ import annotations

import pytest

from building_model_v2.pipeline.dwg_knowledge.semantic_room_builder import (
    SemanticRoom,
    SemanticRoomBuilder,
)
from building_model_v2.pipeline.dwg_knowledge.room_adjacency_graph_builder import (
    RoomAdjacency,
    RoomAdjacencyGraphBuilder,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_room(
    room_id: str,
    room_type: str,
    polygon: list,
    centroid: tuple = (0.0, 0.0),
    area: float = 1.0,
    perimeter: float = 4.0,
    layer: str = "A",
    doors: list | None = None,
    windows: list | None = None,
) -> SemanticRoom:
    return SemanticRoom(
        room_id=room_id,
        room_type=room_type,
        raw_label=room_type,
        polygon=polygon,
        centroid=centroid,
        area=area,
        perimeter=perimeter,
        layer=layer,
        doors=doors or [],
        windows=windows or [],
    )


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


def test_empty_rooms() -> None:
    builder = RoomAdjacencyGraphBuilder()
    assert builder.build([]) == []


def test_single_room() -> None:
    room = _make_room(
        "bedroom_1",
        "Bedroom",
        [[0, 0], [0, 5], [5, 5], [5, 0]],
    )
    builder = RoomAdjacencyGraphBuilder()
    assert builder.build([room]) == []


def test_two_adjacent_rooms_touching() -> None:
    """Rooms that share a boundary edge."""
    room_a = _make_room(
        "bedroom_1",
        "Bedroom",
        [[0, 0], [0, 5], [5, 5], [5, 0]],
    )
    room_b = _make_room(
        "living_1",
        "Living",
        [[5, 0], [5, 5], [10, 5], [10, 0]],
    )
    builder = RoomAdjacencyGraphBuilder()
    result = builder.build([room_a, room_b])
    assert len(result) == 1
    adj = result[0]
    assert adj.source_room_id == "bedroom_1"
    assert adj.target_room_id == "living_1"
    assert adj.relationship == "adjacent"
    assert adj.distance == 0.0
    assert adj.shared_boundary_length > 0.0
    assert adj.door_connected is False


def test_two_non_adjacent_rooms() -> None:
    """Rooms far apart should not produce an adjacency."""
    room_a = _make_room(
        "bedroom_1",
        "Bedroom",
        [[0, 0], [0, 5], [5, 5], [5, 0]],
    )
    room_b = _make_room(
        "living_1",
        "Living",
        [[100, 100], [100, 105], [105, 105], [105, 100]],
    )
    builder = RoomAdjacencyGraphBuilder()
    assert builder.build([room_a, room_b]) == []


def test_tolerance_adjacency() -> None:
    """Rooms within tolerance distance should be adjacent."""
    room_a = _make_room(
        "bedroom_1",
        "Bedroom",
        [[0, 0], [0, 5], [5, 5], [5, 0]],
    )
    # 0.3 units apart – within default 0.5 tolerance
    room_b = _make_room(
        "living_1",
        "Living",
        [[5.3, 0], [5.3, 5], [10.3, 5], [10.3, 0]],
    )
    builder = RoomAdjacencyGraphBuilder()
    result = builder.build([room_a, room_b])
    assert len(result) == 1
    assert result[0].distance <= 0.5


def test_door_connected_rooms() -> None:
    """Rooms with doors at the same position should be door_connected."""
    room_a = _make_room(
        "bedroom_1",
        "Bedroom",
        [[0, 0], [0, 5], [5, 5], [5, 0]],
        doors=[{"centroid": (5.0, 2.5)}],
    )
    room_b = _make_room(
        "living_1",
        "Living",
        [[5, 0], [5, 5], [10, 5], [10, 0]],
        doors=[{"centroid": (5.0, 2.5)}],
    )
    builder = RoomAdjacencyGraphBuilder()
    result = builder.build([room_a, room_b])
    assert len(result) == 1
    adj = result[0]
    assert adj.door_connected is True
    assert adj.relationship == "door_connected"


def test_no_duplicate_pairs() -> None:
    """bedroom_1 ↔ living_1 should appear only once."""
    room_a = _make_room(
        "bedroom_1",
        "Bedroom",
        [[0, 0], [0, 5], [5, 5], [5, 0]],
    )
    room_b = _make_room(
        "living_1",
        "Living",
        [[5, 0], [5, 5], [10, 5], [10, 0]],
    )
    builder = RoomAdjacencyGraphBuilder()
    result = builder.build([room_a, room_b])
    assert len(result) == 1


def test_serialization_round_trip() -> None:
    """RoomAdjacency to_dict / from_dict round-trip."""
    adj = RoomAdjacency(
        source_room_id="bedroom_1",
        target_room_id="living_1",
        relationship="door_connected",
        distance=0.0,
        shared_boundary_length=5.0,
        door_connected=True,
    )
    d = adj.to_dict()
    restored = RoomAdjacency.from_dict(d)
    assert restored == adj


def test_three_rooms_adjacency_graph() -> None:
    """Three rooms in a row: A-B-C, expect 2 adjacencies."""
    room_a = _make_room(
        "room_a",
        "RoomA",
        [[0, 0], [0, 5], [5, 5], [5, 0]],
    )
    room_b = _make_room(
        "room_b",
        "RoomB",
        [[5, 0], [5, 5], [10, 5], [10, 0]],
    )
    room_c = _make_room(
        "room_c",
        "RoomC",
        [[10, 0], [10, 5], [15, 5], [15, 0]],
    )
    builder = RoomAdjacencyGraphBuilder()
    result = builder.build([room_a, room_b, room_c])
    assert len(result) == 2
    ids = {(adj.source_room_id, adj.target_room_id) for adj in result}
    assert ("room_a", "room_b") in ids
    assert ("room_b", "room_c") in ids