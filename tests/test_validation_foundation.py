"""Unit tests for validation engine foundation."""

from __future__ import annotations

import pytest

from building_model_v2.validation import (
    ValidationError,
    ValidationResult,
    ValidationSeverity,
    Validator,
)


class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""
    
    def test_enum_values(self) -> None:
        assert ValidationSeverity.INFO.value == "info"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.CRITICAL.value == "critical"
    
    def test_str_representation(self) -> None:
        assert str(ValidationSeverity.INFO) == "info"
        assert str(ValidationSeverity.WARNING) == "warning"
        assert str(ValidationSeverity.ERROR) == "error"
        assert str(ValidationSeverity.CRITICAL) == "critical"
    
    def test_repr_representation(self) -> None:
        assert repr(ValidationSeverity.INFO) == "ValidationSeverity.INFO"
        assert repr(ValidationSeverity.WARNING) == "ValidationSeverity.WARNING"
        assert repr(ValidationSeverity.ERROR) == "ValidationSeverity.ERROR"
        assert repr(ValidationSeverity.CRITICAL) == "ValidationSeverity.CRITICAL"
    
    def test_comparison_operators(self) -> None:
        assert ValidationSeverity.INFO < ValidationSeverity.WARNING
        assert ValidationSeverity.WARNING < ValidationSeverity.ERROR
        assert ValidationSeverity.ERROR < ValidationSeverity.CRITICAL
        assert ValidationSeverity.INFO <= ValidationSeverity.INFO
        assert ValidationSeverity.CRITICAL > ValidationSeverity.ERROR
        assert ValidationSeverity.WARNING >= ValidationSeverity.WARNING
    
    def test_is_error_property(self) -> None:
        assert ValidationSeverity.INFO.is_error is False
        assert ValidationSeverity.WARNING.is_error is False
        assert ValidationSeverity.ERROR.is_error is True
        assert ValidationSeverity.CRITICAL.is_error is True
    
    def test_is_warning_property(self) -> None:
        assert ValidationSeverity.INFO.is_warning is False
        assert ValidationSeverity.WARNING.is_warning is True
        assert ValidationSeverity.ERROR.is_warning is False
        assert ValidationSeverity.CRITICAL.is_warning is False
    
    def test_is_info_property(self) -> None:
        assert ValidationSeverity.INFO.is_info is True
        assert ValidationSeverity.WARNING.is_info is False
        assert ValidationSeverity.ERROR.is_info is False
        assert ValidationSeverity.CRITICAL.is_info is False
    
    def test_from_value(self) -> None:
        assert ValidationSeverity("info") == ValidationSeverity.INFO
        assert ValidationSeverity("warning") == ValidationSeverity.WARNING
        assert ValidationSeverity("error") == ValidationSeverity.ERROR
        assert ValidationSeverity("critical") == ValidationSeverity.CRITICAL
    
    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            ValidationSeverity("invalid")


class TestValidationError:
    """Tests for ValidationError dataclass."""
    
    def test_create_with_required_fields(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        assert error.code == "TEST_001"
        assert error.message == "Test error"
        assert error.severity == ValidationSeverity.ERROR
        assert error.entity_id is None
        assert error.entity_type is None
        assert error.location is None
        assert error.metadata == {}
    
    def test_create_with_all_fields(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
            entity_id="entity-123",
            entity_type="Room",
            location="x:10,y:20",
            metadata={"key": "value"},
        )
        assert error.entity_id == "entity-123"
        assert error.entity_type == "Room"
        assert error.location == "x:10,y:20"
        assert error.metadata == {"key": "value"}
    
    def test_empty_code_raises(self) -> None:
        with pytest.raises(ValueError, match="code cannot be empty"):
            ValidationError(
                code="",
                message="Test",
                severity=ValidationSeverity.ERROR,
            )
    
    def test_empty_message_raises(self) -> None:
        with pytest.raises(ValueError, match="message cannot be empty"):
            ValidationError(
                code="TEST_001",
                message="",
                severity=ValidationSeverity.ERROR,
            )
    
    def test_str_representation(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        assert str(error) == "[ERROR] TEST_001: Test error"
    
    def test_repr_representation(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        assert "TEST_001" in repr(error)
        assert "Test error" in repr(error)
    
    def test_equality(self) -> None:
        error1 = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        error2 = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        assert error1 == error2
    
    def test_inequality_different_code(self) -> None:
        error1 = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        error2 = ValidationError(
            code="TEST_002",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        assert error1 != error2
    
    def test_inequality_different_severity(self) -> None:
        error1 = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        error2 = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.WARNING,
        )
        assert error1 != error2
    
    def test_hash(self) -> None:
        error1 = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        error2 = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        assert hash(error1) == hash(error2)
    
    def test_to_dict(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
            entity_id="entity-123",
            entity_type="Room",
        )
        d = error.to_dict()
        assert d["code"] == "TEST_001"
        assert d["message"] == "Test error"
        assert d["severity"] == "error"
        assert d["entity_id"] == "entity-123"
        assert d["entity_type"] == "Room"
    
    def test_from_dict(self) -> None:
        data = {
            "code": "TEST_001",
            "message": "Test error",
            "severity": "error",
            "entity_id": "entity-123",
            "entity_type": "Room",
            "location": None,
            "metadata": {},
        }
        error = ValidationError.from_dict(data)
        assert error.code == "TEST_001"
        assert error.message == "Test error"
        assert error.severity == ValidationSeverity.ERROR
    
    def test_with_entity(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        new_error = error.with_entity("entity-123", "Room")
        assert new_error.entity_id == "entity-123"
        assert new_error.entity_type == "Room"
        assert new_error.code == error.code
        assert new_error.message == error.message
    
    def test_with_location(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        new_error = error.with_location("x:10,y:20")
        assert new_error.location == "x:10,y:20"
        assert new_error.code == error.code
    
    def test_with_metadata(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        new_error = error.with_metadata("key", "value")
        assert new_error.metadata == {"key": "value"}
        assert error.metadata == {}  # Original unchanged
    
    def test_frozen(self) -> None:
        error = ValidationError(
            code="TEST_001",
            message="Test error",
            severity=ValidationSeverity.ERROR,
        )
        with pytest.raises(AttributeError):
            error.code = "TEST_002"  # type: ignore


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_create_empty(self) -> None:
        result = ValidationResult()
        assert result.errors == []
        assert result.warnings == []
        assert result.infos == []
        assert result.is_valid is True
    
    def test_is_valid_with_errors(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(
            code="TEST_001",
            message="Error",
            severity=ValidationSeverity.ERROR,
        ))
        assert result.is_valid is False
    
    def test_is_valid_with_only_warnings(self) -> None:
        result = ValidationResult()
        result.add_warning(ValidationError(
            code="TEST_001",
            message="Warning",
            severity=ValidationSeverity.WARNING,
        ))
        assert result.is_valid is True
    
    def test_error_count(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(
            code="TEST_001",
            message="Error 1",
            severity=ValidationSeverity.ERROR,
        ))
        result.add_error(ValidationError(
            code="TEST_002",
            message="Error 2",
            severity=ValidationSeverity.CRITICAL,
        ))
        assert result.error_count == 2
    
    def test_warning_count(self) -> None:
        result = ValidationResult()
        result.add_warning(ValidationError(
            code="TEST_001",
            message="Warning 1",
            severity=ValidationSeverity.WARNING,
        ))
        result.add_warning(ValidationError(
            code="TEST_002",
            message="Warning 2",
            severity=ValidationSeverity.WARNING,
        ))
        assert result.warning_count == 2
    
    def test_info_count(self) -> None:
        result = ValidationResult()
        result.add_info(ValidationError(
            code="TEST_001",
            message="Info",
            severity=ValidationSeverity.INFO,
        ))
        assert result.info_count == 1
    
    def test_critical_count(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(
            code="TEST_001",
            message="Error",
            severity=ValidationSeverity.ERROR,
        ))
        result.add_error(ValidationError(
            code="TEST_002",
            message="Critical",
            severity=ValidationSeverity.CRITICAL,
        ))
        assert result.critical_count == 1
    
    def test_has_errors(self) -> None:
        result = ValidationResult()
        assert result.has_errors is False
        result.add_error(ValidationError(
            code="TEST_001",
            message="Error",
            severity=ValidationSeverity.ERROR,
        ))
        assert result.has_errors is True
    
    def test_has_warnings(self) -> None:
        result = ValidationResult()
        assert result.has_warnings is False
        result.add_warning(ValidationError(
            code="TEST_001",
            message="Warning",
            severity=ValidationSeverity.WARNING,
        ))
        assert result.has_warnings is True
    
    def test_total_count(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(
            code="TEST_001",
            message="Error",
            severity=ValidationSeverity.ERROR,
        ))
        result.add_warning(ValidationError(
            code="TEST_002",
            message="Warning",
            severity=ValidationSeverity.WARNING,
        ))
        result.add_info(ValidationError(
            code="TEST_003",
            message="Info",
            severity=ValidationSeverity.INFO,
        ))
        assert result.total_count == 3
    
    def test_all_issues(self) -> None:
        result = ValidationResult()
        error = ValidationError(code="E", message="Error", severity=ValidationSeverity.ERROR)
        warning = ValidationError(code="W", message="Warning", severity=ValidationSeverity.WARNING)
        info = ValidationError(code="I", message="Info", severity=ValidationSeverity.INFO)
        result.add_error(error)
        result.add_warning(warning)
        result.add_info(info)
        assert result.all_issues == [error, warning, info]
    
    def test_add_by_severity(self) -> None:
        result = ValidationResult()
        error = ValidationError(code="E", message="Error", severity=ValidationSeverity.ERROR)
        critical = ValidationError(code="C", message="Critical", severity=ValidationSeverity.CRITICAL)
        warning = ValidationError(code="W", message="Warning", severity=ValidationSeverity.WARNING)
        info = ValidationError(code="I", message="Info", severity=ValidationSeverity.INFO)
        result.add(error)
        result.add(critical)
        result.add(warning)
        result.add(info)
        assert result.error_count == 2
        assert result.warning_count == 1
        assert result.info_count == 1
    
    def test_merge(self) -> None:
        result1 = ValidationResult()
        result1.add_error(ValidationError(code="E1", message="Error 1", severity=ValidationSeverity.ERROR))
        
        result2 = ValidationResult()
        result2.add_error(ValidationError(code="E2", message="Error 2", severity=ValidationSeverity.ERROR))
        result2.add_warning(ValidationError(code="W1", message="Warning", severity=ValidationSeverity.WARNING))
        
        merged = result1.merge(result2)
        assert merged.error_count == 2
        assert merged.warning_count == 1
    
    def test_get_errors_by_code(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(code="E1", message="Error 1", severity=ValidationSeverity.ERROR))
        result.add_error(ValidationError(code="E2", message="Error 2", severity=ValidationSeverity.ERROR))
        result.add_error(ValidationError(code="E1", message="Error 3", severity=ValidationSeverity.ERROR))
        errors = result.get_errors_by_code("E1")
        assert len(errors) == 2
    
    def test_get_by_severity(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        result.add_error(ValidationError(code="C1", message="Critical", severity=ValidationSeverity.CRITICAL))
        result.add_warning(ValidationError(code="W1", message="Warning", severity=ValidationSeverity.WARNING))
        
        errors = result.get_by_severity(ValidationSeverity.ERROR)
        assert len(errors) == 1
        assert errors[0].code == "E1"
        
        critical = result.get_by_severity(ValidationSeverity.CRITICAL)
        assert len(critical) == 1
        assert critical[0].code == "C1"
    
    def test_to_dict(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        d = result.to_dict()
        assert d["is_valid"] is False
        assert d["error_count"] == 1
        assert len(d["errors"]) == 1
    
    def test_from_dict(self) -> None:
        data = {
            "is_valid": False,
            "error_count": 1,
            "warning_count": 0,
            "info_count": 0,
            "critical_count": 0,
            "errors": [{
                "code": "E1",
                "message": "Error",
                "severity": "error",
                "entity_id": None,
                "entity_type": None,
                "location": None,
                "metadata": {},
            }],
            "warnings": [],
            "infos": [],
        }
        result = ValidationResult.from_dict(data)
        assert result.error_count == 1
        assert result.errors[0].code == "E1"
    
    def test_create_factory(self) -> None:
        result = ValidationResult.create()
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_from_error_factory(self) -> None:
        error = ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR)
        result = ValidationResult.from_error(error)
        assert result.error_count == 1
        assert result.errors[0] == error
    
    def test_from_errors_factory(self) -> None:
        errors = [
            ValidationError(code="E1", message="Error 1", severity=ValidationSeverity.ERROR),
            ValidationError(code="E2", message="Error 2", severity=ValidationSeverity.WARNING),
        ]
        result = ValidationResult.from_errors(errors)
        assert result.error_count == 1
        assert result.warning_count == 1
    
    def test_str_representation(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        s = str(result)
        assert "valid=False" in s
        assert "errors=1" in s
    
    def test_repr_representation(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        r = repr(result)
        assert "errors=1" in r
    
    def test_bool_true_when_valid(self) -> None:
        result = ValidationResult()
        assert bool(result) is True
    
    def test_bool_false_when_invalid(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        assert bool(result) is False
    
    def test_equality(self) -> None:
        result1 = ValidationResult()
        result1.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        
        result2 = ValidationResult()
        result2.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        
        assert result1 == result2
    
    def test_inequality(self) -> None:
        result1 = ValidationResult()
        result1.add_error(ValidationError(code="E1", message="Error", severity=ValidationSeverity.ERROR))
        
        result2 = ValidationResult()
        
        assert result1 != result2


class TestValidator:
    """Tests for Validator abstract base class."""
    
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            Validator()  # type: ignore
    
    def test_concrete_validator(self) -> None:
        class ConcreteValidator(Validator):
            def validate(self, entity: object) -> ValidationResult:
                return ValidationResult.create()
        
        validator = ConcreteValidator()
        result = validator.validate("test")
        assert result.is_valid is True
    
    def test_validate_many(self) -> None:
        class ConcreteValidator(Validator):
            def validate(self, entity: object) -> ValidationResult:
                result = ValidationResult.create()
                if entity == "bad":
                    result.add_error(ValidationError(
                        code="BAD",
                        message="Bad entity",
                        severity=ValidationSeverity.ERROR,
                    ))
                return result
        
        validator = ConcreteValidator()
        result = validator.validate_many(["good", "bad", "good"])
        assert result.error_count == 1
    
    def test_validate_many_empty(self) -> None:
        class ConcreteValidator(Validator):
            def validate(self, entity: object) -> ValidationResult:
                return ValidationResult.create()
        
        validator = ConcreteValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
        assert result.total_count == 0


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_error_with_complex_metadata(self) -> None:
        error = ValidationError(
            code="TEST",
            message="Test",
            severity=ValidationSeverity.ERROR,
            metadata={
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "number": 42,
            },
        )
        assert error.metadata["nested"] == {"key": "value"}
        assert error.metadata["list"] == [1, 2, 3]
    
    def test_result_with_many_issues(self) -> None:
        result = ValidationResult()
        for i in range(100):
            result.add_error(ValidationError(
                code=f"E{i:03d}",
                message=f"Error {i}",
                severity=ValidationSeverity.ERROR,
            ))
        assert result.error_count == 100
    
    def test_merge_empty_with_non_empty(self) -> None:
        result1 = ValidationResult()
        result2 = ValidationResult()
        result2.add_error(ValidationError(code="E", message="Error", severity=ValidationSeverity.ERROR))
        
        merged = result1.merge(result2)
        assert merged.error_count == 1
    
    def test_merge_non_empty_with_empty(self) -> None:
        result1 = ValidationResult()
        result1.add_error(ValidationError(code="E", message="Error", severity=ValidationSeverity.ERROR))
        result2 = ValidationResult()
        
        merged = result1.merge(result2)
        assert merged.error_count == 1
    
    def test_merge_two_empty(self) -> None:
        result1 = ValidationResult()
        result2 = ValidationResult()
        
        merged = result1.merge(result2)
        assert merged.is_valid is True
    
    def test_serialization_roundtrip(self) -> None:
        result = ValidationResult()
        result.add_error(ValidationError(
            code="TEST",
            message="Test error",
            severity=ValidationSeverity.ERROR,
            entity_id="entity-1",
            entity_type="Room",
        ))
        result.add_warning(ValidationError(
            code="WARN",
            message="Test warning",
            severity=ValidationSeverity.WARNING,
        ))
        
        d = result.to_dict()
        restored = ValidationResult.from_dict(d)
        
        assert restored.error_count == 1
        assert restored.warning_count == 1
        assert restored.errors[0].code == "TEST"
        assert restored.warnings[0].code == "WARN"
    
    def test_error_immutability(self) -> None:
        error = ValidationError(
            code="TEST",
            message="Test",
            severity=ValidationSeverity.ERROR,
            metadata={"key": "value"},
        )
        
        # Can't modify frozen dataclass
        with pytest.raises(AttributeError):
            error.code = "OTHER"  # type: ignore
        
        # Metadata dict is still mutable (shallow immutability)
        error.metadata["new_key"] = "new_value"
        assert "new_key" in error.metadata