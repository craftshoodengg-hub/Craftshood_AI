"""Circulation Engine for Building Model v2."""
from __future__ import annotations
from typing import Set
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from .adjacency_engine import AdjacencyEngine
from .circulation_metrics import CirculationMetrics

CIRCULATION_DEAD_END = "CIRCULATION_DEAD_END"
CIRCULATION_ROOM_ISOLATED = "CIRCULATION_ROOM_ISOLATED"
CIRCULATION_EXCESSIVE_PATH = "CIRCULATION_EXCESSIVE_PATH"
CIRCULATION_UNREACHABLE_ROOM = "CIRCULATION_UNREACHABLE_ROOM"
CIRCULATION_KITCHEN_DINING = "CIRCULATION_KITCHEN_DINING"
CIRCULATION_BEDROOM_BATHROOM = "CIRCULATION_BEDROOM_BATHROOM"
CIRCULATION_STAIR_CONNECTIVITY = "CIRCULATION_STAIR_CONNECTIVITY"


class CirculationEngine:
    def __init__(self, max_path_length: int = 4) -> None:
        self._max_path_length = max_path_length
        self._adjacency_engine = AdjacencyEngine()

    def analyze(self, building_model: BuildingModel) -> CirculationMetrics:
        graph = self._adjacency_engine.build_graph(building_model)
        rooms = building_model.rooms
        if not rooms:
            return CirculationMetrics(0.0, 0.0, frozenset(), frozenset(), 1.0, frozenset(), frozenset())
        all_paths = []
        isolated: Set[str] = set()
        dead_ends: Set[str] = set()
        reachable: Set[str] = set()
        unreachable: Set[str] = set()
        room_ids = list(rooms.keys())
        for src in room_ids:
            has_path = False
            for tgt in room_ids:
                if src == tgt: continue
                path = graph.shortest_path(src, tgt)
                if path is not None:
                    has_path = True
                    reachable.add(src); reachable.add(tgt)
                    all_paths.append((src, tgt, len(path) - 1))
            if not has_path:
                isolated.add(src); unreachable.add(src)
        for rid in room_ids:
            if graph.degree(rid) <= 1 and len(room_ids) > 1: dead_ends.add(rid)
        path_lengths = [p[2] for p in all_paths] if all_paths else [0]
        avg_len = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
        max_len = max(path_lengths) if path_lengths else 0.0
        total_pairs = len(room_ids) * (len(room_ids) - 1) if len(room_ids) > 1 else 1
        efficiency = len([p for p in all_paths if p[2] <= self._max_path_length]) / total_pairs if total_pairs > 0 else 1.0
        return CirculationMetrics(average_path_length=avg_len, maximum_path_length=max_len, isolated_rooms=frozenset(isolated), dead_end_rooms=frozenset(dead_ends), circulation_efficiency=min(1.0, efficiency), reachable_rooms=frozenset(reachable), unreachable_rooms=frozenset(unreachable))

    def evaluate(self, building_model: BuildingModel) -> "ConstraintResult":
        from ..constraints.constraint_result import ConstraintResult
        from ..constraints.constraint_issue import ConstraintIssue
        from ..constraints.constraint_severity import ConstraintSeverity
        issues = []
        graph = self._adjacency_engine.build_graph(building_model)
        rooms = building_model.rooms
        if not rooms: return ConstraintResult(issues=issues)
        room_ids = list(rooms.keys())
        for rid in room_ids:
            if graph.degree(rid) == 0 and len(room_ids) > 1:
                issues.append(ConstraintIssue(code=CIRCULATION_ROOM_ISOLATED, message="Room is isolated", severity=ConstraintSeverity.WARNING, entity_id=rid, score=0.8))
            elif graph.degree(rid) == 1 and len(room_ids) > 2:
                issues.append(ConstraintIssue(code=CIRCULATION_DEAD_END, message="Room is a dead end", severity=ConstraintSeverity.SUGGESTION, entity_id=rid, score=0.4))
        entrance_id = None
        for rid, room in rooms.items():
            if room.room_type == RoomType.CORRIDOR or "entrance" in room.metadata.get("name", "").lower():
                entrance_id = rid; break
        if entrance_id is not None:
            for rid in room_ids:
                if rid == entrance_id: continue
                path = graph.shortest_path(entrance_id, rid)
                if path is None:
                    issues.append(ConstraintIssue(code=CIRCULATION_UNREACHABLE_ROOM, message="Room not reachable from entrance", severity=ConstraintSeverity.WARNING, entity_id=rid, score=0.7))
                elif len(path) - 1 > self._max_path_length:
                    issues.append(ConstraintIssue(code=CIRCULATION_EXCESSIVE_PATH, message=f"Room requires {len(path)-1} transitions (max: {self._max_path_length})", severity=ConstraintSeverity.WARNING, entity_id=rid, score=0.5))
        kitchen_id = dining_id = None
        for rid, room in rooms.items():
            if room.room_type == RoomType.KITCHEN: kitchen_id = rid
            if room.room_type == RoomType.DINING: dining_id = rid
        if kitchen_id and dining_id:
            path = graph.shortest_path(kitchen_id, dining_id)
            if path is None or len(path) - 1 > 2:
                issues.append(ConstraintIssue(code=CIRCULATION_KITCHEN_DINING, message="Kitchen should connect to Dining", severity=ConstraintSeverity.SUGGESTION, entity_id=kitchen_id, score=0.3))
        for rid, room in rooms.items():
            if room.room_type == RoomType.BEDROOM:
                bath_path = None
                for oid, oroom in rooms.items():
                    if oroom.room_type == RoomType.BATHROOM:
                        p = graph.shortest_path(rid, oid)
                        if p and (bath_path is None or len(p) < len(bath_path)): bath_path = p
                if bath_path is None or len(bath_path) - 1 > 2:
                    issues.append(ConstraintIssue(code=CIRCULATION_BEDROOM_BATHROOM, message="Bedroom should be near bathroom", severity=ConstraintSeverity.SUGGESTION, entity_id=rid, score=0.3))
        stair_ids = [rid for rid, r in rooms.items() if r.room_type == RoomType.STAIRCASE]
        if stair_ids and len(room_ids) > 2:
            for sid in stair_ids:
                if graph.degree(sid) < 2:
                    issues.append(ConstraintIssue(code=CIRCULATION_STAIR_CONNECTIVITY, message="Stair should connect multiple paths", severity=ConstraintSeverity.SUGGESTION, entity_id=sid, score=0.3))
        return ConstraintResult(issues=issues)
