"""Tests for bubble diagram module."""
from __future__ import annotations

import pytest

from building_model_v2.architect.bubble_node import BubbleNode
from building_model_v2.architect.bubble_connection import BubbleConnection
from building_model_v2.architect.bubble_diagram import BubbleDiagram
from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel
from building_model_v2.types import RoomType


class TestBubbleNodeConstructor:
    """Tests for BubbleNode constructor."""

    def test_create_valid_node(self) -> None:
        """Create a valid BubbleNode."""
        node = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        assert node.id == "living_1"
        assert node.room_type == RoomType.LIVING
        assert node.name == "Living Room"
        assert node.target_area == 200.0
        assert node.privacy_level == PrivacyLevel.PUBLIC
        assert node.preferred_floor == FloorPreference.GROUND
        assert node.preferred_zone is None
        assert node.metadata == {}

    def test_create_with_zone(self) -> None:
        """Create node with preferred zone."""
        node = BubbleNode(
            id="bedroom_1",
            room_type=RoomType.BEDROOM,
            name="Master Bedroom",
            target_area=150.0,
            privacy_level=PrivacyLevel.PRIVATE,
            preferred_floor=FloorPreference.UPPER,
            preferred_zone="north_wing",
        )
        assert node.preferred_zone == "north_wing"

    def test_create_with_metadata(self) -> None:
        """Create node with metadata."""
        node = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
            metadata={"natural_light": True, "window_count": 2},
        )
        assert node.metadata == {"natural_light": True, "window_count": 2}


class TestBubbleNodeValidation:
    """Tests for BubbleNode validation."""

    def test_empty_id_raises_error(self) -> None:
        """Empty id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            BubbleNode(
                id="",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=200.0,
                privacy_level=PrivacyLevel.PUBLIC,
                preferred_floor=FloorPreference.GROUND,
            )

    def test_empty_name_raises_error(self) -> None:
        """Empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            BubbleNode(
                id="living_1",
                room_type=RoomType.LIVING,
                name="",
                target_area=200.0,
                privacy_level=PrivacyLevel.PUBLIC,
                preferred_floor=FloorPreference.GROUND,
            )

    def test_zero_area_raises_error(self) -> None:
        """Zero target_area raises ValueError."""
        with pytest.raises(ValueError, match="target_area must be positive"):
            BubbleNode(
                id="living_1",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=0.0,
                privacy_level=PrivacyLevel.PUBLIC,
                preferred_floor=FloorPreference.GROUND,
            )

    def test_negative_area_raises_error(self) -> None:
        """Negative target_area raises ValueError."""
        with pytest.raises(ValueError, match="target_area must be positive"):
            BubbleNode(
                id="living_1",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=-100.0,
                privacy_level=PrivacyLevel.PUBLIC,
                preferred_floor=FloorPreference.GROUND,
            )


class TestBubbleNodeSerialization:
    """Tests for BubbleNode serialization."""

    def test_to_dict(self) -> None:
        """Serialize to dictionary."""
        node = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
            preferred_zone="north",
            metadata={"key": "value"},
        )
        data = node.to_dict()
        assert data["id"] == "living_1"
        assert data["room_type"] == "Living"
        assert data["name"] == "Living Room"
        assert data["target_area"] == 200.0
        assert data["privacy_level"] == "public"
        assert data["preferred_floor"] == "ground"
        assert data["preferred_zone"] == "north"
        assert data["metadata"] == {"key": "value"}

    def test_from_dict(self) -> None:
        """Deserialize from dictionary."""
        data = {
            "id": "bedroom_1",
            "room_type": "Bedroom",
            "name": "Master Bedroom",
            "target_area": 150.0,
            "privacy_level": "private",
            "preferred_floor": "upper",
            "preferred_zone": "south",
            "metadata": {"window_count": 3},
        }
        node = BubbleNode.from_dict(data)
        assert node.id == "bedroom_1"
        assert node.room_type == RoomType.BEDROOM
        assert node.name == "Master Bedroom"
        assert node.target_area == 150.0
        assert node.privacy_level == PrivacyLevel.PRIVATE
        assert node.preferred_floor == FloorPreference.UPPER
        assert node.preferred_zone == "south"
        assert node.metadata == {"window_count": 3}

    def test_round_trip_serialization(self) -> None:
        """Round-trip serialization preserves all data."""
        original = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=120.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
            preferred_zone="east",
            metadata={"natural_light": True, "area_min": 100.0},
        )
        data = original.to_dict()
        restored = BubbleNode.from_dict(data)
        assert original == restored


class TestBubbleNodeEquality:
    """Tests for BubbleNode equality."""

    def test_equal_nodes(self) -> None:
        """Two nodes with same data are equal."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        assert node1 == node2

    def test_different_ids_not_equal(self) -> None:
        """Nodes with different ids are not equal."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="living_2",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        assert node1 != node2


class TestBubbleNodeImmutability:
    """Tests for BubbleNode immutability."""

    def test_frozen_dataclass(self) -> None:
        """BubbleNode is frozen and cannot be modified."""
        node = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        with pytest.raises(AttributeError):
            node.name = "New Name"


class TestBubbleNodeEnumPreservation:
    """Tests for enum preservation in serialization."""

    def test_room_type_preserved(self) -> None:
        """RoomType enum is preserved through serialization."""
        for room_type in [RoomType.LIVING, RoomType.BEDROOM, RoomType.KITCHEN, RoomType.BATHROOM]:
            node = BubbleNode(
                id="test_1",
                room_type=room_type,
                name="Test Room",
                target_area=100.0,
                privacy_level=PrivacyLevel.PRIVATE,
                preferred_floor=FloorPreference.ANY,
            )
            data = node.to_dict()
            restored = BubbleNode.from_dict(data)
            assert restored.room_type == room_type


class TestBubbleNodeDeterministic:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self) -> None:
        """Same input always produces same output."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        assert node1 == node2
        assert node1.to_dict() == node2.to_dict()


class TestBubbleConnectionConstructor:
    """Tests for BubbleConnection constructor."""

    def test_create_valid_connection(self) -> None:
        """Create a valid BubbleConnection."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
        )
        assert conn.source_id == "living_1"
        assert conn.target_id == "kitchen_1"
        assert conn.weight == 1.0
        assert conn.required is False
        assert conn.bidirectional is True
        assert conn.metadata == {}

    def test_create_with_weight(self) -> None:
        """Create connection with custom weight."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="bedroom_1",
            weight=0.5,
        )
        assert conn.weight == 0.5

    def test_create_required(self) -> None:
        """Create required connection."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="corridor_1",
            required=True,
        )
        assert conn.required is True

    def test_create_unidirectional(self) -> None:
        """Create unidirectional connection."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            bidirectional=False,
        )
        assert conn.bidirectional is False

    def test_create_with_metadata(self) -> None:
        """Create connection with metadata."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            metadata={"door_type": "swing", "width": 3.0},
        )
        assert conn.metadata == {"door_type": "swing", "width": 3.0}


class TestBubbleConnectionValidation:
    """Tests for BubbleConnection validation."""

    def test_empty_source_id_raises_error(self) -> None:
        """Empty source_id raises ValueError."""
        with pytest.raises(ValueError, match="source_id cannot be empty"):
            BubbleConnection(
                source_id="",
                target_id="kitchen_1",
            )

    def test_empty_target_id_raises_error(self) -> None:
        """Empty target_id raises ValueError."""
        with pytest.raises(ValueError, match="target_id cannot be empty"):
            BubbleConnection(
                source_id="living_1",
                target_id="",
            )

    def test_same_source_and_target_raises_error(self) -> None:
        """Same source and target raises ValueError."""
        with pytest.raises(ValueError, match="source_id and target_id must be different"):
            BubbleConnection(
                source_id="living_1",
                target_id="living_1",
            )

    def test_negative_weight_raises_error(self) -> None:
        """Negative weight raises ValueError."""
        with pytest.raises(ValueError, match="weight must be between 0.0 and 1.0"):
            BubbleConnection(
                source_id="living_1",
                target_id="kitchen_1",
                weight=-0.5,
            )

    def test_weight_above_one_raises_error(self) -> None:
        """Weight above 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="weight must be between 0.0 and 1.0"):
            BubbleConnection(
                source_id="living_1",
                target_id="kitchen_1",
                weight=1.5,
            )


class TestBubbleConnectionSerialization:
    """Tests for BubbleConnection serialization."""

    def test_to_dict(self) -> None:
        """Serialize to dictionary."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.8,
            required=True,
            bidirectional=False,
            metadata={"door_type": "swing"},
        )
        data = conn.to_dict()
        assert data["source_id"] == "living_1"
        assert data["target_id"] == "kitchen_1"
        assert data["weight"] == 0.8
        assert data["required"] is True
        assert data["bidirectional"] is False
        assert data["metadata"] == {"door_type": "swing"}

    def test_from_dict(self) -> None:
        """Deserialize from dictionary."""
        data = {
            "source_id": "bedroom_1",
            "target_id": "bathroom_1",
            "weight": 0.9,
            "required": True,
            "bidirectional": True,
            "metadata": {"privacy": "high"},
        }
        conn = BubbleConnection.from_dict(data)
        assert conn.source_id == "bedroom_1"
        assert conn.target_id == "bathroom_1"
        assert conn.weight == 0.9
        assert conn.required is True
        assert conn.bidirectional is True
        assert conn.metadata == {"privacy": "high"}

    def test_round_trip_serialization(self) -> None:
        """Round-trip serialization preserves all data."""
        original = BubbleConnection(
            source_id="living_1",
            target_id="dining_1",
            weight=0.7,
            required=False,
            bidirectional=True,
            metadata={"open_plan": True, "width": 4.0},
        )
        data = original.to_dict()
        restored = BubbleConnection.from_dict(data)
        assert original == restored


class TestBubbleConnectionEquality:
    """Tests for BubbleConnection equality."""

    def test_equal_connections(self) -> None:
        """Two connections with same data are equal."""
        conn1 = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.5,
        )
        conn2 = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.5,
        )
        assert conn1 == conn2


class TestBubbleConnectionImmutability:
    """Tests for BubbleConnection immutability."""

    def test_frozen_dataclass(self) -> None:
        """BubbleConnection is frozen and cannot be modified."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
        )
        with pytest.raises(AttributeError):
            conn.weight = 0.5


class TestBubbleConnectionDeterministic:
    """Tests for deterministic behavior."""

    def test_serialization_deterministic(self) -> None:
        """Serialization is deterministic."""
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.5,
            metadata={"key1": "value1", "key2": "value2"},
        )
        data1 = conn.to_dict()
        data2 = conn.to_dict()
        assert data1 == data2


class TestBubbleDiagramConstructor:
    """Tests for BubbleDiagram constructor."""

    def test_create_empty_diagram(self) -> None:
        """Create an empty BubbleDiagram."""
        diagram = BubbleDiagram()
        assert diagram.room_count == 0
        assert diagram.connection_count == 0
        assert diagram.nodes == ()
        assert diagram.connections == ()
        assert diagram.metadata == {}

    def test_create_with_nodes(self) -> None:
        """Create diagram with nodes."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        diagram = BubbleDiagram(nodes=(node1, node2))
        assert diagram.room_count == 2
        assert diagram.connection_count == 0
        assert diagram.room_ids == ("living_1", "kitchen_1")

    def test_create_with_connections(self) -> None:
        """Create diagram with nodes and connections."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.8,
        )
        diagram = BubbleDiagram(nodes=(node1, node2), connections=(conn,))
        assert diagram.room_count == 2
        assert diagram.connection_count == 1

    def test_create_with_metadata(self) -> None:
        """Create diagram with metadata."""
        diagram = BubbleDiagram(metadata={"project": "test", "version": "1.0"})
        assert diagram.metadata == {"project": "test", "version": "1.0"}


class TestBubbleDiagramValidation:
    """Tests for BubbleDiagram validation."""

    def test_duplicate_node_ids_raises_error(self) -> None:
        """Duplicate node ids raises ValueError."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="living_1",
            room_type=RoomType.BEDROOM,
            name="Bedroom",
            target_area=150.0,
            privacy_level=PrivacyLevel.PRIVATE,
            preferred_floor=FloorPreference.UPPER,
        )
        with pytest.raises(ValueError, match="node ids must be unique"):
            BubbleDiagram(nodes=(node1, node2))

    def test_invalid_connection_source_raises_error(self) -> None:
        """Connection with non-existent source raises ValueError."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="nonexistent",
            target_id="living_1",
        )
        with pytest.raises(ValueError, match="connection source 'nonexistent' does not exist"):
            BubbleDiagram(nodes=(node1,), connections=(conn,))

    def test_invalid_connection_target_raises_error(self) -> None:
        """Connection with non-existent target raises ValueError."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="nonexistent",
        )
        with pytest.raises(ValueError, match="connection target 'nonexistent' does not exist"):
            BubbleDiagram(nodes=(node1,), connections=(conn,))


class TestBubbleDiagramNodeLookup:
    """Tests for node lookup in BubbleDiagram."""

    def test_get_node_exists(self) -> None:
        """Get existing node returns node."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        diagram = BubbleDiagram(nodes=(node1,))
        result = diagram.get_node("living_1")
        assert result == node1

    def test_get_node_not_exists(self) -> None:
        """Get non-existent node returns None."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        diagram = BubbleDiagram(nodes=(node1,))
        result = diagram.get_node("nonexistent")
        assert result is None


class TestBubbleDiagramNeighbors:
    """Tests for neighbors in BubbleDiagram."""

    def test_neighbors_bidirectional(self) -> None:
        """Bidirectional connection returns neighbors in both directions."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            bidirectional=True,
        )
        diagram = BubbleDiagram(nodes=(node1, node2), connections=(conn,))
        assert diagram.neighbors("living_1") == (node2,)
        assert diagram.neighbors("kitchen_1") == (node1,)

    def test_neighbors_unidirectional(self) -> None:
        """Unidirectional connection only returns neighbor in source direction."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            bidirectional=False,
        )
        diagram = BubbleDiagram(nodes=(node1, node2), connections=(conn,))
        assert diagram.neighbors("living_1") == (node2,)
        assert diagram.neighbors("kitchen_1") == ()

    def test_neighbors_no_duplicates(self) -> None:
        """Multiple connections to same neighbor do not create duplicates."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn1 = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.8,
        )
        conn2 = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.5,
        )
        diagram = BubbleDiagram(nodes=(node1, node2), connections=(conn1, conn2))
        neighbors = diagram.neighbors("living_1")
        assert len(neighbors) == 1
        assert neighbors[0] == node2

    def test_neighbors_nonexistent_node(self) -> None:
        """Getting neighbors for non-existent node returns empty tuple."""
        diagram = BubbleDiagram()
        assert diagram.neighbors("nonexistent") == ()


class TestBubbleDiagramAdjacencyMatrix:
    """Tests for adjacency matrix in BubbleDiagram."""

    def test_empty_matrix(self) -> None:
        """Empty diagram has empty matrix."""
        diagram = BubbleDiagram()
        matrix = diagram.adjacency_matrix()
        assert matrix == {}

    def test_matrix_with_nodes_no_connections(self) -> None:
        """Matrix with nodes but no connections has empty dicts for each node."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        diagram = BubbleDiagram(nodes=(node1, node2))
        matrix = diagram.adjacency_matrix()
        assert matrix == {"living_1": {}, "kitchen_1": {}}

    def test_matrix_bidirectional(self) -> None:
        """Bidirectional connection creates entries in both directions."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.8,
            bidirectional=True,
        )
        diagram = BubbleDiagram(nodes=(node1, node2), connections=(conn,))
        matrix = diagram.adjacency_matrix()
        assert matrix["living_1"]["kitchen_1"] == 0.8
        assert matrix["kitchen_1"]["living_1"] == 0.8

    def test_matrix_unidirectional(self) -> None:
        """Unidirectional connection creates entry only in source direction."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.8,
            bidirectional=False,
        )
        diagram = BubbleDiagram(nodes=(node1, node2), connections=(conn,))
        matrix = diagram.adjacency_matrix()
        assert matrix["living_1"]["kitchen_1"] == 0.8
        assert "living_1" not in matrix["kitchen_1"]


class TestBubbleDiagramSerialization:
    """Tests for BubbleDiagram serialization."""

    def test_to_dict(self) -> None:
        """Serialize to dictionary."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.8,
        )
        diagram = BubbleDiagram(
            nodes=(node1, node2),
            connections=(conn,),
            metadata={"project": "test"},
        )
        data = diagram.to_dict()
        assert len(data["nodes"]) == 2
        assert len(data["connections"]) == 1
        assert data["metadata"] == {"project": "test"}

    def test_from_dict(self) -> None:
        """Deserialize from dictionary."""
        data = {
            "nodes": [
                {
                    "id": "living_1",
                    "room_type": "Living",
                    "name": "Living Room",
                    "target_area": 200.0,
                    "privacy_level": "public",
                    "preferred_floor": "ground",
                    "preferred_zone": None,
                    "metadata": {},
                },
                {
                    "id": "kitchen_1",
                    "room_type": "Kitchen",
                    "name": "Kitchen",
                    "target_area": 100.0,
                    "privacy_level": "semi_private",
                    "preferred_floor": "ground",
                    "preferred_zone": None,
                    "metadata": {},
                },
            ],
            "connections": [
                {
                    "source_id": "living_1",
                    "target_id": "kitchen_1",
                    "weight": 0.8,
                    "required": False,
                    "bidirectional": True,
                    "metadata": {},
                },
            ],
            "metadata": {"project": "test"},
        }
        diagram = BubbleDiagram.from_dict(data)
        assert diagram.room_count == 2
        assert diagram.connection_count == 1
        assert diagram.metadata == {"project": "test"}

    def test_round_trip_serialization(self) -> None:
        """Round-trip serialization preserves all data."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        conn = BubbleConnection(
            source_id="living_1",
            target_id="kitchen_1",
            weight=0.8,
        )
        original = BubbleDiagram(
            nodes=(node1, node2),
            connections=(conn,),
            metadata={"project": "test"},
        )
        data = original.to_dict()
        restored = BubbleDiagram.from_dict(data)
        assert original == restored


class TestBubbleDiagramEquality:
    """Tests for BubbleDiagram equality."""

    def test_equal_diagrams(self) -> None:
        """Two diagrams with same data are equal."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        diagram1 = BubbleDiagram(nodes=(node1,))
        diagram2 = BubbleDiagram(nodes=(node1,))
        assert diagram1 == diagram2

    def test_different_node_count_not_equal(self) -> None:
        """Diagrams with different node counts are not equal."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        node2 = BubbleNode(
            id="kitchen_1",
            room_type=RoomType.KITCHEN,
            name="Kitchen",
            target_area=100.0,
            privacy_level=PrivacyLevel.SEMI_PRIVATE,
            preferred_floor=FloorPreference.GROUND,
        )
        diagram1 = BubbleDiagram(nodes=(node1,))
        diagram2 = BubbleDiagram(nodes=(node1, node2))
        assert diagram1 != diagram2


class TestBubbleDiagramImmutability:
    """Tests for BubbleDiagram immutability."""

    def test_frozen_dataclass(self) -> None:
        """BubbleDiagram is frozen and cannot be modified."""
        diagram = BubbleDiagram()
        with pytest.raises(AttributeError):
            diagram.metadata = {"new": "value"}


class TestBubbleDiagramDeterministic:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self) -> None:
        """Same input always produces same output."""
        node1 = BubbleNode(
            id="living_1",
            room_type=RoomType.LIVING,
            name="Living Room",
            target_area=200.0,
            privacy_level=PrivacyLevel.PUBLIC,
            preferred_floor=FloorPreference.GROUND,
        )
        diagram1 = BubbleDiagram(nodes=(node1,))
        diagram2 = BubbleDiagram(nodes=(node1,))
        assert diagram1 == diagram2
        assert diagram1.to_dict() == diagram2.to_dict()