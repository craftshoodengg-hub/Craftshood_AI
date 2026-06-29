"""Drawing Settings for DXF Export."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Dict, Optional


class PaperSize(StrEnum):
    A4 = "A4"
    A3 = "A3"
    A2 = "A2"
    A1 = "A1"
    A0 = "A0"
    LETTER = "LETTER"
    LEGAL = "LEGAL"
    TABLOID = "TABLOID"


class DrawingUnits(StrEnum):
    FEET = "feet"
    INCHES = "inches"
    METERS = "meters"
    MILLIMETERS = "millimeters"


@dataclass(frozen=True, slots=True)
class DrawingSettings:
    paper_size: PaperSize = PaperSize.A3
    units: DrawingUnits = DrawingUnits.FEET
    scale: float = 1.0
    text_height: float = 0.5
    dimension_height: float = 0.35
    line_width: float = 0.25
    show_grid: bool = True
    show_dimensions: bool = True
    show_title_block: bool = True
    show_north_arrow: bool = True
    show_room_labels: bool = True
    show_room_areas: bool = True
    layer_visibility: Dict[str, bool] = field(default_factory=lambda: {
        "A-WALL": True, "A-DOOR": True, "A-WINDOW": True, "A-COLUMN": True,
        "A-STAIR": True, "A-TEXT": True, "A-DIMS": True, "A-GRID": True,
        "A-HATCH": True, "A-TITLE": True,
    })

    @classmethod
    def default(cls) -> DrawingSettings:
        return cls()

    def to_dict(self) -> dict:
        return {
            "paper_size": self.paper_size.value, "units": self.units.value, "scale": self.scale,
            "text_height": self.text_height, "dimension_height": self.dimension_height,
            "line_width": self.line_width, "show_grid": self.show_grid,
            "show_dimensions": self.show_dimensions, "show_title_block": self.show_title_block,
            "show_north_arrow": self.show_north_arrow, "show_room_labels": self.show_room_labels,
            "show_room_areas": self.show_room_areas, "layer_visibility": dict(self.layer_visibility),
        }

    @classmethod
    def from_dict(cls, data: dict) -> DrawingSettings:
        return cls(
            paper_size=PaperSize(data.get("paper_size", "A3")),
            units=DrawingUnits(data.get("units", "feet")),
            scale=float(data.get("scale", 1.0)),
            text_height=float(data.get("text_height", 0.5)),
            dimension_height=float(data.get("dimension_height", 0.35)),
            line_width=float(data.get("line_width", 0.25)),
            show_grid=data.get("show_grid", True),
            show_dimensions=data.get("show_dimensions", True),
            show_title_block=data.get("show_title_block", True),
            show_north_arrow=data.get("show_north_arrow", True),
            show_room_labels=data.get("show_room_labels", True),
            show_room_areas=data.get("show_room_areas", True),
            layer_visibility=data.get("layer_visibility", {}),
        )
