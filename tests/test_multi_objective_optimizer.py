"""Unit tests for the Multi-Objective Optimization framework."""
from __future__ import annotations

import pytest

from building_model_v2.constraints.constraint_issue import ConstraintIssue
from building_model_v2.constraints.constraint_severity import ConstraintSeverity
from building_model_v2.evaluation.evaluation_report import EvaluationReport
from building_model_v2.optimization.multi_objective_optimizer import (
    MultiObjectiveOptimizer,
    SEVERITY_DEDUCTION,
)
from building_model_v2.optimization.objective_score import ObjectiveScore
from building_model_v2.optimization.optimization_objective import OptimizationObjective
from building_model_v2.optimization.optimization_profile import OptimizationProfile


class TestOptimizationObjective:
    """Tests for OptimizationObjective dataclass."""

    def test_create_objective(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1.5, enabled=True, description="Test objective")
        assert obj.name == "Test"
        assert obj.category == "functional"
        assert obj.weight == 1.5
        assert obj.enabled is True

    def test_default_values(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional")
        assert obj.weight == 1.0
        assert obj.enabled is True
        assert obj.description == ""

    def test_is_active_true(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1.0, enabled=True)
        assert obj.is_active is True

    def test_is_active_disabled(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1.0, enabled=False)
        assert obj.is_active is False

    def test_is_active_zero_weight(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=0.0, enabled=True)
        assert obj.is_active is False

    def test_normalized_weight_positive(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=2.5)
        assert obj.normalized_weight == 2.5

    def test_normalized_weight_negative(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=-1.0)
        assert obj.normalized_weight == 0.0

    def test_equality(self) -> None:
        obj1 = OptimizationObjective(name="Test", category="functional", weight=1.0)
        obj2 = OptimizationObjective(name="Test", category="functional", weight=1.0)
        assert obj1 == obj2

    def test_inequality_name(self) -> None:
        obj1 = OptimizationObjective(name="Test1", category="functional", weight=1.0)
        obj2 = OptimizationObjective(name="Test2", category="functional", weight=1.0)
        assert obj1 != obj2

    def test_hash(self) -> None:
        obj1 = OptimizationObjective(name="Test", category="functional", weight=1.0)
        obj2 = OptimizationObjective(name="Test", category="functional", weight=1.0)
        assert hash(obj1) == hash(obj2)

    def test_to_dict(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1.5)
        d = obj.to_dict()
        assert d["name"] == "Test"
        assert d["weight"] == 1.5
        assert d["enabled"] is True

    def test_from_dict(self) -> None:
        data = {"name": "Test", "category": "functional", "weight": 1.5, "enabled": True}
        obj = OptimizationObjective.from_dict(data)
        assert obj.name == "Test"
        assert obj.weight == 1.5

    def test_serialization_round_trip(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1.5)
        d = obj.to_dict()
        obj2 = OptimizationObjective.from_dict(d)
        assert obj == obj2

    def test_immutability(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1.0)
        with pytest.raises(AttributeError):
            obj.name = "NewName"

    def test_very_large_weight(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1000.0)
        assert obj.is_active is True
        assert obj.normalized_weight == 1000.0
    def test_very_large_weight(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1000.0)
        assert obj.is_active is True
        assert obj.normalized_weight == 1000.0


class TestObjectiveScore:
    """Tests for ObjectiveScore dataclass."""

    def test_create_score(self) -> None:
        score = ObjectiveScore(overall=85.0, weighted_score=90.0)
        assert score.overall == 85.0
        assert score.weighted_score == 90.0

    def test_default_values(self) -> None:
        score = ObjectiveScore()
        assert score.overall == 0.0
        assert score.weighted_score == 0.0
        assert score.category_scores == {}
        assert score.objective_breakdown == {}

    def test_percentage(self) -> None:
        score = ObjectiveScore(overall=85.0)
        assert score.percentage == 85.0

    def test_percentage_clamped_high(self) -> None:
        score = ObjectiveScore(overall=150.0)
        assert score.percentage == 100.0

    def test_percentage_clamped_low(self) -> None:
        score = ObjectiveScore(overall=-10.0)
        assert score.percentage == 0.0

    def test_best_category(self) -> None:
        score = ObjectiveScore(category_scores={"functional": 90.0, "building_code": 70.0})
        assert score.best_category == "functional"

    def test_best_category_empty(self) -> None:
        score = ObjectiveScore()
        assert score.best_category is None

    def test_worst_category(self) -> None:
        score = ObjectiveScore(category_scores={"functional": 90.0, "building_code": 70.0})
        assert score.worst_category == "building_code"

    def test_worst_category_empty(self) -> None:
        score = ObjectiveScore()
        assert score.worst_category is None

    def test_to_dict(self) -> None:
        score = ObjectiveScore(overall=85.0, weighted_score=90.0, category_scores={"functional": 90.0})
        d = score.to_dict()
        assert d["overall"] == 85.0
        assert d["weighted_score"] == 90.0
        assert d["category_scores"]["functional"] == 90.0

    def test_get_category_score(self) -> None:
        score = ObjectiveScore(category_scores={"functional": 90.0})
        assert score.get_category_score("functional") == 90.0
        assert score.get_category_score("nonexistent") == 0.0

    def test_get_objective_weight(self) -> None:
        score = ObjectiveScore(objective_breakdown={"Functional": 90.0})
        assert score.get_objective_weight("Functional") == 90.0
        assert score.get_objective_weight("Nonexistent") == 0.0

    def test_equality(self) -> None:
        score1 = ObjectiveScore(overall=85.0, weighted_score=90.0)
        score2 = ObjectiveScore(overall=85.0, weighted_score=90.0)
        assert score1 == score2

    def test_inequality(self) -> None:
        score1 = ObjectiveScore(overall=85.0)
        score2 = ObjectiveScore(overall=90.0)
        assert score1 != score2

    def test_hash(self) -> None:
        score1 = ObjectiveScore(overall=85.0, weighted_score=90.0)
        score2 = ObjectiveScore(overall=85.0, weighted_score=90.0)
        assert hash(score1) == hash(score2)

    def test_immutability(self) -> None:
        score = ObjectiveScore(overall=85.0)
        with pytest.raises(AttributeError):
            score.overall = 90.0
    def test_immutability(self) -> None:
        score = ObjectiveScore(overall=85.0)
        with pytest.raises(AttributeError):
            score.overall = 90.0


class TestOptimizationProfile:
    """Tests for OptimizationProfile dataclass."""

    def test_create_profile(self) -> None:
        obj = OptimizationObjective(name="Test", category="functional", weight=1.0)
        profile = OptimizationProfile(name="Test", description="Test profile", objectives=(obj,))
        assert profile.name == "Test"
        assert len(profile.objectives) == 1

    def test_default_values(self) -> None:
        profile = OptimizationProfile(name="Test")
        assert profile.description == ""
        assert profile.objectives == ()

    def test_balanced_profile(self) -> None:
        profile = OptimizationProfile.balanced()
        assert profile.name == "Balanced"
        assert len(profile.objectives) == 7
        assert profile.total_weight == 7.0

    def test_building_code_first_profile(self) -> None:
        profile = OptimizationProfile.building_code_first()
        assert profile.name == "Building Code First"
        bc_obj = profile.get_objective("building_code")
        assert bc_obj is not None
        assert bc_obj.weight == 3.0

    def test_accessibility_first_profile(self) -> None:
        profile = OptimizationProfile.accessibility_first()
        assert profile.name == "Accessibility First"
        assert len(profile.objectives) == 7

    def test_environmental_first_profile(self) -> None:
        profile = OptimizationProfile.environmental_first()
        assert profile.name == "Environmental First"
        assert len(profile.objectives) == 7

    def test_structural_first_profile(self) -> None:
        profile = OptimizationProfile.structural_first()
        assert profile.name == "Structural First"
        assert len(profile.objectives) == 7

    def test_vastu_first_profile(self) -> None:
        profile = OptimizationProfile.vastu_first()
        assert profile.name == "Vastu First"
        assert len(profile.objectives) == 7

    def test_high_performance_home_profile(self) -> None:
        profile = OptimizationProfile.high_performance_home()
        assert profile.name == "High Performance Home"
        assert len(profile.objectives) == 7

    def test_luxury_villa_profile(self) -> None:
        profile = OptimizationProfile.luxury_villa()
        assert profile.name == "Luxury Villa"
        assert len(profile.objectives) == 7

    def test_compact_house_profile(self) -> None:
        profile = OptimizationProfile.compact_house()
        assert profile.name == "Compact House"
        assert len(profile.objectives) == 7

    def test_custom_profile(self) -> None:
        profile = OptimizationProfile.custom("My Custom", "Test")
        assert profile.name == "My Custom"
        assert len(profile.objectives) == 7

    def test_get_objective(self) -> None:
        profile = OptimizationProfile.balanced()
        obj = profile.get_objective("functional")
        assert obj is not None
        assert obj.name == "Functional"

    def test_get_objective_not_found(self) -> None:
        profile = OptimizationProfile.balanced()
        assert profile.get_objective("nonexistent") is None

    def test_active_objectives(self) -> None:
        profile = OptimizationProfile.balanced()
        assert len(profile.active_objectives) == 7

    def test_normalized(self) -> None:
        profile = OptimizationProfile.balanced()
        normalized = profile.normalized()
        assert normalized.total_weight == pytest.approx(1.0)

    def test_to_dict(self) -> None:
        profile = OptimizationProfile.balanced()
        d = profile.to_dict()
        assert d["name"] == "Balanced"
        assert len(d["objectives"]) == 7

    def test_from_dict(self) -> None:
        profile = OptimizationProfile.balanced()
        d = profile.to_dict()
        profile2 = OptimizationProfile.from_dict(d)
        assert profile == profile2

    def test_equality(self) -> None:
        p1 = OptimizationProfile.balanced()
        p2 = OptimizationProfile.balanced()
        assert p1 == p2

    def test_inequality(self) -> None:
        p1 = OptimizationProfile.balanced()
        p2 = OptimizationProfile.building_code_first()
        assert p1 != p2

    def test_hash(self) -> None:
        p1 = OptimizationProfile.balanced()
        p2 = OptimizationProfile.balanced()
        assert hash(p1) == hash(p2)

    def test_immutability(self) -> None:
        profile = OptimizationProfile.balanced()
        with pytest.raises(AttributeError):
            profile.name = "NewName"


class TestMultiObjectiveOptimizer:
    """Tests for MultiObjectiveOptimizer class."""

    def test_create_optimizer(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        assert optimizer is not None

    def test_empty_report(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(summary=None, constraint_issues=[], validation_errors=[])
        score = optimizer.evaluate(report, profile)
        assert score.overall == 100.0

    def test_empty_profile(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile(name="Empty")
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING)
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.overall == 0.0

    def test_single_issue(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING)
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["building_code"] == 97.0

    def test_multiple_issues_same_category(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
                ConstraintIssue(code="DOOR_WIDTH_BELOW_MIN", message="Test", severity=ConstraintSeverity.RECOMMENDATION),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["building_code"] == 92.0

    def test_issues_different_categories(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
                ConstraintIssue(code="NATURAL_LIGHT_INSUFFICIENT", message="Test", severity=ConstraintSeverity.SUGGESTION),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["building_code"] == 97.0
        assert score.category_scores["environmental"] == 99.0

    def test_deterministic_behavior(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score1 = optimizer.evaluate(report, profile)
        score2 = optimizer.evaluate(report, profile)
        assert score1 == score2

    def test_no_mutation(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        issues = [
            ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
        ]
        report = EvaluationReport(summary=None, constraint_issues=issues)
        original_issues = list(report.constraint_issues)
        optimizer.evaluate(report, profile)
        optimizer.evaluate(report, profile)
        assert list(report.constraint_issues) == original_issues

    def test_weighted_scoring(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.building_code_first()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.overall < 100.0

    def test_best_and_worst_category(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.worst_category == "building_code"

    def test_objective_breakdown(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert "Building Code" in score.objective_breakdown

    def test_severity_deductions(self) -> None:
        assert SEVERITY_DEDUCTION[ConstraintSeverity.INFO] == 0.5
        assert SEVERITY_DEDUCTION[ConstraintSeverity.SUGGESTION] == 1.0
        assert SEVERITY_DEDUCTION[ConstraintSeverity.WARNING] == 3.0
        assert SEVERITY_DEDUCTION[ConstraintSeverity.RECOMMENDATION] == 5.0

    def test_score_clamping(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        issues = [
            ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.RECOMMENDATION)
            for _ in range(100)
        ]
        report = EvaluationReport(summary=None, constraint_issues=issues)
        score = optimizer.evaluate(report, profile)
        assert 0.0 <= score.overall <= 100.0

    def test_unknown_category_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="UNKNOWN_CODE", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.overall == 100.0

    def test_functional_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="EMPTY_BUILDING", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["functional"] == 97.0

    def test_accessibility_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="HALLWAY_WIDTH_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["accessibility"] == 97.0

    def test_environmental_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="NATURAL_LIGHT_INSUFFICIENT", message="Test", severity=ConstraintSeverity.SUGGESTION),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["environmental"] == 99.0

    def test_structural_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="WALL_SPAN_EXCEEDS_MAX", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["structural"] == 97.0

    def test_vastu_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="VASTU_NORTH_ENTRANCE", message="Test", severity=ConstraintSeverity.SUGGESTION),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["vastu"] == 99.0

    def test_repeated_evaluation(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        scores = [optimizer.evaluate(report, profile) for _ in range(10)]
        assert all(s == scores[0] for s in scores)

    def test_different_profiles_different_scores(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        bc_first_score = optimizer.evaluate(report, OptimizationProfile.building_code_first())
        assert balanced_score.overall != bc_first_score.overall

    def test_to_dict(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        d = score.to_dict()
        assert "overall" in d
        assert "category_scores" in d
        assert "overall" in d
        assert "category_scores" in d
        assert "overall" in d
        assert "category_scores" in d
        assert "objective_breakdown" in d

    def test_all_objectives_disabled(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        disabled_obj = OptimizationObjective(name="Disabled", category="functional", enabled=False, weight=1.0)
        profile = OptimizationProfile(name="Disabled", objectives=(disabled_obj,))
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.overall == 0.0

    def test_all_weights_zero(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        zero_obj = OptimizationObjective(name="Zero", category="functional", weight=0.0)
        profile = OptimizationProfile(name="Zero", objectives=(zero_obj,))
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.overall == 0.0

    def test_duplicated_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        issues = [
            ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
        ]
        report = EvaluationReport(summary=None, constraint_issues=issues)
        score = optimizer.evaluate(report, profile)
        assert 0.0 <= score.overall <= 100.0

    def test_mixed_severity_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        issues = [
            ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Info", severity=ConstraintSeverity.INFO),
            ConstraintIssue(code="DOOR_WIDTH_BELOW_MIN", message="Suggestion", severity=ConstraintSeverity.SUGGESTION),
            ConstraintIssue(code="STAIR_WIDTH_BELOW_MIN", message="Warning", severity=ConstraintSeverity.WARNING),
            ConstraintIssue(code="CEILING_HEIGHT_BELOW_MIN", message="Recommendation", severity=ConstraintSeverity.RECOMMENDATION),
        ]
        report = EvaluationReport(summary=None, constraint_issues=issues)
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["building_code"] == 90.5

    def test_empty_objectives_with_issues(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile(name="Empty")
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.overall == 0.0
        assert score.category_scores == {}

    def test_profile_with_custom_objective(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        custom_obj = OptimizationObjective(name="Custom", category="custom", weight=2.0)
        profile = OptimizationProfile(name="Custom", objectives=(custom_obj,))
        report = EvaluationReport(summary=None, constraint_issues=[])
        score = optimizer.evaluate(report, profile)
        assert score.overall == 100.0

    def test_negative_weight_handled(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        neg_obj = OptimizationObjective(name="Neg", category="functional", weight=-1.0)
        profile = OptimizationProfile(name="Neg", objectives=(neg_obj,))
        report = EvaluationReport(summary=None, constraint_issues=[])
        score = optimizer.evaluate(report, profile)
        assert score.overall == 0.0

    def test_percentage_property(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert 0.0 <= score.percentage <= 100.0

    def test_get_category_score_helper(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert score.get_category_score("building_code") == 97.0
        assert score.get_category_score("nonexistent") == 0.0

    def test_serialization_round_trip_with_data(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        d = score.to_dict()
        assert d["overall"] == score.overall
        assert "building_code" in d["category_scores"]

    def test_all_severities_in_one_category(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        issues = [
            ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Info", severity=ConstraintSeverity.INFO),
            ConstraintIssue(code="ROOM_AREA_SMALL", message="Suggestion", severity=ConstraintSeverity.SUGGESTION),
            ConstraintIssue(code="ROOM_AREA_WARNING", message="Warning", severity=ConstraintSeverity.WARNING),
            ConstraintIssue(code="ROOM_AREA_RECOMMENDATION", message="Recommendation", severity=ConstraintSeverity.RECOMMENDATION),
        ]
        report = EvaluationReport(summary=None, constraint_issues=issues)
        score = optimizer.evaluate(report, profile)
        assert score.category_scores["building_code"] == 90.5

    def test_profile_normalization(self) -> None:
        profile = OptimizationProfile.building_code_first()
        normalized = profile.normalized()
        assert normalized.total_weight == pytest.approx(1.0)
        bc_obj = normalized.get_objective("building_code")
        assert bc_obj is not None
        assert bc_obj.weight > 0.4

    def test_multiple_evaluations_no_accumulation(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        scores = [optimizer.evaluate(report, profile) for _ in range(100)]
        assert all(s.overall == scores[0].overall for s in scores)

    def test_very_large_issue_list(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        issues = [
            ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING)
            for _ in range(1000)
        ]
        report = EvaluationReport(summary=None, constraint_issues=issues)
        score = optimizer.evaluate(report, profile)
        assert 0.0 <= score.overall <= 100.0

    def test_get_objective_weight_helper(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert "Building Code" in score.objective_breakdown
        assert score.get_objective_weight("Building Code") > 0.0

    def test_different_profiles_different_scores(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        bc_first_score = optimizer.evaluate(report, OptimizationProfile.building_code_first())
        assert balanced_score.overall != bc_first_score.overall

    def test_environmental_first_profile_scoring(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="NATURAL_LIGHT_INSUFFICIENT", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        env_score = optimizer.evaluate(report, OptimizationProfile.environmental_first())
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        assert env_score.overall != balanced_score.overall

    def test_structural_first_profile_scoring(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="WALL_SPAN_EXCEEDS_MAX", message="Test", severity=ConstraintSeverity.WARNING),
            ]
        )
        struct_score = optimizer.evaluate(report, OptimizationProfile.structural_first())
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        assert struct_score.overall != balanced_score.overall

    def test_vastu_first_profile_scoring(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="VASTU_NORTH_ENTRANCE", message="Test", severity=ConstraintSeverity.SUGGESTION),
            ],
        )
        vastu_score = optimizer.evaluate(report, OptimizationProfile.vastu_first())
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        assert vastu_score.overall != balanced_score.overall

    def test_high_performance_home_profile(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="NATURAL_LIGHT_INSUFFICIENT", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        hph_score = optimizer.evaluate(report, OptimizationProfile.high_performance_home())
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        assert hph_score.overall != balanced_score.overall

    def test_luxury_villa_profile(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="EMPTY_BUILDING", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        lv_score = optimizer.evaluate(report, OptimizationProfile.luxury_villa())
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        assert lv_score.overall != balanced_score.overall

    def test_compact_house_profile(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        ch_score = optimizer.evaluate(report, OptimizationProfile.compact_house())
        balanced_score = optimizer.evaluate(report, OptimizationProfile.balanced())
        assert ch_score.overall != balanced_score.overall

    def test_custom_profile_with_objectives(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        custom_obj = OptimizationObjective(name="MyObj", category="custom", weight=5.0)
        profile = OptimizationProfile.custom("Custom", objectives=[custom_obj])
        report = EvaluationReport(summary=None, constraint_issues=[])
        score = optimizer.evaluate(report, profile)
        assert score.overall == 100.0

    def test_profile_with_disabled_objective(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        disabled_obj = OptimizationObjective(name="Disabled", category="building_code", weight=3.0, enabled=False)
        enabled_obj = OptimizationObjective(name="Enabled", category="functional", weight=1.0, enabled=True)
        profile = OptimizationProfile(name="Mixed", objectives=(disabled_obj, enabled_obj))
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        assert "building_code" not in score.category_scores

    def test_all_categories_have_objectives(self) -> None:
        profile = OptimizationProfile.balanced()
        categories = {obj.category for obj in profile.objectives}
        assert "functional" in categories
        assert "building_code" in categories
        assert "accessibility" in categories
        assert "environmental" in categories
        assert "structural" in categories
        assert "vastu" in categories
        assert "custom" in categories

    def test_normalized_weights_sum_to_one(self) -> None:
        profiles = [
            OptimizationProfile.balanced(),
            OptimizationProfile.building_code_first(),
            OptimizationProfile.accessibility_first(),
            OptimizationProfile.environmental_first(),
            OptimizationProfile.structural_first(),
            OptimizationProfile.vastu_first(),
        ]
        for profile in profiles:
            normalized = profile.normalized()
            assert normalized.total_weight == pytest.approx(1.0)

    def test_empty_report_all_profiles(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        report = EvaluationReport(summary=None, constraint_issues=[], validation_errors=[])
        profiles = [
            OptimizationProfile.balanced(),
            OptimizationProfile.building_code_first(),
            OptimizationProfile.accessibility_first(),
            OptimizationProfile.high_performance_home(),
            OptimizationProfile.luxury_villa(),
            OptimizationProfile.compact_house(),
        ]
        for profile in profiles:
            score = optimizer.evaluate(report, profile)
            assert score.overall == 100.0

    def test_score_to_dict_contains_all_fields(self) -> None:
        optimizer = MultiObjectiveOptimizer()
        profile = OptimizationProfile.balanced()
        report = EvaluationReport(
            summary=None,
            constraint_issues=[
                ConstraintIssue(code="ROOM_AREA_BELOW_MIN", message="Test", severity=ConstraintSeverity.WARNING),
            ],
        )
        score = optimizer.evaluate(report, profile)
        d = score.to_dict()
        assert "overall" in d
        assert "category_scores" in d
        assert "weighted_score" in d
        assert "objective_breakdown" in d
        assert "percentage" in d
        assert "best_category" in d
        assert "worst_category" in d
        assert score.get_category_score("nonexistent") == 0.0
        assert "objective_breakdown" in d


