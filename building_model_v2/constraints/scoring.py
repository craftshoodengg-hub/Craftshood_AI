"""Constraint Scoring Engine for Building Model v2.

Provides weighted scoring of constraint evaluation results.
Produces a design quality score from 0 to 100.

This module does not implement AI optimization or automatic repair.
It only evaluates and reports design quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constraint_category import ConstraintCategory
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity


# ============================================================================
# Default deduction values per severity level
# ============================================================================

DEFAULT_INFO_DEDUCTION: float = 0.5
DEFAULT_SUGGESTION_DEDUCTION: float = 1.0
DEFAULT_WARNING_DEDUCTION: float = 3.0
DEFAULT_RECOMMENDATION_DEDUCTION: float = 5.0


# ============================================================================
# ConstraintWeightProfile
# ============================================================================


@dataclass(frozen=True, slots=True)
class ConstraintWeightProfile:
    """Weight profile for constraint scoring.
    
    All weights default to 1.0 (equal weighting).
    Weights are applied as multipliers to severity deductions.
    
    Attributes:
        functional_weight: Weight for functional constraints.
        building_code_weight: Weight for building code constraints.
        accessibility_weight: Weight for accessibility constraints.
        environmental_weight: Weight for environmental constraints.
        structural_weight: Weight for structural constraints.
        vastu_weight: Weight for Vastu constraints.
        custom_weight: Weight for custom constraints.
    """
    
    functional_weight: float = 1.0
    building_code_weight: float = 1.0
    accessibility_weight: float = 1.0
    environmental_weight: float = 1.0
    structural_weight: float = 1.0
    vastu_weight: float = 1.0
    custom_weight: float = 1.0
    
    def get_weight(self, category: ConstraintCategory) -> float:
        """Get the weight for a specific category.
        
        Args:
            category: The constraint category.
            
        Returns:
            The weight for the category.
        """
        weight_map = {
            ConstraintCategory.FUNCTIONAL: self.functional_weight,
            ConstraintCategory.BUILDING_CODE: self.building_code_weight,
            ConstraintCategory.ACCESSIBILITY: self.accessibility_weight,
            ConstraintCategory.ENVIRONMENTAL: self.environmental_weight,
            ConstraintCategory.STRUCTURAL: self.structural_weight,
            ConstraintCategory.VASTU: self.vastu_weight,
            ConstraintCategory.CUSTOM: self.custom_weight,
        }
        return weight_map.get(category, 1.0)
    
    def normalized(self) -> ConstraintWeightProfile:
        """Return a normalized copy where weights sum to 1.0.
        
        Returns:
            A new ConstraintWeightProfile with normalized weights.
        """
        total = (
            self.functional_weight
            + self.building_code_weight
            + self.accessibility_weight
            + self.environmental_weight
            + self.structural_weight
            + self.vastu_weight
            + self.custom_weight
        )
        
        if total <= 0:
            return ConstraintWeightProfile()
        
        return ConstraintWeightProfile(
            functional_weight=self.functional_weight / total,
            building_code_weight=self.building_code_weight / total,
            accessibility_weight=self.accessibility_weight / total,
            environmental_weight=self.environmental_weight / total,
            structural_weight=self.structural_weight / total,
            vastu_weight=self.vastu_weight / total,
            custom_weight=self.custom_weight / total,
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "functional_weight": self.functional_weight,
            "building_code_weight": self.building_code_weight,
            "accessibility_weight": self.accessibility_weight,
            "environmental_weight": self.environmental_weight,
            "structural_weight": self.structural_weight,
            "vastu_weight": self.vastu_weight,
            "custom_weight": self.custom_weight,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConstraintWeightProfile:
        """Create from dictionary.
        
        Args:
            data: Dictionary with weight data.
            
        Returns:
            New ConstraintWeightProfile instance.
        """
        return cls(
            functional_weight=float(data.get("functional_weight", 1.0)),
            building_code_weight=float(data.get("building_code_weight", 1.0)),
            accessibility_weight=float(data.get("accessibility_weight", 1.0)),
            environmental_weight=float(data.get("environmental_weight", 1.0)),
            structural_weight=float(data.get("structural_weight", 1.0)),
            vastu_weight=float(data.get("vastu_weight", 1.0)),
            custom_weight=float(data.get("custom_weight", 1.0)),
        )
    
    @classmethod
    def equal_weights(cls) -> ConstraintWeightProfile:
        """Create a profile with all weights equal to 1.0.
        
        Returns:
            A new ConstraintWeightProfile with equal weights.
        """
        return cls()
    
    @classmethod
    def prioritize_category(
        cls,
        category: ConstraintCategory,
        weight: float = 2.0,
    ) -> ConstraintWeightProfile:
        """Create a profile that prioritizes a specific category.
        
        Args:
            category: The category to prioritize.
            weight: The weight to assign to the prioritized category.
            
        Returns:
            A new ConstraintWeightProfile with the category prioritized.
        """
        profile = cls()
        if category == ConstraintCategory.FUNCTIONAL:
            return cls(functional_weight=weight)
        elif category == ConstraintCategory.BUILDING_CODE:
            return cls(building_code_weight=weight)
        elif category == ConstraintCategory.ACCESSIBILITY:
            return cls(accessibility_weight=weight)
        elif category == ConstraintCategory.ENVIRONMENTAL:
            return cls(environmental_weight=weight)
        elif category == ConstraintCategory.STRUCTURAL:
            return cls(structural_weight=weight)
        elif category == ConstraintCategory.VASTU:
            return cls(vastu_weight=weight)
        elif category == ConstraintCategory.CUSTOM:
            return cls(custom_weight=weight)
        return profile


# ============================================================================
# ConstraintScore
# ============================================================================


@dataclass(frozen=True, slots=True)
class ConstraintScore:
    """Immutable result of constraint scoring.
    
    Represents the overall design quality score with category breakdowns.
    
    Attributes:
        overall_score: The final score from 0 to 100.
        maximum_score: The maximum possible score (always 100).
        percentage: The score as a percentage (0.0 to 100.0).
        category_scores: Scores broken down by category.
        issue_count: Total number of issues.
        recommendation_count: Number of recommendation-severity issues.
        warning_count: Number of warning-severity issues.
        suggestion_count: Number of suggestion-severity issues.
    """
    
    overall_score: float
    maximum_score: float = 100.0
    category_scores: dict[str, float] = field(default_factory=dict)
    issue_count: int = 0
    recommendation_count: int = 0
    warning_count: int = 0
    suggestion_count: int = 0
    
    @property
    def percentage(self) -> float:
        """Get the score as a percentage.
        
        Returns:
            Score percentage (0.0 to 100.0).
        """
        if self.maximum_score <= 0:
            return 0.0
        return (self.overall_score / self.maximum_score) * 100.0
    
    @property
    def is_excellent(self) -> bool:
        """Check if the score is excellent (>=95%).
        
        Returns:
            True if percentage >= 95.
        """
        return self.percentage >= 95.0
    
    @property
    def is_good(self) -> bool:
        """Check if the score is good (>=85%).
        
        Returns:
            True if percentage >= 85.
        """
        return self.percentage >= 85.0
    
    @property
    def is_fair(self) -> bool:
        """Check if the score is fair (>=70%).
        
        Returns:
            True if percentage >= 70.
        """
        return self.percentage >= 70.0
    
    @property
    def is_poor(self) -> bool:
        """Check if the score is poor (<70%).
        
        Returns:
            True if percentage < 70.
        """
        return self.percentage < 70.0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "overall_score": self.overall_score,
            "maximum_score": self.maximum_score,
            "percentage": self.percentage,
            "category_scores": self.category_scores,
            "issue_count": self.issue_count,
            "recommendation_count": self.recommendation_count,
            "warning_count": self.warning_count,
            "suggestion_count": self.suggestion_count,
            "is_excellent": self.is_excellent,
            "is_good": self.is_good,
            "is_fair": self.is_fair,
            "is_poor": self.is_poor,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConstraintScore:
        """Create from dictionary.
        
        Args:
            data: Dictionary with score data.
            
        Returns:
            New ConstraintScore instance.
        """
        return cls(
            overall_score=float(data.get("overall_score", 0.0)),
            maximum_score=float(data.get("maximum_score", 100.0)),
            category_scores=data.get("category_scores", {}),
            issue_count=int(data.get("issue_count", 0)),
            recommendation_count=int(data.get("recommendation_count", 0)),
            warning_count=int(data.get("warning_count", 0)),
            suggestion_count=int(data.get("suggestion_count", 0)),
        )
    
    @classmethod
    def perfect(cls) -> ConstraintScore:
        """Create a perfect score (100).
        
        Returns:
            A new ConstraintScore with maximum score.
        """
        return cls(overall_score=100.0)
    
    @classmethod
    def zero(cls) -> ConstraintScore:
        """Create a zero score (0).
        
        Returns:
            A new ConstraintScore with zero score.
        """
        return cls(overall_score=0.0)


# ============================================================================
# ConstraintScoreEngine
# ============================================================================


class ConstraintScoreEngine:
    """Engine for computing weighted constraint scores.
    
    Evaluates a ConstraintResult and produces a ConstraintScore.
    Never modifies the input ConstraintResult.
    
    Scoring principles:
        - Start from 100.
        - Deduct according to severity.
        - Apply category weights.
        - Clamp score between 0 and 100.
        - Empty ConstraintResult = 100%.
    """
    
    def __init__(
        self,
        info_deduction: float = DEFAULT_INFO_DEDUCTION,
        suggestion_deduction: float = DEFAULT_SUGGESTION_DEDUCTION,
        warning_deduction: float = DEFAULT_WARNING_DEDUCTION,
        recommendation_deduction: float = DEFAULT_RECOMMENDATION_DEDUCTION,
    ) -> None:
        """Initialize the scoring engine.
        
        Args:
            info_deduction: Deduction per INFO severity issue.
            suggestion_deduction: Deduction per SUGGESTION severity issue.
            warning_deduction: Deduction per WARNING severity issue.
            recommendation_deduction: Deduction per RECOMMENDATION severity issue.
        """
        self._info_deduction = info_deduction
        self._suggestion_deduction = suggestion_deduction
        self._warning_deduction = warning_deduction
        self._recommendation_deduction = recommendation_deduction
    
    @property
    def info_deduction(self) -> float:
        """Get the info deduction value."""
        return self._info_deduction
    
    @property
    def suggestion_deduction(self) -> float:
        """Get the suggestion deduction value."""
        return self._suggestion_deduction
    
    @property
    def warning_deduction(self) -> float:
        """Get the warning deduction value."""
        return self._warning_deduction
    
    @property
    def recommendation_deduction(self) -> float:
        """Get the recommendation deduction value."""
        return self._recommendation_deduction
    
    def _get_severity_deduction(self, severity: ConstraintSeverity) -> float:
        """Get the deduction value for a severity level.
        
        Args:
            severity: The severity level.
            
        Returns:
            The deduction value.
        """
        deduction_map = {
            ConstraintSeverity.INFO: self._info_deduction,
            ConstraintSeverity.SUGGESTION: self._suggestion_deduction,
            ConstraintSeverity.WARNING: self._warning_deduction,
            ConstraintSeverity.RECOMMENDATION: self._recommendation_deduction,
        }
        return deduction_map.get(severity, 0.0)
    
    def _categorize_issues(
        self,
        result: ConstraintResult,
    ) -> dict[ConstraintCategory, list]:
        """Group issues by constraint category.
        
        Uses the issue code prefix to determine category.
        
        Args:
            result: The constraint result to categorize.
            
        Returns:
            Dictionary mapping categories to issue lists.
        """
        categories: dict[ConstraintCategory, list] = {
            category: []
            for category in ConstraintCategory
        }
        
        for issue in result.issues:
            category = self._determine_category(issue)
            categories[category].append(issue)
        
        return categories
    
    def _determine_category(self, issue: Any) -> ConstraintCategory:
        """Determine the category of an issue based on its code.
        
        Args:
            issue: The constraint issue.
            
        Returns:
            The determined category.
        """
        code = issue.code.upper()
        
        # Building code constraints
        if any(code.startswith(prefix) for prefix in [
            "ROOM_AREA", "DOOR_WIDTH", "WINDOW_AREA", "STAIR_WIDTH",
            "CEILING_HEIGHT", "MAX_TRAVEL_DISTANCE",
        ]):
            return ConstraintCategory.BUILDING_CODE
        
        # Accessibility constraints
        if any(code.startswith(prefix) for prefix in [
            "DOOR_WIDTH_BELOW_ACCESSIBLE", "HALLWAY_WIDTH",
            "TURNING_RADIUS", "RAMP_SLOPE", "BATHROOM_ACCESSIBILITY",
            "STAIR_HANDRAIL",
        ]):
            return ConstraintCategory.ACCESSIBILITY
        
        # Functional constraints
        if any(code.startswith(prefix) for prefix in [
            "EMPTY_BUILDING", "EMPTY_FLOOR", "ISOLATED_ROOM",
            "ROOM_WITHOUT_DOOR", "ROOM_WITHOUT_WINDOW",
            "UNCONNECTED_FLOOR",
        ]):
            return ConstraintCategory.FUNCTIONAL
        
        # Default to custom for unknown codes
        return ConstraintCategory.CUSTOM
    
    def evaluate(
        self,
        constraint_result: ConstraintResult,
        weight_profile: ConstraintWeightProfile | None = None,
    ) -> ConstraintScore:
        """Evaluate a constraint result and produce a score.
        
        Args:
            constraint_result: The result to evaluate.
            weight_profile: Optional weight profile. Defaults to equal weights.
            
        Returns:
            The computed ConstraintScore.
        """
        if weight_profile is None:
            weight_profile = ConstraintWeightProfile.equal_weights()
        
        # Empty result = perfect score
        if constraint_result.is_optimal:
            return ConstraintScore.perfect()
        
        # Categorize issues
        categories = self._categorize_issues(constraint_result)
        
        # Calculate weighted deductions per category
        category_scores: dict[str, float] = {}
        total_deduction = 0.0
        
        for category, issues in categories.items():
            if not issues:
                category_scores[category.value] = 100.0
                continue
            
            category_deduction = 0.0
            for issue in issues:
                severity_deduction = self._get_severity_deduction(issue.severity)
                category_deduction += severity_deduction
            
            weight = weight_profile.get_weight(category)
            weighted_deduction = category_deduction * weight
            total_deduction += weighted_deduction
            
            # Category score (clamped to 0)
            category_score = max(0.0, 100.0 - weighted_deduction)
            category_scores[category.value] = round(category_score, 2)
        
        # Calculate overall score (clamped between 0 and 100)
        overall_score = max(0.0, min(100.0, 100.0 - total_deduction))
        overall_score = round(overall_score, 2)
        
        return ConstraintScore(
            overall_score=overall_score,
            maximum_score=100.0,
            category_scores=category_scores,
            issue_count=constraint_result.issue_count,
            recommendation_count=constraint_result.recommendation_count,
            warning_count=constraint_result.warning_count,
            suggestion_count=constraint_result.suggestion_count,
        )