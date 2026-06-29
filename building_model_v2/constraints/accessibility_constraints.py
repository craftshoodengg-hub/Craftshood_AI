"""Accessibility Constraints for Building Model v2.

Implements configurable accessibility-related architectural constraints.
These constraints evaluate general accessibility principles without
enforcing any specific country's legal requirements.

Do not modify the model - only report issues.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..entities_opening import Door
from ..entities_room import Room
from ..entities_stair import Stair
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from .constraint import Constraint
from .constraint_category import ConstraintCategory
from .constraint_issue import ConstraintIssue
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity


# ============================================================================
# Error codes
# ============================================================================

DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM: Final[str] = "DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM"
HALLWAY_WIDTH_BELOW_MINIMUM: Final[str] = "HALLWAY_WIDTH_BELOW_MINIMUM"
TURNING_RADIUS_INSUFFICIENT: Final[str] = "TURNING_RADIUS_INSUFFICIENT"
RAMP_SLOPE_EXCEEDS_MAXIMUM: Final[str] = "RAMP_SLOPE_EXCEEDS_MAXIMUM"
BATHROOM_ACCESSIBILITY_MISSING: Final[str] = "BATHROOM_ACCESSIBILITY_MISSING"
STAIR_HANDRAIL_MISSING: Final[str] = "STAIR_HANDRAIL_MISSING"


# ============================================================================
# Base class
# ============================================================================


class AccessibilityConstraint(Constraint):
    """Base class for accessibility constraints.
    
    Provides common functionality for all accessibility constraints.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        default_severity: ConstraintSeverity = ConstraintSeverity.WARNING,
    ) -> None:
        """Initialize the accessibility constraint.
        
        Args:
            name: Human-readable name of the constraint.
            description: Description of what the constraint checks.
            default_severity: Default severity for issues.
        """
        super().__init__(name=name, description=description)
        self._category = ConstraintCategory.ACCESSIBILITY
        self._default_severity = default_severity
    
    @property
    def category(self) -> ConstraintCategory:
        """Get the constraint category.
        
        Returns:
            ConstraintCategory.ACCESSIBILITY
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
# Configuration dataclasses
# ============================================================================


@dataclass(frozen=True, slots=True)
class MinimumAccessibleDoorWidthConfig:
    """Configuration for MinimumAccessibleDoorWidthConstraint.
    
    Attributes:
        minimum_width: Minimum clear door width in feet.
    """
    
    minimum_width: float = 3.0  # Default: 3 ft (36 inches) clear width


@dataclass(frozen=True, slots=True)
class MinimumHallwayWidthConfig:
    """Configuration for MinimumHallwayWidthConstraint.
    
    Attributes:
        minimum_width: Minimum hallway/corridor width in feet.
    """
    
    minimum_width: float = 3.5  # Default: 3.5 ft (42 inches)


@dataclass(frozen=True, slots=True)
class WheelchairTurningRadiusConfig:
    """Configuration for WheelchairTurningRadiusConstraint.
    
    Attributes:
        minimum_radius: Minimum turning radius in feet.
    """
    
    minimum_radius: float = 5.0  # Default: 5 ft radius


@dataclass(frozen=True, slots=True)
class RampSlopeConfig:
    """Configuration for RampSlopeConstraint.
    
    Attributes:
        maximum_slope_ratio: Maximum rise/run ratio (e.g., 1/12 = 0.083).
    """
    
    maximum_slope_ratio: float = 0.083  # Default: 1/12 slope


@dataclass(frozen=True, slots=True)
class AccessibleBathroomConfig:
    """Configuration for AccessibleBathroomConstraint.
    
    Attributes:
        require_accessible_metadata: Whether to require accessibility metadata.
    """
    
    require_accessible_metadata: bool = True


@dataclass(frozen=True, slots=True)
class StairHandrailConfig:
    """Configuration for StairHandrailConstraint.
    
    Attributes:
        require_handrail_metadata: Whether to require handrail metadata.
    """
    
    require_handrail_metadata: bool = True


# ============================================================================
# Helper functions
# ============================================================================


def _get_room_width(room: Room) -> float | None:
    """Calculate the width of a room from its polygon.
    
    Uses the minimum dimension of the bounding box as an approximation
    of room width.
    
    Args:
        room: The room to measure.
        
    Returns:
        The room width in feet, or None if polygon is empty.
    """
    if room.polygon.is_empty:
        return None
    
    bounds = room.polygon.bounds  # (minx, miny, maxx, maxy)
    width = bounds[2] - bounds[0]
    depth = bounds[3] - bounds[1]
    
    # Return the smaller dimension as width
    return min(width, depth)


# ============================================================================
# Constraints
# ============================================================================


class MinimumAccessibleDoorWidthConstraint(AccessibilityConstraint):
    """Checks if any door has a clear width below the accessible minimum.
    
    This constraint evaluates door widths for general accessibility.
    It does not enforce any specific legal requirement.
    
    Attributes:
        config: Configuration with minimum door width threshold.
    """
    
    def __init__(
        self,
        config: MinimumAccessibleDoorWidthConfig | None = None,
    ) -> None:
        """Initialize the MinimumAccessibleDoorWidthConstraint.
        
        Args:
            config: Configuration with minimum door width threshold.
        """
        super().__init__(
            name="Minimum Accessible Door Width",
            description="Checks if any door has a clear width below the accessible minimum threshold",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or MinimumAccessibleDoorWidthConfig()
    
    @property
    def config(self) -> MinimumAccessibleDoorWidthConfig:
        """Get the constraint configuration.
        
        Returns:
            The configuration.
        """
        return self._config
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for doors below minimum width.
        """
        result = ConstraintResult.create()
        
        for door_id, door in building_model.doors.items():
            if not isinstance(door, Door):
                continue
            
            if door.width < self._config.minimum_width:
                result.add_issue(ConstraintIssue(
                    code=DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM,
                    message=(
                        f"Door width ({door.width:.2f} ft) is below "
                        f"accessible minimum ({self._config.minimum_width:.2f} ft)"
                    ),
                    severity=self.default_severity,
                    entity_id=door_id,
                    entity_type="Door",
                    score=self._calculate_score(door.width, self._config.minimum_width),
                ))
        
        return result
    
    def _calculate_score(self, actual: float, minimum: float) -> float:
        """Calculate quality score impact.
        
        Args:
            actual: The actual width.
            minimum: The minimum required width.
            
        Returns:
            Score impact (0.0 to 1.0).
        """
        if minimum <= 0:
            return 0.0
        ratio = actual / minimum
        if ratio >= 1.0:
            return 0.0
        return min(1.0, 1.0 - ratio)


class MinimumHallwayWidthConstraint(AccessibilityConstraint):
    """Checks if hallway/corridor rooms meet minimum width requirements.
    
    Identifies rooms classified as corridors and checks their width.
    If a room is not classified as corridor, it is skipped.
    
    Attributes:
        config: Configuration with minimum hallway width threshold.
    """
    
    def __init__(
        self,
        config: MinimumHallwayWidthConfig | None = None,
    ) -> None:
        """Initialize the MinimumHallwayWidthConstraint.
        
        Args:
            config: Configuration with minimum hallway width threshold.
        """
        super().__init__(
            name="Minimum Hallway Width",
            description="Checks if hallway/corridor rooms meet minimum width requirements",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or MinimumHallwayWidthConfig()
    
    @property
    def config(self) -> MinimumHallwayWidthConfig:
        """Get the constraint configuration.
        
        Returns:
            The configuration.
        """
        return self._config
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Only checks rooms explicitly classified as corridors.
        Other room types are skipped with graceful fallback.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for hallways below minimum width.
        """
        result = ConstraintResult.create()
        
        for room_id, room in building_model.rooms.items():
            # Only check rooms explicitly classified as corridors
            if room.room_type != RoomType.CORRIDOR:
                continue
            
            room_width = _get_room_width(room)
            if room_width is None:
                continue
            
            if room_width < self._config.minimum_width:
                room_name = room.metadata.get("name", room_id)
                result.add_issue(ConstraintIssue(
                    code=HALLWAY_WIDTH_BELOW_MINIMUM,
                    message=(
                        f"Hallway/corridor '{room_name}' width ({room_width:.2f} ft) is below "
                        f"minimum ({self._config.minimum_width:.2f} ft)"
                    ),
                    severity=self.default_severity,
                    entity_id=room_id,
                    entity_type="Room",
                    score=self._calculate_score(room_width, self._config.minimum_width),
                ))
        
        return result
    
    def _calculate_score(self, actual: float, minimum: float) -> float:
        """Calculate quality score impact.
        
        Args:
            actual: The actual width.
            minimum: The minimum required width.
            
        Returns:
            Score impact (0.0 to 1.0).
        """
        if minimum <= 0:
            return 0.0
        ratio = actual / minimum
        if ratio >= 1.0:
            return 0.0
        return min(1.0, 1.0 - ratio)


class WheelchairTurningRadiusConstraint(AccessibilityConstraint):
    """Placeholder for wheelchair turning radius constraint.
    
    This constraint is structured but not yet implemented.
    Spatial analysis algorithms will be added in a future phase.
    """
    
    def __init__(
        self,
        config: WheelchairTurningRadiusConfig | None = None,
    ) -> None:
        """Initialize the WheelchairTurningRadiusConstraint.
        
        Args:
            config: Configuration with minimum turning radius threshold.
        """
        super().__init__(
            name="Wheelchair Turning Radius",
            description="Checks if spaces accommodate wheelchair turning radius (placeholder)",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or WheelchairTurningRadiusConfig()
    
    @property
    def config(self) -> WheelchairTurningRadiusConfig:
        """Get the constraint configuration.
        
        Returns:
            The configuration.
        """
        return self._config
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        This is a placeholder implementation that returns an optimal result.
        Spatial analysis algorithms will be added in a future phase.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult - currently always optimal.
        """
        # Placeholder - spatial analysis not yet implemented
        return ConstraintResult.create()


class RampSlopeConstraint(AccessibilityConstraint):
    """Placeholder for ramp slope constraint.
    
    This constraint is structured but not yet implemented.
    Elevation data and geometry solvers will be added in a future phase.
    """
    
    def __init__(
        self,
        config: RampSlopeConfig | None = None,
    ) -> None:
        """Initialize the RampSlopeConstraint.
        
        Args:
            config: Configuration with maximum slope ratio.
        """
        super().__init__(
            name="Ramp Slope",
            description="Checks if ramp slopes exceed maximum threshold (placeholder)",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or RampSlopeConfig()
    
    @property
    def config(self) -> RampSlopeConfig:
        """Get the constraint configuration.
        
        Returns:
            The configuration.
        """
        return self._config
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        This is a placeholder implementation that returns an optimal result.
        Elevation data and geometry solvers will be added in a future phase.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult - currently always optimal.
        """
        # Placeholder - elevation data not yet available
        return ConstraintResult.create()


class AccessibleBathroomConstraint(AccessibilityConstraint):
    """Placeholder for accessible bathroom constraint.
    
    Checks for accessibility metadata presence on bathroom rooms.
    Full spatial analysis is deferred to a future phase.
    """
    
    def __init__(
        self,
        config: AccessibleBathroomConfig | None = None,
    ) -> None:
        """Initialize the AccessibleBathroomConstraint.
        
        Args:
            config: Configuration for bathroom accessibility checks.
        """
        super().__init__(
            name="Accessible Bathroom",
            description="Checks bathroom accessibility features (placeholder)",
            default_severity=ConstraintSeverity.RECOMMENDATION,
        )
        self._config = config or AccessibleBathroomConfig()
    
    @property
    def config(self) -> AccessibleBathroomConfig:
        """Get the constraint configuration.
        
        Returns:
            The configuration.
        """
        return self._config
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Checks for accessibility metadata on bathroom rooms.
        If metadata is not required, returns optimal.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for bathrooms missing accessibility metadata.
        """
        result = ConstraintResult.create()
        
        if not self._config.require_accessible_metadata:
            return result
        
        for room_id, room in building_model.rooms.items():
            if room.room_type != RoomType.BATHROOM:
                continue
            
            # Check for accessibility metadata
            is_accessible = room.metadata.get("accessible", False)
            if not is_accessible:
                room_name = room.metadata.get("name", room_id)
                result.add_issue(ConstraintIssue(
                    code=BATHROOM_ACCESSIBILITY_MISSING,
                    message=(
                        f"Bathroom '{room_name}' lacks accessibility metadata. "
                        "Consider adding accessible features."
                    ),
                    severity=self.default_severity,
                    entity_id=room_id,
                    entity_type="Room",
                    score=0.5,
                ))
        
        return result


class StairHandrailConstraint(AccessibilityConstraint):
    """Placeholder for stair handrail constraint.
    
    Checks for handrail metadata on stair entities.
    Full verification is deferred to a future phase.
    """
    
    def __init__(
        self,
        config: StairHandrailConfig | None = None,
    ) -> None:
        """Initialize the StairHandrailConstraint.
        
        Args:
            config: Configuration for stair handrail checks.
        """
        super().__init__(
            name="Stair Handrail",
            description="Checks if stairs have handrail metadata (placeholder)",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or StairHandrailConfig()
    
    @property
    def config(self) -> StairHandrailConfig:
        """Get the constraint configuration.
        
        Returns:
            The configuration.
        """
        return self._config
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        Checks for handrail metadata on stair entities.
        If metadata is not required, returns optimal.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult with issues for stairs missing handrail metadata.
        """
        result = ConstraintResult.create()
        
        if not self._config.require_handrail_metadata:
            return result
        
        for stair_id, stair in building_model.stairs.items():
            # Check for handrail metadata
            has_handrail = stair.metadata.get("handrail", False)
            if not has_handrail:
                result.add_issue(ConstraintIssue(
                    code=STAIR_HANDRAIL_MISSING,
                    message=(
                        f"Stair lacks handrail metadata. "
                        "Consider adding handrails for accessibility."
                    ),
                    severity=self.default_severity,
                    entity_id=stair_id,
                    entity_type="Stair",
                    score=0.5,
                ))
        
        return result