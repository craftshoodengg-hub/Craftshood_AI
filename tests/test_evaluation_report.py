"""Unit tests for Evaluation Report."""

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
from building_model_v2.evaluation import (
    EvaluationPipeline,
    EvaluationPipelineConfig,
    EvaluationReport,
    EvaluationSummary,
)
from building_model_v2.validation import ValidationPipeline, ValidationResult
from building_model_v2.validation.validation_error import ValidationError
from building_model_v2.validation.validation_severity import ValidationSeverity
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType


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
    """Create a test constraint issue."""
    return ConstraintIssue(
        code=code,
        message=message,
        severity=severity,
        entity_id=entity_id,
        score=score,
    )


def create_validation_error(
    code: str = "TEST_ERROR",
    message: str = "Test error",
    severity: ValidationSeverity = ValidationSeverity.ERROR,
) -> ValidationError:
    """Create a test validation error."""
    return ValidationError(
        code=code,
        message=message,
        severity=severity,
    )


# ============================================================================
# EvaluationSummary tests
# ============================================================================


class TestEvaluationSummary:
    """Tests for EvaluationSummary."""
    
    def test_create(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore.perfect()
        
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        assert summary.overall_score == 100.0
        assert summary.is_valid is True
        assert summary.total_issues == 0
    
    def test_is_valid_with_errors(self) -> None:
        validation_result = ValidationResult(
            errors=[create_validation_error()],
        )
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore.perfect()
        
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        assert summary.is_valid is False
    
    def test_total_counts(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult(issues=[
            create_issue(severity=ConstraintSeverity.WARNING),
            create_issue(severity=ConstraintSeverity.RECOMMENDATION),
            create_issue(severity=ConstraintSeverity.SUGGESTION),
        ])
        constraint_score = ConstraintScore(overall_score=90.0)
        
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        assert summary.total_issues == 3
        assert summary.total_warnings == 1
        assert summary.total_recommendations == 1
        assert summary.total_suggestions == 1
    
    def test_to_dict(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore.perfect()
        
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        d = summary.to_dict()
        assert d["overall_score"] == 100.0
        assert d["is_valid"] is True
        assert "validation_summary" in d
        assert "constraint_summary" in d
        assert "score_summary" in d


# ============================================================================
# EvaluationReport tests
# ============================================================================


class TestEvaluationReport:
    """Tests for EvaluationReport."""
    
    def test_create(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore.perfect()
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert report.is_valid is True
        assert len(report.validation_errors) == 0
        assert len(report.constraint_issues) == 0
    
    def test_is_valid_with_errors(self) -> None:
        validation_result = ValidationResult(
            errors=[create_validation_error()],
        )
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore.perfect()
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert report.is_valid is False
    
    def test_is_buildable(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore.perfect()
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert report.is_buildable is True
    
    def test_design_quality_excellent(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore(overall_score=98.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert report.design_quality == "Excellent"
    
    def test_design_quality_good(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore(overall_score=90.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert report.design_quality == "Good"
    
    def test_design_quality_fair(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore(overall_score=75.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert report.design_quality == "Fair"
    
    def test_design_quality_poor(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore(overall_score=50.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert report.design_quality == "Poor"
    
    def test_improvement_opportunities(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult(issues=[
            create_issue(code="ROOM_AREA_BELOW_MINIMUM"),
            create_issue(code="DOOR_WIDTH_BELOW_MINIMUM"),
        ])
        constraint_score = ConstraintScore(overall_score=90.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert len(report.improvement_opportunities) == 2
        assert any("room area" in opp.lower() for opp in report.improvement_opportunities)
        assert any("door width" in opp.lower() for opp in report.improvement_opportunities)
    
    def test_highest_priority_issues(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult(issues=[
            create_issue(code="ROOM_AREA_BELOW_MINIMUM", severity=ConstraintSeverity.WARNING),
            create_issue(code="DOOR_WIDTH_BELOW_MINIMUM", severity=ConstraintSeverity.RECOMMENDATION),
            create_issue(code="WINDOW_AREA_BELOW_MINIMUM", severity=ConstraintSeverity.INFO),
        ])
        constraint_score = ConstraintScore(overall_score=90.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        # Only WARNING and RECOMMENDATION should be highest priority
        assert len(report.highest_priority_issues) == 2
    
    def test_to_dict(self) -> None:
        validation_result = ValidationResult()
        constraint_result = ConstraintResult()
        constraint_score = ConstraintScore.perfect()
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        d = report.to_dict()
        assert d["is_valid"] is True
        assert d["is_buildable"] is True
        assert d["design_quality"] == "Excellent"
        assert d["validation_error_count"] == 0
        assert d["constraint_issue_count"] == 0


# ============================================================================
# EvaluationPipeline tests
# ============================================================================


class TestEvaluationPipeline:
    """Tests for EvaluationPipeline."""
    
    def test_evaluate_empty_building(self) -> None:
        pipeline = EvaluationPipeline()
        model = BuildingModel()
        
        report = pipeline.evaluate(model)
        
        assert report.is_valid is True
        assert isinstance(report, EvaluationReport)
    
    def test_evaluate_with_rooms(self) -> None:
        pipeline = EvaluationPipeline()
        
        # Create a room and add to model
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        )
        model = BuildingModel(rooms={room.id: room})
        
        report = pipeline.evaluate(model)
        
        assert isinstance(report, EvaluationReport)
        assert report.design_quality in ("Excellent", "Good", "Fair", "Poor")
    
    def test_pipeline_properties(self) -> None:
        pipeline = EvaluationPipeline()
        
        assert pipeline.validation_pipeline is not None
        assert pipeline.constraint_engine is not None
        assert pipeline.score_engine is not None
    
    def test_pipeline_with_custom_config(self) -> None:
        config = EvaluationPipelineConfig(
            enable_all_constraints=True,
        )
        pipeline = EvaluationPipeline(config=config)
        
        model = BuildingModel()
        report = pipeline.evaluate(model)
        
        assert isinstance(report, EvaluationReport)
    
    def test_pipeline_with_weight_profile(self) -> None:
        weight_profile = ConstraintWeightProfile.prioritize_category(
            ConstraintCategory.ACCESSIBILITY,
            weight=2.0,
        )
        config = EvaluationPipelineConfig(
            weight_profile=weight_profile,
        )
        pipeline = EvaluationPipeline(config=config)
        
        model = BuildingModel()
        report = pipeline.evaluate(model)
        
        assert isinstance(report, EvaluationReport)
    
    def test_improvement_opportunities_deterministic(self) -> None:
        """Verify that improvement opportunities are deterministic."""
        pipeline = EvaluationPipeline()
        model = BuildingModel()
        
        report1 = pipeline.evaluate(model)
        report2 = pipeline.evaluate(model)
        
        assert report1.improvement_opportunities == report2.improvement_opportunities
    
    def test_serialization_round_trip(self) -> None:
        pipeline = EvaluationPipeline()
        model = BuildingModel()
        
        report = pipeline.evaluate(model)
        d = report.to_dict()
        
        assert "is_valid" in d
        assert "design_quality" in d
        assert "summary" in d


# ============================================================================
# Edge case tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_building_report(self) -> None:
        """Empty building should produce valid report."""
        pipeline = EvaluationPipeline()
        model = BuildingModel()
        
        report = pipeline.evaluate(model)
        
        assert isinstance(report, EvaluationReport)
        assert report.is_valid is True
    
    def test_perfect_building_report(self) -> None:
        """Building with no issues should have excellent quality."""
        pipeline = EvaluationPipeline()
        model = BuildingModel()
        
        report = pipeline.evaluate(model)
        
        # Empty building should be valid
        assert report.is_valid is True
    
    def test_report_with_many_issues(self) -> None:
        """Report should handle many issues correctly."""
        validation_result = ValidationResult()
        constraint_result = ConstraintResult(issues=[
            create_issue(code="ROOM_AREA_BELOW_MINIMUM", severity=ConstraintSeverity.WARNING),
            create_issue(code="DOOR_WIDTH_BELOW_MINIMUM", severity=ConstraintSeverity.WARNING),
            create_issue(code="WINDOW_AREA_BELOW_MINIMUM", severity=ConstraintSeverity.RECOMMENDATION),
        ])
        constraint_score = ConstraintScore(overall_score=85.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert len(report.constraint_issues) == 3
        assert len(report.improvement_opportunities) == 3
        assert report.design_quality == "Good"
    
    def test_improvement_opportunities_unknown_code(self) -> None:
        """Unknown issue codes should generate generic suggestion."""
        validation_result = ValidationResult()
        constraint_result = ConstraintResult(issues=[
            create_issue(code="UNKNOWN_CONSTRAINT_CODE"),
        ])
        constraint_score = ConstraintScore(overall_score=95.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        assert len(report.improvement_opportunities) == 1
        assert "UNKNOWN_CONSTRAINT_CODE" in report.improvement_opportunities[0]
    
    def test_multiple_same_issue_code_deduplicated(self) -> None:
        """Same issue code should only generate one suggestion."""
        validation_result = ValidationResult()
        constraint_result = ConstraintResult(issues=[
            create_issue(code="ROOM_AREA_BELOW_MINIMUM"),
            create_issue(code="ROOM_AREA_BELOW_MINIMUM"),
            create_issue(code="ROOM_AREA_BELOW_MINIMUM"),
        ])
        constraint_score = ConstraintScore(overall_score=85.0)
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        # Should only have one suggestion for ROOM_AREA_BELOW_MINIMUM
        room_area_suggestions = [
            opp for opp in report.improvement_opportunities
            if "room area" in opp.lower()
        ]
        assert len(room_area_suggestions) == 1
