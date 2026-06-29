"""Adjacency Engine for Building Model v2."""
from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from ..base import Point2D
from ..entities_room import Room
from ..geometry.polygon import centroid as poly_centroid
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from .adjacency_rules import AdjacencyRuleSet, ConnectionType, create_default_rules
from .room_graph import RoomConnection, RoomGraph


LAYOUT_KITCHEN_NOT_NEAR_DINING = "LAYOUT_KITCHEN_NOT_NEAR_DINING"
LAYOUT_KITCHEN_NOT_NEAR_UTILITY = "LAYOUT_KITCHEN_NOT_NEAR_UTILITY"
LAYOUT_BATHROOM_NEAR_KITCHEN = "LAYOUT_BATHROOM_NEAR_KITCHEN"
LAYOUT_BATHROOM_NEAR_DINING = "LAYOUT_BATHROOM_NEAR_DINING"
LAYOUT_MASTER_BEDROOM_NO_BATH = "LAYOUT_MASTER_BEDROOM_NO_BATH"
LAYOUT_GARAGE_TOO_REMOTE = "LAYOUT_GARAGE_TOO_REMOTE"
LAYOUT_POOJA_NEAR_TOILET = "LAYOUT_POOJA_NEAR_TOILET"
LAYOUT_STAIR_POOR_CONNECTIVITY = "LAYOUT_STAIR_POOR_CONNECTIVITY"


def _rooms_are_adjacent(room_a: Room, room_b: Room, threshold_ft: float = 15.0) -> bool:
    if room_a.polygon.is_empty or room_b.polygon.is_empty:
        return False
    ca = poly_centroid(room_a.polygon)
    cb = poly_centroid(room_b.polygon)
    if ca is None or cb is None:
        return False
    return ca.distance_to(cb) <= threshold_ft


def _rooms_share_wall(room_a: Room, room_b: Room) -> bool:
    return bool(room_a.wall_ids & room_b.wall_ids)


class AdjacencyEngine:
    def __init__(self, rules: Optional[AdjacencyRuleSet] = None) -> None:
        self._rules = rules or create_default_rules()

    def build_graph(self, building_model: BuildingModel) -> RoomGraph:
        graph = RoomGraph()
        rooms = list(building_model.rooms.values())
        # Build a mapping from room object id to the key used in building_model.rooms
        id_to_key = {id(r): k for k, r in building_model.rooms.items()}
        for i, r1 in enumerate(rooms):
            for r2 in rooms[i + 1:]:
                if _rooms_share_wall(r1, r2) or _rooms_are_adjacent(r1, r2):
                    ct = ConnectionType.DIRECT
                    door_id = None
                    for did in r1.door_ids:
                        if did in r2.door_ids:
                            door_id = did
                            ct = ConnectionType.VIA_DOOR
                            break
                    # Use the building model keys (names) for graph nodes
                    key1 = id_to_key.get(id(r1), r1.id)
                    key2 = id_to_key.get(id(r2), r2.id)
                    graph.add_connection(RoomConnection(key1, key2, ct, door_id))
        return graph

    def evaluate(self, building_model: BuildingModel) -> "ConstraintResult":
        from ..constraints.constraint_result import ConstraintResult
        from ..constraints.constraint_issue import ConstraintIssue
        from ..constraints.constraint_severity import ConstraintSeverity
        issues = []
        graph = self.build_graph(building_model)
        rooms = building_model.rooms
        id_to_type = {rid: room.room_type.value for rid, room in rooms.items()}
        for room_id, room in rooms.items():
            rule = self._rules.get_rule(room.room_type.value)
            if rule is None:
                continue
            neighbors = graph.neighbors(room_id)
            neighbor_types = {id_to_type[n] for n in neighbors if n in id_to_type}
            rt_val = room.room_type.value
            for req in rule.required_adjacent:
                if req not in neighbor_types:
                    is_bedroom = rt_val == "Bedroom" or room.metadata.get("name", "") in ("Bedroom", "Master Bedroom")
                    code = LAYOUT_MASTER_BEDROOM_NO_BATH if (req == "Bathroom" and is_bedroom) else "LAYOUT_REQUIRED_ADJACENCY_MISSING"
                    issues.append(ConstraintIssue(
                        code=code,
                        message=f"{rt_val} missing required adjacency to {req}",
                        severity=ConstraintSeverity.WARNING,
                        entity_id=room_id,
                        score=0.7,
                    ))
            for disc in rule.discouraged_adjacent:
                if disc in neighbor_types:
                    code = "LAYOUT_DISCOURAGED_ADJACENCY"
                    if disc == "Kitchen" and rt_val in ("Bathroom", "Toilet", "Common Toilet"):
                        code = LAYOUT_BATHROOM_NEAR_KITCHEN
                    elif disc == "Dining" and rt_val in ("Bathroom", "Toilet", "Common Toilet"):
                        code = LAYOUT_BATHROOM_NEAR_DINING
                    elif disc in ("Toilet", "Common Toilet") and (rt_val == "Pooja" or room.metadata.get("name", "") == "Pooja"):
                        code = LAYOUT_POOJA_NEAR_TOILET
                    issues.append(ConstraintIssue(
                        code=code,
                        message=f"{rt_val} should not be adjacent to {disc}",
                        severity=ConstraintSeverity.WARNING,
                        entity_id=room_id,
                        score=0.6,
                    ))
            for pref in rule.preferred_adjacent:
                if pref not in neighbor_types:
                    code = "LAYOUT_PREFERRED_ADJACENCY_MISSING"
                    if room.room_type.value == "Kitchen" and pref == "Dining":
                        code = LAYOUT_KITCHEN_NOT_NEAR_DINING
                    elif room.room_type.value == "Kitchen" and pref == "Utility":
                        code = LAYOUT_KITCHEN_NOT_NEAR_UTILITY
                    issues.append(ConstraintIssue(
                        code=code,
                        message=f"{room.room_type.value} should be near {pref}",
                        severity=ConstraintSeverity.SUGGESTION,
                        entity_id=room_id,
                        score=0.3,
                    ))
        return ConstraintResult(issues=issues)
