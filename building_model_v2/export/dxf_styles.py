"""DXF Line Types and Styles for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Final, Tuple


@dataclass(frozen=True, slots=True)
class LineType:
    name: str
    description: str = ""
    pattern: Tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class Color:
    r: int
    g: int
    b: int

    @property
    def aci(self) -> int:
        """AutoCAD Color Index."""
        color_map = {
            (0, 0, 0): 7, (255, 0, 0): 1, (255, 255, 0): 2, (0, 255, 0): 3,
            (0, 255, 255): 4, (0, 0, 255): 5, (255, 0, 255): 6, (255, 255, 255): 7,
            (128, 128, 128): 8, (192, 192, 192): 9,
        }
        return color_map.get((self.r, self.g, self.b), 7)


@dataclass(frozen=True, slots=True)
class DXFStyle:
    name: str
    color: Color
    line_type: LineType
    line_width: float = 0.25
    text_height: float = 0.5


# Line types
LINE_CONTINUOUS: Final = LineType("CONTINUOUS", "Solid line")
LINE_HIDDEN: Final = LineType("HIDDEN", "Hidden line", (0.25, -0.12))
LINE_CENTER: Final = LineType("CENTER", "Center line", (0.5, -0.12, 0.12, -0.12))

# Colors
COLOR_WALL: Final = Color(0, 0, 0)
COLOR_DOOR: Final = Color(0, 0, 255)
COLOR_WINDOW: Final = Color(0, 255, 255)
COLOR_COLUMN: Final = Color(128, 128, 128)
COLOR_STAIR: Final = Color(255, 255, 0)
COLOR_TEXT: Final = Color(255, 255, 255)
COLOR_DIM: Final = Color(128, 128, 128)
COLOR_GRID: Final = Color(200, 200, 200)
COLOR_HATCH: Final = Color(220, 220, 220)
COLOR_TITLE: Final = Color(0, 0, 0)

# Styles
STYLE_WALL: Final = DXFStyle("A-WALL", COLOR_WALL, LINE_CONTINUOUS, 0.35)
STYLE_DOOR: Final = DXFStyle("A-DOOR", COLOR_DOOR, LINE_CONTINUOUS, 0.25)
STYLE_WINDOW: Final = DXFStyle("A-WINDOW", COLOR_WINDOW, LINE_CONTINUOUS, 0.25)
STYLE_COLUMN: Final = DXFStyle("A-COLUMN", COLOR_COLUMN, LINE_CONTINUOUS, 0.25)
STYLE_STAIR: Final = DXFStyle("A-STAIR", COLOR_STAIR, LINE_CONTINUOUS, 0.25)
STYLE_TEXT: Final = DXFStyle("A-TEXT", COLOR_TEXT, LINE_CONTINUOUS, 0.18, 0.5)
STYLE_DIM: Final = DXFStyle("A-DIMS", COLOR_DIM, LINE_CONTINUOUS, 0.18)
STYLE_GRID: Final = DXFStyle("A-GRID", COLOR_GRID, LINE_CONTINUOUS, 0.09)

ALL_STYLES: Final = [STYLE_WALL, STYLE_DOOR, STYLE_WINDOW, STYLE_COLUMN, STYLE_STAIR, STYLE_TEXT, STYLE_DIM, STYLE_GRID]
STYLE_MAP: Final[Dict[str, DXFStyle]] = {s.name: s for s in ALL_STYLES}
