"""Vastu Shastra constraints for Building Model v2."""
from __future__ import annotations
from typing import Any, Dict, Final, FrozenSet, List
from ..entities_room import Room
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from ..vastu.vastu_direction import VastuDirection
from ..vastu.vastu_metadata import VastuMetadata
from ..vastu.vastu_zone import VastuZone
from .constraint import Constraint
from .constraint_category import ConstraintCategory
from .constraint_issue import ConstraintIssue
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity

VASTU_ENTRANCE_DIRECTION: Final[str] = "VASTU_ENTRANCE_DIRECTION"
VASTU_KITCHEN_PLACEMENT: Final[str] = "VASTU_KITCHEN_PLACEMENT"
VASTU_MASTER_BEDROOM: Final[str] = "VASTU_MASTER_BEDROOM"
VASTU_POOJA_ROOM: Final[str] = "VASTU_POOJA_ROOM"
VASTU_STAIRCASE: Final[str] = "VASTU_STAIRCASE"
VASTU_TOILET: Final[str] = "VASTU_TOILET"
VASTU_BRAHMASTHAN: Final[str] = "VASTU_BRAHMASTHAN"
SCORE_PREFERRED: Final[float] = 0.0
SCORE_ACCEPTABLE: Final[float] = 0.2
SCORE_DISALLOWED: Final[float] = 0.7
SCORE_MISSING: Final[float] = 0.3


class VastuConstraint(Constraint):
    def __init__(self, name, description="", default_severity=ConstraintSeverity.RECOMMENDATION):
        super().__init__(name=name, description=description)
        self._category = ConstraintCategory.VASTU
        self._default_severity = default_severity
    @property
    def category(self):
        return self._category
    @property
    def default_severity(self):
        return self._default_severity


def _get_vastu_metadata(m):
    if m.building is None: return None
    d = m.building.metadata.get("vastu")
    if d is None: return None
    if isinstance(d, dict):
        try: return VastuMetadata.from_dict(d)
        except: return None
    if isinstance(d, VastuMetadata): return d
    return None

def _rooms_by_type(m, rt):
    return [r for r in m.rooms.values() if r.room_type == rt]

def _get_room_vastu_zone(room):
    zv = room.metadata.get("vastu_zone")
    if zv is None: return None
    if isinstance(zv, VastuZone): return zv
    if isinstance(zv, str):
        try: return VastuZone[zv.upper()]
        except: return None
    return None

def _dname(d):
    return "Unknown" if d is None else d.display_name

def _mk(code, msg, sev, eid=None, etype=None, loc=None, score=SCORE_DISALLOWED):
    return ConstraintIssue(code=code, message=msg, severity=sev, entity_id=eid, entity_type=etype, location=loc, score=score, metadata={"category": "vastu"})

def _d2z(d):
    return {VastuDirection.NORTH: VastuZone.NORTH, VastuDirection.NORTH_EAST: VastuZone.ISHANYA, VastuDirection.EAST: VastuZone.EAST, VastuDirection.SOUTH_EAST: VastuZone.AGNEYA, VastuDirection.SOUTH: VastuZone.SOUTH, VastuDirection.SOUTH_WEST: VastuZone.NAIRUTYA, VastuDirection.WEST: VastuZone.WEST, VastuDirection.NORTH_WEST: VastuZone.VAYAVYA, VastuDirection.CENTER: VastuZone.BRAHMASTHAN}.get(d)

def _z4m(md):
    zv = md.get("vastu_zone")
    if zv is None: return None
    if isinstance(zv, VastuZone): return zv
    if isinstance(zv, str):
        try: return VastuZone[zv.upper()]
        except: return None
    return None


class EntranceDirectionConstraint(VastuConstraint):
    PREFERRED = frozenset({VastuDirection.NORTH, VastuDirection.EAST, VastuDirection.NORTH_EAST})
    def __init__(self):
        super().__init__(name="Entrance Direction", description="Main entrance should face North, East, or North-East")
    def evaluate(self, m):
        r = ConstraintResult.create()
        md = _get_vastu_metadata(m)
        if md is None or md.entrance_direction is None:
            r.add_issue(_mk(VASTU_ENTRANCE_DIRECTION, "Entrance direction not specified; preferred: North, East, or North-East", self.default_severity, etype="Building", score=SCORE_MISSING))
            return r
        if md.entrance_direction in self.PREFERRED: return r
        r.add_issue(_mk(VASTU_ENTRANCE_DIRECTION, f"Entrance facing {_dname(md.entrance_direction)} is not preferred", self.default_severity, etype="Building", loc=_dname(md.entrance_direction), score=SCORE_DISALLOWED))
        return r


class KitchenPlacementConstraint(VastuConstraint):
    PREFERRED_ZONES = frozenset({VastuZone.AGNEYA})
    ACCEPTABLE_ZONES = frozenset({VastuZone.VAYAVYA})
    def __init__(self):
        super().__init__(name="Kitchen Placement", description="Kitchen should be in the South-East (Agneya) zone")
    def evaluate(self, m):
        r = ConstraintResult.create()
        kitchens = _rooms_by_type(m, RoomType.KITCHEN)
        if not kitchens:
            md = _get_vastu_metadata(m)
            if md and md.kitchen_direction is not None:
                zone = _d2z(md.kitchen_direction)
                if zone is None: return r
                if zone in self.PREFERRED_ZONES: return r
                if zone in self.ACCEPTABLE_ZONES:
                    r.add_issue(_mk(VASTU_KITCHEN_PLACEMENT, f"Kitchen in {zone.display_name} is acceptable; South-East preferred", self.default_severity, etype="Building", loc=zone.display_name, score=SCORE_ACCEPTABLE))
                    return r
                r.add_issue(_mk(VASTU_KITCHEN_PLACEMENT, f"Kitchen in {zone.display_name} is not suitable", self.default_severity, etype="Building", loc=zone.display_name, score=SCORE_DISALLOWED))
                return r
            return r
        for k in kitchens:
            zone = _get_room_vastu_zone(k)
            if zone is None:
                r.add_issue(_mk(VASTU_KITCHEN_PLACEMENT, "Kitchen has no Vastu zone; South-East preferred", self.default_severity, eid=k.id, etype="Room", score=SCORE_MISSING))
                continue
            if zone in self.PREFERRED_ZONES: continue
            if zone in self.ACCEPTABLE_ZONES:
                r.add_issue(_mk(VASTU_KITCHEN_PLACEMENT, f"Kitchen in {zone.display_name} is acceptable; South-East preferred", self.default_severity, eid=k.id, etype="Room", loc=zone.display_name, score=SCORE_ACCEPTABLE))
                continue
            r.add_issue(_mk(VASTU_KITCHEN_PLACEMENT, f"Kitchen in {zone.display_name} is not suitable", self.default_severity, eid=k.id, etype="Room", loc=zone.display_name, score=SCORE_DISALLOWED))
        return r


class MasterBedroomConstraint(VastuConstraint):
    PREFERRED = frozenset({VastuZone.NAIRUTYA})
    def __init__(self):
        super().__init__(name="Master Bedroom Placement", description="Master bedroom should be in the South-West (Nairutya) zone")
    def evaluate(self, m):
        r = ConstraintResult.create()
        md = _get_vastu_metadata(m)
        if md and md.master_bedroom_direction is not None:
            zone = _d2z(md.master_bedroom_direction)
            if zone is None: return r
            if zone in self.PREFERRED: return r
            r.add_issue(_mk(VASTU_MASTER_BEDROOM, f"Master bedroom in {zone.display_name}; South-West preferred", self.default_severity, etype="Building", loc=zone.display_name, score=SCORE_DISALLOWED))
            return r
        for bed in _rooms_by_type(m, RoomType.BEDROOM):
            zone = _get_room_vastu_zone(bed)
            if zone is None or zone in self.PREFERRED: continue
            r.add_issue(_mk(VASTU_MASTER_BEDROOM, f"Bedroom in {zone.display_name}; South-West preferred", self.default_severity, eid=bed.id, etype="Room", loc=zone.display_name, score=SCORE_DISALLOWED))
        return r


class PoojaRoomConstraint(VastuConstraint):
    PREFERRED = frozenset({VastuZone.ISHANYA})
    def __init__(self):
        super().__init__(name="Pooja Room Placement", description="Pooja room should be in the North-East (Ishanya) zone")
    def evaluate(self, m):
        r = ConstraintResult.create()
        md = _get_vastu_metadata(m)
        if md and md.pooja_direction is not None:
            zone = _d2z(md.pooja_direction)
            if zone is None: return r
            if zone in self.PREFERRED: return r
            r.add_issue(_mk(VASTU_POOJA_ROOM, f"Pooja room in {zone.display_name}; North-East preferred", self.default_severity, etype="Building", loc=zone.display_name, score=SCORE_DISALLOWED))
            return r
        for room in m.rooms.values():
            rn = room.metadata.get("name", "").lower()
            if "pooja" in rn or "puja" in rn or "prayer" in rn:
                zone = _get_room_vastu_zone(room)
                if zone is None: continue
                if zone in self.PREFERRED: return r
                r.add_issue(_mk(VASTU_POOJA_ROOM, f"Pooja room in {zone.display_name}; North-East preferred", self.default_severity, eid=room.id, etype="Room", loc=zone.display_name, score=SCORE_DISALLOWED))
        return r


class StaircaseConstraint(VastuConstraint):
    PREFERRED = frozenset({VastuZone.SOUTH, VastuZone.WEST, VastuZone.NAIRUTYA})
    DISALLOWED = frozenset({VastuZone.BRAHMASTHAN})
    def __init__(self):
        super().__init__(name="Staircase Placement", description="Staircase in South, West, or South-West; avoid center")
    def evaluate(self, m):
        r = ConstraintResult.create()
        md = _get_vastu_metadata(m)
        if md and md.staircase_direction is not None:
            zone = _d2z(md.staircase_direction)
            if zone is not None:
                if zone in self.DISALLOWED:
                    r.add_issue(_mk(VASTU_STAIRCASE, f"Staircase in {zone.display_name} is disallowed", self.default_severity, etype="Building", loc=zone.display_name, score=SCORE_DISALLOWED))
                    return r
                if zone in self.PREFERRED: return r
                r.add_issue(_mk(VASTU_STAIRCASE, f"Staircase in {zone.display_name}; South/West/South-West preferred", self.default_severity, etype="Building", loc=zone.display_name, score=SCORE_ACCEPTABLE))
                return r
        for sid in m.stairs:
            sz = _z4m(getattr(m.stairs[sid], "metadata", {}))
            if sz is None: continue
            if sz in self.DISALLOWED:
                r.add_issue(_mk(VASTU_STAIRCASE, f"Staircase in {sz.display_name} is disallowed", self.default_severity, eid=sid, etype="Stair", loc=sz.display_name, score=SCORE_DISALLOWED))
            elif sz not in self.PREFERRED:
                r.add_issue(_mk(VASTU_STAIRCASE, f"Staircase in {sz.display_name}; South/West/South-West preferred", self.default_severity, eid=sid, etype="Stair", loc=sz.display_name, score=SCORE_ACCEPTABLE))
        return r


class ToiletPlacementConstraint(VastuConstraint):
    DISALLOWED = frozenset({VastuZone.ISHANYA, VastuZone.BRAHMASTHAN})
    def __init__(self):
        super().__init__(name="Toilet Placement", description="Toilets should not be in North-East or Center")
    def evaluate(self, m):
        r = ConstraintResult.create()
        md = _get_vastu_metadata(m)
        if md and md.toilet_direction is not None:
            zone = _d2z(md.toilet_direction)
            if zone is not None and zone in self.DISALLOWED:
                r.add_issue(_mk(VASTU_TOILET, f"Toilet in {zone.display_name} is disallowed", self.default_severity, etype="Building", loc=zone.display_name, score=SCORE_DISALLOWED))
                return r
        for rt in (RoomType.TOILET, RoomType.BATHROOM):
            for room in _rooms_by_type(m, rt):
                zone = _get_room_vastu_zone(room)
                if zone and zone in self.DISALLOWED:
                    r.add_issue(_mk(VASTU_TOILET, f"{rt.value} in {zone.display_name} is disallowed", self.default_severity, eid=room.id, etype="Room", loc=zone.display_name, score=SCORE_DISALLOWED))
        return r


class BrahmasthanConstraint(VastuConstraint):
    DISALLOWED_TYPES = frozenset({"stair", "column", "toilet", "bathroom"})
    def __init__(self):
        super().__init__(name="Brahmasthan (Center) Clear", description="Center zone should remain clear of obstructions")
    def evaluate(self, m):
        r = ConstraintResult.create()
        for cid, col in m.columns.items():
            cz = _z4m(getattr(col, "metadata", {}))
            if cz == VastuZone.BRAHMASTHAN:
                cn = getattr(col, "name", cid) if hasattr(col, "name") else cid
                r.add_issue(_mk(VASTU_BRAHMASTHAN, f"Column {cn} is in Brahmasthan (center) zone", self.default_severity, eid=cid, etype="Column", loc="Brahmasthan (Center)", score=SCORE_DISALLOWED))
        for sid, st in m.stairs.items():
            sz = _z4m(getattr(st, "metadata", {}))
            if sz == VastuZone.BRAHMASTHAN:
                sn = getattr(st, "name", sid) if hasattr(st, "name") else sid
                r.add_issue(_mk(VASTU_BRAHMASTHAN, f"Staircase {sn} is in Brahmasthan (center) zone", self.default_severity, eid=sid, etype="Stair", loc="Brahmasthan (Center)", score=SCORE_DISALLOWED))
        for rid, room in m.rooms.items():
            rz = _get_room_vastu_zone(room)
            if rz == VastuZone.BRAHMASTHAN:
                rt = room.room_type.value if hasattr(room.room_type, "value") else str(room.room_type)
                if rt.lower() in self.DISALLOWED_TYPES or room.room_type in (RoomType.TOILET, RoomType.BATHROOM, RoomType.STAIRCASE):
                    rn = room.metadata.get("name", rid)
                    r.add_issue(_mk(VASTU_BRAHMASTHAN, f"{rt} in Brahmasthan (center) zone obstructs the center", self.default_severity, eid=rid, etype="Room", loc="Brahmasthan (Center)", score=SCORE_DISALLOWED))
        return r

