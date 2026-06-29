"""Validation Pipeline for Building Model v2.

Orchestrates all validators and produces a single ValidationResult.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from .cross_entity_validator import BuildingModel, CrossEntityValidator
from .floor_validator import FloorValidator
from .relationship_validator import RelationshipValidator
from .room_validator import RoomValidator
from .stair_validator import StairValidator
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator
from .wall_validator import WallValidator


@dataclass(slots=True)
class ValidationPipelineConfig:
    """Configuration for the validation pipeline.
    
    Attributes:
        enable_room_validation: Whether to run room validation.
        enable_wall_validation: Whether to run wall validation.
        enable_door_validation: Whether to run door validation.
        enable_window_validation: Whether to run window validation.
        enable_stair_validation: Whether to run stair validation.
        enable_column_validation: Whether to run column validation.
        enable_floor_validation: Whether to run floor validation.
        enable_relationship_validation: Whether to run relationship validation.
        enable_cross_entity_validation: Whether to run cross-entity validation.
        stop_on_critical: Whether to stop on first critical error.
    """
    
    enable_room_validation: bool = True
    enable_wall_validation: bool = True
    enable_door_validation: bool = True
    enable_window_validation: bool = True
    enable_stair_validation: bool = True
    enable_column_validation: bool = True
    enable_floor_validation: bool = True
    enable_relationship_validation: bool = True
    enable_cross_entity_validation: bool = True
    stop_on_critical: bool = False


class ValidationPipeline:
    """Orchestrates validation of a building model.
    
    Coordinates multiple validators and merges their results into a single
    ValidationResult.
    
    Attributes:
        config: Pipeline configuration.
    """
    
    def __init__(self, config: ValidationPipelineConfig | None = None) -> None:
        """Initialize the validation pipeline.
        
        Args:
            config: Optional pipeline configuration. Uses defaults if not provided.
        """
        self._config = config or ValidationPipelineConfig()
        self._room_validator = RoomValidator()
        self._wall_validator = WallValidator()
        self._floor_validator = FloorValidator()
        self._relationship_validator = RelationshipValidator()
        self._cross_entity_validator = CrossEntityValidator()
    
    @property
    def config(self) -> ValidationPipelineConfig:
        """Get the pipeline configuration.
        
        Returns:
            The current pipeline configuration.
        """
        return self._config
    
    def validate(self, building_model: BuildingModel) -> ValidationResult:
        """Validate a complete building model.
        
        Runs all enabled validators and merges their results.
        
        Args:
            building_model: The building model to validate.
            
        Returns:
            ValidationResult containing all issues found.
        """
        result = ValidationResult.create()
        
        # Validate individual entities
        result = self.validate_entities(building_model, result)
        
        # Validate relationships
        result = self.validate_relationships(building_model, result)
        
        # Validate building
        result = self.validate_building(building_model, result)
        
        return result
    
    def validate_entities(
        self,
        building_model: BuildingModel,
        result: ValidationResult | None = None,
    ) -> ValidationResult:
        """Validate all individual entities in the building model.
        
        Args:
            building_model: The building model containing entities.
            result: Optional existing result to merge into.
            
        Returns:
            ValidationResult containing entity validation issues.
        """
        if result is None:
            result = ValidationResult.create()
        
        # Validate rooms
        if self._config.enable_room_validation:
            for room in building_model.rooms.values():
                room_result = self._room_validator.validate(room)
                result = result.merge(room_result)
                if self._should_stop(result):
                    return result
        
        # Validate walls
        if self._config.enable_wall_validation:
            for wall in building_model.walls.values():
                wall_result = self._wall_validator.validate(wall)
                result = result.merge(wall_result)
                if self._should_stop(result):
                    return result
        
        # Validate floors
        if self._config.enable_floor_validation:
            for floor in building_model.floors.values():
                floor_result = self._floor_validator.validate(floor)
                result = result.merge(floor_result)
                if self._should_stop(result):
                    return result
        
        return result
    
    def validate_relationships(
        self,
        building_model: BuildingModel,
        result: ValidationResult | None = None,
    ) -> ValidationResult:
        """Validate all relationships in the building model.
        
        Args:
            building_model: The building model containing relationships.
            result: Optional existing result to merge into.
            
        Returns:
            ValidationResult containing relationship validation issues.
        """
        if result is None:
            result = ValidationResult.create()
        
        if not self._config.enable_relationship_validation:
            return result
        
        for relationship in building_model.relationships:
            rel_result = self._relationship_validator.validate(relationship)
            result = result.merge(rel_result)
            if self._should_stop(result):
                return result
        
        return result
    
    def validate_building(
        self,
        building_model: BuildingModel,
        result: ValidationResult | None = None,
    ) -> ValidationResult:
        """Validate the building structure and cross-entity references.
        
        Args:
            building_model: The building model to validate.
            result: Optional existing result to merge into.
            
        Returns:
            ValidationResult containing building validation issues.
        """
        if result is None:
            result = ValidationResult.create()
        
        if not self._config.enable_cross_entity_validation:
            return result
        
        cross_result = self._cross_entity_validator.validate(building_model)
        result = result.merge(cross_result)
        
        return result
    
    def _should_stop(self, result: ValidationResult) -> bool:
        """Check if validation should stop due to critical errors.
        
        Args:
            result: The current validation result.
            
        Returns:
            True if validation should stop.
        """
        if not self._config.stop_on_critical:
            return False
        return result.critical_count > 0