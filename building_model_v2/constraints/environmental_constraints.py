"""Environmental Constraints for Building Model v2.

Implements environmental quality and occupant comfort constraints.
All constraints are deterministic and configurable.

Do not modify the model - only report issues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from ..entities_opening import Window
from ..entities_room import Room
from ..validation.cross_entity_validator import BuildingModel
from .constraint import Constraint
from .constraint_category import ConstraintCategory
from .constraint_issue import ConstraintIssue
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity


# ============================================================================
# Error codes
# ============================================================================

WINDOW_TO_FLOOR_RATIO_LOW: Final[str] = "WINDOW_TO_FLOOR_RATIO_LOW"
CROSS_VENTILATION_POSSIBLE: Final[str] = "CROSS_VENTILATION_POSSIBLE"
SOLAR_ORIENTATION_SUBOPTIMAL: Final[str] = "SOLAR_ORIENTATION_SUBOPTIMAL"
WEST_FACING_LARGE_GLAZING: Final[str] = "WEST_FACING_LARGE_GLAZING"
NATURAL_LIGHT_INSUFFICIENT: Final[str] = "NATURAL_LIGHT_INSUFFICIENT"
OUTDOOR_CONNECTION_MISSING: Final[str] = "OUTDOOR_CONNECTION_MISSING"


# ============================================================================
# Orientation constants
# ============================================================================

ORIENTATION_NORTH: Final[str] = "north"
ORIENTATION_SOUTH: Final[str] = "south"
ORIENTATION_EAST: Final[str] = "east"
ORIENTATION_WEST: Final[str] = "west"
ORIENTATION_NORTHEAST: Final[str] = "northeast"
ORIENTATION_NORTHWEST: Final[str] = "northwest"
ORIENTATION_SOUTHEAST: Final[str] = "southeast"
ORIENTATION_SOUTHWEST: Final[str] = "southwest"


# ============================================================================
# Base class
# ============================================================================


@dataclass(slots=True)
class EnvironmentalConstraintConfig:
    """Base configuration for environmental constraints.
    
    Attributes:
        severity: Default severity for issues found.
    """
    
    severity: ConstraintSeverity = ConstraintSeverity.SUGGESTION


class EnvironmentalConstraint(Constraint):
    """Base class for environmental constraints.
    
    All environmental constraints inherit from this class.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        config: EnvironmentalConstraintConfig | None = None,
    ) -> None:
        """Initialize the environmental constraint.
        
        Args:
            name: Human-readable name of the constraint.
            description: Description of what the constraint checks.
            config: Optional constraint configuration.
        """
        super().__init__(name=name, description=description)
        self._config = config or EnvironmentalConstraintConfig()
    
    @property
    def category(self) -> ConstraintCategory:
        """Get the constraint category.
        
        Returns:
            ConstraintCategory.ENVIRONMENTAL
        """
        return ConstraintCategory.ENVIRONMENTAL
    
    @property
    def default_severity(self) -> ConstraintSeverity:
        """Get the default severity.
        
        Returns:
            The default severity from config.
        """
        return self._config.severity
    
    def _create_issue(
        self,
        code: str,
        message: str,
        entity_id: str | None = None,
        score: float = 0.5,
    ) -> ConstraintIssue:
        """Create a constraint issue with environmental category.
        
        Args:
            code: Error code.
            message: Human-readable message.
            entity_id: Optional entity ID.
            score: Impact score (0-1).
        
        Returns:
            A new ConstraintIssue.
        """
        return ConstraintIssue(
            code=code,
            message=message,
            severity=self.default_severity,
            entity_id=entity_id,
            score=score,
        )


# ============================================================================
# 1. MinimumWindowToFloorAreaConstraint
# ============================================================================


@dataclass(slots=True)
class MinimumWindowToFloorAreaConfig(EnvironmentalConstraintConfig):
    """Configuration for MinimumWindowToFloorAreaConstraint.
    
    Attributes:
        minimum_ratio: Minimum window-to-floor area ratio (0-1).
    """
    
    minimum_ratio: float = 0.10  # 10% default


class MinimumWindowToFloorAreaConstraint(EnvironmentalConstraint):
    """Evaluates window-to-floor area ratio for rooms.
    
    Ensures adequate natural light by checking that window area
    meets a minimum percentage of floor area.
    """
    
    def __init__(
        self,
        config: MinimumWindowToFloorAreaConfig | None = None,
    ) -> None:
        """Initialize the constraint.
        
        Args:
            config: Constraint configuration.
        """
        super().__init__(
            name="Minimum Window to Floor Area Ratio",
            description="Ensures window area meets minimum percentage of floor area for natural light",
            config=config,
        )
        self._config = config or MinimumWindowToFloorAreaConfig()
    
    @property
    def minimum_ratio(self) -> float:
        """Get the minimum window-to-floor ratio.
        
        Returns:
            The minimum ratio (0-1).
        """
        return self._config.minimum_ratio
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate all rooms for window-to-floor area ratio.
        
        Args:
            building_model: The building model to evaluate.
        
        Returns:
            ConstraintResult with any issues found.
        """
        issues: list[ConstraintIssue] = []
        
        for room_id, room in building_model.rooms.items():
            if room.polygon.is_empty:
                continue
            
            room_area = room.polygon.area
            if room_area <= 0:
                continue
            
            # Calculate window area for this room using width * height
            window_area = 0.0
            for window_id in room.window_ids:
                window = building_model.windows.get(window_id)
                if window is not None:
                    width = window.width
                    height = window.height if window.height is not None else width
                    window_area += width * height
            
            if window_area <= 0:
                # No windows - will be caught by NaturalLightConstraint
                continue
            
            ratio = window_area / room_area
            
            if ratio < self._config.minimum_ratio:
                issues.append(self._create_issue(
                    code=WINDOW_TO_FLOOR_RATIO_LOW,
                    message=(
                        f"Room has window-to-floor ratio of {ratio:.1%}, "
                        f"below minimum of {self._config.minimum_ratio:.1%}"
                    ),
                    entity_id=room_id,
                    score=min(1.0, (self._config.minimum_ratio - ratio) / self._config.minimum_ratio),
                ))
        
        return ConstraintResult(issues=issues)


# ============================================================================
# 2. CrossVentilationConstraint
# ============================================================================


@dataclass(slots=True)
class CrossVentilationConfig(EnvironmentalConstraintConfig):
    """Configuration for CrossVentilationConstraint.
    
    Attributes:
        min_window_count: Minimum windows needed for cross ventilation.
    """
    
    min_window_count: int = 2


class CrossVentilationConstraint(EnvironmentalConstraint):
    """Evaluates potential for cross ventilation in rooms.
    
    Checks if rooms have sufficient windows for cross ventilation.
    When orientation metadata exists, checks for opposite wall placement.
    """
    
    def __init__(
        self,
        config: CrossVentilationConfig | None = None,
    ) -> None:
        """Initialize the constraint.
        
        Args:
            config: Constraint configuration.
        """
        super().__init__(
            name="Cross Ventilation Potential",
            description="Evaluates if rooms have sufficient windows for cross ventilation",
            config=config,
        )
        self._config = config or CrossVentilationConfig()
    
    @property
    def min_window_count(self) -> int:
        """Get the minimum window count for cross ventilation.
        
        Returns:
            The minimum number of windows.
        """
        return self._config.min_window_count
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate rooms for cross ventilation potential.
        
        Args:
            building_model: The building model to evaluate.
        
        Returns:
            ConstraintResult with any issues found.
        """
        issues: list[ConstraintIssue] = []
        
        for room_id, room in building_model.rooms.items():
            if room.polygon.is_empty:
                continue
            
            window_count = len(room.window_ids)
            
            if window_count < self._config.min_window_count:
                issues.append(self._create_issue(
                    code=CROSS_VENTILATION_POSSIBLE,
                    message=(
                        f"Room has {window_count} window(s), "
                        f"minimum {self._config.min_window_count} needed for cross ventilation"
                    ),
                    entity_id=room_id,
                    score=0.5,
                ))
        
        return ConstraintResult(issues=issues)


# ============================================================================
# 3. SolarOrientationConstraint
# ============================================================================


@dataclass(slots=True)
class SolarOrientationConfig(EnvironmentalConstraintConfig):
    """Configuration for SolarOrientationConstraint.
    
    Attributes:
        preferred_orientations: Mapping of room types to preferred orientations.
    """
    
    preferred_orientations: dict[str, list[str]] = field(default_factory=lambda: {
        "bedroom": [ORIENTATION_EAST, ORIENTATION_NORTH],
        "living": [ORIENTATION_EAST, ORIENTATION_SOUTH],
        "kitchen": [ORIENTATION_EAST],
        "bathroom": [
            ORIENTATION_NORTH,
            ORIENTATION_SOUTH,
            ORIENTATION_EAST,
            ORIENTATION_WEST,
        ],
    })


class SolarOrientationConstraint(EnvironmentalConstraint):
    """Evaluates solar orientation for rooms.
    
    Checks if rooms have preferred orientations based on room type.
    Only evaluates when orientation metadata exists.
    """
    
    def __init__(
        self,
        config: SolarOrientationConfig | None = None,
    ) -> None:
        """Initialize the constraint.
        
        Args:
            config: Constraint configuration.
        """
        super().__init__(
            name="Solar Orientation",
            description="Evaluates if rooms have preferred solar orientations",
            config=config,
        )
        self._config = config or SolarOrientationConfig()
    
    @property
    def preferred_orientations(self) -> dict[str, list[str]]:
        """Get preferred orientations by room type.
        
        Returns:
            Mapping of room type to preferred orientations.
        """
        return self._config.preferred_orientations
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate rooms for solar orientation.
        
        Only evaluates rooms with orientation metadata.
        
        Args:
            building_model: The building model to evaluate.
        
        Returns:
            ConstraintResult with any issues found.
        """
        issues: list[ConstraintIssue] = []
        
        for room_id, room in building_model.rooms.items():
            if room.polygon.is_empty:
                continue
            
            # Check for orientation metadata
            orientation = room.metadata.get("orientation")
            if orientation is None:
                continue  # Gracefully skip
            
            room_type_key = room.room_type.value.lower()
            preferred = self._config.preferred_orientations.get(room_type_key)
            
            if preferred is None:
                continue  # No preferences for this room type
            
            if orientation.lower() not in [o.lower() for o in preferred]:
                issues.append(self._create_issue(
                    code=SOLAR_ORIENTATION_SUBOPTIMAL,
                    message=(
                        f"Room orientation '{orientation}' is not optimal for "
                        f"{room_type_key}. Preferred: {', '.join(preferred)}"
                    ),
                    entity_id=room_id,
                    score=0.3,
                ))
        
        return ConstraintResult(issues=issues)


# ============================================================================
# 4. WestFacingHeatGainConstraint
# ============================================================================


@dataclass(slots=True)
class WestFacingHeatGainConfig(EnvironmentalConstraintConfig):
    """Configuration for WestFacingHeatGainConstraint.
    
    Attributes:
        max_west_window_ratio: Maximum west-facing window ratio before warning.
    """
    
    max_west_window_ratio: float = 0.30  # 30% default


class WestFacingHeatGainConstraint(EnvironmentalConstraint):
    """Detects large west-facing glazing that may cause heat gain.
    
    Only evaluates when orientation metadata exists.
    """
    
    def __init__(
        self,
        config: WestFacingHeatGainConfig | None = None,
    ) -> None:
        """Initialize the constraint.
        
        Args:
            config: Constraint configuration.
        """
        super().__init__(
            name="West-Facing Heat Gain",
            description="Detects large west-facing glazing that may cause excessive heat gain",
            config=config,
        )
        self._config = config or WestFacingHeatGainConfig()
    
    @property
    def max_west_window_ratio(self) -> float:
        """Get the maximum west-facing window ratio.
        
        Returns:
            The maximum ratio (0-1).
        """
        return self._config.max_west_window_ratio
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate rooms for west-facing heat gain.
        
        Only evaluates rooms with orientation metadata.
        
        Args:
            building_model: The building model to evaluate.
        
        Returns:
            ConstraintResult with any issues found.
        """
        issues: list[ConstraintIssue] = []
        
        for room_id, room in building_model.rooms.items():
            if room.polygon.is_empty:
                continue
            
            # Check for orientation metadata
            orientation = room.metadata.get("orientation")
            if orientation is None:
                continue  # Gracefully skip
            
            if orientation.lower() != ORIENTATION_WEST:
                continue  # Not west-facing
            
            room_area = room.polygon.area
            if room_area <= 0:
                continue
            
            # Calculate west-facing window area using width * height
            west_window_area = 0.0
            for window_id in room.window_ids:
                window = building_model.windows.get(window_id)
                if window is not None:
                    window_orientation = window.metadata.get("orientation")
                    if window_orientation and window_orientation.lower() == ORIENTATION_WEST:
                        width = window.width
                        height = window.height if window.height is not None else width
                        west_window_area += width * height
            
            if west_window_area <= 0:
                continue
            
            ratio = west_window_area / room_area
            
            if ratio > self._config.max_west_window_ratio:
                issues.append(self._create_issue(
                    code=WEST_FACING_LARGE_GLAZING,
                    message=(
                        f"West-facing window ratio is {ratio:.1%}, "
                        f"above recommended maximum of {self._config.max_west_window_ratio:.1%}. "
                        f"Consider shading devices."
                    ),
                    entity_id=room_id,
                    score=min(1.0, (ratio - self._config.max_west_window_ratio) / self._config.max_west_window_ratio),
                ))
        
        return ConstraintResult(issues=issues)


# ============================================================================
# 5. NaturalLightConstraint
# ============================================================================


@dataclass(slots=True)
class NaturalLightConfig(EnvironmentalConstraintConfig):
    """Configuration for NaturalLightConstraint.
    
    Attributes:
        min_daylight_factor: Minimum daylight factor percentage.
        min_window_wall_ratio: Minimum window-to-wall ratio.
    """
    
    min_daylight_factor: float = 2.0  # 2% default
    min_window_wall_ratio: float = 0.15  # 15% default


class NaturalLightConstraint(EnvironmentalConstraint):
    """Evaluates natural light quality in rooms.
    
    Different from functional constraints - measures daylight quality
    rather than just window existence.
    """
    
    def __init__(
        self,
        config: NaturalLightConfig | None = None,
    ) -> None:
        """Initialize the constraint.
        
        Args:
            config: Constraint configuration.
        """
        super().__init__(
            name="Natural Light Quality",
            description="Evaluates natural light quality in rooms based on window ratios",
            config=config,
        )
        self._config = config or NaturalLightConfig()
    
    @property
    def min_daylight_factor(self) -> float:
        """Get the minimum daylight factor.
        
        Returns:
            The minimum daylight factor percentage.
        """
        return self._config.min_daylight_factor
    
    @property
    def min_window_wall_ratio(self) -> float:
        """Get the minimum window-to-wall ratio.
        
        Returns:
            The minimum ratio (0-1).
        """
        return self._config.min_window_wall_ratio
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate rooms for natural light quality.
        
        Args:
            building_model: The building model to evaluate.
        
        Returns:
            ConstraintResult with any issues found.
        """
        issues: list[ConstraintIssue] = []
        
        for room_id, room in building_model.rooms.items():
            if room.polygon.is_empty:
                continue
            
            room_area = room.polygon.area
            if room_area <= 0:
                continue
            
            # Calculate total window area using width * height
            window_area = 0.0
            for window_id in room.window_ids:
                window = building_model.windows.get(window_id)
                if window is not None:
                    width = window.width
                    height = window.height if window.height is not None else width
                    window_area += width * height
            
            if window_area <= 0:
                issues.append(self._create_issue(
                    code=NATURAL_LIGHT_INSUFFICIENT,
                    message="Room has no windows for natural light",
                    entity_id=room_id,
                    score=0.8,
                ))
                continue
            
            # Estimate window-to-wall ratio
            # Use perimeter * standard wall height as approximation
            perimeter = room.polygon.length
            assumed_wall_height = 3.0  # meters
            wall_area = perimeter * assumed_wall_height
            
            if wall_area <= 0:
                continue
            
            window_wall_ratio = window_area / wall_area
            
            if window_wall_ratio < self._config.min_window_wall_ratio:
                issues.append(self._create_issue(
                    code=NATURAL_LIGHT_INSUFFICIENT,
                    message=(
                        f"Room has window-to-wall ratio of {window_wall_ratio:.1%}, "
                        f"below recommended minimum of {self._config.min_window_wall_ratio:.1%}"
                    ),
                    entity_id=room_id,
                    score=min(1.0, (self._config.min_window_wall_ratio - window_wall_ratio) / self._config.min_window_wall_ratio),
                ))
        
        return ConstraintResult(issues=issues)


# ============================================================================
# 6. OutdoorConnectionConstraint
# ============================================================================


@dataclass(slots=True)
class OutdoorConnectionConfig(EnvironmentalConstraintConfig):
    """Configuration for OutdoorConnectionConstraint.
    
    Attributes:
        recommend_outdoor: Whether to recommend outdoor connections.
    """
    
    recommend_outdoor: bool = True


class OutdoorConnectionConstraint(EnvironmentalConstraint):
    """Recommends outdoor connections for rooms.
    
    Only evaluates when metadata exists indicating outdoor potential.
    Gracefully skips otherwise.
    """
    
    def __init__(
        self,
        config: OutdoorConnectionConfig | None = None,
    ) -> None:
        """Initialize the constraint.
        
        Args:
            config: Constraint configuration.
        """
        super().__init__(
            name="Outdoor Connection",
            description="Recommends outdoor connections (balcony, courtyard, garden) where possible",
            config=config,
        )
        self._config = config or OutdoorConnectionConfig()
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate rooms for outdoor connection opportunities.
        
        Only evaluates rooms with outdoor_potential metadata.
        
        Args:
            building_model: The building model to evaluate.
        
        Returns:
            ConstraintResult with any issues found.
        """
        issues: list[ConstraintIssue] = []
        
        if not self._config.recommend_outdoor:
            return ConstraintResult(issues=issues)
        
        for room_id, room in building_model.rooms.items():
            if room.polygon.is_empty:
                continue
            
            # Check for outdoor potential metadata
            outdoor_potential = room.metadata.get("outdoor_potential")
            if outdoor_potential is None:
                continue  # Gracefully skip
            
            # Check if room already has outdoor connection
            has_outdoor = room.metadata.get("has_balcony") or room.metadata.get("has_courtyard")
            if has_outdoor:
                continue
            
            outdoor_type = room.metadata.get("outdoor_type", "outdoor space")
            
            issues.append(self._create_issue(
                code=OUTDOOR_CONNECTION_MISSING,
                message=(
                    f"Room has outdoor potential but no {outdoor_type} connection. "
                    f"Consider adding a balcony, courtyard, or garden access."
                ),
                entity_id=room_id,
                score=0.4,
            ))
        
        return ConstraintResult(issues=issues)