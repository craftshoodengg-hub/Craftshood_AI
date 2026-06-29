"""Evaluation Report for Building Model v2.

Comprehensive report summarizing validation, constraints, and scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..constraints.constraint_result import ConstraintResult
from ..constraints.constraint_severity import ConstraintSeverity
from ..constraints.scoring import ConstraintScore
from ..validation.validation_result import ValidationResult


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """Comprehensive evaluation report.
    
    Contains all evaluation results including validation errors,
    constraint issues, and design quality scoring.
    
    Attributes:
        summary: The evaluation summary.
        validation_errors: List of validation errors.
        constraint_issues: List of constraint issues.
        highest_priority_issues: Top priority issues to address.
        category_breakdown: Scores broken down by category.
        improvement_opportunities: Deterministic improvement suggestions.
    """
    
    summary: Any
    validation_errors: List[Any] = field(default_factory=list)
    constraint_issues: List[Any] = field(default_factory=list)
    highest_priority_issues: List[Any] = field(default_factory=list)
    category_breakdown: Dict[str, float] = field(default_factory=dict)
    improvement_opportunities: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if the building model passes validation.
        
        Returns:
            True if no validation errors.
        """
        return len(self.validation_errors) == 0
    
    @property
    def is_buildable(self) -> bool:
        """Check if the building is buildable.
        
        A building is buildable if it has no critical validation errors
        and no critical constraint issues.
        
        Returns:
            True if the building is buildable.
        """
        # Check for critical validation errors
        for error in self.validation_errors:
            if hasattr(error, 'severity') and str(error.severity) in ('critical', 'error'):
                return False
        return True
    
    @property
    def design_quality(self) -> str:
        """Get the design quality rating.
        
        Returns:
            Quality rating: Excellent, Good, Fair, or Poor.
        """
        if self.summary.constraint_score.is_excellent:
            return "Excellent"
        elif self.summary.constraint_score.is_good:
            return "Good"
        elif self.summary.constraint_score.is_fair:
            return "Fair"
        else:
            return "Poor"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "is_valid": self.is_valid,
            "is_buildable": self.is_buildable,
            "design_quality": self.design_quality,
            "summary": self.summary.to_dict() if hasattr(self.summary, 'to_dict') else {},
            "validation_error_count": len(self.validation_errors),
            "constraint_issue_count": len(self.constraint_issues),
            "highest_priority_issues": [
                issue.to_dict() if hasattr(issue, 'to_dict') else str(issue)
                for issue in self.highest_priority_issues
            ],
            "category_breakdown": self.category_breakdown,
            "improvement_opportunities": self.improvement_opportunities,
        }
    
    @classmethod
    def create(
        cls,
        validation_result: ValidationResult,
        constraint_result: ConstraintResult,
        constraint_score: ConstraintScore,
        summary: Any,
    ) -> EvaluationReport:
        """Create an evaluation report.
        
        Args:
            validation_result: The validation result.
            constraint_result: The constraint result.
            constraint_score: The constraint score.
            summary: The evaluation summary.
        
        Returns:
            A new EvaluationReport.
        """
        # Extract validation errors
        validation_errors = list(validation_result.errors)
        
        # Extract constraint issues
        constraint_issues = list(constraint_result.issues)
        
        # Determine highest priority issues (recommendations and warnings)
        highest_priority = [
            issue for issue in constraint_issues
            if issue.severity in (ConstraintSeverity.RECOMMENDATION, ConstraintSeverity.WARNING)
        ]
        
        # Generate improvement opportunities
        opportunities = cls._generate_improvement_opportunities(constraint_issues)
        
        return cls(
            summary=summary,
            validation_errors=validation_errors,
            constraint_issues=constraint_issues,
            highest_priority_issues=highest_priority,
            category_breakdown=constraint_score.category_scores,
            improvement_opportunities=opportunities,
        )
    
    @staticmethod
    def _generate_improvement_opportunities(
        issues: List[Any],
    ) -> List[str]:
        """Generate deterministic improvement suggestions.
        
        Based entirely on existing constraint codes.
        No AI reasoning.
        
        Args:
            issues: List of constraint issues.
        
        Returns:
            List of improvement suggestions.
        """
        opportunities: List[str] = []
        seen_codes: set = set()
        
        for issue in issues:
            code = issue.code
            
            if code in seen_codes:
                continue
            seen_codes.add(code)
            
            # Map issue codes to improvement suggestions
            if code == "ROOM_AREA_BELOW_MINIMUM":
                opportunities.append(
                    "Increase room area to meet minimum requirements"
                )
            elif code == "DOOR_WIDTH_BELOW_MINIMUM":
                opportunities.append(
                    "Increase door width to meet minimum requirements"
                )
            elif code == "DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM":
                opportunities.append(
                    "Increase door width to improve accessibility"
                )
            elif code == "WINDOW_AREA_BELOW_MINIMUM":
                opportunities.append(
                    "Increase window area to meet minimum requirements"
                )
            elif code == "STAIR_WIDTH_BELOW_MINIMUM":
                opportunities.append(
                    "Increase stair width to meet minimum requirements"
                )
            elif code == "CEILING_HEIGHT_BELOW_MINIMUM":
                opportunities.append(
                    "Increase ceiling height to meet minimum requirements"
                )
            elif code == "HALLWAY_WIDTH_BELOW_MINIMUM":
                opportunities.append(
                    "Increase hallway/corridor width to improve accessibility"
                )
            elif code == "EMPTY_BUILDING":
                opportunities.append(
                    "Add rooms to the building"
                )
            elif code == "EMPTY_FLOOR":
                opportunities.append(
                    "Add rooms to empty floors"
                )
            elif code == "ISOLATED_ROOM":
                opportunities.append(
                    "Add connections to isolated rooms"
                )
            elif code == "ROOM_WITHOUT_DOOR":
                opportunities.append(
                    "Add doors to rooms"
                )
            elif code == "ROOM_WITHOUT_WINDOW":
                opportunities.append(
                    "Add windows to rooms for natural light"
                )
            elif code == "UNCONNECTED_FLOOR":
                opportunities.append(
                    "Add stair connections between floors"
                )
            elif code == "BATHROOM_ACCESSIBILITY_MISSING":
                opportunities.append(
                    "Add accessibility features to bathrooms"
                )
            elif code == "STAIR_HANDRAIL_MISSING":
                opportunities.append(
                    "Add handrails to stairs for safety"
                )
            elif code == "TURNING_RADIUS_INSUFFICIENT":
                opportunities.append(
                    "Increase space for wheelchair turning radius"
                )
            elif code == "RAMP_SLOPE_EXCEEDS_MAXIMUM":
                opportunities.append(
                    "Reduce ramp slope for accessibility"
                )
            else:
                opportunities.append(
                    f"Address issue: {code}"
                )
        
        return opportunities