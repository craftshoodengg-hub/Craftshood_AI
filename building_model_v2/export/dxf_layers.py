"""DXF Layers for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Final

from .dxf_styles import ALL_STYLES, COLOR_GRID, COLOR_TEXT, LINE_CONTINUOUS, STYLE_GRID, STYLE_TEXT, Color, DXFStyle, LineType


@dataclass(frozen=True, slots=True)
class DXFLayer:
    name: str
    color: Color
    line_type: LineType
    line_width: float = 0.25
    visible: bool = True
    locked: bool = False

    def to_style(self) -> DXFStyle:
        return DXFStyle(name=self.name, color=self.color, line_type=self.line_type, line_width=self.line_width)


LAYER_WALL: Final = DXFLayer("A-WALL", Color(0, 0, 0), LineType("CONTINUOUS"), 0.35)
LAYER_DOOR: Final = DXFLayer("A-DOOR", Color(0, 0, 255), LineType("CONTINUOUS"), 0.25)
LAYER_WINDOW: Final = DXFLayer("A-WINDOW", Color(0, 255, 255), LineType("CONTINUOUS"), 0.25)
LAYER_COLUMN: Final = DXFLayer("A-COLUMN", Color(128, 128, 128), LineType("CONTINUOUS"), 0.25)
LAYER_STAIR: Final = DXFLayer("A-STAIR", Color(255, 255, 0), LineType("CONTINUOUS"), 0.25)
LAYER_TEXT: Final = DXFLayer("A-TEXT", Color(255, 255, 255), LineType("CONTINUOUS"), 0.18)
LAYER_DIM: Final = DXFLayer("A-DIMS", Color(128, 128, 128), LineType("CONTINUOUS"), 0.18)
LAYER_GRID: Final = DXFLayer("A-GRID", Color(200, 200, 200), LineType("CONTINUOUS"), 0.09)
LAYER_HATCH: Final = DXFLayer("A-HATCH", Color(220, 220, 220), LineType("CONTINUOUS"), 0.09)
LAYER_TITLE: Final = DXFLayer("A-TITLE", Color(0, 0, 0), LineType("CONTINUOUS"), 0.25)

ALL_LAYERS: Final = [
    LAYER_WALL, LAYER_DOOR, LAYER_WINDOW, LAYER_COLUMN, LAYER_STAIR,
    LAYER_TEXT, LAYER_DIM, LAYER_GRID, LAYER_HATCH, LAYER_TITLE,
]

LAYER_MAP: Final[Dict[str, DXFLayer]] = {layer.name: layer for layer in ALL_LAYERS}
