"""Building Code constraints for Building Model v2.

Implements configurable building code style constraints.
These constraints are generic and do not hardcode country-specific regulations.

Do not modify the model - only report issues.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..entities_opening import Door, Opening, Window
from ..entities_room import Room
from ..entities_stair import Stair
from ..validation.cross_entity_validator import BuildingModel
from .constraint import Constraint
from .constraint_category import ConstraintCategory
from .constraint_issue import ConstraintIssue
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity


# ============================================================================
# Error codes
# ============================================================================

ROOM_AREA_BELOW_MINIMUM: Final[str] = "ROOM_AREA_BELOW_MINIMUM"
DOOR_WIDTH_BELOW_MINIMUM: Final[str] = "DOOR_WIDTH_BELOW_MINIMUM"
WINDOW_AREA_BELOW_MINIMUM: Final[str] = "WINDOW_AREA_BELOW_MINIMUM"
STAIR_WIDTH_BELOW_MINIMUM: Final[str] = "STAIR_WIDTH_BELOW_MINIMUM"
CEILING_HEIGHT_BELOW_MINIMUM: Final[str] = "CEILING_HEIGHT_BELOW_MINIMUM"
MAX_TRAVEL_DISTANCE_EXCEEDED: Final[str] = "MAX_TRAVEL_DISTANCE_EXCEEDED"


# ============================================================================
# Base class
# ============================================================================


class BuildingCodeConstraint(Constraint):
    """Base class for building code constraints.
    
    Provides common functionality for all building code constraints.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        default_severity: ConstraintSeverity = ConstraintSeverity.WARNING,
    ) -> None:
        """Initialize the building code constraint.
        
        Args:
            name: Human-readable name of the constraint.
            description: Description of what the constraint checks.
            default_severity: Default severity for issues.
        """
        super().__init__(name=name, description=description)
        self._category = ConstraintCategory.BUILDING_CODE
        self._default_severity = default_severity
    
    @property
    def category(self) -> ConstraintCategory:
        """Get the constraint category.
        
        Returns:
            ConstraintCategory.BUILDING_CODE
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
class MinimumRoomAreaConfig:
    """Configuration for MinimumRoomAreaConstraint.
    
    Attributes:
        minimum_area: Minimum room area in square feet.
    """
    
    minimum_area: float = 70.0  # Default: 70 sq ft


@dataclass(frozen=True, slots=True)
class MinimumDoorWidthConfig:
    """Configuration for MinimumDoorWidthConstraint.
    
    Attributes:
        minimum_width: Minimum door width in feet.
    """
    
    minimum_width: float = 2.5  # Default: 2.5 ft (30 inches)


@dataclass(frozen=True, slots=True)
class MinimumWindowAreaConfig:
    """Configuration for MinimumWindowAreaConstraint.
    
    Attributes:
        minimum_area: Minimum window area in square feet.
    """
    
    minimum_area: float = 3.0  # Default: 3 sq ft


@dataclass(frozen=True, slots=True)
class MinimumStairWidthConfig:
    """Configuration for StairWidthConstraint.
    
    Attributes:
        minimum_width: Minimum stair width in feet.
    """
    
    minimum_width: float = 3.0  # Default: 3 ft (36 inches)


@dataclass(frozen=True, slots=True)
class MinimumCeilingHeightConfig:
    """Configuration for CeilingHeightConstraint.
    
    Attributes:
        minimum_height: Minimum ceiling height in feet.
    """
    
    minimum_height: float = 7.0  # Default: 7 ft


@dataclass(frozen=True, slots=True)
class MaximumTravelDistanceConfig:
    """Configuration for MaximumTravelDistanceConstraint.
    
    Attributes:
        maximum_distance: Maximum travel distance in feet.
    """
    
    maximum_distance: float = 75.0  # Default: 75 ft


# ============================================================================
# Constraints
# ============================================================================


class MinimumRoomAreaConstraint(BuildingCodeConstraint):
    """Checks if any room has an area below the minimum threshold.
    
    Attributes:
        config: Configuration with minimum area threshold.
    """
    
    def __init__(
        self,
        config: MinimumRoomAreaConfig | None = None,
    ) -> None:
        """Initialize the MinimumRoomAreaConstraint.
        
        Args:
            config: Configuration with minimum area threshold.
        """
        super().__init__(
            name="Minimum Room Area",
            description="Checks if any room has an area below the minimum threshold",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or MinimumRoomAreaConfig()
    
    @property
    def config(self) -> MinimumRoomAreaConfig:
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
            ConstraintResult with issues for rooms below minimum area.
        """
        result = ConstraintResult.create()
        
        for room_id, room in building_model.rooms.items():
            area = room.area
            if area < self._config.minimum_area:
                room_name = room.metadata.get("name", room_id)
                result.add_issue(ConstraintIssue(
                    code=ROOM_AREA_BELOW_MINIMUM,
                    message=(
                        f"Room '{room_name}' area ({area:.1f} sq ft) is below "
                        f"minimum ({self._config.minimum_area:.1f} sq ft)"
                    ),
                    severity=self.default_severity,
                    entity_id=room_id,
                    entity_type="Room",
                    score=self._calculate_score(area, self._config.minimum_area),
                ))
        
        return result
    
    def _calculate_score(self, actual: float, minimum: float) -> float:
        """Calculate quality score impact.
        
        Args:
            actual: The actual area.
            minimum: The minimum required area.
            
        Returns:
            Score impact (0.0 to 1.0).
        """
        if minimum <= 0:
            return 0.0
        ratio = actual / minimum
        if ratio >= 1.0:
            return 0.0
        return min(1.0, 1.0 - ratio)


class MinimumDoorWidthConstraint(BuildingCodeConstraint):
    """Checks if any door has a width below the minimum threshold.
    
    Attributes:
        config: Configuration with minimum door width threshold.
    """
    
    def __init__(
        self,
        config: MinimumDoorWidthConfig | None = None,
    ) -> None:
        """Initialize the MinimumDoorWidthConstraint.
        
        Args:
            config: Configuration with minimum door width threshold.
        """
        super().__init__(
            name="Minimum Door Width",
            description="Checks if any door has a width below the minimum threshold",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or MinimumDoorWidthConfig()
    
    @property
    def config(self) -> MinimumDoorWidthConfig:
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
                    code=DOOR_WIDTH_BELOW_MINIMUM,
                    message=(
                        f"Door width ({door.width:.2f} ft) is below "
                        f"minimum ({self._config.minimum_width:.2f} ft)"
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


class MinimumWindowAreaConstraint(BuildingCodeConstraint):
    """Checks if any window has an area below the minimum threshold.
    
    Attributes:
        config: Configuration with minimum window area threshold.
    """
    
    def __init__(
        self,
        config: MinimumWindowAreaConfig | None = None,
    ) -> None:
        """Initialize the MinimumWindowAreaConstraint.
        
        Args:
            config: Configuration with minimum window area threshold.
        """
        super().__init__(
            name="Minimum Window Area",
            description="Checks if any window has an area below the minimum threshold",
            default_severity=ConstraintSeverity.RECOMMENDATION,
        )
        self._config = config or MinimumWindowAreaConfig()
    
    @property
    def config(self) -> MinimumWindowAreaConfig:
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
            ConstraintResult with issues for windows below minimum area.
        """
        result = ConstraintResult.create()
        
        for window_id, window in building_model.windows.items():
            if not isinstance(window, Window):
                continue
            
            # Calculate window area from width and height
            if window.height is not None:
                area = window.width * window.height
                if area < self._config.minimum_area:
                    result.add_issue(ConstraintIssue(
                        code=WINDOW_AREA_BELOW_MINIMUM,
                        message=(
                            f"Window area ({area:.1f} sq ft) is below "
                            f"minimum ({self._config.minimum_area:.1f} sq ft)"
                        ),
                        severity=self.default_severity,
                        entity_id=window_id,
                        entity_type="Window",
                        score=self._calculate_score(area, self._config.minimum_area),
                    ))
        
        return result
    
    def _calculate_score(self, actual: float, minimum: float) -> float:
        """Calculate quality score impact.
        
        Args:
            actual: The actual area.
            minimum: The minimum required area.
            
        Returns:
            Score impact (0.0 to 1.0).
        """
        if minimum <= 0:
            return 0.0
        ratio = actual / minimum
        if ratio >= 1.0:
            return 0.0
        return min(1.0, 1.0 - ratio)


class MaximumTravelDistanceConstraint(BuildingCodeConstraint):
    """Placeholder for maximum travel distance constraint.
    
    This constraint is structured but not yet implemented.
    Routing algorithms will be added in a future phase.
    """
    
    def __init__(
        self,
        config: MaximumTravelDistanceConfig | None = None,
    ) -> None:
        """Initialize the MaximumTravelDistanceConstraint.
        
        Args:
            config: Configuration with maximum travel distance threshold.
        """
        super().__init__(
            name="Maximum Travel Distance",
            description="Checks if travel distances exceed maximum threshold (placeholder)",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or MaximumTravelDistanceConfig()
    
    @property
    def config(self) -> MaximumTravelDistanceConfig:
        """Get the constraint configuration.
        
        Returns:
            The configuration.
        """
        return self._config
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint.
        
        This is a placeholder implementation that returns an optimal result.
        Routing algorithms will be added in a future phase.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult - currently always optimal.
        """
        # Placeholder - routing not yet implemented
        return ConstraintResult.create()


class StairWidthConstraint(BuildingCodeConstraint):
    """Checks if any stair has a width below the minimum threshold.
    
    Attributes:
        config: Configuration with minimum stair width threshold.
    """
    
    def __init__(
        self,
        config: MinimumStairWidthConfig | None = None,
    ) -> None:
        """Initialize the StairWidthConstraint.
        
        Args:
            config: Configuration with minimum stair width threshold.
        """
        super().__init__(
            name="Minimum Stair Width",
            description="Checks if any stair has a width below the minimum threshold",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or MinimumStairWidthConfig()
    
    @property
    def config(self) -> MinimumStairWidthConfig:
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
            ConstraintResult with issues for stairs below minimum width.
        """
        result = ConstraintResult.create()
        
        for stair_id, stair in building_model.stairs.items():
            if stair.width < self._config.minimum_width:
                result.add_issue(ConstraintIssue(
                    code=STAIR_WIDTH_BELOW_MINIMUM,
                    message=(
                        f"Stair width ({stair.width:.2f} ft) is below "
                        f"minimum ({self._config.minimum_width:.2f} ft)"
                    ),
                    severity=self.default_severity,
                    entity_id=stair_id,
                    entity_type="Stair",
                    score=self._calculate_score(stair.width, self._config.minimum_width),
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


class CeilingHeightConstraint(BuildingCodeConstraint):
    """Checks if any room has a ceiling height below the minimum threshold.
    
    Attributes:
        config: Configuration with minimum ceiling height threshold.
    """
    
    def __init__(
        self,
        config: MinimumCeilingHeightConfig | None = None,
    ) -> None:
        """Initialize the CeilingHeightConstraint.
        
        Args:
            config: Configuration with minimum ceiling height threshold.
        """
        super().__init__(
            name="Minimum Ceiling Height",
            description="Checks if any room has a ceiling height below the minimum threshold",
            default_severity=ConstraintSeverity.WARNING,
        )
        self._config = config or MinimumCeilingHeightConfig()
    
    @property
    def config(self) -> MinimumCeilingHeightConfig:
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
            ConstraintResult with issues for rooms below minimum ceiling height.
        """
        result = ConstraintResult.create()
        
        for room_id, room in building_model.rooms.items():
            if room.ceiling_height is None:
                continue
            
            if room.ceiling_height < self._config.minimum_height:
                room_name = room.metadata.get("name", room_id)
                result.add_issue(ConstraintIssue(
                    code=CEILING_HEIGHT_BELOW_MINIMUM,
                    message=(
                        f"Room '{room_name}' ceiling height ({room.ceiling_height:.1f} ft) "
                        f"is below minimum ({self._config.minimum_height:.1f} ft)"
                    ),
                    severity=self.default_severity,
                    entity_id=room_id,
                    entity_type="Room",
                    score=self._calculate_score(room.ceiling_height, self._config.minimum_height),
                ))
        
        return result
    
    def _calculate_score(self, actual: float, minimum: float) -> float:
        """Calculate quality score impact.
        
        Args:
            actual: The actual height.
            minimum: The minimum required height.
            
        Returns:
            Score impact (0.0 to 1.0).
        """
        if minimum <= 0:
            return 0.0
        ratio = actual / minimum
        if ratio >= 1.0:
            return 0.0
        return min(1.0, 1.0 - ratio)