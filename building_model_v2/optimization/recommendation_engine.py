"""Recommendation Engine for Building Model v2.

Deterministic engine that converts EvaluationReport into ImprovementPlan.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..constraints.constraint_issue import ConstraintIssue
from ..constraints.constraint_severity import ConstraintSeverity
from ..evaluation.evaluation_report import EvaluationReport
from .improvement_plan import ImprovementPlan
from .optimization_action import OptimizationAction


# Centralized constraint code to action mapping
CONSTRAINT_ACTION_MAP: Dict[str, Tuple[str, str, str, float]] = {
    "ROOM_AREA_BELOW_MINIMUM": ("Increase room dimensions", "Expand the room area to meet minimum requirements", "room", 0.95),
    "DOOR_WIDTH_BELOW_MINIMUM": ("Increase door width", "Widen the door opening to meet minimum requirements", "door", 0.95),
    "DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM": ("Increase clear opening", "Widen the door to improve accessibility", "door", 0.95),
    "WINDOW_AREA_BELOW_MINIMUM": ("Increase window size", "Enlarge windows to meet minimum requirements", "window", 0.95),
    "STAIR_WIDTH_BELOW_MINIMUM": ("Increase stair width", "Widen the stair to meet minimum requirements", "stair", 0.95),
    "CEILING_HEIGHT_BELOW_MINIMUM": ("Increase ceiling height", "Raise the ceiling to meet minimum requirements", "room", 0.95),
    "HALLWAY_WIDTH_BELOW_MINIMUM": ("Increase hallway width", "Widen the hallway to improve accessibility", "hallway", 0.95),
    "WINDOW_TO_FLOOR_RATIO_LOW": ("Increase glazing", "Add or enlarge windows to improve natural light", "window", 0.90),
    "NATURAL_LIGHT_INSUFFICIENT": ("Increase glazing", "Add windows to improve natural light quality", "window", 0.90),
    "CROSS_VENTILATION_POSSIBLE": ("Add opposing window", "Add a window on the opposite wall for cross ventilation", "window", 0.85),
    "WEST_FACING_LARGE_GLAZING": ("Provide external shading", "Add shading devices to reduce west-facing heat gain", "window", 0.80),
    "WALL_SPAN_EXCEEDS_MAXIMUM": ("Add structural support", "Add columns or reduce wall span", "wall", 0.75),
    "LARGE_WALL_OPENING": ("Reinforce opening", "Add structural reinforcement around large openings", "wall", 0.75),
    "EMPTY_BUILDING": ("Add first floor", "Add floors and rooms to the building", "building", 0.50),
    "EMPTY_FLOOR": ("Add rooms to floor", "Add rooms to the empty floor", "floor", 0.50),
    "ISOLATED_ROOM": ("Add room connections", "Add doors or openings to connect isolated rooms", "room", 0.85),
    "ROOM_WITHOUT_DOOR": ("Add door to room", "Add a door to provide room access", "room", 0.90),
    "ROOM_WITHOUT_WINDOW": ("Add window to room", "Add a window for natural light and ventilation", "room", 0.90),
    "UNCONNECTED_FLOOR": ("Add floor connections", "Add stairs or elevators to connect floors", "floor", 0.75),
    "BATHROOM_ACCESSIBILITY_MISSING": ("Add accessibility features", "Add grab bars, turning space, and accessible fixtures", "bathroom", 0.85),
    "STAIR_HANDRAIL_MISSING": ("Add stair handrails", "Install handrails on both sides of stairs", "stair", 0.95),
    "TURNING_RADIUS_INSUFFICIENT": ("Increase turning space", "Enlarge the space to accommodate wheelchair turning", "room", 0.90),
    "RAMP_SLOPE_EXCEEDS_MAXIMUM": ("Reduce ramp slope", "Lengthen the ramp or reduce the slope ratio", "ramp", 0.85),
}

SEVERITY_PRIORITY: Dict[ConstraintSeverity, int] = {
    ConstraintSeverity.RECOMMENDATION: 1,
    ConstraintSeverity.WARNING: 2,
    ConstraintSeverity.SUGGESTION: 3,
    ConstraintSeverity.INFO: 4,
}


class RecommendationEngine:
    """Deterministic recommendation engine."""
    
    def generate(self, evaluation_report: EvaluationReport) -> ImprovementPlan:
        """Generate an improvement plan from an evaluation report."""
        current_score = self._extract_current_score(evaluation_report)
        actions = self._map_issues_to_actions(evaluation_report)
        sorted_actions = sorted(actions)
        estimated_final = self._estimate_final_score(current_score, sorted_actions)
        
        return ImprovementPlan(
            actions=sorted_actions,
            current_score=current_score,
            estimated_final_score=estimated_final,
        )
    
    def _extract_current_score(self, report: EvaluationReport) -> float:
        """Extract the current quality score from the report."""
        try:
            return report.summary.overall_score
        except AttributeError:
            return 0.0
    
    def _map_issues_to_actions(self, report: EvaluationReport) -> List[OptimizationAction]:
        """Map constraint issues to optimization actions."""
        actions: List[OptimizationAction] = []
        seen_codes: set = set()
        
        for issue in report.constraint_issues:
            code = issue.code
            if code in seen_codes:
                continue
            seen_codes.add(code)
            action = self._create_action_from_issue(issue)
            if action is not None:
                actions.append(action)
        
        for error in report.validation_errors:
            if hasattr(error, 'code'):
                code = error.code
                if code not in seen_codes:
                    seen_codes.add(code)
                    action = self._create_action_from_validation_error(error)
                    if action is not None:
                        actions.append(action)
        
        return actions
    
    def _create_action_from_issue(self, issue: ConstraintIssue) -> OptimizationAction | None:
        """Create an optimization action from a constraint issue."""
        code = issue.code
        if code not in CONSTRAINT_ACTION_MAP:
            return None
        
        title, description, entity_type, confidence = CONSTRAINT_ACTION_MAP[code]
        priority = self._calculate_priority(issue)
        estimated_gain = self._calculate_estimated_gain(issue, priority)
        action_id = f"{code.lower()}_{issue.entity_id or 'unknown'}"
        
        return OptimizationAction(
            id=action_id,
            title=title,
            description=description,
            target_entity_id=issue.entity_id or "",
            target_entity_type=entity_type,
            constraint_codes=[code],
            current_score=issue.score,
            estimated_score_gain=estimated_gain,
            priority=priority,
            confidence=confidence,
            metadata={"source_severity": str(issue.severity), "source_message": issue.message},
        )
    
    def _create_action_from_validation_error(self, error: Any) -> OptimizationAction | None:
        """Create an optimization action from a validation error."""
        code = error.code
        if code not in CONSTRAINT_ACTION_MAP:
            return None
        
        title, description, entity_type, confidence = CONSTRAINT_ACTION_MAP[code]
        priority = 1
        estimated_gain = 0.15
        action_id = f"{code.lower()}_{getattr(error, 'entity_id', 'unknown')}"
        
        return OptimizationAction(
            id=action_id,
            title=title,
            description=description,
            target_entity_id=getattr(error, 'entity_id', "") or "",
            target_entity_type=entity_type,
            constraint_codes=[code],
            current_score=0.0,
            estimated_score_gain=estimated_gain,
            priority=priority,
            confidence=confidence,
            metadata={"source": "validation_error", "source_message": getattr(error, 'message', '')},
        )
    
    def _calculate_priority(self, issue: ConstraintIssue) -> int:
        """Calculate priority based on severity."""
        return SEVERITY_PRIORITY.get(issue.severity, 99)
    
    def _calculate_estimated_gain(self, issue: ConstraintIssue, priority: int) -> float:
        """Calculate estimated score gain."""
        base_gain = issue.score
        priority_multiplier = 1.0 / priority
        estimated_gain = base_gain * priority_multiplier
        return min(1.0, max(0.01, estimated_gain))
    
    def _estimate_final_score(self, current_score: float, actions: List[OptimizationAction]) -> float:
        """Estimate the final score after applying all actions."""
        adjusted_gain = 0.0
        for i, action in enumerate(actions):
            factor = 1.0 / (1.0 + i * 0.1)
            adjusted_gain += action.estimated_score_gain * factor
        
        estimated_final = min(100.0, current_score + adjusted_gain * 10)
        return estimated_final