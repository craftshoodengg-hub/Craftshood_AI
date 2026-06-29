"""Functional constraints for Building Model v2.

Implements design quality constraints that evaluate architectural quality.
These constraints do not modify the model - they only report issues.
"""

from __future__ import annotations

from typing import Final

from ..validation.cross_entity_validator import BuildingModel
from .constraint import Constraint
from .constraint_category import ConstraintCategory
from .constraint_issue import ConstraintIssue
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity


class FunctionalConstraint(Constraint):
    """Base class for functional constraints.
    
    Provides common functionality for all functional constraints.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        category: ConstraintCategory = ConstraintCategory.FUNCTIONAL,
        default_severity: ConstraintSeverity = ConstraintSeverity.WARNING,
    ) -> None:
        """Initialize the functional constraint.
        
        Args:
            name: Human-readable name of the constraint.
            description: Description of what the constraint checks.
            category: The constraint category.
            default_severity: Default severity for issues.
        """
        super().__init__(name=name, description=description)
        self._category = category
        self._default_severity = default_severity
    
    @property
    def category(self) -> ConstraintCategory:
        """Get the constraint category.
        
        Returns:
            The constraint category.
        """
        return self._category
    
    @property
    def default_severity(self) -> ConstraintSeverity:
        """Get the default severity for issues.
        
        Returns:
            The default severity.
        """
        return self._default_severity


# ============================================================================
# Error codes
# ============================================================================

EMPTY_BUILDING: Final[str] = "EMPTY_BUILDING"
EMPTY_FLOOR: Final[str] = "EMPTY_FLOOR"
ROOM_WITHOUT_DOOR: Final[str] = "ROOM_WITHOUT_DOOR"
ROOM_WITHOUT_WINDOW: Final[str] = "ROOM_WITHOUT_WINDOW"
ISOLATED_ROOM: Final[str] = "ISOLATED_ROOM"
UNCONNECTED_FLOOR: Final[str] = "UNCONNECTED_FLOOR"


# ============================================================================
# Constraints
# ============================================================================


class EmptyBuildingConstraint(FunctionalConstraint):
    """Checks if a building model has no floors.
    
    A building without floors may indicate incomplete design.
    """
    
    def __init__(self) -> None:
        """Initialize the EmptyBuildingConstraint."""
        super().__init__(
            name="Empty Building",
            description="Checks if the building has no floors",
            default_severity=ConstraintSeverity.WARNING,
        )
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues if building is empty.
        """
        result = ConstraintResult.create()
        
        if building_model.floors:
            return result
        
        result.add_issue(ConstraintIssue(
            code=EMPTY_BUILDING,
            message="Building has no floors",
            severity=self.default_severity,
            entity_type="Building",
        ))
        
        return result


class EmptyFloorConstraint(FunctionalConstraint):
    """Checks if any floor has no rooms, walls, columns, or stairs.
    
    A floor with no entities may indicate incomplete design.
    """
    
    def __init__(self) -> None:
        """Initialize the EmptyFloorConstraint."""
        super().__init__(
            name="Empty Floor",
            description="Checks if any floor has no associated entities",
            default_severity=ConstraintSeverity.WARNING,
        )
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for empty floors.
        """
        result = ConstraintResult.create()
        
        for floor_id, floor in building_model.floors.items():
            has_rooms = bool(floor.room_ids)
            has_walls = bool(floor.wall_ids)
            has_columns = bool(floor.column_ids)
            has_stairs = bool(floor.stair_ids)
            
            if not (has_rooms or has_walls or has_columns or has_stairs):
                result.add_issue(ConstraintIssue(
                    code=EMPTY_FLOOR,
                    message=f"Floor '{floor.name}' has no rooms, walls, columns, or stairs",
                    severity=self.default_severity,
                    entity_id=floor_id,
                    entity_type="Floor",
                    location=floor.name,
                ))
        
        return result


class RoomWithoutDoorConstraint(FunctionalConstraint):
    """Checks if any room has no doors.
    
    Rooms without doors may have accessibility issues.
    """
    
    def __init__(self) -> None:
        """Initialize the RoomWithoutDoorConstraint."""
        super().__init__(
            name="Room Without Door",
            description="Checks if any room has no doors for access",
            default_severity=ConstraintSeverity.RECOMMENDATION,
        )
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for rooms without doors.
        """
        result = ConstraintResult.create()
        
        for room_id, room in building_model.rooms.items():
            if not room.door_ids:
                room_name = room.metadata.get("name", room_id)
                result.add_issue(ConstraintIssue(
                    code=ROOM_WITHOUT_DOOR,
                    message=f"Room '{room_name}' has no doors",
                    severity=self.default_severity,
                    entity_id=room_id,
                    entity_type="Room",
                ))
        
        return result


class RoomWithoutWindowConstraint(FunctionalConstraint):
    """Checks if any room has no windows.
    
    Rooms without windows may have ventilation and lighting issues.
    """
    
    def __init__(self) -> None:
        """Initialize the RoomWithoutWindowConstraint."""
        super().__init__(
            name="Room Without Window",
            description="Checks if any room has no windows for ventilation and light",
            default_severity=ConstraintSeverity.SUGGESTION,
        )
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for rooms without windows.
        """
        result = ConstraintResult.create()
        
        for room_id, room in building_model.rooms.items():
            if not room.window_ids:
                room_name = room.metadata.get("name", room_id)
                result.add_issue(ConstraintIssue(
                    code=ROOM_WITHOUT_WINDOW,
                    message=f"Room '{room_name}' has no windows",
                    severity=self.default_severity,
                    entity_id=room_id,
                    entity_type="Room",
                ))
        
        return result


class IsolatedRoomConstraint(FunctionalConstraint):
    """Checks if any room is not connected to other rooms via relationships.
    
    Isolated rooms may indicate connectivity issues in the design.
    """
    
    def __init__(self) -> None:
        """Initialize the IsolatedRoomConstraint."""
        super().__init__(
            name="Isolated Room",
            description="Checks if any room has no connections to other rooms",
            default_severity=ConstraintSeverity.SUGGESTION,
        )
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for isolated rooms.
        """
        result = ConstraintResult.create()
        
        # Get all connected room IDs from relationships
        connected_rooms: set[str] = set()
        for relationship in building_model.relationships:
            if relationship.source_id in building_model.rooms:
                connected_rooms.add(relationship.source_id)
            if relationship.target_id in building_model.rooms:
                connected_rooms.add(relationship.target_id)
        
        # Find isolated rooms
        for room_id, room in building_model.rooms.items():
            if room_id not in connected_rooms:
                room_name = room.metadata.get("name", room_id)
                result.add_issue(ConstraintIssue(
                    code=ISOLATED_ROOM,
                    message=f"Room '{room_name}' has no connections to other rooms",
                    severity=self.default_severity,
                    entity_id=room_id,
                    entity_type="Room",
                ))
        
        return result


class UnconnectedFloorConstraint(FunctionalConstraint):
    """Checks if any floor is not connected to the building via relationships.
    
    Unconnected floors may indicate missing vertical circulation.
    """
    
    def __init__(self) -> None:
        """Initialize the UnconnectedFloorConstraint."""
        super().__init__(
            name="Unconnected Floor",
            description="Checks if any floor has no connections via relationships",
            default_severity=ConstraintSeverity.WARNING,
        )
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for unconnected floors.
        """
        result = ConstraintResult.create()
        
        # Get all connected floor IDs from relationships
        connected_floors: set[str] = set()
        for relationship in building_model.relationships:
            if relationship.source_id in building_model.floors:
                connected_floors.add(relationship.source_id)
            if relationship.target_id in building_model.floors:
                connected_floors.add(relationship.target_id)
        
        # Find unconnected floors
        for floor_id, floor in building_model.floors.items():
            if floor_id not in connected_floors:
                result.add_issue(ConstraintIssue(
                    code=UNCONNECTED_FLOOR,
                    message=f"Floor '{floor.name}' has no connections via relationships",
                    severity=self.default_severity,
                    entity_id=floor_id,
                    entity_type="Floor",
                    location=floor.name,
                ))
        
        return result