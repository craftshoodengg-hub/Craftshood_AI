"""Tests for zoning engine."""
from __future__ import annotations

import pytest

from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.architect.bubble_diagram import BubbleDiagram
from building_model_v2.architect.bubble_generator import BubbleGenerator
from building_model_v2.architect.zone import Zone
from building_model_v2.architect.zoning_engine import ZoningEngine
from building_model_v2.architect.zoning_result import ZoningResult
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


def _generate_diagram(program: SpaceProgram) -> BubbleDiagram:
    """Helper to generate a diagram from a program."""
    generator = BubbleGenerator()
    return generator.generate(program)


class TestZoningEngineEmpty:
    """Tests for empty diagram zoning."""

    def test_empty_diagram(self) -> None:
        """Empty diagram produces empty zoning result."""
        engine = ZoningEngine()
        diagram = BubbleDiagram()
        result = engine.analyze(diagram)
        assert result.total_zone_count == 0
        assert result.assigned_room_count == 0
        assert result.zones == ()
        assert result.unassigned_rooms == ()


class TestZoningEngine1BHK:
    """Tests for 1BHK zoning."""

    def test_1bhk_zoning(self) -> None:
        """1BHK produces correct zones."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("bathroom", "bathroom", "Bathroom", 50.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        assert result.total_zone_count >= 3
        assert result.assigned_room_count == 5
        assert len(result.unassigned_rooms) == 0

    def test_1bhk_public_zone(self) -> None:
        """1BHK has public zone with living and entrance."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        public_zones = [z for z in result.zones if z.zone_type == "PUBLIC"]
        assert len(public_zones) == 1
        public_room_ids = {r.id for r in public_zones[0].rooms}
        assert "living" in public_room_ids
        assert "entrance" in public_room_ids


class TestZoningEngine2BHK:
    """Tests for 2BHK zoning."""

    def test_2bhk_zoning(self) -> None:
        """2BHK produces correct zones."""
        engine = ZoningEngine()
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
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        assert result.total_zone_count >= 3
        assert result.assigned_room_count == 7


class TestZoningEngine3BHK:
    """Tests for 3BHK zoning."""

    def test_3bhk_zoning(self) -> None:
        """3BHK produces correct zones."""
        engine = ZoningEngine()
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
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        assert result.total_zone_count >= 3
        assert result.assigned_room_count == 9


class TestZoningEngineDuplex:
    """Tests for duplex zoning."""

    def test_duplex_zoning(self) -> None:
        """Duplex produces vertical zone."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0, floor_preference=FloorPreference.GROUND),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0, floor_preference=FloorPreference.GROUND),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0, floor_preference=FloorPreference.UPPER),
            _make_room("stair", "stair", "Stair", 50.0, floor_preference=FloorPreference.ANY),
            _make_room("entrance", "entrance", "Entrance", 20.0, floor_preference=FloorPreference.GROUND),
        )
        program = _make_program(rooms, floor_count=2)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        vertical_zones = [z for z in result.zones if z.zone_type == "VERTICAL"]
        assert len(vertical_zones) == 1
        assert vertical_zones[0].rooms[0].id == "stair"


class TestZoningEngineParking:
    """Tests for parking zoning."""

    def test_parking_service_zone(self) -> None:
        """Parking is in service zone."""
        engine = ZoningEngine()
        rooms = (
            _make_room("parking", "parking", "Parking", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        service_zones = [z for z in result.zones if z.zone_type == "SERVICE"]
        assert len(service_zones) == 1
        service_room_ids = {r.id for r in service_zones[0].rooms}
        assert "parking" in service_room_ids


class TestZoningEngineBalcony:
    """Tests for balcony zoning."""

    def test_balcony_outdoor_zone(self) -> None:
        """Balcony is in outdoor zone."""
        engine = ZoningEngine()
        rooms = (
            _make_room("balcony", "balcony", "Balcony", 60.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        outdoor_zones = [z for z in result.zones if z.zone_type == "OUTDOOR"]
        assert len(outdoor_zones) == 1
        assert outdoor_zones[0].rooms[0].id == "balcony"


class TestZoningEngineOffice:
    """Tests for office zoning."""

    def test_office_semi_private_zone(self) -> None:
        """Office is in semi-private zone."""
        engine = ZoningEngine()
        rooms = (
            _make_room("office", "office", "Office", 80.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        semi_private_zones = [z for z in result.zones if z.zone_type == "SEMI_PRIVATE"]
        assert len(semi_private_zones) >= 1
        all_semi_private_ids = set()
        for z in semi_private_zones:
            all_semi_private_ids.update(r.id for r in z.rooms)
        assert "office" in all_semi_private_ids


class TestZoningEnginePooja:
    """Tests for pooja room zoning."""

    def test_pooja_semi_private_zone(self) -> None:
        """Pooja room is in semi-private zone."""
        engine = ZoningEngine()
        rooms = (
            _make_room("pooja", "pooja", "Pooja", 40.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        semi_private_zones = [z for z in result.zones if z.zone_type == "SEMI_PRIVATE"]
        all_semi_private_ids = set()
        for z in semi_private_zones:
            all_semi_private_ids.update(r.id for r in z.rooms)
        assert "pooja" in all_semi_private_ids


class TestZoningEngineStair:
    """Tests for stair zoning."""

    def test_stair_vertical_zone(self) -> None:
        """Stair is in vertical zone."""
        engine = ZoningEngine()
        rooms = (
            _make_room("stair", "stair", "Stair", 50.0),
            _make_room("living", "living", "Living Room", 200.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        vertical_zones = [z for z in result.zones if z.zone_type == "VERTICAL"]
        assert len(vertical_zones) == 1
        assert vertical_zones[0].rooms[0].id == "stair"


class TestZoningEngineSerialization:
    """Tests for serialization."""

    def test_zone_serialization(self) -> None:
        """Zone can be serialized and deserialized."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        zone = result.zones[0]
        data = zone.to_dict()
        restored = Zone.from_dict(data)
        assert zone == restored

    def test_zoning_result_serialization(self) -> None:
        """ZoningResult can be serialized and deserialized."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        data = result.to_dict()
        restored = ZoningResult.from_dict(data)
        assert result == restored


class TestZoningEngineDeterministic:
    """Tests for deterministic zoning."""

    def test_same_input_same_output(self) -> None:
        """Same input always produces same output."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("dining", "dining", "Dining", 120.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result1 = engine.analyze(diagram)
        result2 = engine.analyze(diagram)
        assert result1 == result2
        assert result1.to_dict() == result2.to_dict()


class TestZoningEngineAreaCalculation:
    """Tests for area calculation."""

    def test_zone_total_area(self) -> None:
        """Zone total_area is sum of room areas."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        public_zones = [z for z in result.zones if z.zone_type == "PUBLIC"]
        assert len(public_zones) == 1
        assert public_zones[0].total_area == 220.0


class TestZoningEngineDuplicatePrevention:
    """Tests for duplicate prevention."""

    def test_no_duplicate_rooms(self) -> None:
        """No room appears in multiple zones."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("bathroom", "bathroom", "Bathroom", 50.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        all_room_ids = []
        for zone in result.zones:
            all_room_ids.extend(r.id for r in zone.rooms)
        assert len(all_room_ids) == len(set(all_room_ids))

    def test_all_rooms_assigned(self) -> None:
        """All rooms are assigned to zones."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("bedroom", "bedroom", "Bedroom", 150.0),
            _make_room("kitchen", "kitchen", "Kitchen", 100.0),
            _make_room("bathroom", "bathroom", "Bathroom", 50.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        assert result.assigned_room_count == 5
        assert len(result.unassigned_rooms) == 0


class TestZoningEngineValidation:
    """Tests for validation."""

    def test_zone_room_count(self) -> None:
        """Zone room_count matches actual rooms."""
        engine = ZoningEngine()
        rooms = (
            _make_room("living", "living", "Living Room", 200.0),
            _make_room("entrance", "entrance", "Entrance", 20.0),
        )
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        for zone in result.zones:
            assert zone.room_count == len(zone.rooms)

    def test_metadata_present(self) -> None:
        """Metadata is present in result."""
        engine = ZoningEngine()
        rooms = (_make_room("living", "living", "Living Room", 200.0),)
        program = _make_program(rooms)
        diagram = _generate_diagram(program)
        result = engine.analyze(diagram)
        assert "source" in result.metadata
        assert result.metadata["source"] == "zoning_engine"
        assert "total_rooms" in result.metadata