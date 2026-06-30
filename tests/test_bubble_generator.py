"""Tests for bubble diagram generator."""
from __future__ import annotations

import pytest

from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.architect.bubble_diagram import BubbleDiagram
from building_model_v2.architect.bubble_generator import BubbleGenerator
from building_model_v2.types import RoomType


def _make_room(
    id: str,
    room_type: str,
    name: str = "",
    target_area: float | None = None,
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE,
    floor_preference: FloorPreference = FloorPreference.ANY,
    metadata: dict | None = None,
) -> RoomProgram:
    """Helper to create a RoomProgram."""
    return RoomProgram(
        id=id,
        room_type=room_type,
        name=name,
        target_area=target_area,
        privacy_level=privacy_level,
        floor_preference=floor_preference,
        metadata=metadata or {},
    )


def _make_program(
    rooms: tuple[RoomProgram, ...],
    floor_count: int = 1,
    metadata: dict | None = None,
) -> SpaceProgram:
    """Helper to create a SpaceProgram."""
    return SpaceProgram(
        rooms=rooms,
        floor_count=floor_count,
        metadata=metadata or {},
    )


class TestBubbleGeneratorEmpty:
    """Tests for empty program generation."""

    def test_empty_program(self) -> None:
        """Empty program generates empty diagram."""
        generator = BubbleGenerator()
        program = _make_program(())
        diagram = generator.generate(program)
        assert diagram.room_count == 0
        assert diagram.connection_count == 0
        assert diagram.nodes == ()
        assert diagram.connections == ()


class TestBubbleGenerator1BHK:
    """Tests for 1BHK generation."""

    def test_1bhk_generation(self) -> None:
        """1BHK generates correct nodes and connections."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("bathroom", "bathroom", "Bathroom", 50.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.room_count == 5
        assert diagram.connection_count >= 1

    def test_1bhk_has_entrance_living_connection(self) -> None:
        """1BHK has entrance-living connection."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "entrance" in matrix
        assert "living" in matrix["entrance"]


class TestBubbleGenerator2BHK:
    """Tests for 2BHK generation."""

    def test_2bhk_generation(self) -> None:
        """2BHK generates correct nodes and connections."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("dining", "dining", "Dining", 120.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("bedroom1", "bedroom", "Bedroom 1", 150.0),
            _make_room("bedroom2", "bedroom", "Bedroom 2", 120.0),
            _make_room("bathroom", "bathroom", "Bathroom", 50.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.room_count == 7
        assert diagram.connection_count >= 3


class TestBubbleGenerator3BHK:
    """Tests for 3BHK generation."""

    def test_3bhk_generation(self) -> None:
        """3BHK generates correct nodes and connections."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 250.0),
            _make_room("dining", "dining", "Dining", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 120.0),
            _make_room("master_bedroom", "master_bedroom", "Master Bedroom", 180.0),
            _make_room("master_bathroom", "master_bathroom", "Master Bathroom", 60.0),
            _make_room("bedroom2", "bedroom", "Bedroom 2", 140.0),
            _make_room("bedroom3", "bedroom", "Bedroom 3", 120.0),
            _make_room("common_bathroom", "common_bathroom", "Common Bathroom", 50.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.room_count == 9
        assert diagram.connection_count >= 6


class TestBubbleGeneratorDuplex:
    """Tests for duplex generation."""

    def test_duplex_stair_connection(self) -> None:
        """Duplex with stair generates stair-living connection."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0, floor_preference=FloorPreference.GROUND),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0, floor_preference=FloorPreference.GROUND),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0, floor_preference=FloorPreference.UPPER),
            _make_room("stair", "stair", "Stair", 50.0, floor_preference=FloorPreference.ANY),
            _make_room("entrance", "entrance", "Entrance", 20.0, floor_preference=FloorPreference.GROUND),
        )
        program = _make_program(rooms, floor_count=2)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "stair" in matrix
        assert "living" in matrix["stair"]


class TestBubbleGeneratorParking:
    """Tests for parking generation."""

    def test_parking_entrance_connection(self) -> None:
        """Parking connects to entrance."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("parking", "parking", "Parking", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "parking" in matrix
        assert "entrance" in matrix["parking"]

    def test_utility_parking_connection(self) -> None:
        """Utility connects to parking (optional)."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("utility", "utility", "Utility", 50.0),
            _make_room("parking", "parking", "Parking", 200.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "utility" in matrix
        assert "parking" in matrix["utility"]
        assert matrix["utility"]["parking"] == 0.5


class TestBubbleGeneratorPooja:
    """Tests for pooja room generation."""

    def test_pooja_living_connection(self) -> None:
        """Pooja room connects to living."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("pooja", "pooja", "Pooja", 40.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "pooja" in matrix
        assert "living" in matrix["pooja"]


class TestBubbleGeneratorOffice:
    """Tests for office room generation."""

    def test_office_living_connection(self) -> None:
        """Office connects to living."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("office", "office", "Office", 80.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "office" in matrix
        assert "living" in matrix["office"]


class TestBubbleGeneratorBalcony:
    """Tests for balcony generation."""

    def test_balcony_living_connection(self) -> None:
        """Balcony connects to living."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("balcony", "balcony", "Balcony", 60.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "balcony" in matrix
        assert "living" in matrix["balcony"]


class TestBubbleGeneratorUtility:
    """Tests for utility room generation."""

    def test_utility_kitchen_connection(self) -> None:
        """Utility connects to kitchen."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("utility", "utility", "Utility", 50.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert "utility" in matrix
        assert "kitchen" in matrix["utility"]


class TestBubbleGeneratorConnectionWeights:
    """Tests for connection weights."""

    def test_required_weight_is_1_0(self) -> None:
        """Required connections have weight 1.0."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("dining", "dining", "Dining", 120.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert matrix["living"]["dining"] == 1.0

    def test_preferred_weight_is_0_8(self) -> None:
        """Preferred connections have weight 0.8."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("utility", "utility", "Utility", 50.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert matrix["kitchen"]["utility"] == 0.8

    def test_optional_weight_is_0_5(self) -> None:
        """Optional connections have weight 0.5."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("utility", "utility", "Utility", 50.0),
            _make_room("parking", "parking", "Parking", 200.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        matrix = diagram.adjacency_matrix()
        assert matrix["utility"]["parking"] == 0.5


class TestBubbleGeneratorDuplicatePrevention:
    """Tests for duplicate prevention."""

    def test_no_duplicate_nodes(self) -> None:
        """Generator never creates duplicate nodes."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("dining", "dining", "Dining", 120.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        node_ids = [node.id for node in diagram.nodes]
        assert len(node_ids) == len(set(node_ids))

    def test_no_duplicate_edges(self) -> None:
        """Generator never creates duplicate edges."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("dining", "dining", "Dining", 120.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        edges = set()
        for conn in diagram.connections:
            edge_key = (conn.source_id, conn.target_id)
            assert edge_key not in edges
            edges.add(edge_key)


class TestBubbleGeneratorDeterministic:
    """Tests for deterministic generation."""

    def test_same_input_same_output(self) -> None:
        """Same input always produces same output."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("dining", "dining", "Dining", 120.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram1 = generator.generate(program)
        diagram2 = generator.generate(program)
        assert diagram1 == diagram2
        assert diagram1.to_dict() == diagram2.to_dict()


class TestBubbleGeneratorSerialization:
    """Tests for serialization compatibility."""

    def test_serialization_round_trip(self) -> None:
        """Diagram can be serialized and deserialized."""
        generator = BubbleGenerator()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("dining", "dining", "Dining", 120.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = generator.generate(program)
        data = diagram.to_dict()
        restored = BubbleDiagram.from_dict(data)
        assert diagram == restored


class TestBubbleGeneratorNodeMapping:
    """Tests for node type mapping."""

    def test_living_room_mapping(self) -> None:
        """Living room maps to LIVING type."""
        generator = BubbleGenerator()
        rooms = (_make_room("living", "living", "Living Room", 200.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.LIVING

    def test_kitchen_mapping(self) -> None:
        """Kitchen maps to KITCHEN type."""
        generator = BubbleGenerator()
        rooms = (_make_room("kitchen", "kitchen", "Kitchen", 100.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.KITCHEN

    def test_bedroom_mapping(self) -> None:
        """Bedroom maps to BEDROOM type."""
        generator = BubbleGenerator()
        rooms = (_make_room("bedroom", "bedroom", "Bedroom", 150.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.BEDROOM

    def test_master_bedroom_mapping(self) -> None:
        """Master bedroom maps to BEDROOM type."""
        generator = BubbleGenerator()
        rooms = (_make_room("master_bedroom", "master_bedroom", "Master Bedroom", 180.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.BEDROOM

    def test_bathroom_mapping(self) -> None:
        """Bathroom maps to BATHROOM type."""
        generator = BubbleGenerator()
        rooms = (_make_room("bathroom", "bathroom", "Bathroom", 50.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.BATHROOM

    def test_stair_mapping(self) -> None:
        """Stair maps to STAIRCASE type."""
        generator = BubbleGenerator()
        rooms = (_make_room("stair", "stair", "Stair", 50.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.STAIRCASE

    def test_balcony_mapping(self) -> None:
        """Balcony maps to BALCONY type."""
        generator = BubbleGenerator()
        rooms = (_make_room("balcony", "balcony", "Balcony", 60.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.BALCONY

    def test_utility_mapping(self) -> None:
        """Utility maps to UTILITY type."""
        generator = BubbleGenerator()
        rooms = (_make_room("utility", "utility", "Utility", 50.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.UTILITY

    def test_unknown_mapping(self) -> None:
        """Unknown room type maps to UNKNOWN."""
        generator = BubbleGenerator()
        rooms = (_make_room("unknown_room", "unknown_type", "Unknown", 50.0),)
        program = _make_program(rooms)
        diagram = generator.generate(program)
        assert diagram.nodes[0].room_type == RoomType.UNKNOWN