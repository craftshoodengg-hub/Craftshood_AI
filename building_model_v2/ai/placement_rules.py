"""Placement Rules for Craftshood AI.

Deterministic room placement rules for layout generation.
No AI. Pure deterministic heuristics.
"""
from __future__ import annotations
from typing import Dict, FrozenSet, List, Tuple

from .room_program import FloorPreference, PrivacyLevel


# ============================================================================
# Floor Assignment Rules
# ============================================================================

GROUND_FLOOR_TYPES: FrozenSet[str] = frozenset({
    "living", "dining", "kitchen", "parking", "entrance", "utility", "stair",
})

UPPER_FLOOR_TYPES: FrozenSet[str] = frozenset({
    "bedroom", "master_bedroom", "bathroom", "common_bathroom", "balcony",
    "office",
})


def assign_floor(room_type: str, floor_preference: FloorPreference, max_floors: int) -> int:
    """Assign a room to a specific floor (0-indexed).

    Args:
        room_type: Type of room.
        floor_preference: Preferred floor level.
        max_floors: Maximum number of floors.

    Returns:
        Floor index (0-based).
    """
    if max_floors <= 1:
        return 0

    if floor_preference == FloorPreference.GROUND:
        return 0
    elif floor_preference == FloorPreference.UPPER:
        return min(1, max_floors - 1)

    # Use type-based defaults
    if room_type in GROUND_FLOOR_TYPES:
        return 0
    elif room_type in UPPER_FLOOR_TYPES:
        return min(1, max_floors - 1)

    # Default: ground floor
    return 0


# ============================================================================
# Adjacency Rules (room_type -> preferred neighbors)
# ============================================================================

ROOM_ADJACENCY: Dict[str, FrozenSet[str]] = {
    "entrance": frozenset({"living"}),
    "living": frozenset({"dining", "entrance", "pooja"}),
    "dining": frozenset({"living", "kitchen"}),
    "kitchen": frozenset({"dining", "utility"}),
    "utility": frozenset({"kitchen"}),
    "master_bedroom": frozenset({"bathroom"}),
    "bedroom": frozenset({"common_bathroom"}),
    "bathroom": frozenset({"master_bedroom"}),
    "common_bathroom": frozenset({"bedroom"}),
    "parking": frozenset({"entrance"}),
    "office": frozenset({"living", "entrance"}),
    "pooja": frozenset({"living", "entrance"}),
    "stair": frozenset({"living"}),
    "balcony": frozenset({"bedroom", "master_bedroom"}),
}


# ============================================================================
# Privacy-based Placement Priority (lower = closer to entrance)
# ============================================================================

PRIVACY_PLACEMENT_ORDER: Dict[PrivacyLevel, int] = {
    PrivacyLevel.PUBLIC: 0,
    PrivacyLevel.SEMI_PRIVATE: 1,
    PrivacyLevel.PRIVATE: 2,
    PrivacyLevel.SERVICE: 1,
}


# ============================================================================
# Room Placement Order (sorted by priority)
# ============================================================================

PLACEMENT_PRIORITY: Dict[str, int] = {
    "entrance": 0,
    "parking": 1,
    "living": 2,
    "dining": 3,
    "kitchen": 4,
    "stair": 5,
    "master_bedroom": 6,
    "bedroom": 7,
    "common_bathroom": 8,
    "bathroom": 9,
    "balcony": 10,
    "utility": 11,
    "office": 12,
    "pooja": 13,
}


# ============================================================================
# Grid Layout Constants
# ============================================================================

GRID_MODULE_FT: float = 10.0  # Base grid module size
CORRIDOR_WIDTH_FT: float = 5.0  # Corridors between rooms
ENTRANCE_SIZE_FT: float = 40.0  # Minimum entrance area


def get_priority(room_type: str) -> int:
    """Get placement priority for a room type (lower = placed first)."""
    return PLACEMENT_PRIORITY.get(room_type, 99)
