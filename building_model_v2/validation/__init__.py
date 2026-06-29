"""Validation Engine for Building Model v2.

Provides a foundation for validation rules and results. This module
is independent from entities and contains no entity-specific validation
logic.

Modules:
    validation_severity: Severity levels for validation issues.
    validation_error: Validation error representation.
    validation_result: Collection of validation issues.
    validator: Abstract base class for validators.
"""

from .column_validator import ColumnValidationConfig, ColumnValidator
from .cross_entity_validator import CrossEntityValidationConfig, CrossEntityValidator
from .door_validator import DoorValidationConfig, DoorValidator
from .floor_validator import FloorValidationConfig, FloorValidator
from .relationship_validator import RelationshipValidationConfig, RelationshipValidator
from .room_validator import RoomValidationConfig, RoomValidator
from .stair_validator import StairValidationConfig, StairValidator
from .validation_error import ValidationError
from .validation_pipeline import ValidationPipeline, ValidationPipelineConfig
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator
from .wall_validator import WallValidationConfig, WallValidator
from .window_validator import WindowValidationConfig, WindowValidator

__all__ = [
    "ColumnValidationConfig",
    "ColumnValidator",
    "CrossEntityValidationConfig",
    "CrossEntityValidator",
    "DoorValidationConfig",
    "DoorValidator",
    "FloorValidationConfig",
    "FloorValidator",
    "RelationshipValidationConfig",
    "RelationshipValidator",
    "RoomValidationConfig",
    "RoomValidator",
    "StairValidationConfig",
    "StairValidator",
    "ValidationError",
    "ValidationPipeline",
    "ValidationPipelineConfig",
    "ValidationResult",
    "ValidationSeverity",
    "Validator",
    "WallValidationConfig",
    "WallValidator",
    "WindowValidationConfig",
    "WindowValidator",
]
