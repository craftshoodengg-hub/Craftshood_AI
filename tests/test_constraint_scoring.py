"""Unit tests for Constraint Scoring Engine."""

from __future__ import annotations

import pytest

from building_model_v2.constraints import (
    ConstraintCategory,
    ConstraintScore,
    ConstraintScoreEngine,
    ConstraintSeverity,
    ConstraintWeightProfile,
)
from building_model_v2.constraints.constraint_issue import ConstraintIssue
from building_model_v2.constraints.constraint_result import ConstraintResult
from building_model_v2.constraints.scoring import (
    DEFAULT_INFO_DEDUCTION,
    DEFAULT_RECOMMENDATION_DEDUCTION,
    DEFAULT_SUGGESTION_DEDUCTION,
    DEFAULT_WARNING_DEDUCTION,
)


# ============================================================================
# Helper functions
# ============================================================================


def create_issue(
    code: str = "TEST_ISSUE",
    message: str = "Test issue",
    severity: ConstraintSeverity = ConstraintSeverity.WARNING,
    entity_id: str | None = None,
    score: float = 0.5,
) -> ConstraintIssue:
    """Create a test constraint issue.
    
    Args:
        code: Issue code.
        message: Issue message.
        severity: Issue severity.
        entity_id: Optional entity ID.
        score: Issue score impact.
    
    Returns:
        A new ConstraintIssue.
    """
    return ConstraintIssue(
        code=code,
        message=message,
        severity=severity,
        entity_id=entity_id,
        score=score,
    )


def create_result_with_issues(
    issues: list[ConstraintIssue],
) -> ConstraintResult:
    """Create a ConstraintResult with the given issues.
    
    Args:
        issues: List of issues.
    
    Returns:
        A new ConstraintResult.
    """
    return ConstraintResult(issues=issues)


# ============================================================================
# ConstraintWeightProfile tests
# ============================================================================


class TestConstraintWeightProfile:
    """Tests for ConstraintWeightProfile."""
    
    def test_default_weights(self) -> None:
        profile = ConstraintWeightProfile()
        assert profile.functional_weight == 1.0
        assert profile.building_code_weight == 1.0
        assert profile.accessibility_weight == 1.0
        assert profile.environmental_weight == 1.0
        assert profile.structural_weight == 1.0
        assert profile.vastu_weight == 1.0
        assert profile.custom_weight == 1.0
    
    def test_custom_weights(self) -> None:
        profile = ConstraintWeightProfile(
            functional_weight=2.0,
            building_code_weight=1.5,
        )
        assert profile.functional_weight == 2.0
        assert profile.building_code_weight == 1.5
    
    def test_get_weight(self) -> None:
        profile = ConstraintWeightProfile(
            functional_weight=2.0,
            building_code_weight=1.5,
        )
        assert profile.get_weight(ConstraintCategory.FUNCTIONAL) == 2.0
        assert profile.get_weight(ConstraintCategory.BUILDING_CODE) == 1.5
        assert profile.get_weight(ConstraintCategory.ACCESSIBILITY) == 1.0
    
    def test_normalized(self) -> None:
        profile = ConstraintWeightProfile(
            functional_weight=2.0,
            building_code_weight=2.0,
            accessibility_weight=2.0,
            environmental_weight=2.0,
            structural_weight=2.0,
            vastu_weight=2.0,
            custom_weight=2.0,
        )
        normalized = profile.normalized()
        assert normalized.functional_weight == pytest.approx(1 / 7)
        assert normalized.building_code_weight == pytest.approx(1 / 7)
    
    def test_normalized_zero_total(self) -> None:
        """When all weights are zero, normalized returns default profile."""
        profile = ConstraintWeightProfile(
            functional_weight=0.0,
            building_code_weight=0.0,
            accessibility_weight=0.0,
            environmental_weight=0.0,
            structural_weight=0.0,
            vastu_weight=0.0,
            custom_weight=0.0,
        )
        normalized = profile.normalized()
        # When total is 0, returns default equal weights
        assert normalized.functional_weight == 1.0
        assert normalized.building_code_weight == 1.0
    
    def test_to_dict(self) -> None:
        profile = ConstraintWeightProfile()
        d = profile.to_dict()
        assert d["functional_weight"] == 1.0
        assert d["building_code_weight"] == 1.0
    
    def test_from_dict(self) -> None:
        data = {
            "functional_weight": 2.0,
            "building_code_weight": 1.5,
        }
        profile = ConstraintWeightProfile.from_dict(data)
        assert profile.functional_weight == 2.0
        assert profile.building_code_weight == 1.5
    
    def test_equal_weights_factory(self) -> None:
        profile = ConstraintWeightProfile.equal_weights()
        assert profile.functional_weight == 1.0
    
    def test_prioritize_category_functional(self) -> None:
        profile = ConstraintWeightProfile.prioritize_category(
            ConstraintCategory.FUNCTIONAL,
            weight=3.0,
        )
        assert profile.functional_weight == 3.0
        assert profile.building_code_weight == 1.0
    
    def test_prioritize_category_building_code(self) -> None:
        profile = ConstraintWeightProfile.prioritize_category(
            ConstraintCategory.BUILDING_CODE,
            weight=2.5,
        )
        assert profile.building_code_weight == 2.5
    
    def test_prioritize_category_accessibility(self) -> None:
        profile = ConstraintWeightProfile.prioritize_category(
            ConstraintCategory.ACCESSIBILITY,
            weight=2.0,
        )
        assert profile.accessibility_weight == 2.0


# ============================================================================
# ConstraintScore tests
# ============================================================================


class TestConstraintScore:
    """Tests for ConstraintScore."""
    
    def test_perfect_score(self) -> None:
        score = ConstraintScore.perfect()
        assert score.overall_score == 100.0
        assert score.maximum_score == 100.0
        assert score.percentage == 100.0
    
    def test_zero_score(self) -> None:
        score = ConstraintScore.zero()
        assert score.overall_score == 0.0
        assert score.percentage == 0.0
    
    def test_custom_score(self) -> None:
        score = ConstraintScore(overall_score=75.0)
        assert score.overall_score == 75.0
        assert score.percentage == 75.0
    
    def test_is_excellent(self) -> None:
        assert ConstraintScore(overall_score=95.0).is_excellent is True
        assert ConstraintScore(overall_score=100.0).is_excellent is True
        assert ConstraintScore(overall_score=94.9).is_excellent is False
    
    def test_is_good(self) -> None:
        assert ConstraintScore(overall_score=85.0).is_good is True
        assert ConstraintScore(overall_score=95.0).is_good is True
        assert ConstraintScore(overall_score=84.9).is_good is False
    
    def test_is_fair(self) -> None:
        assert ConstraintScore(overall_score=70.0).is_fair is True
        assert ConstraintScore(overall_score=85.0).is_fair is True
        assert ConstraintScore(overall_score=69.9).is_fair is False
    
    def test_is_poor(self) -> None:
        assert ConstraintScore(overall_score=69.9).is_poor is True
        assert ConstraintScore(overall_score=0.0).is_poor is True
        assert ConstraintScore(overall_score=70.0).is_poor is False
    
    def test_to_dict(self) -> None:
        score = ConstraintScore(
            overall_score=85.0,
            category_scores={"functional": 90.0},
            issue_count=2,
        )
        d = score.to_dict()
        assert d["overall_score"] == 85.0
        assert d["percentage"] == 85.0
        assert d["is_good"] is True
        assert d["is_fair"] is True
    
    def test_from_dict(self) -> None:
        data = {
            "overall_score": 85.0,
            "maximum_score": 100.0,
            "category_scores": {"functional": 90.0},
            "issue_count": 2,
        }
        score = ConstraintScore.from_dict(data)
        assert score.overall_score == 85.0
        assert score.issue_count == 2
    
    def test_from_dict_defaults(self) -> None:
        data = {}
        score = ConstraintScore.from_dict(data)
        assert score.overall_score == 0.0
        assert score.issue_count == 0


# ============================================================================
# ConstraintScoreEngine tests
# ============================================================================


class TestConstraintScoreEngine:
    """Tests for ConstraintScoreEngine."""
    
    def test_default_deductions(self) -> None:
        engine = ConstraintScoreEngine()
        assert engine.info_deduction == DEFAULT_INFO_DEDUCTION
        assert engine.suggestion_deduction == DEFAULT_SUGGESTION_DEDUCTION
        assert engine.warning_deduction == DEFAULT_WARNING_DEDUCTION
        assert engine.recommendation_deduction == DEFAULT_RECOMMENDATION_DEDUCTION
    
    def test_custom_deductions(self) -> None:
        engine = ConstraintScoreEngine(
            info_deduction=0.25,
            suggestion_deduction=0.5,
            warning_deduction=2.0,
            recommendation_deduction=4.0,
        )
        assert engine.info_deduction == 0.25
        assert engine.suggestion_deduction == 0.5
        assert engine.warning_deduction == 2.0
        assert engine.recommendation_deduction == 4.0
    
    def test_empty_result_returns_perfect(self) -> None:
        engine = ConstraintScoreEngine()
        result = ConstraintResult.create()
        score = engine.evaluate(result)
        assert score.overall_score == 100.0
        assert score.is_excellent is True
    
    def test_one_warning_issue(self) -> None:
        engine = ConstraintScoreEngine()
        result = create_result_with_issues([
            create_issue(severity=ConstraintSeverity.WARNING),
        ])
        score = engine.evaluate(result)
        assert score.overall_score == pytest.approx(100.0 - DEFAULT_WARNING_DEDUCTION)
        assert score.issue_count == 1
        assert score.warning_count == 1
    
    def test_one_recommendation_issue(self) -> None:
        engine = ConstraintScoreEngine()
        result = create_result_with_issues([
            create_issue(severity=ConstraintSeverity.RECOMMENDATION),
        ])
        score = engine.evaluate(result)
        assert score.overall_score == pytest.approx(100.0 - DEFAULT_RECOMMENDATION_DEDUCTION)
        assert score.recommendation_count == 1
    
    def test_one_suggestion_issue(self) -> None:
        engine = ConstraintScoreEngine()
        result = create_result_with_issues([
            create_issue(severity=ConstraintSeverity.SUGGESTION),
        ])
        score = engine.evaluate(result)
        assert score.overall_score == pytest.approx(100.0 - DEFAULT_SUGGESTION_DEDUCTION)
        assert score.suggestion_count == 1
    
    def test_one_info_issue(self) -> None:
        engine = ConstraintScoreEngine()
        result = create_result_with_issues([
            create_issue(severity=ConstraintSeverity.INFO),
        ])
        score = engine.evaluate(result)
        assert score.overall_score == pytest.approx(100.0 - DEFAULT_INFO_DEDUCTION)
    
    def test_multiple_issues_same_severity(self) -> None:
        engine = ConstraintScoreEngine()
        result = create_result_with_issues([
            create_issue(severity=ConstraintSeverity.WARNING),
            create_issue(severity=ConstraintSeverity.WARNING),
            create_issue(severity=ConstraintSeverity.WARNING),
        ])
        score = engine.evaluate(result)
        expected = 100.0 - (3 * DEFAULT_WARNING_DEDUCTION)
        assert score.overall_score == pytest.approx(expected)
        assert score.issue_count == 3
        assert score.warning_count == 3
    
    def test_multiple_issues_mixed_severity(self) -> None:
        engine = ConstraintScoreEngine()
        result = create_result_with_issues([
            create_issue(severity=ConstraintSeverity.WARNING),
            create_issue(severity=ConstraintSeverity.RECOMMENDATION),
            create_issue(severity=ConstraintSeverity.SUGGESTION),
        ])
        score = engine.evaluate(result)
        expected = 100.0 - (
            DEFAULT_WARNING_DEDUCTION
            + DEFAULT_RECOMMENDATION_DEDUCTION
            + DEFAULT_SUGGESTION_DEDUCTION
        )
        assert score.overall_score == pytest.approx(expected)
        assert score.issue_count == 3
    
    def test_score_clamped_to_zero(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [
            create_issue(severity=ConstraintSeverity.RECOMMENDATION)
            for _ in range(30)
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert score.overall_score == 0.0
        assert score.is_poor is True
    
    def test_score_clamped_to_100(self) -> None:
        engine = ConstraintScoreEngine()
        result = ConstraintResult.create()
        score = engine.evaluate(result)
        assert score.overall_score == 100.0
    
    def test_weighted_categories(self) -> None:
        engine = ConstraintScoreEngine()
        profile = ConstraintWeightProfile(
            building_code_weight=2.0,
            functional_weight=1.0,
        )
        
        issues = [
            create_issue(
                code="ROOM_AREA_BELOW_MINIMUM",
                severity=ConstraintSeverity.WARNING,
            ),
            create_issue(
                code="EMPTY_BUILDING",
                severity=ConstraintSeverity.WARNING,
            ),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result, weight_profile=profile)
        
        # Building code issue gets 2x weight
        # Functional issue gets 1x weight
        expected = 100.0 - (DEFAULT_WARNING_DEDUCTION * 2.0) - (DEFAULT_WARNING_DEDUCTION * 1.0)
        assert score.overall_score == pytest.approx(expected)
    
    def test_equal_weights_default(self) -> None:
        engine = ConstraintScoreEngine()
        profile = ConstraintWeightProfile.equal_weights()
        
        issues = [
            create_issue(code="ROOM_AREA_BELOW_MINIMUM", severity=ConstraintSeverity.WARNING),
            create_issue(code="EMPTY_BUILDING", severity=ConstraintSeverity.WARNING),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result, weight_profile=profile)
        
        expected = 100.0 - (2 * DEFAULT_WARNING_DEDUCTION)
        assert score.overall_score == pytest.approx(expected)
    
    def test_category_scores_populated(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [
            create_issue(code="ROOM_AREA_BELOW_MINIMUM", severity=ConstraintSeverity.WARNING),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert "building_code" in score.category_scores
    
    def test_engine_does_not_modify_result(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [create_issue(severity=ConstraintSeverity.WARNING)]
        result = create_result_with_issues(issues)
        original_count = result.issue_count
        
        engine.evaluate(result)
        
        assert result.issue_count == original_count
    
    def test_categorization_building_code(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [
            create_issue(code="ROOM_AREA_BELOW_MINIMUM"),
            create_issue(code="DOOR_WIDTH_BELOW_MINIMUM"),
            create_issue(code="WINDOW_AREA_BELOW_MINIMUM"),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert "building_code" in score.category_scores
    
    def test_categorization_accessibility(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [
            create_issue(code="DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM"),
            create_issue(code="HALLWAY_WIDTH_BELOW_MINIMUM"),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert "accessibility" in score.category_scores
    
    def test_categorization_functional(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [
            create_issue(code="EMPTY_BUILDING"),
            create_issue(code="ISOLATED_ROOM"),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert "functional" in score.category_scores
    
    def test_categorization_custom_fallback(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [
            create_issue(code="UNKNOWN_CODE"),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert "custom" in score.category_scores
    
    def test_perfect_score_properties(self) -> None:
        score = ConstraintScore.perfect()
        assert score.is_excellent is True
        assert score.is_good is True
        assert score.is_fair is True
        assert score.is_poor is False
    
    def test_poor_score_properties(self) -> None:
        score = ConstraintScore(overall_score=50.0)
        assert score.is_excellent is False
        assert score.is_good is False
        assert score.is_fair is False
        assert score.is_poor is True
    
    def test_fair_score_properties(self) -> None:
        score = ConstraintScore(overall_score=75.0)
        assert score.is_excellent is False
        assert score.is_good is False
        assert score.is_fair is True
        assert score.is_poor is False
    
    def test_good_score_properties(self) -> None:
        score = ConstraintScore(overall_score=90.0)
        assert score.is_excellent is False
        assert score.is_good is True
        assert score.is_fair is True
        assert score.is_poor is False
    
    def test_excellent_score_properties(self) -> None:
        score = ConstraintScore(overall_score=95.0)
        assert score.is_excellent is True
        assert score.is_good is True
        assert score.is_fair is True
        assert score.is_poor is False


# ============================================================================
# Serialization tests
# ============================================================================


class TestSerialization:
    """Tests for serialization compatibility."""
    
    def test_weight_profile_round_trip(self) -> None:
        profile = ConstraintWeightProfile(
            functional_weight=2.0,
            building_code_weight=1.5,
        )
        d = profile.to_dict()
        restored = ConstraintWeightProfile.from_dict(d)
        assert restored == profile
    
    def test_score_round_trip(self) -> None:
        score = ConstraintScore(
            overall_score=85.0,
            category_scores={"functional": 90.0},
            issue_count=2,
            warning_count=1,
        )
        d = score.to_dict()
        restored = ConstraintScore.from_dict(d)
        assert restored.overall_score == score.overall_score
        assert restored.issue_count == score.issue_count
    
    def test_score_to_dict_contains_all_fields(self) -> None:
        score = ConstraintScore(overall_score=85.0)
        d = score.to_dict()
        assert "overall_score" in d
        assert "maximum_score" in d
        assert "percentage" in d
        assert "category_scores" in d
        assert "issue_count" in d
        assert "recommendation_count" in d
        assert "warning_count" in d
        assert "suggestion_count" in d
        assert "is_excellent" in d
        assert "is_good" in d
        assert "is_fair" in d
        assert "is_poor" in d


# ============================================================================
# Edge case tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_zero_deductions(self) -> None:
        engine = ConstraintScoreEngine(
            info_deduction=0.0,
            suggestion_deduction=0.0,
            warning_deduction=0.0,
            recommendation_deduction=0.0,
        )
        issues = [
            create_issue(severity=ConstraintSeverity.WARNING),
            create_issue(severity=ConstraintSeverity.RECOMMENDATION),
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert score.overall_score == 100.0
    
    def test_very_large_deductions(self) -> None:
        engine = ConstraintScoreEngine(
            warning_deduction=100.0,
        )
        issues = [create_issue(severity=ConstraintSeverity.WARNING)]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert score.overall_score == 0.0
    
    def test_empty_issues_list(self) -> None:
        engine = ConstraintScoreEngine()
        result = ConstraintResult(issues=[])
        score = engine.evaluate(result)
        assert score.overall_score == 100.0
        assert score.issue_count == 0
    
    def test_many_issues_same_category(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [
            create_issue(severity=ConstraintSeverity.WARNING)
            for _ in range(10)
        ]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        expected = 100.0 - (10 * DEFAULT_WARNING_DEDUCTION)
        assert score.overall_score == pytest.approx(expected)
    
    def test_single_issue_at_boundary(self) -> None:
        engine = ConstraintScoreEngine()
        issues = [create_issue(severity=ConstraintSeverity.WARNING)]
        result = create_result_with_issues(issues)
        score = engine.evaluate(result)
        assert score.overall_score == pytest.approx(97.0)
        assert score.is_excellent is True
    
    def test_score_percentage_calculation(self) -> None:
        score = ConstraintScore(overall_score=50.0, maximum_score=100.0)
        assert score.percentage == 50.0
    
    def test_score_percentage_zero_max(self) -> None:
        score = ConstraintScore(overall_score=0.0, maximum_score=0.0)
        assert score.percentage == 0.0