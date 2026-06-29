"""Vastu Grid for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from shapely.geometry import Polygon, box
from ..base import BoundingBox, Point2D
from .vastu_zone import VastuZone


@dataclass(frozen=True, slots=True)
class VastuCell:
    row: int
    column: int
    polygon: Polygon
    zone: VastuZone

    @property
    def center(self) -> Point2D:
        c = self.polygon.centroid
        return Point2D(x=c.x, y=c.y)

    @property
    def area(self) -> float:
        return float(self.polygon.area)

    def to_dict(self) -> Dict[str, Any]:
        return {"row": self.row, "column": self.column, "zone": self.zone.name, "area": self.area, "center": self.center.to_dict()}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VastuCell): return NotImplemented
        return self.row == other.row and self.column == other.column and self.zone == other.zone

    def __hash__(self) -> int:
        return hash((self.row, self.column, self.zone))


@dataclass(frozen=True, slots=True)
class VastuGrid:
    boundary_polygon: Polygon
    cells: Tuple[VastuCell, ...]
    center_cell: VastuCell

    @property
    def width(self) -> float:
        b = self.boundary_polygon.bounds
        return b[2] - b[0]

    @property
    def height(self) -> float:
        b = self.boundary_polygon.bounds
        return b[3] - b[1]

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    def get_cell(self, row: int, column: int) -> Optional[VastuCell]:
        for cell in self.cells:
            if cell.row == row and cell.column == column:
                return cell
        return None

    def get_zone(self, zone: VastuZone) -> Optional[VastuCell]:
        for cell in self.cells:
            if cell.zone == zone:
                return cell
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {"width": self.width, "height": self.height, "cell_count": self.cell_count, "cells": [c.to_dict() for c in self.cells], "center_cell": self.center_cell.to_dict()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VastuGrid:
        cells_data = data.get("cells", [])
        cells_list = []
        center_cell = None
        for cd in cells_data:
            zone = VastuZone[cd["zone"]]
            bbox = cd.get("bbox")
            poly = box(bbox["min_x"], bbox["min_y"], bbox["max_x"], bbox["max_y"]) if bbox else box(0, 0, 1, 1)
            cell = VastuCell(row=cd["row"], column=cd["column"], polygon=poly, zone=zone)
            cells_list.append(cell)
            if zone == VastuZone.BRAHMASTHAN: center_cell = cell
        if center_cell is None and cells_list:
            for cell in cells_list:
                if cell.row == 1 and cell.column == 1: center_cell = cell; break
        boundary = box(0, 0, data.get("width", 1), data.get("height", 1))
        return cls(boundary_polygon=boundary, cells=tuple(cells_list), center_cell=center_cell or cells_list[0])

    @classmethod
    def generate(cls, boundary: Polygon) -> VastuGrid:
        if boundary.is_empty:
            empty = box(0, 0, 1, 1)
            return cls(boundary_polygon=empty, cells=(), center_cell=VastuCell(row=1, column=1, polygon=empty, zone=VastuZone.BRAHMASTHAN))
        min_x, min_y, max_x, max_y = boundary.bounds
        cw = (max_x - min_x) / 3.0
        ch = (max_y - min_y) / 3.0
        zone_map = {(0,0): VastuZone.VAYAVYA, (0,1): VastuZone.NORTH, (0,2): VastuZone.ISHANYA, (1,0): VastuZone.WEST, (1,1): VastuZone.BRAHMASTHAN, (1,2): VastuZone.EAST, (2,0): VastuZone.NAIRUTYA, (2,1): VastuZone.SOUTH, (2,2): VastuZone.AGNEYA}
        cells = []
        center_cell = None
        for row in range(3):
            for col in range(3):
                cx = min_x + col * cw
                cy = min_y + row * ch
                cp = box(cx, cy, cx + cw, cy + ch)
                zone = zone_map[(row, col)]
                cell = VastuCell(row=row, column=col, polygon=cp, zone=zone)
                cells.append(cell)
                if zone == VastuZone.BRAHMASTHAN: center_cell = cell
        return cls(boundary_polygon=boundary, cells=tuple(cells), center_cell=center_cell or cells[4])


__all__ = ["VastuCell", "VastuGrid"]
