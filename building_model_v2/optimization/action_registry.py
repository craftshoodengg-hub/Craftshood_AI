"""Action Registry for Building Model v2.

Central registry mapping constraint codes to optimization functions.
All mappings exist in one location - no scattered dictionaries.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from .optimization_action import OptimizationAction
from .optimization_actions import (
    add_elevator_placeholder,
    add_opposite_window_placeholder,
    add_ramp_placeholder,
    add_window_placeholder,
    expand_room,
    increase_ceiling_height,
    increase_door_width,
    increase_room_height,
    increase_stair_width,
    increase_window_area,
    increase_window_size,
)

# Type alias for optimization functions
OptimizationFunc = Callable[[object, OptimizationAction], object]


class ActionRegistry:
    """Central registry mapping constraint codes to optimization functions.

    This class provides a single location for all constraint-to-action mappings.
    Actions are registered deterministically and looked up by constraint code.

    Future extension points:
        - topology optimization
        - wall movement
        - room relocation
        - corridor optimization
        - furniture placement
    """

    def __init__(self) -> None:
        """Initialize the registry with default mappings."""
        self._registry: Dict[str, OptimizationFunc] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all default optimization actions."""
        # Room optimizations
        self.register("ROOM_AREA_BELOW_MINIMUM", expand_room)
        self.register("ROOM_TOO_SMALL", expand_room)
        self.register("ROOM_WITHOUT_WINDOW", add_window_placeholder)

        # Window optimizations
        self.register("WINDOW_TO_FLOOR_RATIO_LOW", increase_window_size)
        self.register("NATURAL_LIGHT_INSUFFICIENT", increase_window_area)
        self.register("CROSS_VENTILATION_POSSIBLE", add_opposite_window_placeholder)

        # Door optimizations
        self.register("DOOR_WIDTH_BELOW_MINIMUM", increase_door_width)
        self.register("DOOR_TOO_NARROW", increase_door_width)

        # Stair optimizations
        self.register("STAIR_WIDTH_BELOW_MINIMUM", increase_stair_width)
        self.register("STAIR_TOO_NARROW", increase_stair_width)

        # Ceiling/Room height optimizations
        self.register("CEILING_HEIGHT_BELOW_MINIMUM", increase_ceiling_height)
        self.register("ROOM_HEIGHT_INSUFFICIENT", increase_room_height)

        # Accessibility optimizations
        self.register("ACCESSIBILITY_RAMP_MISSING", add_ramp_placeholder)
        self.register("ELEVATOR_MISSING", add_elevator_placeholder)

    def register(self, constraint_code: str, func: OptimizationFunc) -> None:
        """Register an optimization function for a constraint code.

        Args:
            constraint_code: The constraint code to map.
            func: The optimization function to call.
        """
        self._registry[constraint_code] = func

    def get(self, constraint_code: str) -> Optional[OptimizationFunc]:
        """Get the optimization function for a constraint code.

        Args:
            constraint_code: The constraint code to look up.

        Returns:
            The optimization function if found, None otherwise.
        """
        return self._registry.get(constraint_code)

    def has(self, constraint_code: str) -> bool:
        """Check if a constraint code has a registered action.

        Args:
            constraint_code: The constraint code to check.

        Returns:
            True if a function is registered.
        """
        return constraint_code in self._registry

    @property
    def registered_codes(self) -> frozenset[str]:
        """Get all registered constraint codes.

        Returns:
            Frozenset of registered constraint codes.
        """
        return frozenset(self._registry.keys())

    def __contains__(self, constraint_code: str) -> bool:
        """Check if constraint code is registered."""
        return self.has(constraint_code)

    def __len__(self) -> int:
        """Get number of registered actions."""
        return len(self._registry)
