"""Evaluation Summary for Building Model v2.

Immutable summary of evaluation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from ..constraints.scoring import ConstraintScore
from ..validation.validation_result import ValidationResult


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    """Immutable summary of evaluation results.
    
    Contains all evaluation metrics in a single immutable object.
    
    Attributes:
        overall_score: The final design quality score (0-100).
        validation_result: The validation result.
        constraint_result: The constraint result.
        constraint_score: The constraint score.
        category_scores: Scores broken down by category.
        issue_counts: Counts of issues by type.
        recommendation_counts: Counts of recommendations by category.
        warning_counts: Counts of warnings by category.
        suggestion_counts: Counts of suggestions by category.
    """
    
    overall_score: float
    validation_result: ValidationResult
    constraint_result: Any
    constraint_score: ConstraintScore
    category_scores: Dict[str, float] = field(default_factory=dict)
    issue_counts: Dict[str, int] = field(default_factory=dict)
    recommendation_counts: Dict[str, int] = field(default_factory=dict)
    warning_counts: Dict[str, int] = field(default_factory=dict)
    suggestion_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if the building model is valid.
        
        Returns:
            True if validation passed.
        """
        return self.validation_result.is_valid
    
    @property
    def total_issues(self) -> int:
        """Get the total number of issues.
        
        Returns:
            Total count of all issues.
        """
        return self.constraint_result.issue_count
    
    @property
    def total_warnings(self) -> int:
        """Get the total number of warnings.
        
        Returns:
            Total count of warnings.
        """
        return self.constraint_result.warning_count
    
    @property
    def total_recommendations(self) -> int:
        """Get the total number of recommendations.
        
        Returns:
            Total count of recommendations.
        """
        return self.constraint_result.recommendation_count
    
    @property
    def total_suggestions(self) -> int:
        """Get the total number of suggestions.
        
        Returns:
            Total count of suggestions.
        """
        return self.constraint_result.suggestion_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "overall_score": self.overall_score,
            "is_valid": self.is_valid,
            "total_issues": self.total_issues,
            "total_warnings": self.total_warnings,
            "total_recommendations": self.total_recommendations,
            "total_suggestions": self.total_suggestions,
            "category_scores": self.category_scores,
            "issue_counts": self.issue_counts,
            "recommendation_counts": self.recommendation_counts,
            "warning_counts": self.warning_counts,
            "suggestion_counts": self.suggestion_counts,
            "validation_summary": {
                "is_valid": self.validation_result.is_valid,
                "error_count": self.validation_result.error_count,
                "warning_count": self.validation_result.warning_count,
            },
            "constraint_summary": {
                "is_optimal": self.constraint_result.is_optimal,
                "issue_count": self.constraint_result.issue_count,
                "recommendation_count": self.constraint_result.recommendation_count,
                "warning_count": self.constraint_result.warning_count,
                "suggestion_count": self.constraint_result.suggestion_count,
            },
            "score_summary": {
                "overall_score": self.constraint_score.overall_score,
                "percentage": self.constraint_score.percentage,
                "is_excellent": self.constraint_score.is_excellent,
                "is_good": self.constraint_score.is_good,
                "is_fair": self.constraint_score.is_fair,
                "is_poor": self.constraint_score.is_poor,
            },
        }
    
    @classmethod
    def create(
        cls,
        validation_result: ValidationResult,
        constraint_result: Any,
        constraint_score: ConstraintScore,
    ) -> EvaluationSummary:
        """Create an evaluation summary.
        
        Args:
            validation_result: The validation result.
            constraint_result: The constraint result.
            constraint_score: The constraint score.
        
        Returns:
            A new EvaluationSummary.
        """
        return cls(
            overall_score=constraint_score.overall_score,
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            category_scores=constraint_score.category_scores,
        )