import pytest

from building_model_v2.pipeline.dwg_knowledge.semantic_room_builder import (
    SemanticRoom,
    SemanticRoomBuilder,
)


def sample_room_payload(room_type: str = "Bedroom", raw_label: str = "BR", count: int = 1):
    return {
        "room_type": room_type,
        "raw_label": raw_label,
        "polygon": [[0, 0], [0, 5], [5, 5], [5, 0]],
        "centroid": (2.5, 2.5),
        "area": 25.0,
        "perimeter": 20.0,
        "layer": "Layer1",
        "doors": [{"id": f"door_{count}"}],
        "windows": [{"id": f"window_{count}"}],
    }


def test_empty_list_returns_empty():
    builder = SemanticRoomBuilder()
    assert builder.build([]) == []


def test_single_room_builds_correctly():
    payload = [sample_room_payload()]
    builder = SemanticRoomBuilder()
    rooms = builder.build(payload)
    assert len(rooms) == 1
    room = rooms[0]
    assert isinstance(room, SemanticRoom)
    assert room.room_id == "bedroom_1"
    assert room.room_type == "Bedroom"
    assert room.door_count == 1
    assert room.window_count == 1
    # geometry preserved
    assert room.polygon == payload[0]["polygon"]
    assert room.centroid == payload[0]["centroid"]


def test_multiple_rooms_deterministic_ids():
    payload = [
        sample_room_payload(room_type="Bedroom", raw_label="BR", count=1),
        sample_room_payload(room_type="Bedroom", raw_label="BR", count=2),
        sample_room_payload(room_type="Kitchen", raw_label="KT", count=1),
    ]
    builder = SemanticRoomBuilder()
    rooms = builder.build(payload)
    ids = [r.room_id for r in rooms]
    assert ids == ["bedroom_1", "bedroom_2", "kitchen_1"]


def test_serialization_and_deserialization():
    payload = [sample_room_payload()]
    builder = SemanticRoomBuilder()
    room = builder.build(payload)[0]
    d = room.to_dict()
    restored = SemanticRoom.from_dict(d)
    assert restored == room
