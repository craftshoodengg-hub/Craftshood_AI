"""Unit tests for Constraint Framework."""

from __future__ import annotations

import pytest

from building_model_v2.constraints import (
    Constraint,
    ConstraintEngine,
    ConstraintIssue,
    ConstraintResult,
    ConstraintSeverity,
)
from building_model_v2.validation.cross_entity_validator import BuildingModel


# ============================================================================
# ConstraintSeverity tests
# ============================================================================


class TestConstraintSeverity:
    """Tests for ConstraintSeverity enum."""
    
    def test_enum_values(self) -> None:
        assert ConstraintSeverity.INFO.value == "info"
        assert ConstraintSeverity.SUGGESTION.value == "suggestion"
        assert ConstraintSeverity.WARNING.value == "warning"
        assert ConstraintSeverity.RECOMMENDATION.value == "recommendation"
    
    def test_str_representation(self) -> None:
        assert str(ConstraintSeverity.INFO) == "info"
        assert str(ConstraintSeverity.SUGGESTION) == "suggestion"
        assert str(ConstraintSeverity.WARNING) == "warning"
        assert str(ConstraintSeverity.RECOMMENDATION) == "recommendation"
    
    def test_repr_representation(self) -> None:
        assert repr(ConstraintSeverity.INFO) == "ConstraintSeverity.INFO"
        assert repr(ConstraintSeverity.RECOMMENDATION) == "ConstraintSeverity.RECOMMENDATION"
    
    def test_ordering(self) -> None:
        assert ConstraintSeverity.INFO < ConstraintSeverity.SUGGESTION
        assert ConstraintSeverity.SUGGESTION < ConstraintSeverity.WARNING
        assert ConstraintSeverity.WARNING < ConstraintSeverity.RECOMMENDATION
    
    def test_ordering_le(self) -> None:
        assert ConstraintSeverity.INFO <= ConstraintSeverity.INFO
        assert ConstraintSeverity.INFO <= ConstraintSeverity.WARNING
        assert not ConstraintSeverity.WARNING <= ConstraintSeverity.INFO
    
    def test_ordering_gt(self) -> None:
        assert ConstraintSeverity.RECOMMENDATION > ConstraintSeverity.WARNING
        assert ConstraintSeverity.WARNING > ConstraintSeverity.SUGGESTION
        assert not ConstraintSeverity.INFO > ConstraintSeverity.WARNING
    
    def test_ordering_ge(self) -> None:
        assert ConstraintSeverity.WARNING >= ConstraintSeverity.WARNING
        assert ConstraintSeverity.RECOMMENDATION >= ConstraintSeverity.WARNING
        assert not ConstraintSeverity.SUGGESTION >= ConstraintSeverity.WARNING
    
    def test_is_info(self) -> None:
        assert ConstraintSeverity.INFO.is_info is True
        assert ConstraintSeverity.WARNING.is_info is False
    
    def test_is_suggestion(self) -> None:
        assert ConstraintSeverity.SUGGESTION.is_suggestion is True
        assert ConstraintSeverity.WARNING.is_suggestion is False
    
    def test_is_warning(self) -> None:
        assert ConstraintSeverity.WARNING.is_warning is True
        assert ConstraintSeverity.INFO.is_warning is False
    
    def test_is_recommendation(self) -> None:
        assert ConstraintSeverity.RECOMMENDATION.is_recommendation is True
        assert ConstraintSeverity.WARNING.is_recommendation is False


# ============================================================================
# ConstraintIssue tests
# ============================================================================


class TestConstraintIssue:
    """Tests for ConstraintIssue."""
    
    def test_create_issue(self) -> None:
        issue = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        assert issue.code == "TEST_001"
        assert issue.message == "Test issue"
        assert issue.severity == ConstraintSeverity.WARNING
        assert issue.entity_id is None
        assert issue.entity_type is None
        assert issue.location is None
        assert issue.score == 0.0
        assert issue.metadata == {}
    
    def test_create_issue_with_all_fields(self) -> None:
        issue = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.RECOMMENDATION,
            entity_id="entity-1",
            entity_type="Room",
            location="Floor 1",
            score=0.5,
            metadata={"key": "value"},
        )
        assert issue.code == "TEST_001"
        assert issue.entity_id == "entity-1"
        assert issue.entity_type == "Room"
        assert issue.location == "Floor 1"
        assert issue.score == 0.5
        assert issue.metadata == {"key": "value"}
    
    def test_to_dict(self) -> None:
        issue = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
            entity_id="entity-1",
            score=0.5,
        )
        d = issue.to_dict()
        assert d["code"] == "TEST_001"
        assert d["message"] == "Test issue"
        assert d["severity"] == "warning"
        assert d["entity_id"] == "entity-1"
        assert d["score"] == 0.5
    
    def test_from_dict(self) -> None:
        data = {
            "code": "TEST_001",
            "message": "Test issue",
            "severity": "warning",
            "entity_id": "entity-1",
            "score": 0.5,
        }
        issue = ConstraintIssue.from_dict(data)
        assert issue.code == "TEST_001"
        assert issue.message == "Test issue"
        assert issue.severity == ConstraintSeverity.WARNING
        assert issue.entity_id == "entity-1"
        assert issue.score == 0.5
    
    def test_equality(self) -> None:
        issue1 = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        issue2 = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        assert issue1 == issue2
    
    def test_inequality(self) -> None:
        issue1 = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        issue2 = ConstraintIssue(
            code="TEST_002",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        assert issue1 != issue2
    
    def test_hash(self) -> None:
        issue1 = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        issue2 = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        assert hash(issue1) == hash(issue2)
    
    def test_frozen(self) -> None:
        issue = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        with pytest.raises(AttributeError):
            issue.code = "TEST_002"


# ============================================================================
# ConstraintResult tests
# ============================================================================


class TestConstraintResult:
    """Tests for ConstraintResult."""
    
    def test_create_empty(self) -> None:
        result = ConstraintResult.create()
        assert result.is_optimal is True
        assert result.issue_count == 0
        assert result.recommendation_count == 0
        assert result.warning_count == 0
        assert result.suggestion_count == 0
        assert result.info_count == 0
        assert result.total_score == 0.0
    
    def test_add_issue(self) -> None:
        result = ConstraintResult.create()
        issue = ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        )
        result.add_issue(issue)
        assert result.is_optimal is False
        assert result.issue_count == 1
        assert result.warning_count == 1
    
    def test_add_multiple_issues(self) -> None:
        result = ConstraintResult.create()
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Info",
            severity=ConstraintSeverity.INFO,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_002",
            message="Suggestion",
            severity=ConstraintSeverity.SUGGESTION,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_003",
            message="Warning",
            severity=ConstraintSeverity.WARNING,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_004",
            message="Recommendation",
            severity=ConstraintSeverity.RECOMMENDATION,
        ))
        assert result.issue_count == 4
        assert result.info_count == 1
        assert result.suggestion_count == 1
        assert result.warning_count == 1
        assert result.recommendation_count == 1
    
    def test_total_score(self) -> None:
        result = ConstraintResult.create()
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Issue 1",
            severity=ConstraintSeverity.WARNING,
            score=0.3,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_002",
            message="Issue 2",
            severity=ConstraintSeverity.WARNING,
            score=0.5,
        ))
        assert result.total_score == 0.8
    
    def test_merge(self) -> None:
        result1 = ConstraintResult.create()
        result1.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Issue 1",
            severity=ConstraintSeverity.WARNING,
        ))
        result2 = ConstraintResult.create()
        result2.add_issue(ConstraintIssue(
            code="TEST_002",
            message="Issue 2",
            severity=ConstraintSeverity.RECOMMENDATION,
        ))
        merged = result1.merge(result2)
        assert merged.issue_count == 2
        assert merged.warning_count == 1
        assert merged.recommendation_count == 1
    
    def test_get_issues_by_severity(self) -> None:
        result = ConstraintResult.create()
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Warning 1",
            severity=ConstraintSeverity.WARNING,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_002",
            message="Warning 2",
            severity=ConstraintSeverity.WARNING,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_003",
            message="Info",
            severity=ConstraintSeverity.INFO,
        ))
        warnings = result.get_issues_by_severity(ConstraintSeverity.WARNING)
        assert len(warnings) == 2
    
    def test_get_issues_by_code(self) -> None:
        result = ConstraintResult.create()
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Issue 1",
            severity=ConstraintSeverity.WARNING,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Issue 2",
            severity=ConstraintSeverity.WARNING,
        ))
        result.add_issue(ConstraintIssue(
            code="TEST_002",
            message="Issue 3",
            severity=ConstraintSeverity.INFO,
        ))
        issues = result.get_issues_by_code("TEST_001")
        assert len(issues) == 2
    
    def test_to_dict(self) -> None:
        result = ConstraintResult.create()
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Test issue",
            severity=ConstraintSeverity.WARNING,
        ))
        d = result.to_dict()
        assert d["is_optimal"] is False
        assert d["issue_count"] == 1
        assert d["warning_count"] == 1
        assert len(d["issues"]) == 1
    
    def test_from_dict(self) -> None:
        data = {
            "is_optimal": False,
            "issue_count": 1,
            "issues": [
                {
                    "code": "TEST_001",
                    "message": "Test issue",
                    "severity": "warning",
                }
            ],
        }
        result = ConstraintResult.from_dict(data)
        assert result.is_optimal is False
        assert result.issue_count == 1
        assert result.issues[0].code == "TEST_001"
    
    def test_from_issues(self) -> None:
        issues = [
            ConstraintIssue(
                code="TEST_001",
                message="Issue 1",
                severity=ConstraintSeverity.WARNING,
            ),
            ConstraintIssue(
                code="TEST_002",
                message="Issue 2",
                severity=ConstraintSeverity.INFO,
            ),
        ]
        result = ConstraintResult.from_issues(issues)
        assert result.issue_count == 2
    
    def test_equality(self) -> None:
        result1 = ConstraintResult.create()
        result2 = ConstraintResult.create()
        assert result1 == result2
    
    def test_bool_true(self) -> None:
        result = ConstraintResult.create()
        assert bool(result) is True
    
    def test_bool_false(self) -> None:
        result = ConstraintResult.create()
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Issue",
            severity=ConstraintSeverity.WARNING,
        ))
        assert bool(result) is False
    
    def test_str_representation(self) -> None:
        result = ConstraintResult.create()
        result.add_issue(ConstraintIssue(
            code="TEST_001",
            message="Issue",
            severity=ConstraintSeverity.WARNING,
        ))
        s = str(result)
        "ConstraintResult" in s
        "issues=1" in s


# ============================================================================
# Constraint tests
# ============================================================================


class TestConstraint:
    """Tests for Constraint abstract base class."""
    
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            Constraint(name="Test")
    
    def test_concrete_implementation(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        constraint = TestConstraint(name="Test Constraint")
        assert constraint.name == "Test Constraint"
        assert constraint.description == ""
    
    def test_concrete_with_description(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        constraint = TestConstraint(
            name="Test Constraint",
            description="A test constraint",
        )
        assert constraint.name == "Test Constraint"
        assert constraint.description == "A test constraint"
    
    def test_repr(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        constraint = TestConstraint(name="Test")
        assert repr(constraint) == "TestConstraint(name='Test')"
    
    def test_str(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        constraint = TestConstraint(name="Test Constraint")
        assert str(constraint) == "Test Constraint"


# ============================================================================
# ConstraintEngine tests
# ============================================================================


class TestConstraintEngine:
    """Tests for ConstraintEngine."""
    
    def test_create_empty(self) -> None:
        engine = ConstraintEngine()
        assert engine.constraint_count == 0
        assert engine.constraints == []
    
    def test_create_with_constraints(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        constraint = TestConstraint(name="Test")
        engine = ConstraintEngine(constraints=[constraint])
        assert engine.constraint_count == 1
    
    def test_register(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        engine = ConstraintEngine()
        constraint = TestConstraint(name="Test")
        engine.register(constraint)
        assert engine.constraint_count == 1
    
    def test_unregister(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        engine = ConstraintEngine()
        constraint = TestConstraint(name="Test")
        engine.register(constraint)
        assert engine.unregister(constraint) is True
        assert engine.constraint_count == 0
    
    def test_unregister_not_found(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        engine = ConstraintEngine()
        constraint = TestConstraint(name="Test")
        assert engine.unregister(constraint) is False
    
    def test_clear(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        engine = ConstraintEngine()
        engine.register(TestConstraint(name="Test1"))
        engine.register(TestConstraint(name="Test2"))
        engine.clear()
        assert engine.constraint_count == 0
    
    def test_evaluate_empty(self) -> None:
        engine = ConstraintEngine()
        model = BuildingModel()
        result = engine.evaluate(model)
        assert result.is_optimal is True
    
    def test_evaluate_with_constraint(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                result = ConstraintResult.create()
                result.add_issue(ConstraintIssue(
                    code="TEST_001",
                    message="Test issue",
                    severity=ConstraintSeverity.WARNING,
                ))
                return result
        
        engine = ConstraintEngine()
        engine.register(TestConstraint(name="Test"))
        model = BuildingModel()
        result = engine.evaluate(model)
        assert result.issue_count == 1
        assert result.warning_count == 1
    
    def test_evaluate_multiple_constraints(self) -> None:
        class Constraint1(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                result = ConstraintResult.create()
                result.add_issue(ConstraintIssue(
                    code="TEST_001",
                    message="Issue 1",
                    severity=ConstraintSeverity.WARNING,
                ))
                return result
        
        class Constraint2(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                result = ConstraintResult.create()
                result.add_issue(ConstraintIssue(
                    code="TEST_002",
                    message="Issue 2",
                    severity=ConstraintSeverity.RECOMMENDATION,
                ))
                return result
        
        engine = ConstraintEngine()
        engine.register(Constraint1(name="Test1"))
        engine.register(Constraint2(name="Test2"))
        model = BuildingModel()
        result = engine.evaluate(model)
        assert result.issue_count == 2
        assert result.warning_count == 1
        assert result.recommendation_count == 1
    
    def test_repr(self) -> None:
        engine = ConstraintEngine()
        assert repr(engine) == "ConstraintEngine(constraints=0)"
    
    def test_str(self) -> None:
        engine = ConstraintEngine()
        assert str(engine) == "ConstraintEngine(0 constraints)"
    
    def test_constraints_returns_copy(self) -> None:
        class TestConstraint(Constraint):
            def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
                return ConstraintResult.create()
        
        engine = ConstraintEngine()
        constraint = TestConstraint(name="Test")
        engine.register(constraint)
        
        constraints = engine.constraints
        constraints.clear()
        
        assert engine.constraint_count == 1


# ============================================================================
# Edge case tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_issue_with_empty_metadata(self) -> None:
        issue = ConstraintIssue(
            code="TEST",
            message="Test",
            severity=ConstraintSeverity.INFO,
        )
        assert issue.metadata == {}
    
    def test_issue_metadata_mutable(self) -> None:
        """Metadata is a regular dict, not frozen."""
        issue = ConstraintIssue(
            code="TEST",
            message="Test",
            severity=ConstraintSeverity.INFO,
            metadata={"key": "value"},
        )
        # Metadata is mutable (regular dict)
        issue.metadata["key"] = "new_value"
        assert issue.metadata["key"] == "new_value"
    
    def test_result_from_empty_issues(self) -> None:
        result = ConstraintResult.from_issues([])
        assert result.is_optimal is True
    
    def test_merge_empty_results(self) -> None:
        result1 = ConstraintResult.create()
        result2 = ConstraintResult.create()
        merged = result1.merge(result2)
        assert merged.is_optimal is True
    
    def test_merge_with_empty(self) -> None:
        result1 = ConstraintResult.create()
        result1.add_issue(ConstraintIssue(
            code="TEST",
            message="Test",
            severity=ConstraintSeverity.WARNING,
        ))
        result2 = ConstraintResult.create()
        merged = result1.merge(result2)
        assert merged.issue_count == 1
    
    def test_issue_with_zero_score(self) -> None:
        issue = ConstraintIssue(
            code="TEST",
            message="Test",
            severity=ConstraintSeverity.INFO,
            score=0.0,
        )
        assert issue.score == 0.0
    
    def test_issue_with_max_score(self) -> None:
        issue = ConstraintIssue(
            code="TEST",
            message="Test",
            severity=ConstraintSeverity.INFO,
            score=1.0,
        )
        assert issue.score == 1.0
    
    def test_severity_comparison_with_different_types(self) -> None:
        """Comparing severity with non-severity raises KeyError."""
        with pytest.raises((TypeError, KeyError)):
            ConstraintSeverity.INFO < 1
