"""Enumeration types for Building Model v2.

All enumerations use StrEnum for direct JSON serialization compatibility.
Values are human-readable strings suitable for display in UI and export formats.
"""

from __future__ import annotations

from enum import StrEnum


class RoomType(StrEnum):
    """Room classification types.
    
    Used for:
    - Room identification and labeling
    - Zoning analysis
    - Vastu compliance checking
    - Flutter UI display
    """
    
    LIVING = "Living"
    BEDROOM = "Bedroom"
    KITCHEN = "Kitchen"
    DINING = "Dining"
    TOILET = "Toilet"
    BATHROOM = "Bathroom"
    STORAGE = "Storage"
    CORRIDOR = "Corridor"
    STAIRCASE = "Staircase"
    BALCONY = "Balcony"
    UTILITY = "Utility"
    UNKNOWN = "Unknown"


class WallType(StrEnum):
    """Wall classification types.
    
    Used for:
    - Structural analysis
    - Wall thickness estimation
    - BIM/IFC export mapping
    """
    
    EXTERIOR = "Exterior"
    INTERIOR = "Interior"
    PARTITION = "Partition"
    BEARING = "Bearing"
    SHEAR = "Shear"
    UNKNOWN = "Unknown"


class OpeningType(StrEnum):
    """Opening classification types.
    
    Base classification for doors, windows, and other openings.
    Used for:
    - Opening type filtering
    - BIM/IFC export mapping
    """
    
    DOOR = "Door"
    WINDOW = "Window"
    VENTILATION = "Ventilation"
    ARCHWAY = "Archway"
    SLIDING_DOOR = "Sliding Door"
    FRENCH_DOOR = "French Door"
    UNKNOWN = "Unknown"


class DoorType(StrEnum):
    """Door classification types.
    
    Used for:
    - Door type identification
    - Swing direction analysis
    - BIM/IFC export mapping
    """
    
    SINGLE_LEAF = "Single Leaf"
    DOUBLE_LEAF = "Double Leaf"
    SLIDING = "Sliding"
    FOLDING = "Folding"
    REVOLVING = "Revolving"
    UNKNOWN = "Unknown"


class WindowType(StrEnum):
    """Window classification types.
    
    Used for:
    - Window type identification
    - Ventilation analysis
    - BIM/IFC export mapping
    """
    
    FIXED = "Fixed"
    CASEMENT = "Casement"
    SLIDING = "Sliding"
    AWNING = "Awning"
    BAY = "Bay"
    UNKNOWN = "Unknown"


class ColumnType(StrEnum):
    """Column classification types.
    
    Used for:
    - Structural analysis
    - Column type identification
    - BIM/IFC export mapping
    """
    
    RECTANGULAR = "Rectangular"
    CIRCULAR = "Circular"
    SQUARE = "Square"
    STRUCTURAL = "Structural"
    UNKNOWN = "Unknown"


class StairType(StrEnum):
    """Stair classification types.
    
    Used for:
    - Stair type identification
    - Egress analysis
    - BIM/IFC export mapping
    """
    
    STRAIGHT = "Straight"
    L_SHAPED = "L-Shaped"
    U_SHAPED = "U-Shaped"
    SPIRAL = "Spiral"
    CURVED = "Curved"
    UNKNOWN = "Unknown"


class FloorType(StrEnum):
    """Floor classification types.
    
    Used for:
    - Floor level identification
    - Multi-floor analysis
    - Vastu analysis (ground floor importance)
    """
    
    GROUND = "Ground"
    BASEMENT = "Basement"
    UPPER = "Upper"
    ROOF = "Roof"
    MEZZANINE = "Mezzanine"
    UNKNOWN = "Unknown"


class Orientation(StrEnum):
    """Cardinal and intercardinal directions.
    
    Used for:
    - Room orientation analysis
    - Vastu compliance checking
    - Building orientation calculation
    - Flutter compass display
    """
    
    NORTH = "North"
    NORTHEAST = "Northeast"
    EAST = "East"
    SOUTHEAST = "Southeast"
    SOUTH = "South"
    SOUTHWEST = "Southwest"
    WEST = "West"
    NORTHWEST = "Northwest"
    CENTER = "Center"
    UNKNOWN = "Unknown"