"""Unit tests for Relationship and RelationshipType."""

from __future__ import annotations

import pytest

from building_model_v2 import Relationship, RelationshipType


class TestRelationshipType:
    """Tests for RelationshipType enum."""
    
    def test_all_enum_values_unique(self) -> None:
        values = [rt.value for rt in RelationshipType]
        assert len(values) == len(set(values))
    
    def test_enum_value_count(self) -> None:
        assert len(RelationshipType) == 10
    
    def test_room_to_wall_value(self) -> None:
        assert RelationshipType.ROOM_TO_WALL.value == "room_to_wall"
    
    def test_room_to_door_value(self) -> None:
        assert RelationshipType.ROOM_TO_DOOR.value == "room_to_door"
    
    def test_room_to_window_value(self) -> None:
        assert RelationshipType.ROOM_TO_WINDOW.value == "room_to_window"
    
    def test_room_to_room_value(self) -> None:
        assert RelationshipType.ROOM_TO_ROOM.value == "room_to_room"
    
    def test_wall_to_window_value(self) -> None:
        assert RelationshipType.WALL_TO_WINDOW.value == "wall_to_window"
    
    def test_wall_to_door_value(self) -> None:
        assert RelationshipType.WALL_TO_DOOR.value == "wall_to_door"
    
    def test_floor_to_room_value(self) -> None:
        assert RelationshipType.FLOOR_TO_ROOM.value == "floor_to_room"
    
    def test_floor_to_stair_value(self) -> None:
        assert RelationshipType.FLOOR_TO_STAIR.value == "floor_to_stair"
    
    def test_building_to_floor_value(self) -> None:
        assert RelationshipType.BUILDING_TO_FLOOR.value == "building_to_floor"
    
    def test_stair_to_floor_value(self) -> None:
        assert RelationshipType.STAIR_TO_FLOOR.value == "stair_to_floor"
    
    def test_is_bidirectional_room_to_room(self) -> None:
        assert RelationshipType.ROOM_TO_ROOM.is_bidirectional is True
    
    def test_is_bidirectional_room_to_wall(self) -> None:
        assert RelationshipType.ROOM_TO_WALL.is_bidirectional is False
    
    def test_is_bidirectional_floor_to_room(self) -> None:
        assert RelationshipType.FLOOR_TO_ROOM.is_bidirectional is False
    
    def test_is_hierarchical_floor_to_room(self) -> None:
        assert RelationshipType.FLOOR_TO_ROOM.is_hierarchical is True
    
    def test_is_hierarchical_floor_to_stair(self) -> None:
        assert RelationshipType.FLOOR_TO_STAIR.is_hierarchical is True
    
    def test_is_hierarchical_building_to_floor(self) -> None:
        assert RelationshipType.BUILDING_TO_FLOOR.is_hierarchical is True
    
    def test_is_hierarchical_room_to_room(self) -> None:
        assert RelationshipType.ROOM_TO_ROOM.is_hierarchical is False
    
    def test_is_hierarchical_room_to_wall(self) -> None:
        assert RelationshipType.ROOM_TO_WALL.is_hierarchical is False
    
    def test_enum_from_value(self) -> None:
        assert RelationshipType("room_to_wall") == RelationshipType.ROOM_TO_WALL
    
    def test_enum_from_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            RelationshipType("invalid_type")


class TestRelationship:
    """Tests for Relationship entity."""
    
    def test_create_with_defaults(self) -> None:
        rel = Relationship()
        assert rel.relationship_type == RelationshipType.ROOM_TO_ROOM
        assert rel.source_id == ""
        assert rel.target_id == ""
    
    def test_create_with_values(self) -> None:
        rel = Relationship(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        assert rel.relationship_type == RelationshipType.ROOM_TO_WALL
        assert rel.source_id == "room-1"
        assert rel.target_id == "wall-1"
    
    def test_create_factory(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.FLOOR_TO_ROOM,
            source_id="floor-1",
            target_id="room-1",
        )
        assert rel.relationship_type == RelationshipType.FLOOR_TO_ROOM
        assert rel.source_id == "floor-1"
        assert rel.target_id == "room-1"
    
    def test_create_factory_with_metadata(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.BUILDING_TO_FLOOR,
            source_id="building-1",
            target_id="floor-1",
            metadata={"order": 0},
        )
        assert rel.metadata["order"] == 0
    
    def test_is_bidirectional_room_to_room(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-2",
        )
        assert rel.is_bidirectional is True
    
    def test_is_bidirectional_room_to_wall(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        assert rel.is_bidirectional is False
    
    def test_is_hierarchical_floor_to_room(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.FLOOR_TO_ROOM,
            source_id="floor-1",
            target_id="room-1",
        )
        assert rel.is_hierarchical is True
    
    def test_is_hierarchical_room_to_room(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-2",
        )
        assert rel.is_hierarchical is False
    
    def test_inverse(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        inverse = rel.inverse
        assert inverse.source_id == "wall-1"
        assert inverse.target_id == "room-1"
        assert inverse.relationship_type == RelationshipType.ROOM_TO_WALL
    
    def test_inverse_preserves_metadata(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-2",
            metadata={"weight": 1.0},
        )
        inverse = rel.inverse
        assert inverse.metadata["weight"] == 1.0
    
    def test_to_dict(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.WALL_TO_DOOR,
            source_id="wall-1",
            target_id="door-1",
        )
        result = rel.to_dict()
        assert result["relationship_type"] == "wall_to_door"
        assert result["source_id"] == "wall-1"
        assert result["target_id"] == "door-1"
        assert result["is_bidirectional"] is False
        assert result["is_hierarchical"] is False
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "rel-1",
            "relationship_type": "floor_to_room",
            "source_id": "floor-1",
            "target_id": "room-1",
        }
        rel = Relationship.from_dict(payload)
        assert rel.id == "rel-1"
        assert rel.relationship_type == RelationshipType.FLOOR_TO_ROOM
        assert rel.source_id == "floor-1"
        assert rel.target_id == "room-1"
    
    def test_from_dict_defaults(self) -> None:
        rel = Relationship.from_dict({})
        assert rel.relationship_type == RelationshipType.ROOM_TO_ROOM
        assert rel.source_id == ""
        assert rel.target_id == ""
    
    def test_from_dict_invalid_type_uses_default(self) -> None:
        payload = {
            "relationship_type": "invalid_type",
            "source_id": "a",
            "target_id": "b",
        }
        rel = Relationship.from_dict(payload)
        assert rel.relationship_type == RelationshipType.ROOM_TO_ROOM
    
    def test_immutability(self) -> None:
        rel = Relationship()
        with pytest.raises(AttributeError):
            rel.source_id = "new-source"  # type: ignore
    
    def test_immutability_type(self) -> None:
        rel = Relationship()
        with pytest.raises(AttributeError):
            rel.relationship_type = RelationshipType.ROOM_TO_WALL  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        rel = Relationship()
        assert hasattr(rel, "id")
        assert hasattr(rel, "created_at")
        assert hasattr(rel, "updated_at")
        assert hasattr(rel, "metadata")
    
    def test_round_trip_serialization(self) -> None:
        original = Relationship.create(
            relationship_type=RelationshipType.BUILDING_TO_FLOOR,
            source_id="building-1",
            target_id="floor-2",
            metadata={"level": 0},
        )
        data = original.to_dict()
        restored = Relationship.from_dict(data)
        assert restored.relationship_type == original.relationship_type
        assert restored.source_id == original.source_id
        assert restored.target_id == original.target_id
        assert restored.metadata == original.metadata
    
    def test_equality(self) -> None:
        rel1 = Relationship(source_id="a", target_id="b")
        rel2 = Relationship(source_id="a", target_id="b")
        # Different IDs by default
        assert rel1 != rel2
    
    def test_equality_same_id(self) -> None:
        rel1 = Relationship(
            id="same-id",
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
            source_id="a",
            target_id="b",
        )
        rel2 = Relationship(
            id="same-id",
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
            source_id="a",
            target_id="b",
        )
        assert rel1 == rel2
    
    def test_to_dict_includes_base_fields(self) -> None:
        rel = Relationship()
        result = rel.to_dict()
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "metadata" in result
    
    def test_from_dict_preserves_timestamps(self) -> None:
        payload = {
            "id": "rel-1",
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-02T00:00:00+00:00",
        }
        rel = Relationship.from_dict(payload)
        assert rel.created_at == "2024-01-01T00:00:00+00:00"
        assert rel.updated_at == "2024-01-02T00:00:00+00:00"
    
    def test_from_dict_generates_timestamps_if_missing(self) -> None:
        rel = Relationship.from_dict({"id": "rel-1"})
        assert rel.created_at is not None
        assert rel.updated_at is not None
    
    def test_all_relationship_types(self) -> None:
        for rel_type in RelationshipType:
            rel = Relationship(
                relationship_type=rel_type,
                source_id="source",
                target_id="target",
            )
            assert rel.relationship_type == rel_type
    
    def test_empty_source_and_target(self) -> None:
        rel = Relationship(source_id="", target_id="")
        assert rel.source_id == ""
        assert rel.target_id == ""
    
    def test_metadata_preserved(self) -> None:
        rel = Relationship(
            source_id="a",
            target_id="b",
            metadata={"key1": "value1", "key2": 42},
        )
        assert rel.metadata["key1"] == "value1"
        assert rel.metadata["key2"] == 42
    
    def test_inverse_of_inverse_equals_original(self) -> None:
        original = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        double_inverse = original.inverse.inverse
        assert double_inverse.source_id == original.source_id
        assert double_inverse.target_id == original.target_id
        assert double_inverse.relationship_type == original.relationship_type
    
    def test_hierarchical_types(self) -> None:
        hierarchical_types = {
            RelationshipType.FLOOR_TO_ROOM,
            RelationshipType.FLOOR_TO_STAIR,
            RelationshipType.BUILDING_TO_FLOOR,
        }
        for rel_type in hierarchical_types:
            rel = Relationship(
                relationship_type=rel_type,
                source_id="parent",
                target_id="child",
            )
            assert rel.is_hierarchical is True
    
    def test_non_hierarchical_types(self) -> None:
        non_hierarchical_types = {
            RelationshipType.ROOM_TO_WALL,
            RelationshipType.ROOM_TO_DOOR,
            RelationshipType.ROOM_TO_WINDOW,
            RelationshipType.ROOM_TO_ROOM,
            RelationshipType.WALL_TO_WINDOW,
            RelationshipType.WALL_TO_DOOR,
            RelationshipType.STAIR_TO_FLOOR,
        }
        for rel_type in non_hierarchical_types:
            rel = Relationship(
                relationship_type=rel_type,
                source_id="a",
                target_id="b",
            )
            assert rel.is_hierarchical is False
    
    def test_bidirectional_types(self) -> None:
        bidirectional_types = {RelationshipType.ROOM_TO_ROOM}
        for rel_type in bidirectional_types:
            rel = Relationship(
                relationship_type=rel_type,
                source_id="a",
                target_id="b",
            )
            assert rel.is_bidirectional is True
    
    def test_non_bidirectional_types(self) -> None:
        non_bidirectional_types = {
            RelationshipType.ROOM_TO_WALL,
            RelationshipType.ROOM_TO_DOOR,
            RelationshipType.ROOM_TO_WINDOW,
            RelationshipType.WALL_TO_WINDOW,
            RelationshipType.WALL_TO_DOOR,
            RelationshipType.FLOOR_TO_ROOM,
            RelationshipType.FLOOR_TO_STAIR,
            RelationshipType.BUILDING_TO_FLOOR,
            RelationshipType.STAIR_TO_FLOOR,
        }
        for rel_type in non_bidirectional_types:
            rel = Relationship(
                relationship_type=rel_type,
                source_id="a",
                target_id="b",
            )
            assert rel.is_bidirectional is False