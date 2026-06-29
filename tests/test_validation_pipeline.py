"""Unit tests for ValidationPipeline."""

from __future__ import annotations

import pytest

from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.relationships import Relationship, RelationshipType
from building_model_v2.types import FloorType, RoomType
from building_model_v2.validation import (
    ValidationPipeline,
    ValidationPipelineConfig,
)
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.validation.validation_result import ValidationResult


# ============================================================================
# Helper functions
# ============================================================================


def create_valid_building_model() -> BuildingModel:
    """Create a valid building model with all references intact."""
    room1 = Room.create(
        vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
        room_type=RoomType.LIVING,
        floor_id="floor-1",
        ceiling_height=10.0,
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


def create_invalid_building_model() -> BuildingModel:
    """Create an invalid building model with broken references."""
    room1 = Room.create(
        vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
        room_type=RoomType.LIVING,
        wall_ids=frozenset(["wall-missing"]),
        ceiling_height=10.0,
        metadata={"name": "Living Room"},
    )
    floor1 = Floor.create(
        name="Ground Floor",
        level=0,
        floor_type=FloorType.GROUND,
        room_ids=frozenset(["room-missing"]),
    )
    building = Building.create(
        name="Test Building",
        floor_ids=("floor-missing",),
    )
    return BuildingModel(
        building=building,
        floors={"floor-1": floor1},
        rooms={"room-1": room1},
    )


# ============================================================================
# Config tests
# ============================================================================


class TestValidationPipelineConfig:
    """Tests for ValidationPipelineConfig."""
    
    def test_default_values(self) -> None:
        config = ValidationPipelineConfig()
        assert config.enable_room_validation is True
        assert config.enable_wall_validation is True
        assert config.enable_door_validation is True
        assert config.enable_window_validation is True
        assert config.enable_stair_validation is True
        assert config.enable_column_validation is True
        assert config.enable_floor_validation is True
        assert config.enable_relationship_validation is True
        assert config.enable_cross_entity_validation is True
        assert config.stop_on_critical is False
    
    def test_custom_values(self) -> None:
        config = ValidationPipelineConfig(
            enable_room_validation=False,
            enable_wall_validation=False,
            enable_door_validation=False,
            enable_window_validation=False,
            enable_stair_validation=False,
            enable_column_validation=False,
            enable_floor_validation=False,
            enable_relationship_validation=False,
            enable_cross_entity_validation=False,
            stop_on_critical=True,
        )
        assert config.enable_room_validation is False
        assert config.enable_wall_validation is False
        assert config.enable_door_validation is False
        assert config.enable_window_validation is False
        assert config.enable_stair_validation is False
        assert config.enable_column_validation is False
        assert config.enable_floor_validation is False
        assert config.enable_relationship_validation is False
        assert config.enable_cross_entity_validation is False
        assert config.stop_on_critical is True


# ============================================================================
# Pipeline validation tests
# ============================================================================


class TestValidationPipelineValid:
    """Tests for valid building model validation."""
    
    def test_valid_building_model(self) -> None:
        model = create_valid_building_model()
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_empty_building_model(self) -> None:
        model = BuildingModel()
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        assert result.is_valid is True


class TestValidationPipelineInvalid:
    """Tests for invalid building model validation."""
    
    def test_invalid_building_model(self) -> None:
        model = create_invalid_building_model()
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        assert result.warning_count > 0


# ============================================================================
# Validator enable/disable tests
# ============================================================================


class TestValidatorEnableDisable:
    """Tests for individual validator enable/disable."""
    
    def test_disable_room_validation(self) -> None:
        model = create_invalid_building_model()
        config = ValidationPipelineConfig(
            enable_room_validation=False,
            enable_cross_entity_validation=False,
        )
        pipeline = ValidationPipeline(config)
        result = pipeline.validate(model)
        # Should have fewer warnings since room validation is disabled
        room_warnings = [w for w in result.warnings if "Room" in w.entity_type]
        assert len(room_warnings) == 0
    
    def test_disable_floor_validation(self) -> None:
        model = create_invalid_building_model()
        config = ValidationPipelineConfig(
            enable_floor_validation=False,
            enable_cross_entity_validation=False,
        )
        pipeline = ValidationPipeline(config)
        result = pipeline.validate(model)
        # Should have fewer warnings since floor validation is disabled
        floor_warnings = [w for w in result.warnings if w.entity_type == "Floor"]
        assert len(floor_warnings) == 0
    
    def test_disable_cross_entity_validation(self) -> None:
        model = create_invalid_building_model()
        config = ValidationPipelineConfig(enable_cross_entity_validation=False)
        pipeline = ValidationPipeline(config)
        result = pipeline.validate(model)
        # Should have fewer warnings since cross-entity validation is disabled
        cross_warnings = [w for w in result.warnings if "unknown" in w.message.lower()]
        assert len(cross_warnings) == 0
    
    def test_disable_relationship_validation(self) -> None:
        model = create_valid_building_model()
        model.relationships = [
            Relationship.create(
                relationship_type=RelationshipType.ROOM_TO_WALL,
                source_id="missing",
                target_id="also-missing",
            )
        ]
        config = ValidationPipelineConfig(
            enable_relationship_validation=False,
            enable_cross_entity_validation=False,
        )
        pipeline = ValidationPipeline(config)
        result = pipeline.validate(model)
        rel_warnings = [w for w in result.warnings if w.entity_type == "Relationship"]
        assert len(rel_warnings) == 0
    
    def test_all_validators_disabled(self) -> None:
        model = create_invalid_building_model()
        config = ValidationPipelineConfig(
            enable_room_validation=False,
            enable_wall_validation=False,
            enable_door_validation=False,
            enable_window_validation=False,
            enable_stair_validation=False,
            enable_column_validation=False,
            enable_floor_validation=False,
            enable_relationship_validation=False,
            enable_cross_entity_validation=False,
        )
        pipeline = ValidationPipeline(config)
        result = pipeline.validate(model)
        assert result.is_valid is True
        assert result.total_count == 0


# ============================================================================
# stop_on_critical tests
# ============================================================================


class TestStopOnCritical:
    """Tests for stop_on_critical behavior."""
    
    def test_stop_on_critical_false(self) -> None:
        """Pipeline should continue validation when stop_on_critical is False."""
        model = create_invalid_building_model()
        config = ValidationPipelineConfig(stop_on_critical=False)
        pipeline = ValidationPipeline(config)
        result = pipeline.validate(model)
        # Should accumulate all warnings
        assert result.warning_count >= 1
    
    def test_stop_on_critical_true_no_critical(self) -> None:
        """Pipeline should continue when no critical errors exist."""
        model = create_invalid_building_model()
        config = ValidationPipelineConfig(stop_on_critical=True)
        pipeline = ValidationPipeline(config)
        result = pipeline.validate(model)
        # Should complete since no critical errors
        assert result.warning_count >= 1


# ============================================================================
# Merge behavior tests
# ============================================================================


class TestMergeBehavior:
    """Tests for result merging behavior."""
    
    def test_merge_results(self) -> None:
        """Pipeline should merge results from multiple validators."""
        model = create_invalid_building_model()
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        # Should have warnings from multiple validators
        assert result.warning_count >= 1
    
    def test_validate_entities_separate(self) -> None:
        """validate_entities should work independently."""
        model = create_valid_building_model()
        pipeline = ValidationPipeline()
        result = pipeline.validate_entities(model)
        assert result.is_valid is True
    
    def test_validate_relationships_separate(self) -> None:
        """validate_relationships should work independently."""
        model = create_valid_building_model()
        model.relationships = [
            Relationship.create(
                relationship_type=RelationshipType.ROOM_TO_ROOM,
                source_id="room-1",
                target_id="room-1",  # Self-reference
            )
        ]
        pipeline = ValidationPipeline()
        result = pipeline.validate_relationships(model)
        assert result.error_count == 1  # Self-reference error
    
    def test_validate_building_separate(self) -> None:
        """validate_building should work independently."""
        model = create_invalid_building_model()
        pipeline = ValidationPipeline()
        result = pipeline.validate_building(model)
        assert result.warning_count >= 1


# ============================================================================
# Configuration tests
# ============================================================================


class TestConfiguration:
    """Tests for pipeline configuration."""
    
    def test_config_property(self) -> None:
        config = ValidationPipelineConfig(enable_room_validation=False)
        pipeline = ValidationPipeline(config)
        assert pipeline.config.enable_room_validation is False
    
    def test_default_config(self) -> None:
        pipeline = ValidationPipeline()
        assert pipeline.config.enable_room_validation is True
        assert pipeline.config.stop_on_critical is False


# ============================================================================
# Edge case tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_validate_with_existing_result(self) -> None:
        """Pipeline should merge into existing result."""
        model = create_valid_building_model()
        pipeline = ValidationPipeline()
        existing = ValidationResult.create()
        result = pipeline.validate_entities(model, existing)
        assert result.is_valid is True
    
    def test_validate_relationships_with_existing_result(self) -> None:
        """validate_relationships should merge into existing result."""
        model = create_valid_building_model()
        pipeline = ValidationPipeline()
        existing = ValidationResult.create()
        result = pipeline.validate_relationships(model, existing)
        assert result.is_valid is True
    
    def test_validate_building_with_existing_result(self) -> None:
        """validate_building should merge into existing result."""
        model = create_valid_building_model()
        pipeline = ValidationPipeline()
        existing = ValidationResult.create()
        result = pipeline.validate_building(model, existing)
        assert result.is_valid is True
    
    def test_multiple_invalid_entities(self) -> None:
        """Pipeline should report all invalid entities."""
        room1 = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            wall_ids=frozenset(["wall-missing-1", "wall-missing-2"]),
        )
        room2 = Room.create(
            vertices=[(0, 0), (5, 0), (5, 5), (0, 5)],
            room_type=RoomType.BEDROOM,
            door_ids=frozenset(["door-missing"]),
        )
        model = BuildingModel(
            rooms={"room-1": room1, "room-2": room2},
        )
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        assert result.warning_count >= 3  # 2 walls + 1 door
    
    def test_empty_rooms(self) -> None:
        """Pipeline should handle empty room collection."""
        model = BuildingModel(rooms={})
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        assert result.is_valid is True
    
    def test_empty_floors(self) -> None:
        """Pipeline should handle empty floor collection."""
        model = BuildingModel(floors={})
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        assert result.is_valid is True
    
    def test_empty_relationships(self) -> None:
        """Pipeline should handle empty relationship collection."""
        model = create_valid_building_model()
        model.relationships = []
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        assert result.is_valid is True


# ============================================================================
# Serialization tests
# ============================================================================


class TestSerialization:
    """Tests for serialization compatibility."""
    
    def test_result_can_serialize(self) -> None:
        model = create_valid_building_model()
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d
    
    def test_result_serialization_with_issues(self) -> None:
        model = create_invalid_building_model()
        pipeline = ValidationPipeline()
        result = pipeline.validate(model)
        d = result.to_dict()
        assert d["warning_count"] > 0
        assert len(d["warnings"]) > 0