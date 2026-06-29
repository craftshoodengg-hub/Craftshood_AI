"""SVG styling constants and utilities.

Separates visual styling from the SVG exporter logic.
All colors, stroke widths, font sizes, and fill opacities are defined here
to ensure consistency across the SVG output.

Deterministic — no randomness, no AI.
"""
from __future__ import annotations


# ==================== Layer Colors (hex) ====================

COLOR_WALL = "#000000"
COLOR_DOOR = "#0000FF"
COLOR_WINDOW = "#0080FF"
COLOR_COLUMN = "#808080"
COLOR_STAIR = "#FF8000"
COLOR_TEXT = "#000000"
COLOR_DIM = "#808080"
COLOR_GRID = "#D0D0D0"
COLOR_HATCH = "#C0C0C0"
COLOR_TITLE = "#000000"
COLOR_NORTH_ARROW = "#000000"
COLOR_SCALE_BAR = "#000000"
COLOR_BUILDING_OUTLINE = "#333333"
COLOR_ROOM_FILL = "#F5F5F5"


# ==================== Stroke Widths ====================

STROKE_WALL = 0.5
STROKE_DOOR = 0.35
STROKE_WINDOW = 0.25
STROKE_COLUMN = 0.25
STROKE_STAIR = 0.25
STROKE_GRID = 0.1
STROKE_DIM = 0.15
STROKE_BUILDING_OUTLINE = 0.7
STROKE_NORTH_ARROW = 0.3
STROKE_SCALE_BAR = 0.3


# ==================== Font Sizes ====================

FONT_SIZE_ROOM_LABEL = 0.5
FONT_SIZE_ROOM_AREA = 0.35
FONT_SIZE_DIM = 0.35
FONT_SIZE_TITLE = 0.4
FONT_SIZE_NORTH = 0.7
FONT_SIZE_SCALE = 0.35


# ==================== Fill Opacities ====================

OPACITY_ROOM_FILL = 0.3
OPACITY_HATCH = 0.5
OPACITY_COLUMN_FILL = 0.6


# ==================== Room Type Fill Colors ====================

ROOM_TYPE_COLORS: dict[str, str] = {
    "Living": "#E8F5E9",
    "Bedroom": "#E3F2FD",
    "Kitchen": "#FFF3E0",
    "Dining": "#F3E5F5",
    "Toilet": "#E0F7FA",
    "Bathroom": "#E0F2F1",
    "Storage": "#F5F5F5",
    "Corridor": "#ECEFF1",
    "Staircase": "#FFF8E1",
    "Balcony": "#F1F8E9",
    "Utility": "#EFEBE9",
    "Unknown": "#FAFAFA",
}


# ==================== Layer Name Constants ====================

LAYER_WALL = "A-WALL"
LAYER_DOOR = "A-DOOR"
LAYER_WINDOW = "A-WINDOW"
LAYER_COLUMN = "A-COLUMN"
LAYER_STAIR = "A-STAIR"
LAYER_TEXT = "A-TEXT"
LAYER_DIM = "A-DIMS"
LAYER_GRID = "A-GRID"
LAYER_HATCH = "A-HATCH"
LAYER_TITLE = "A-TITLE"


# ==================== SVG Defaults ====================

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SVG_VERSION = "1.1"
SVG_FONT_FAMILY = "Arial, Helvetica, sans-serif"
SVG_BACKGROUND = "#FFFFFF"


def room_fill_color(room_type_value: str) -> str:
    """Get the fill color for a room type.

    Args:
        room_type_value: The room type string value.

    Returns:
        Hex color string for the room fill.
    """
    return ROOM_TYPE_COLORS.get(room_type_value, ROOM_TYPE_COLORS["Unknown"])
