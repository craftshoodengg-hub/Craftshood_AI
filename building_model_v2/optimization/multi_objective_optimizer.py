"""Multi-Objective Optimizer for Building Model v2.

Evaluates an EvaluationReport using an OptimizationProfile to produce
weighted objective scores. Does not modify the building or perform optimization.

Future extension points:
    - Cost optimization
    - Carbon scoring
    - Energy simulation
    - User preferences
    - ML-assisted weighting
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..constraints.constraint_issue import ConstraintIssue
from ..constraints.constraint_severity import ConstraintSeverity
from ..evaluation.evaluation_report import EvaluationReport
from .objective_score import ObjectiveScore
from .optimization_profile import OptimizationProfile

SEVERITY_DEDUCTION: Dict[ConstraintSeverity, float] = {
    ConstraintSeverity.INFO: 0.5,
    ConstraintSeverity.SUGGESTION: 1.0,
    ConstraintSeverity.WARNING: 3.0,
    ConstraintSeverity.RECOMMENDATION: 5.0,
}


class MultiObjectiveOptimizer:
    """Evaluates an EvaluationReport using an OptimizationProfile.

    Computes weighted objective scores based on constraint issues and
    profile weights. Does not modify the building or perform optimization.

    No AI.
    No randomness.
    No mutation.
    Pure deterministic calculations.
    """

    def evaluate(
        self,
        evaluation_report: EvaluationReport,
        profile: OptimizationProfile,
    ) -> ObjectiveScore:
        """Evaluate an evaluation report using the given profile."""
        if not profile.objectives:
            return ObjectiveScore(
                overall=0.0,
                category_scores={},
                weighted_score=0.0,
                objective_breakdown={},
            )

        issues = list(evaluation_report.constraint_issues)

        category_scores: Dict[str, float] = {}
        objective_breakdown: Dict[str, float] = {}
        total_weighted_score = 0.0
        total_weight = 0.0

        for objective in profile.objectives:
            if not objective.is_active:
                continue

            category_issues = self._collect_category_issues(issues, objective.category)
            category_score = self._calculate_category_score(category_issues)
            weighted_score = self._apply_weight(category_score, objective.normalized_weight)

            category_scores[objective.category] = self._clamp_score(category_score)
            objective_breakdown[objective.name] = self._clamp_score(weighted_score)
            total_weighted_score += weighted_score
            total_weight += objective.normalized_weight

        # Calculate weighted average for overall score
        if total_weight > 0:
            overall = self._clamp_score(total_weighted_score / total_weight)
        else:
            overall = 0.0

        return ObjectiveScore(
            overall=overall,
            category_scores=category_scores,
            weighted_score=overall,
            objective_breakdown=objective_breakdown,
        )

    def _collect_category_issues(
        self,
        issues: List[ConstraintIssue],
        category: str,
    ) -> List[ConstraintIssue]:
        """Collect issues matching the given category."""
        return [issue for issue in issues if self._issue_belongs_to_category(issue, category)]

    def _issue_belongs_to_category(self, issue: ConstraintIssue, category: str) -> bool:
        """Determine if an issue belongs to a category."""
        code = issue.code.upper()

        category_prefixes = {
            "functional": [
                "EMPTY_BUILDING",
                "EMPTY_FLOOR",
                "ISOLATED_ROOM",
                "ROOM_WITHOUT_DOOR",
                "ROOM_WITHOUT_WINDOW",
                "UNCONNECTED_FLOOR",
            ],
            "building_code": [
                "ROOM_AREA",
                "DOOR_WIDTH",
                "WINDOW_AREA",
                "STAIR_WIDTH",
                "CEILING_HEIGHT",
                "MAX_TRAVEL_DISTANCE",
            ],
            "accessibility": [
                "DOOR_WIDTH_BELOW_ACCESSIBLE",
                "HALLWAY_WIDTH",
                "TURNING_RADIUS",
                "RAMP_SLOPE",
                "BATHROOM_ACCESSIBILITY",
                "STAIR_HANDRAIL",
            ],
            "environmental": [
                "WINDOW_TO_FLOOR_RATIO",
                "NATURAL_LIGHT",
                "CROSS_VENTILATION",
                "OUTDOOR_CONNECTION",
                "SOLAR_ORIENTATION",
            ],
            "structural": [
                "WALL_SPAN",
                "COLUMN_SPACING",
                "LOAD_BEARING",
                "STAIR_SUPPORT",
                "STRUCTURAL_SYMMETRY",
                "LARGE_OPENING",
            ],
            "vastu": [
                "VASTU",
            ],
        }

        prefixes = category_prefixes.get(category, [])
        return any(code.startswith(prefix) for prefix in prefixes)

    def _calculate_category_score(self, issues: List[ConstraintIssue]) -> float:
        """Calculate raw category score based on issues."""
        if not issues:
            return 100.0

        total_deduction = 0.0
        for issue in issues:
            deduction = SEVERITY_DEDUCTION.get(issue.severity, 0.0)
            total_deduction += deduction

        return self._clamp_score(100.0 - total_deduction)

    def _apply_weight(self, score: float, weight: float) -> float:
        """Apply weight to a score."""
        return score * weight

    def _clamp_score(self, score: float) -> float:
        """Clamp score to valid range (0-100)."""
        return max(0.0, min(100.0, score))