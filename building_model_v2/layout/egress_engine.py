"""Egress Engine for Building Model v2."""
from __future__ import annotations
from typing import Dict, List, Optional, Set
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from .adjacency_engine import AdjacencyEngine
from .egress_metrics import EgressMetrics, ExitPath
from .room_graph import RoomGraph

EGRESS_UNREACHABLE_EXIT = "EGRESS_UNREACHABLE_EXIT"
EGRESS_EXCESSIVE_TRAVEL_DISTANCE = "EGRESS_EXCESSIVE_TRAVEL_DISTANCE"
EGRESS_DEAD_END_CORRIDOR = "EGRESS_DEAD_END_CORRIDOR"
EGRESS_SINGLE_ESCAPE_ROUTE = "EGRESS_SINGLE_ESCAPE_ROUTE"
EGRESS_STAIR_NOT_REACHABLE = "EGRESS_STAIR_NOT_REACHABLE"
EGRESS_NO_EXIT = "EGRESS_NO_EXIT"


def _is_exit_room(room) -> bool:
    if room.metadata.get("is_exit"):
        return True
    name = room.metadata.get("name", "").lower()
    rt = room.room_type.value.lower()
    for keyword in ("entrance", "entry", "main entrance", "exit"):
        if keyword in name or keyword in rt:
            return True
    return False


class EgressEngine:
    def __init__(self, max_exit_distance: int = 6) -> None:
        self._max_exit_distance = max_exit_distance
        self._adjacency_engine = AdjacencyEngine()

    def analyze(self, building_model: BuildingModel, room_graph: Optional[RoomGraph] = None) -> EgressMetrics:
        rooms = building_model.rooms
        if not rooms:
            return EgressMetrics(frozenset(), frozenset(), 0.0, 0.0, frozenset(), (), 1.0)
        graph = room_graph if room_graph is not None else self._adjacency_engine.build_graph(building_model)
        exit_ids = {rid for rid, r in rooms.items() if _is_exit_room(r)}
        if not exit_ids:
            return EgressMetrics(frozenset(), frozenset(rooms.keys()), 0.0, 0.0, frozenset(), (), 0.0)
        room_ids = list(rooms.keys())
        reachable: Set[str] = set()
        unreachable: Set[str] = set()
        all_distances: List[float] = []
        exit_paths: List[ExitPath] = []
        dead_ends: Set[str] = set()
        for rid in room_ids:
            best_path = None
            best_dist = float("inf")
            best_exit = None
            for eid in exit_ids:
                path = graph.shortest_path(rid, eid)
                if path is not None:
                    dist = len(path) - 1
                    if dist < best_dist:
                        best_dist = dist
                        best_path = path
                        best_exit = eid
            if best_path is not None:
                reachable.add(rid)
                all_distances.append(best_dist)
                door_count = 0
                for i in range(len(best_path) - 1):
                    r1 = rooms.get(best_path[i])
                    r2 = rooms.get(best_path[i + 1])
                    if r1 and r2:
                        door_count += len(r1.door_ids & r2.door_ids)
                exit_paths.append(ExitPath(rid, best_exit, tuple(best_path), float(best_dist), door_count))
            else:
                unreachable.add(rid)
        for rid in room_ids:
            if graph.degree(rid) <= 1 and len(room_ids) > 1:
                dead_ends.add(rid)
        max_dist = max(all_distances) if all_distances else 0.0
        avg_dist = sum(all_distances) / len(all_distances) if all_distances else 0.0
        total_rooms = len(rooms)
        unreachable_count = len(unreachable)
        egress_score = max(0.0, 1.0 - (unreachable_count / total_rooms)) if total_rooms > 0 else 1.0
        return EgressMetrics(
            reachable_rooms=frozenset(reachable), unreachable_rooms=frozenset(unreachable),
            maximum_exit_distance=max_dist, average_exit_distance=avg_dist,
            dead_end_rooms=frozenset(dead_ends), exit_paths=tuple(exit_paths), egress_score=egress_score,
        )

    def evaluate(self, building_model: BuildingModel, room_graph: Optional[RoomGraph] = None) -> "ConstraintResult":
        from ..constraints.constraint_result import ConstraintResult
        from ..constraints.constraint_issue import ConstraintIssue
        from ..constraints.constraint_severity import ConstraintSeverity
        issues = []
        graph = room_graph if room_graph is not None else self._adjacency_engine.build_graph(building_model)
        rooms = building_model.rooms
        if not rooms:
            return ConstraintResult(issues=issues)
        exit_ids = {rid for rid, r in rooms.items() if _is_exit_room(r)}
        if not exit_ids:
            issues.append(ConstraintIssue(code=EGRESS_NO_EXIT, message="Building has no exit room", severity=ConstraintSeverity.WARNING, score=0.9))
            return ConstraintResult(issues=issues)
        room_ids = list(rooms.keys())
        for rid in room_ids:
            reachable = False
            best_dist = 0
            for eid in exit_ids:
                path = graph.shortest_path(rid, eid)
                if path is not None:
                    reachable = True
                    best_dist = len(path) - 1
                    break
            if not reachable:
                issues.append(ConstraintIssue(code=EGRESS_UNREACHABLE_EXIT, message="Room has no path to any exit", severity=ConstraintSeverity.WARNING, entity_id=rid, score=0.8))
            elif best_dist > self._max_exit_distance:
                issues.append(ConstraintIssue(code=EGRESS_EXCESSIVE_TRAVEL_DISTANCE, message=f"Room requires {best_dist} transitions to exit (max: {self._max_exit_distance})", severity=ConstraintSeverity.WARNING, entity_id=rid, score=0.6))
        for rid in room_ids:
            if graph.degree(rid) <= 1 and len(room_ids) > 1:
                issues.append(ConstraintIssue(code=EGRESS_DEAD_END_CORRIDOR, message="Room is a dead end corridor", severity=ConstraintSeverity.SUGGESTION, entity_id=rid, score=0.4))
        if len(room_ids) > 2:
            exit_reachable_count = 0
            for eid in exit_ids:
                all_reachable = all(graph.shortest_path(rid, eid) is not None for rid in room_ids)
                if all_reachable:
                    exit_reachable_count += 1
            if exit_reachable_count <= 1:
                for rid in room_ids:
                    if rid not in exit_ids:
                        issues.append(ConstraintIssue(code=EGRESS_SINGLE_ESCAPE_ROUTE, message="Only one escape route available", severity=ConstraintSeverity.WARNING, entity_id=rid, score=0.5))
                        break
        stair_ids = [rid for rid, r in rooms.items() if r.room_type == RoomType.STAIRCASE]
        if stair_ids and len(room_ids) > 2:
            for rid in room_ids:
                if rooms[rid].room_type == RoomType.STAIRCASE:
                    continue
                stair_reachable = any(graph.shortest_path(rid, sid) is not None for sid in stair_ids)
                if not stair_reachable:
                    issues.append(ConstraintIssue(code=EGRESS_STAIR_NOT_REACHABLE, message="Room cannot reach any stair", severity=ConstraintSeverity.WARNING, entity_id=rid, score=0.5))
                    break
        return ConstraintResult(issues=issues)
