"""Vastu package for Building Model v2.

Provides deterministic Vastu Shastra data models for building analysis.
Includes direction, zone, rule, metadata, grid, geometry, and analyzer types.

No AI. No evaluation. No constraint engine integration.
Pure deterministic data structures only.
"""

from .vastu_direction import VastuDirection
from .vastu_geometry import (
    calculate_building_center,
    calculate_plot_rotation,
    calculate_room_centroid,
    calculate_room_direction,
    determine_zone,
    rotate_point,
    zone_to_vastu_zone,
)
from .vastu_grid import VastuCell, VastuGrid
from .vastu_analyzer import VastuAnalyzer
from .vastu_metadata import VastuMetadata
from .vastu_rule import VastuRule
from .vastu_zone import VastuZone

__all__ = [
    "VastuDirection",
    "VastuMetadata",
    "VastuRule",
    "VastuZone",
    "VastuCell",
    "VastuGrid",
    "VastuAnalyzer",
    "calculate_building_center",
    "calculate_plot_rotation",
    "calculate_room_centroid",
    "calculate_room_direction",
    "determine_zone",
    "rotate_point",
    "zone_to_vastu_zone",
]