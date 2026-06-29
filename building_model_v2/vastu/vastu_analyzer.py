"""Vastu Analyzer for Building Model v2."""
from __future__ import annotations
import math
from typing import Optional
from shapely.geometry import LineString, Point, Polygon
from ..base import Point2D
from ..geometry.polygon import centroid as poly_centroid
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from .vastu_direction import VastuDirection
from .vastu_metadata import VastuMetadata


def _room_dir(room_center: Point2D, building_center: Point2D) -> VastuDirection:
    dx = room_center.x - building_center.x
    dy = room_center.y - building_center.y
    angle = math.degrees(math.atan2(dx, -dy)) % 360.0
    return VastuDirection.from_angle(angle)


def _has_pooja_name(md: dict) -> bool:
    name = md.get("name", "").lower()
    return any(kw in name for kw in ("pooja", "puja", "prayer", "temple", "worship"))


def _is_entrance(md: dict, rt: RoomType) -> bool:
    name = md.get("name", "").lower()
    tv = rt.value.lower()
    return "entrance" in name or "entrance" in tv or "main door" in name or tv == "corridor"


def _stair_center(stair) -> Optional[Point2D]:
    if stair.polygon and not stair.polygon.is_empty:
        return poly_centroid(stair.polygon)
    if stair.geometry and not stair.geometry.is_empty:
        c = stair.geometry.centroid
        return Point2D(x=c.x, y=c.y)
    return None


class VastuAnalyzer:
    def analyze(self, building_model: BuildingModel) -> VastuMetadata:
        if building_model.building is None:
            return VastuMetadata()
        existing = building_model.building.metadata.get("vastu")
        if isinstance(existing, dict):
            try: return VastuMetadata.from_dict(existing)
            except: pass
        if isinstance(existing, VastuMetadata):
            return existing
        bc = self._get_center(building_model)
        nr = building_model.building.north_direction
        ed = self._find_entrance(building_model, bc)
        kd = self._find_type(building_model, RoomType.KITCHEN, bc)
        bd = self._find_type(building_model, RoomType.BEDROOM, bc)
        pd = self._find_pooja(building_model, bc)
        sd = self._find_stair_direction(building_model, bc)
        td = self._find_type(building_model, RoomType.TOILET, bc)
        if td is None:
            td = self._find_type(building_model, RoomType.BATHROOM, bc)
        pf = VastuDirection.from_angle(nr) if nr else None
        return VastuMetadata(
            entrance_direction=ed, kitchen_direction=kd,
            master_bedroom_direction=bd, pooja_direction=pd,
            staircase_direction=sd, toilet_direction=td,
            plot_facing=pf, north_rotation=nr,
        )

    def _get_center(self, m: BuildingModel) -> Optional[Point2D]:
        polys = [r.polygon for r in m.rooms.values() if not r.polygon.is_empty]
        if not polys: return None
        from shapely.ops import unary_union
        combined = unary_union(polys)
        c = combined.centroid
        return Point2D(x=c.x, y=c.y)

    def _find_entrance(self, m: BuildingModel, bc: Optional[Point2D]) -> Optional[VastuDirection]:
        if bc is None: return None
        for room in m.rooms.values():
            if _is_entrance(room.metadata, room.room_type):
                rc = poly_centroid(room.polygon)
                if rc: return _room_dir(rc, bc)
        return None

    def _find_type(self, m: BuildingModel, rt: RoomType, bc: Optional[Point2D]) -> Optional[VastuDirection]:
        if bc is None: return None
        for room in m.rooms.values():
            if room.room_type == rt:
                rc = poly_centroid(room.polygon)
                if rc: return _room_dir(rc, bc)
        return None

    def _find_pooja(self, m: BuildingModel, bc: Optional[Point2D]) -> Optional[VastuDirection]:
        if bc is None: return None
        for room in m.rooms.values():
            if _has_pooja_name(room.metadata):
                rc = poly_centroid(room.polygon)
                if rc: return _room_dir(rc, bc)
        return None

    def _find_stair_direction(self, m: BuildingModel, bc: Optional[Point2D]) -> Optional[VastuDirection]:
        if bc is None: return None
        for stair in m.stairs.values():
            sc = _stair_center(stair)
            if sc:
                return _room_dir(sc, bc)
        return None


__all__ = ["VastuAnalyzer"]
