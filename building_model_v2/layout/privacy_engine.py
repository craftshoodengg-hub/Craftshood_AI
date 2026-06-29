"""Privacy Engine for Building Model v2."""
from __future__ import annotations
from typing import Dict, List, Optional, Set
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from .adjacency_engine import AdjacencyEngine
from .room_graph import RoomGraph
from .privacy_metrics import PrivacyMetrics, PrivacyConflict

PRIVACY_MASTER_BEDROOM_ACCESS = "PRIVACY_MASTER_BEDROOM_ACCESS"
PRIVACY_TOILET_VISIBILITY = "PRIVACY_TOILET_VISIBILITY"
PRIVACY_POOJA_DISTURBANCE = "PRIVACY_POOJA_DISTURBANCE"
PRIVACY_GUEST_ACCESS = "PRIVACY_GUEST_ACCESS"
PRIVACY_LIVING_TRANSITION = "PRIVACY_LIVING_TRANSITION"
PRIVACY_BEDROOM_CORRIDOR = "PRIVACY_BEDROOM_CORRIDOR"


class PrivacyEngine:
    def __init__(self) -> None:
        self._adjacency_engine = AdjacencyEngine()

    def analyze(self, building_model: BuildingModel, room_graph: Optional[RoomGraph] = None) -> PrivacyMetrics:
        rooms = building_model.rooms
        if not rooms:
            return PrivacyMetrics(public_rooms=frozenset(), semi_private_rooms=frozenset(), private_rooms=frozenset(), privacy_score=1.0, privacy_conflicts=(), circulation_crossings=0)
        graph = room_graph if room_graph is not None else self._adjacency_engine.build_graph(building_model)
        public_rooms: Set[str] = set()
        semi_private_rooms: Set[str] = set()
        private_rooms: Set[str] = set()
        for rid, room in rooms.items():
            rt = room.room_type
            if rt in (RoomType.LIVING, RoomType.DINING, RoomType.KITCHEN):
                public_rooms.add(rid)
            elif rt in (RoomType.BEDROOM, RoomType.BATHROOM):
                private_rooms.add(rid)
            else:
                semi_private_rooms.add(rid)
        conflicts: List[PrivacyConflict] = []
        for rid, room in rooms.items():
            neighbors = graph.neighbors(rid)
            for nid in neighbors:
                if nid not in rooms:
                    continue
                neighbor_room = rooms[nid]
                self._check_privacy_conflict(rid, room, nid, neighbor_room, conflicts)
        self._check_master_bedroom_privacy(building_model, graph, conflicts)
        self._check_bedroom_corridor(building_model, graph, conflicts)
        crossings = self._count_circulation_crossings(building_model, graph)
        total_pairs = len(rooms) * (len(rooms) - 1) / 2 if len(rooms) > 1 else 1
        conflict_ratio = len(conflicts) / total_pairs if total_pairs > 0 else 0
        privacy_score = max(0.0, 1.0 - conflict_ratio)
        return PrivacyMetrics(public_rooms=frozenset(public_rooms), semi_private_rooms=frozenset(semi_private_rooms), private_rooms=frozenset(private_rooms), privacy_score=privacy_score, privacy_conflicts=tuple(conflicts), circulation_crossings=crossings)

    def evaluate(self, building_model: BuildingModel, room_graph: Optional[RoomGraph] = None) -> "ConstraintResult":
        from ..constraints.constraint_result import ConstraintResult
        from ..constraints.constraint_issue import ConstraintIssue
        from ..constraints.constraint_severity import ConstraintSeverity
        issues = []
        metrics = self.analyze(building_model, room_graph)
        for conflict in metrics.privacy_conflicts:
            issues.append(ConstraintIssue(code=conflict.issue_code, message=conflict.description, severity=ConstraintSeverity.WARNING, entity_id=conflict.room_a, score=0.6))
        return ConstraintResult(issues=issues)

    def _check_privacy_conflict(self, rid: str, room, nid: str, neighbor_room, conflicts: List[PrivacyConflict]) -> None:
        rt = room.room_type
        nrt = neighbor_room.room_type
        if rt == RoomType.TOILET and nrt in (RoomType.DINING, RoomType.KITCHEN):
            conflicts.append(PrivacyConflict(rid, nid, PRIVACY_TOILET_VISIBILITY, f"Toilet opens directly into {nrt.value}"))
        if rt == RoomType.BATHROOM and nrt in (RoomType.DINING, RoomType.KITCHEN):
            conflicts.append(PrivacyConflict(rid, nid, PRIVACY_TOILET_VISIBILITY, f"Bathroom opens directly into {nrt.value}"))
        room_name = room.metadata.get("name", "")
        neighbor_name = neighbor_room.metadata.get("name", "")
        if "Pooja" in room_name and "Toilet" in neighbor_name:
            conflicts.append(PrivacyConflict(rid, nid, PRIVACY_POOJA_DISTURBANCE, "Pooja room is adjacent to Toilet"))
        if "Pooja" in neighbor_name and "Toilet" in room_name:
            conflicts.append(PrivacyConflict(rid, nid, PRIVACY_POOJA_DISTURBANCE, "Pooja room is adjacent to Toilet"))

    def _check_master_bedroom_privacy(self, building_model: BuildingModel, graph: RoomGraph, conflicts: List[PrivacyConflict]) -> None:
        rooms = building_model.rooms
        for rid, room in rooms.items():
            if room.room_type != RoomType.BEDROOM:
                continue
            if "Master" not in room.metadata.get("name", ""):
                continue
            for other_id, other_room in rooms.items():
                if other_id == rid or other_room.room_type not in (RoomType.KITCHEN, RoomType.DINING, RoomType.UTILITY):
                    continue
                path = graph.shortest_path(rid, other_id)
                if path and len(path) == 2:
                    conflicts.append(PrivacyConflict(rid, other_id, PRIVACY_MASTER_BEDROOM_ACCESS, f"Master Bedroom requires passing through {other_room.room_type.value}"))

    def _check_bedroom_corridor(self, building_model: BuildingModel, graph: RoomGraph, conflicts: List[PrivacyConflict]) -> None:
        rooms = building_model.rooms
        if len(rooms) <= 2:
            return
        for rid, room in rooms.items():
            if room.room_type != RoomType.BEDROOM:
                continue
            if graph.degree(rid) < 2:
                continue
            neighbors = graph.neighbors(rid)
            private_neighbors = [n for n in neighbors if n in rooms and rooms[n].room_type in (RoomType.BEDROOM, RoomType.BATHROOM)]
            if len(private_neighbors) >= 2:
                pass

    def _count_circulation_crossings(self, building_model: BuildingModel, graph: RoomGraph) -> int:
        rooms = building_model.rooms
        crossings = 0
        for rid, room in rooms.items():
            if room.room_type == RoomType.BEDROOM and graph.degree(rid) >= 2:
                neighbors = graph.neighbors(rid)
                public_neighbors = [n for n in neighbors if n in rooms and rooms[n].room_type in (RoomType.LIVING, RoomType.DINING)]
                if public_neighbors:
                    crossings += 1
        return crossings
