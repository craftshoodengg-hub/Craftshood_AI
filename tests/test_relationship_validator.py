"""Unit tests for RelationshipValidator."""

from __future__ import annotations

import pytest

from building_model_v2.relationships import Relationship, RelationshipType
from building_model_v2.validation import (
    RelationshipValidationConfig,
    RelationshipValidator,
)
from building_model_v2.validation.relationship_validator import (
    RELATIONSHIP_INVALID_METADATA,
    RELATIONSHIP_INVALID_TYPE,
    RELATIONSHIP_MISSING_SOURCE,
    RELATIONSHIP_MISSING_TARGET,
    RELATIONSHIP_SELF_REFERENCE,
)


class TestRelationshipValidationConfig:
    """Tests for RelationshipValidationConfig."""
    
    def test_default_values(self) -> None:
        config = RelationshipValidationConfig()
        assert config.allow_self_relationship is False
        assert config.allow_empty_metadata is True
        assert config.allow_unknown_relationship is True
    
    def test_custom_values(self) -> None:
        config = RelationshipValidationConfig(
            allow_self_relationship=True,
            allow_empty_metadata=False,
            allow_unknown_relationship=False,
        )
        assert config.allow_self_relationship is True
        assert config.allow_empty_metadata is False
        assert config.allow_unknown_relationship is False


class TestRelationshipValidatorValid:
    """Tests for valid relationship validation."""
    
    def test_valid_relationship(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_with_metadata(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.FLOOR_TO_ROOM,
            source_id="floor-1",
            target_id="room-1",
            metadata={"key": "value"},
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True
    
    def test_valid_bidirectional(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-2",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True
    
    def test_valid_hierarchical(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.BUILDING_TO_FLOOR,
            source_id="building-1",
            target_id="floor-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True


class TestRelationshipValidatorSource:
    """Tests for source_id validation."""
    
    def test_missing_source(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.error_count == 1
        assert result.errors[0].code == RELATIONSHIP_MISSING_SOURCE
    
    def test_whitespace_source(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="   ",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.error_count == 1
        assert result.errors[0].code == RELATIONSHIP_MISSING_SOURCE
    
    def test_valid_source(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True


class TestRelationshipValidatorTarget:
    """Tests for target_id validation."""
    
    def test_missing_target(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.error_count == 1
        assert result.errors[0].code == RELATIONSHIP_MISSING_TARGET
    
    def test_whitespace_target(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="   ",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.error_count == 1
        assert result.errors[0].code == RELATIONSHIP_MISSING_TARGET
    
    def test_valid_target(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True


class TestRelationshipValidatorSelfReference:
    """Tests for self-reference validation."""
    
    def test_self_reference_disallowed(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-1",
        )
        config = RelationshipValidationConfig(allow_self_relationship=False)
        validator = RelationshipValidator(config)
        result = validator.validate(rel)
        assert result.error_count == 1
        assert result.errors[0].code == RELATIONSHIP_SELF_REFERENCE
    
    def test_self_reference_allowed(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-1",
        )
        config = RelationshipValidationConfig(allow_self_relationship=True)
        validator = RelationshipValidator(config)
        result = validator.validate(rel)
        assert result.is_valid is True
    
    def test_different_source_target(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="room-2",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True


class TestRelationshipValidatorType:
    """Tests for relationship type validation."""
    
    def test_valid_types(self) -> None:
        for rel_type in RelationshipType:
            rel = Relationship.create(
                relationship_type=rel_type,
                source_id="entity-1",
                target_id="entity-2",
            )
            validator = RelationshipValidator()
            result = validator.validate(rel)
            assert result.is_valid is True, f"Type '{rel_type}' should be valid"


class TestRelationshipValidatorMetadata:
    """Tests for metadata validation."""
    
    def test_empty_metadata_allowed(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
            metadata={},
        )
        config = RelationshipValidationConfig(allow_empty_metadata=True)
        validator = RelationshipValidator(config)
        result = validator.validate(rel)
        assert result.is_valid is True
    
    def test_empty_metadata_disallowed(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
            metadata={},
        )
        config = RelationshipValidationConfig(allow_empty_metadata=False)
        validator = RelationshipValidator(config)
        result = validator.validate(rel)
        assert result.warning_count == 1
        assert result.warnings[0].code == RELATIONSHIP_INVALID_METADATA
    
    def test_valid_metadata(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
            metadata={"key": "value", "count": 42},
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.is_valid is True


class TestRelationshipValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="",
            target_id="",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.error_count >= 2  # missing source, missing target
    
    def test_self_ref_and_missing_target(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_ROOM,
            source_id="room-1",
            target_id="",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.error_count == 1  # missing target only (self-reference not checked when target is empty)


class TestRelationshipValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_relationship_entity(self) -> None:
        validator = RelationshipValidator()
        result = validator.validate("not a relationship")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = RelationshipValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        invalid_rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate_many([valid_rel, invalid_rel])
        assert result.error_count == 1  # missing source only
    
    def test_validate_many_empty_list(self) -> None:
        validator = RelationshipValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_all_relationship_types(self) -> None:
        for rel_type in [
            RelationshipType.ROOM_TO_WALL,
            RelationshipType.ROOM_TO_DOOR,
            RelationshipType.ROOM_TO_WINDOW,
            RelationshipType.ROOM_TO_ROOM,
            RelationshipType.WALL_TO_WINDOW,
            RelationshipType.WALL_TO_DOOR,
            RelationshipType.FLOOR_TO_ROOM,
            RelationshipType.FLOOR_TO_STAIR,
            RelationshipType.BUILDING_TO_FLOOR,
            RelationshipType.STAIR_TO_FLOOR,
        ]:
            rel = Relationship.create(
                relationship_type=rel_type,
                source_id="source-1",
                target_id="target-1",
            )
            validator = RelationshipValidator()
            result = validator.validate(rel)
            assert result.is_valid is True, f"Type '{rel_type}' should be valid"


class TestRelationshipValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        assert result.errors[0].entity_id == rel.id
        assert result.errors[0].entity_type == "Relationship"
    
    def test_result_can_serialize(self) -> None:
        rel = Relationship.create(
            relationship_type=RelationshipType.ROOM_TO_WALL,
            source_id="room-1",
            target_id="wall-1",
        )
        validator = RelationshipValidator()
        result = validator.validate(rel)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestRelationshipValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = RelationshipValidationConfig(allow_self_relationship=True)
        validator = RelationshipValidator(config)
        assert validator.config.allow_self_relationship is True
    
    def test_default_config(self) -> None:
        validator = RelationshipValidator()
        assert validator.config.allow_self_relationship is False