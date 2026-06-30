"""Tests for architect engine."""
from __future__ import annotations

import pytest

from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.architect.architect_engine import ArchitectEngine
from building_model_v2.architect.architect_result import ArchitectResult
from building_model_v2.architect.bubble_generator import BubbleGenerator
from building_model_v2.architect.zoning_engine import ZoningEngine


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


class TestArchitectEngineEmpty:
    """Tests for empty program analysis."""

    def test_empty_program(self) -> None:
        """Empty program produces empty result."""
        engine = ArchitectEngine()
        program = _make_program(())
        result = engine.analyze(program)
        assert result.room_count == 0
        assert result.connection_count == 0
        assert result.zone_count == 0
        assert result.bubble_diagram.nodes == ()
        assert result.zoning_result.zones == ()


class TestArchitectEngine1BHK:
    """Tests for 1BHK analysis."""

    def test_1bhk_analysis(self) -> None:
        """1BHK produces correct result."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("bathroom", "bathroom", "Bathroom", 50.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.room_count == 5
        assert result.zone_count >= 3
        assert result.connection_count >= 1


class TestArchitectEngine2BHK:
    """Tests for 2BHK analysis."""

    def test_2bhk_analysis(self) -> None:
        """2BHK produces correct result."""
        engine = ArchitectEngine()
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
        result = engine.analyze(program)
        assert result.room_count == 7
        assert result.zone_count >= 3
        assert result.zoning_result.assigned_room_count == 7


class TestArchitectEngineDuplex:
    """Tests for duplex analysis."""

    def test_duplex_analysis(self) -> None:
        """Duplex produces vertical zone."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0, floor_preference=FloorPreference.GROUND),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0, floor_preference=FloorPreference.GROUND),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0, floor_preference=FloorPreference.UPPER),
            _make_room("stair", "stair", "Stair", 50.0, floor_preference=FloorPreference.ANY),
            _make_room("entrance", "entrance", "Entrance", 20.0, floor_preference=FloorPreference.GROUND),
        )
        program = _make_program(rooms, floor_count=2)
        result = engine.analyze(program)
        assert result.room_count == 5
        vertical_zones = [z for z in result.zoning_result.zones if z.zone_type == "VERTICAL"]
        assert len(vertical_zones) == 1


class TestArchitectEngineParking:
    """Tests for parking analysis."""

    def test_parking_analysis(self) -> None:
        """Parking produces service zone."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("parking", "parking", "Parking", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.room_count == 2
        service_zones = [z for z in result.zoning_result.zones if z.zone_type == "SERVICE"]
        assert len(service_zones) == 1


class TestArchitectEnginePooja:
    """Tests for pooja room analysis."""

    def test_pooja_analysis(self) -> None:
        """Pooja produces semi-private zone."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("pooja", "pooja", "Pooja", 40.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.room_count == 2
        semi_private_zones = [z for z in result.zoning_result.zones if z.zone_type == "SEMI_PRIVATE"]
        assert len(semi_private_zones) >= 1


class TestArchitectEngineOffice:
    """Tests for office analysis."""

    def test_office_analysis(self) -> None:
        """Office produces semi-private zone."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("office", "office", "Office", 80.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.room_count == 2
        semi_private_zones = [z for z in result.zoning_result.zones if z.zone_type == "SEMI_PRIVATE"]
        assert len(semi_private_zones) >= 1


class TestArchitectEngineSerialization:
    """Tests for serialization."""

    def test_result_serialization(self) -> None:
        """ArchitectResult can be serialized and deserialized."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        data = result.to_dict()
        restored = ArchitectResult.from_dict(data)
        assert result == restored


class TestArchitectEngineDeterministic:
    """Tests for deterministic output."""

    def test_same_input_same_output(self) -> None:
        """Same input always produces same output."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
        )
        program = _make_program(rooms)
        result1 = engine.analyze(program)
        result2 = engine.analyze(program)
        assert result1 == result2
        assert result1.to_dict() == result2.to_dict()


class TestArchitectEnginePipelineOrder:
    """Tests for pipeline order."""

    def test_pipeline_generates_bubble_diagram_first(self) -> None:
        """Pipeline generates bubble diagram before zoning."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        # Bubble diagram should have nodes
        assert result.bubble_diagram.room_count == 2
        # Zoning result should have zones
        assert result.zoning_result.total_zone_count >= 1


class TestArchitectEngineMetadata:
    """Tests for metadata."""

    def test_metadata_present(self) -> None:
        """Metadata is present in result."""
        engine = ArchitectEngine()
        rooms = (_make_room("living", "living", "Living Room", 200.0),)
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert "source" in result.metadata
        assert result.metadata["source"] == "architect_engine"
        assert "program_room_count" in result.metadata
        assert result.metadata["program_room_count"] == 1
        assert "floor_count" in result.metadata
        assert result.metadata["floor_count"] == 1


class TestArchitectEngineComputedProperties:
    """Tests for computed properties."""

    def test_room_count_matches_diagram(self) -> None:
        """Room count matches bubble diagram."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.room_count == result.bubble_diagram.room_count

    def test_zone_count_matches_zoning(self) -> None:
        """Zone count matches zoning result."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.zone_count == result.zoning_result.total_zone_count

    def test_connection_count_matches_diagram(self) -> None:
        """Connection count matches bubble diagram."""
        engine = ArchitectEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.connection_count == result.bubble_diagram.connection_count


class TestArchitectEngineCustomInstances:
    """Tests for custom engine instances."""

    def test_custom_bubble_generator(self) -> None:
        """Custom bubble generator can be used."""
        bubble_gen = BubbleGenerator()
        zoning_eng = ZoningEngine()
        engine = ArchitectEngine(
            bubble_generator=bubble_gen,
            zoning_engine=zoning_eng,
        )
        rooms = (_make_room("living", "living", "Living Room", 200.0),)
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.room_count == 1

    def test_default_instances(self) -> None:
        """Default instances are created when not provided."""
        engine = ArchitectEngine()
        rooms = (_make_room("living", "living", "Living Room", 200.0),)
        program = _make_program(rooms)
        result = engine.analyze(program)
        assert result.room_count == 1