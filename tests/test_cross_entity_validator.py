"""Unit tests for CrossEntityValidator."""

from __future__ import annotations

import pytest

from building_model_v2.entities_building import Building
from building_model_v2.entities_column import Column
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.entities_wall import Wall
from building_model_v2.relationships import Relationship, RelationshipType
from building_model_v2.types import ColumnType, FloorType, RoomType, StairType, WallType
from building_model_v2.validation import (
    CrossEntityValidationConfig,
    CrossEntityValidator,
)
from building_model_v2.validation.cross_entity_validator import (
    BUILDING_UNKNOWN_FLOOR,
    COLUMN_UNKNOWN_FLOOR,
    CrossEntityValidationConfig as Config,
    BuildingModel,
    FLOOR_UNKNOWN_COLUMN,
    FLOOR_UNKNOWN_ROOM,
    FLOOR_UNKNOWN_STAIR,
    RELATIONSHIP_UNKNOWN_SOURCE,
    RELATIONSHIP_UNKNOWN_TARGET,
    ROOM_UNKNOWN_DOOR,
    ROOM_UNKNOWN_WALL,
    ROOM_UNKNOWN_WINDOW,
    STAIR_UNKNOWN_FLOOR,
)


# ============================================================================
# Helper functions
# ============================================================================


def create_valid_building_model() -> BuildingModel:
    """Create a valid building model with all references intact."""
    # Create walls
    wall1 = Wall.create(
        start=(0, 0),
        end=(10, 0),
        width=0.5,
        wall_type=WallType.EXTERIOR,
        floor_id="floor-1",
    )
    wall2 = Wall.create(
        start=(10, 0),
        end=(10, 10),
        width=0.5,
        wall_type=WallType.INTERIOR,
        floor_id="floor-1",
    )
    
    # Create room
    room1 = Room.create(
        vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
        room_type=RoomType.LIVING,
        floor_id="floor-1",
        wall_ids=frozenset([wall1.id, wall2.id]),
    )
    
    # Create column
    column1 = Column.create(
        location=(5, 5),
        size=1.0,
        column_type=ColumnType.RECTANGULAR,
        floor_id="floor-1",
    )
    
    # Create stair
    stair1 = Stair.create(
        start=(0, 0),
        end=(5, 5),
        stair_type=StairType.STRAIGHT,
        floor_id="floor-1",
    )
    
    # Create floor
    floor1 = Floor.create(
        name="Ground Floor",
        level=0,
        elevation=0.0,
        floor_height=10.0,
        slab_thickness=0.5,
        floor_type=FloorType.GROUND,
        room_ids=frozenset([room1.id]),
        column_ids=frozenset([column1.id]),
        stair_ids=frozenset([stair1.id]),
    )
    
    # Create building
    building = Building.create(
        name="Test Building",
        floor_ids=(floor1.id,),
    )
    
    return BuildingModel(
        building=building,
        floors={floor1.id: floor1},
        rooms={room1.id: room1},
        walls={wall1.id: wall1, wall2.id: wall2},
        columns={column1.id: column1},
        stairs={stair1.id: stair1},
        relationships=[],
    )


# ============================================================================
# Config tests
# ============================================================================


class TestCrossEntityValidationConfig:
    """Tests for CrossEntityValidationConfig."""
    
    def test_default_values(self) -> None:
        config = CrossEntityValidationConfig()
        assert config.require_room_walls is False
        assert config.require_door_wall is False
        assert config.require_window_wall is False
        assert config.require_stair_floors is False
        assert config.require_building_floors is False
        assert config.allow_orphan_entities is True
    
    def test_custom_values(self) -> None:
        config = CrossEntityValidationConfig(
            require_room_walls=True,
            require_door_wall=True,
            require_window_wall=True,
            require_stair_floors=True,
            require_building_floors=True,
            allow_orphan_entities=False,
        )
        assert config.require_room_walls is True
        assert config.require_door_wall is True
        assert config.require_window_wall is True
        assert config.require_stair_floors is True
        assert config.require_building_floors is True
        assert config.allow_orphan_entities is False


# ============================================================================
# Valid model tests
# ============================================================================


class TestCrossEntityValidatorValid:
    """Tests for valid building model validation."""
    
    def test_valid_building_model(self) -> None:
        model = create_valid_building_model()
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_empty_building_model(self) -> None:
        model = BuildingModel()
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True
    
    def test_building_without_floors(self) -> None:
        building = Building.create(name="Empty Building")
        model = BuildingModel(building=building)
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Invalid input tests
# ============================================================================


class TestCrossEntityValidatorInvalidInput:
    """Tests for invalid input handling."""
    
    def test_non_building_model(self) -> None:
        validator = CrossEntityValidator()
        result = validator.validate("not a model")
        assert result.error_count == 1
    
    def test_none_input(self) -> None:
        validator = CrossEntityValidator()
        result = validator.validate(None)
        assert result.error_count == 1


# ============================================================================
# Building reference tests
# ============================================================================


class TestBuildingReferences:
    """Tests for building reference validation."""
    
    def test_building_unknown_floor(self) -> None:
        building = Building.create(
            name="Test Building",
            floor_ids=("floor-1", "floor-missing"),
        )
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
        )
        model = BuildingModel(
            building=building,
            floors={"floor-1": floor1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == BUILDING_UNKNOWN_FLOOR
    
    def test_building_unknown_floor_strict(self) -> None:
        building = Building.create(
            name="Test Building",
            floor_ids=("floor-missing",),
        )
        config = CrossEntityValidationConfig(require_building_floors=True)
        validator = CrossEntityValidator(config)
        result = validator.validate(BuildingModel(building=building))
        assert result.error_count == 1
        assert result.errors[0].code == BUILDING_UNKNOWN_FLOOR
    
    def test_building_all_floors_exist(self) -> None:
        building = Building.create(
            name="Test Building",
            floor_ids=("floor-1", "floor-2"),
        )
        floor1 = Floor.create(name="Floor 1", level=0, floor_type=FloorType.GROUND)
        floor2 = Floor.create(name="Floor 2", level=1, floor_type=FloorType.UPPER)
        model = BuildingModel(
            building=building,
            floors={"floor-1": floor1, "floor-2": floor2},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Floor reference tests
# ============================================================================


class TestFloorReferences:
    """Tests for floor reference validation."""
    
    def test_floor_unknown_room(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
            room_ids=frozenset(["room-missing"]),
        )
        model = BuildingModel(
            floors={"floor-1": floor1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == FLOOR_UNKNOWN_ROOM
    
    def test_floor_unknown_column(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
            column_ids=frozenset(["col-missing"]),
        )
        model = BuildingModel(
            floors={"floor-1": floor1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == FLOOR_UNKNOWN_COLUMN
    
    def test_floor_unknown_stair(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
            stair_ids=frozenset(["stair-missing"]),
        )
        model = BuildingModel(
            floors={"floor-1": floor1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == FLOOR_UNKNOWN_STAIR
    
    def test_floor_all_references_valid(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        )
        column1 = Column.create(location=(5, 5), size=1.0, column_type=ColumnType.RECTANGULAR)
        stair1 = Stair.create(start=(0, 0), end=(5, 5), stair_type=StairType.STRAIGHT)
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
            room_ids=frozenset([room1.id]),
            column_ids=frozenset([column1.id]),
            stair_ids=frozenset([stair1.id]),
        )
        model = BuildingModel(
            floors={"floor-1": floor1},
            rooms={"room-1": room1},
            columns={"col-1": column1},
            stairs={"stair-1": stair1},
        )
        # Override IDs to match floor references
        model.rooms = {room1.id: room1}
        model.columns = {column1.id: column1}
        model.stairs = {stair1.id: stair1}
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Room reference tests
# ============================================================================


class TestRoomReferences:
    """Tests for room reference validation."""
    
    def test_room_unknown_wall(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            wall_ids=frozenset(["wall-missing"]),
        )
        model = BuildingModel(
            rooms={"room-1": room1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == ROOM_UNKNOWN_WALL
    
    def test_room_unknown_wall_strict(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            wall_ids=frozenset(["wall-missing"]),
        )
        config = CrossEntityValidationConfig(require_room_walls=True)
        validator = CrossEntityValidator(config)
        result = validator.validate(BuildingModel(rooms={"room-1": room1}))
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_UNKNOWN_WALL
    
    def test_room_unknown_door(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            door_ids=frozenset(["door-missing"]),
        )
        model = BuildingModel(
            rooms={"room-1": room1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == ROOM_UNKNOWN_DOOR
    
    def test_room_unknown_window(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            window_ids=frozenset(["window-missing"]),
        )
        model = BuildingModel(
            rooms={"room-1": room1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == ROOM_UNKNOWN_WINDOW
    
    def test_room_all_references_valid(self) -> None:
        wall1 = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            wall_ids=frozenset([wall1.id]),
        )
        model = BuildingModel(
            rooms={room1.id: room1},
            walls={wall1.id: wall1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Wall reference tests
# ============================================================================


class TestWallReferences:
    """Tests for wall reference validation."""
    
    def test_wall_unknown_floor(self) -> None:
        wall1 = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-missing",
        )
        model = BuildingModel(
            walls={"wall-1": wall1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
    
    def test_wall_valid_floor(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
        )
        wall1 = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        model = BuildingModel(
            walls={wall1.id: wall1},
            floors={"floor-1": floor1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Column reference tests
# ============================================================================


class TestColumnReferences:
    """Tests for column reference validation."""
    
    def test_column_unknown_floor(self) -> None:
        column1 = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-missing",
        )
        model = BuildingModel(
            columns={"col-1": column1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == COLUMN_UNKNOWN_FLOOR
    
    def test_column_unknown_floor_strict(self) -> None:
        column1 = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-missing",
        )
        config = CrossEntityValidationConfig(require_stair_floors=True)
        validator = CrossEntityValidator(config)
        result = validator.validate(BuildingModel(columns={"col-1": column1}))
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_UNKNOWN_FLOOR
    
    def test_column_valid_floor(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
        )
        column1 = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        model = BuildingModel(
            columns={column1.id: column1},
            floors={"floor-1": floor1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Stair reference tests
# ============================================================================


class TestStairReferences:
    """Tests for stair reference validation."""
    
    def test_stair_unknown_floor(self) -> None:
        stair1 = Stair.create(
            start=(0, 0),
            end=(5, 5),
            stair_type=StairType.STRAIGHT,
            floor_id="floor-missing",
        )
        model = BuildingModel(
            stairs={"stair-1": stair1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == STAIR_UNKNOWN_FLOOR
    
    def test_stair_unknown_floor_strict(self) -> None:
        stair1 = Stair.create(
            start=(0, 0),
            end=(5, 5),
            stair_type=StairType.STRAIGHT,
            floor_id="floor-missing",
        )
        config = CrossEntityValidationConfig(require_stair_floors=True)
        validator = CrossEntityValidator(config)
        result = validator.validate(BuildingModel(stairs={"stair-1": stair1}))
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_UNKNOWN_FLOOR
    
    def test_stair_valid_floor(self) -> None:
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
        )
        stair1 = Stair.create(
            start=(0, 0),
            end=(5, 5),
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        model = BuildingModel(
            stairs={stair1.id: stair1},
            floors={"floor-1": floor1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Relationship reference tests
# ============================================================================


class TestRelationshipReferences:
    """Tests for relationship reference validation."""
    
    def test_relationship_unknown_source(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        )
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="entity-missing",
            target_id=room1.id,
        )
        model = BuildingModel(
            rooms={room1.id: room1},
            relationships=[rel],
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == RELATIONSHIP_UNKNOWN_SOURCE
    
    def test_relationship_unknown_target(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        )
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id=room1.id,
            target_id="entity-missing",
        )
        model = BuildingModel(
            rooms={room1.id: room1},
            relationships=[rel],
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 1
        assert result.warnings[0].code == RELATIONSHIP_UNKNOWN_TARGET
    
    def test_relationship_both_unknown(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="source-missing",
            target_id="target-missing",
        )
        model = BuildingModel(
            relationships=[rel],
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 2
    
    def test_relationship_valid_references(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        )
        wall1 = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        model = BuildingModel(
            rooms={"room-1": room1},
            walls={"wall-1": wall1},
            relationships=[rel],
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True


# ============================================================================
# Multiple errors tests
# ============================================================================


class TestMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_unknown_references(self) -> None:
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            wall_ids=frozenset(["wall-missing-1", "wall-missing-2"]),
            door_ids=frozenset(["door-missing"]),
        )
        model = BuildingModel(
            rooms={"room-1": room1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 3  # 2 walls + 1 door
    
    def test_mixed_errors_and_warnings(self) -> None:
        building = Building.create(
            name="Test Building",
            floor_ids=("floor-missing",),
        )
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            wall_ids=frozenset(["wall-missing"]),
        )
        model = BuildingModel(
            building=building,
            rooms={"room-1": room1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warning_count == 2  # building floor + room wall


# ============================================================================
# Serialization tests
# ============================================================================


class TestSerialization:
    """Tests for serialization compatibility."""
    
    def test_result_can_serialize(self) -> None:
        model = create_valid_building_model()
        validator = CrossEntityValidator()
        result = validator.validate(model)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d
    
    def test_error_includes_entity_id(self) -> None:
        building = Building.create(
            name="Test Building",
            floor_ids=("floor-missing",),
        )
        model = BuildingModel(building=building)
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.warnings[0].entity_id == building.id
        assert result.warnings[0].entity_type == "Building"


# ============================================================================
# Config access tests
# ============================================================================


class TestConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = CrossEntityValidationConfig(require_room_walls=True)
        validator = CrossEntityValidator(config)
        assert validator.config.require_room_walls is True
    
    def test_default_config(self) -> None:
        validator = CrossEntityValidator()
        assert validator.config.require_room_walls is False


# ============================================================================
# Edge case tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_validate_many_not_supported(self) -> None:
        """CrossEntityValidator validates a single BuildingModel, not many."""
        model = create_valid_building_model()
        validator = CrossEntityValidator()
        # validate_many should still work but treat each as BuildingModel
        result = validator.validate_many([model])
        assert result.is_valid is True
    
    def test_empty_relationships(self) -> None:
        model = create_valid_building_model()
        model.relationships = []
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True
    
    def test_all_entity_types_present(self) -> None:
        building = Building.create(name="Test Building", floor_ids=("floor-1",))
        floor1 = Floor.create(
            name="Ground Floor",
            level=0,
            floor_type=FloorType.GROUND,
            room_ids=frozenset(["room-1"]),
            column_ids=frozenset(["col-1"]),
            stair_ids=frozenset(["stair-1"]),
        )
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        )
        wall1 = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        column1 = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
        )
        stair1 = Stair.create(
            start=(0, 0),
            end=(5, 5),
            stair_type=StairType.STRAIGHT,
        )
        
        model = BuildingModel(
            building=building,
            floors={floor1.id: floor1},
            rooms={room1.id: room1},
            walls={wall1.id: wall1},
            columns={column1.id: column1},
            stairs={stair1.id: stair1},
        )
        validator = CrossEntityValidator()
        result = validator.validate(model)
        assert result.is_valid is True
