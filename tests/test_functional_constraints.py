"""Unit tests for Functional Constraints."""

from __future__ import annotations

import pytest

from building_model_v2.constraints import (
    ConstraintCategory,
    ConstraintEngine,
    ConstraintResult,
    ConstraintSeverity,
    FunctionalConstraint,
)
from building_model_v2.constraints.functional_constraints import (
    EmptyBuildingConstraint,
    EmptyFloorConstraint,
    IsolatedRoomConstraint,
    RoomWithoutDoorConstraint,
    RoomWithoutWindowConstraint,
    UnconnectedFloorConstraint,
)
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.relationships import Relationship, RelationshipType
from building_model_v2.types import FloorType, RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel


# ============================================================================
# Helper functions
# ============================================================================


def create_building_with_floors() -> BuildingModel:
    """Create a building model with one floor."""
    floor1 = Floor.create(
        name="Ground Floor",
        level=0,
        elevation=0.0,
        floor_height=10.0,
        slab_thickness=0.5,
        floor_type=FloorType.GROUND,
    )
    building = Building.create(
        name="Test Building",
        floor_ids=(floor1.id,),
    )
    return BuildingModel(
        building=building,
        floors={floor1.id: floor1},
    )


def create_building_with_room(
    has_door: bool = True,
    has_window: bool = True,
) -> BuildingModel:
    """Create a building model with a room.
    
    Args:
        has_door: Whether the room has a door.
        has_window: Whether the room has a window.
    """
    door_ids = frozenset(["door-1"]) if has_door else frozenset()
    window_ids = frozenset(["window-1"]) if has_window else frozenset()
    
    room1 = Room.create(
        vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
        room_type=RoomType.LIVING,
        floor_id="floor-1",
        door_ids=door_ids,
        window_ids=window_ids,
        metadata={"name": "Living Room"},
    )
    floor1 = Floor.create(
        name="Ground Floor",
        level=0,
        elevation=0.0,
        floor_height=10.0,
        slab_thickness=0.5,
        floor_type=FloorType.GROUND,
        room_ids=frozenset([room1.id]),
    )
    building = Building.create(
        name="Test Building",
        floor_ids=(floor1.id,),
    )
    return BuildingModel(
        building=building,
        floors={floor1.id: floor1},
        rooms={room1.id: room1},
    )


# ============================================================================
# ConstraintCategory tests
# ============================================================================


class TestConstraintCategory:
    """Tests for ConstraintCategory enum."""
    
    def test_enum_values(self) -> None:
        assert ConstraintCategory.FUNCTIONAL.value == "functional"
        assert ConstraintCategory.BUILDING_CODE.value == "building_code"
        assert ConstraintCategory.ACCESSIBILITY.value == "accessibility"
        assert ConstraintCategory.STRUCTURAL.value == "structural"
        assert ConstraintCategory.ENVIRONMENTAL.value == "environmental"
        assert ConstraintCategory.VASTU.value == "vastu"
        assert ConstraintCategory.CUSTOM.value == "custom"
    
    def test_str_representation(self) -> None:
        assert str(ConstraintCategory.FUNCTIONAL) == "functional"
        assert str(ConstraintCategory.BUILDING_CODE) == "building_code"
    
    def test_repr_representation(self) -> None:
        assert repr(ConstraintCategory.FUNCTIONAL) == "ConstraintCategory.FUNCTIONAL"
    
    def test_display_name(self) -> None:
        assert ConstraintCategory.FUNCTIONAL.display_name == "Functional"
        assert ConstraintCategory.BUILDING_CODE.display_name == "Building Code"
        assert ConstraintCategory.ACCESSIBILITY.display_name == "Accessibility"
        assert ConstraintCategory.STRUCTURAL.display_name == "Structural"
        assert ConstraintCategory.ENVIRONMENTAL.display_name == "Environmental"
        assert ConstraintCategory.VASTU.display_name == "Vastu"
        assert ConstraintCategory.CUSTOM.display_name == "Custom"


# ============================================================================
# FunctionalConstraint base class tests
# ============================================================================


class TestFunctionalConstraint:
    """Tests for FunctionalConstraint base class."""
    
    def test_create_with_defaults(self) -> None:
        class TestConstraint(FunctionalConstraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        constraint = TestConstraint(name="Test")
        assert constraint.name == "Test"
        assert constraint.description == ""
        assert constraint.category == ConstraintCategory.FUNCTIONAL
        assert constraint.default_severity == ConstraintSeverity.WARNING
    
    def test_create_with_custom_values(self) -> None:
        class TestConstraint(FunctionalConstraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        constraint = TestConstraint(
            name="Test",
            description="A test constraint",
            category=ConstraintCategory.ACCESSIBILITY,
            default_severity=ConstraintSeverity.RECOMMENDATION,
        )
        assert constraint.name == "Test"
        assert constraint.description == "A test constraint"
        assert constraint.category == ConstraintCategory.ACCESSIBILITY
        assert constraint.default_severity == ConstraintSeverity.RECOMMENDATION


# ============================================================================
# EmptyBuildingConstraint tests
# ============================================================================


class TestEmptyBuildingConstraint:
    """Tests for EmptyBuildingConstraint."""
    
    def test_metadata(self) -> None:
        constraint = EmptyBuildingConstraint()
        assert constraint.name == "Empty Building"
        assert constraint.description == "Checks if the building has no floors"
        assert constraint.category == ConstraintCategory.FUNCTIONAL
        assert constraint.default_severity == ConstraintSeverity.WARNING
    
    def test_empty_building(self) -> None:
        model = BuildingModel()
        constraint = EmptyBuildingConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "EMPTY_BUILDING"
        assert result.issues[0].severity == ConstraintSeverity.WARNING
    
    def test_building_with_floors(self) -> None:
        model = create_building_with_floors()
        constraint = EmptyBuildingConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
        assert result.issue_count == 0


# ============================================================================
# EmptyFloorConstraint tests
# ============================================================================


class TestEmptyFloorConstraint:
    """Tests for EmptyFloorConstraint."""
    
    def test_metadata(self) -> None:
        constraint = EmptyFloorConstraint()
        assert constraint.name == "Empty Floor"
        assert constraint.description == "Checks if any floor has no associated entities"
        assert constraint.category == ConstraintCategory.FUNCTIONAL
        assert constraint.default_severity == ConstraintSeverity.WARNING
    
    def test_empty_floor(self) -> None:
        floor1 = Floor.create(
            name="Empty Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        model = BuildingModel(floors={floor1.id: floor1})
        constraint = EmptyFloorConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "EMPTY_FLOOR"
        assert result.issues[0].entity_id == floor1.id
    
    def test_floor_with_rooms(self) -> None:
        model = create_building_with_room()
        constraint = EmptyFloorConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_floors_mixed(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        floor2 = Floor.create(
            name="First Floor",
            level=1,
            elevation=10.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
            room_ids=frozenset(["room-1"]),
        )
        model = BuildingModel(floors={floor1.id: floor1, floor2.id: floor2})
        constraint = EmptyFloorConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == floor1.id


# ============================================================================
# RoomWithoutDoorConstraint tests
# ============================================================================


class TestRoomWithoutDoorConstraint:
    """Tests for RoomWithoutDoorConstraint."""
    
    def test_metadata(self) -> None:
        constraint = RoomWithoutDoorConstraint()
        assert constraint.name == "Room Without Door"
        assert constraint.description == "Checks if any room has no doors for access"
        assert constraint.category == ConstraintCategory.FUNCTIONAL
        assert constraint.default_severity == ConstraintSeverity.RECOMMENDATION
    
    def test_room_without_door(self) -> None:
        model = create_building_with_room(has_door=False)
        constraint = RoomWithoutDoorConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "ROOM_WITHOUT_DOOR"
        assert result.issues[0].entity_type == "Room"
    
    def test_room_with_door(self) -> None:
        model = create_building_with_room(has_door=True)
        constraint = RoomWithoutDoorConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_rooms_mixed(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            door_ids=frozenset(["door-1"]),
            metadata={"name": "Living Room"},
        )
        room2 = Room.create(
            vertices=[(0, 0), (5, 0), (5, 5), (0, 5)],
            room_type=RoomType.BEDROOM,
            metadata={"name": "Bedroom"},
        )
        model = BuildingModel(rooms={"room-1": room1, "room-2": room2})
        constraint = RoomWithoutDoorConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "room-2"


# ============================================================================
# RoomWithoutWindowConstraint tests
# ============================================================================


class TestRoomWithoutWindowConstraint:
    """Tests for RoomWithoutWindowConstraint."""
    
    def test_metadata(self) -> None:
        constraint = RoomWithoutWindowConstraint()
        assert constraint.name == "Room Without Window"
        assert constraint.description == "Checks if any room has no windows for ventilation and light"
        assert constraint.category == ConstraintCategory.FUNCTIONAL
        assert constraint.default_severity == ConstraintSeverity.SUGGESTION
    
    def test_room_without_window(self) -> None:
        model = create_building_with_room(has_window=False)
        constraint = RoomWithoutWindowConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "ROOM_WITHOUT_WINDOW"
        assert result.issues[0].entity_type == "Room"
    
    def test_room_with_window(self) -> None:
        model = create_building_with_room(has_window=True)
        constraint = RoomWithoutWindowConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_rooms_mixed(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            window_ids=frozenset(["window-1"]),
            metadata={"name": "Living Room"},
        )
        room2 = Room.create(
            vertices=[(0, 0), (5, 0), (5, 5), (0, 5)],
            room_type=RoomType.BEDROOM,
            metadata={"name": "Bedroom"},
        )
        model = BuildingModel(rooms={"room-1": room1, "room-2": room2})
        constraint = RoomWithoutWindowConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "room-2"


# ============================================================================
# IsolatedRoomConstraint tests
# ============================================================================


class TestIsolatedRoomConstraint:
    """Tests for IsolatedRoomConstraint."""
    
    def test_metadata(self) -> None:
        constraint = IsolatedRoomConstraint()
        assert constraint.name == "Isolated Room"
        assert constraint.description == "Checks if any room has no connections to other rooms"
        assert constraint.category == ConstraintCategory.FUNCTIONAL
        assert constraint.default_severity == ConstraintSeverity.SUGGESTION
    
    def test_isolated_room(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            metadata={"name": "Living Room"},
        )
        model = BuildingModel(rooms={"room-1": room1})
        constraint = IsolatedRoomConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "ISOLATED_ROOM"
    
    def test_connected_rooms(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            metadata={"name": "Living Room"},
        )
        room2 = Room.create(
            vertices=[(0, 0), (5, 0), (5, 5), (0, 5)],
            room_type=RoomType.BEDROOM,
            metadata={"name": "Bedroom"},
        )
        relationship = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-2",
        )
        model = BuildingModel(
            rooms={"room-1": room1, "room-2": room2},
            relationships=[relationship],
        )
        constraint = IsolatedRoomConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_rooms_partial_connection(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            metadata={"name": "Living Room"},
        )
        room2 = Room.create(
            vertices=[(0, 0), (5, 0), (5, 5), (0, 5)],
            room_type=RoomType.BEDROOM,
            metadata={"name": "Bedroom"},
        )
        room3 = Room.create(
            vertices=[(0, 0), (3, 0), (3, 3), (0, 3)],
            room_type=RoomType.KITCHEN,
            metadata={"name": "Kitchen"},
        )
        relationship = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-2",
        )
        model = BuildingModel(
            rooms={"room-1": room1, "room-2": room2, "room-3": room3},
            relationships=[relationship],
        )
        constraint = IsolatedRoomConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "room-3"


# ============================================================================
# UnconnectedFloorConstraint tests
# ============================================================================


class TestUnconnectedFloorConstraint:
    """Tests for UnconnectedFloorConstraint."""
    
    def test_metadata(self) -> None:
        constraint = UnconnectedFloorConstraint()
        assert constraint.name == "Unconnected Floor"
        assert constraint.description == "Checks if any floor has no connections via relationships"
        assert constraint.category == ConstraintCategory.FUNCTIONAL
        assert constraint.default_severity == ConstraintSeverity.WARNING
    
    def test_unconnected_floor(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        model = BuildingModel(floors={floor1.id: floor1})
        constraint = UnconnectedFloorConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "UNCONNECTED_FLOOR"
    
    def test_connected_floors(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        floor2 = Floor.create(
            name="First Floor",
            level=1,
            elevation=10.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
        )
        # Use BUILDING_TO_FLOOR relationship to connect floors via building
        relationship1 = Relationship.create(
            relationship_type=RelationshipType.BUILDING_TO_FLOOR,
            source_id="building-1",
            target_id=floor1.id,
        )
        relationship2 = Relationship.create(
            relationship_type=RelationshipType.BUILDING_TO_FLOOR,
            source_id="building-1",
            target_id=floor2.id,
        )
        model = BuildingModel(
            floors={floor1.id: floor1, floor2.id: floor2},
            relationships=[relationship1, relationship2],
        )
        constraint = UnconnectedFloorConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_floors_partial_connection(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        floor2 = Floor.create(
            name="First Floor",
            level=1,
            elevation=10.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
        )
        floor3 = Floor.create(
            name="Second Floor",
            level=2,
            elevation=20.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
        )
        # Only connect floor1 and floor2 via BUILDING_TO_FLOOR
        relationship1 = Relationship.create(
            relationship_type=RelationshipType.BUILDING_TO_FLOOR,
            source_id="building-1",
            target_id=floor1.id,
        )
        relationship2 = Relationship.create(
            relationship_type=RelationshipType.BUILDING_TO_FLOOR,
            source_id="building-1",
            target_id=floor2.id,
        )
        model = BuildingModel(
            floors={floor1.id: floor1, floor2.id: floor2, floor3.id: floor3},
            relationships=[relationship1, relationship2],
        )
        constraint = UnconnectedFloorConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == floor3.id


# ============================================================================
# Constraint Engine Integration tests
# ============================================================================


class TestConstraintEngineIntegration:
    """Tests for constraint engine with functional constraints."""
    
    def test_engine_with_multiple_constraints(self) -> None:
        model = BuildingModel()
        engine = ConstraintEngine()
        engine.register(EmptyBuildingConstraint())
        engine.register(EmptyFloorConstraint())
        result = engine.evaluate(model)
        assert result.issue_count == 1  # Only EmptyBuilding fires
    
    def test_engine_with_all_constraints(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            metadata={"name": "Living Room"},
        )
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        model = BuildingModel(
            floors={floor1.id: floor1},
            rooms={"room-1": room1},
        )
        engine = ConstraintEngine()
        engine.register(EmptyBuildingConstraint())
        engine.register(EmptyFloorConstraint())
        engine.register(RoomWithoutDoorConstraint())
        engine.register(RoomWithoutWindowConstraint())
        engine.register(IsolatedRoomConstraint())
        result = engine.evaluate(model)
        assert result.issue_count >= 4  # EmptyFloor + NoDoor + NoWindow + Isolated
    
    def test_engine_empty_optimal(self) -> None:
        model = create_building_with_room()
        engine = ConstraintEngine()
        engine.register(RoomWithoutDoorConstraint())
        engine.register(RoomWithoutWindowConstraint())
        result = engine.evaluate(model)
        assert result.is_optimal is True


# ============================================================================
# Multiple simultaneous issues tests
# ============================================================================


class TestMultipleSimultaneousIssues:
    """Tests for multiple issues occurring simultaneously."""
    
    def test_all_constraint_types_firing(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            metadata={"name": "Living Room"},
        )
        floor1 = Floor.create(
            name="Empty Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        floor2 = Floor.create(
            name="Another Empty Floor",
            level=1,
            elevation=10.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
        )
        model = BuildingModel(
            floors={floor1.id: floor1, floor2.id: floor2},
            rooms={"room-1": room1},
        )
        engine = ConstraintEngine()
        engine.register(EmptyFloorConstraint())
        engine.register(RoomWithoutDoorConstraint())
        engine.register(RoomWithoutWindowConstraint())
        engine.register(IsolatedRoomConstraint())
        engine.register(UnconnectedFloorConstraint())
        result = engine.evaluate(model)
        assert result.issue_count >= 5  # 2 EmptyFloor + NoDoor + NoWindow + Isolated + 2 UnconnectedFloor
    
    def test_severity_counts(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            metadata={"name": "Living Room"},
        )
        model = BuildingModel(rooms={"room-1": room1})
        engine = ConstraintEngine()
        engine.register(RoomWithoutDoorConstraint())  # RECOMMENDATION
        engine.register(RoomWithoutWindowConstraint())  # SUGGESTION
        engine.register(IsolatedRoomConstraint())  # SUGGESTION
        result = engine.evaluate(model)
        assert result.recommendation_count == 1
        assert result.suggestion_count == 2


# ============================================================================
# Serialization tests
# ============================================================================


class TestSerialization:
    """Tests for serialization compatibility."""
    
    def test_empty_building_issue_serialization(self) -> None:
        constraint = EmptyBuildingConstraint()
        model = BuildingModel()
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert len(d["issues"]) == 1
        assert d["issues"][0]["code"] == "EMPTY_BUILDING"
    
    def test_room_without_door_issue_serialization(self) -> None:
        constraint = RoomWithoutDoorConstraint()
        model = create_building_with_room(has_door=False)
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert d["issues"][0]["code"] == "ROOM_WITHOUT_DOOR"
        assert d["issues"][0]["severity"] == "recommendation"
    
    def test_result_round_trip(self) -> None:
        constraint = EmptyBuildingConstraint()
        model = BuildingModel()
        result = constraint.evaluate(model)
        d = result.to_dict()
        restored = ConstraintResult.from_dict(d)
        assert restored == result