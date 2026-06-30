"""Tests for the pipeline constraint framework."""
from __future__ import annotations

from building_model_v2.pipeline.constraints.base_constraint import BaseConstraint
from building_model_v2.pipeline.constraints.constraint_engine import ConstraintEngine
from building_model_v2.pipeline.constraints.constraint_result import ConstraintResult
from building_model_v2.pipeline.design_request import DesignRequest


class DummyPipelineConstraint(BaseConstraint):
    def __init__(self, name: str, passed: bool, warnings: tuple[str, ...] = (), errors: tuple[str, ...] = ()) -> None:
        self._name = name
        self.passed = passed
        self.warnings = warnings
        self.errors = errors

    @property
    def name(self) -> str:
        return self._name

    def validate(self, design_request: DesignRequest) -> ConstraintResult:
        return ConstraintResult(
            passed=self.passed,
            warnings=self.warnings,
            errors=self.errors,
            constraint_name=self.name,
        )


class TestPipelineConstraintFramework:
    def _make_request(self) -> DesignRequest:
        return DesignRequest(
            project_type="residential",
            plot_width=20.0,
            plot_depth=20.0,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=1,
            kitchen_type="open",
            pooja_room=False,
            living_room=True,
            dining_room=True,
            staircase=False,
            orientation="north",
            special_requirements=(),
        )

    def test_register_constraint(self) -> None:
        engine = ConstraintEngine()
        constraint = DummyPipelineConstraint(name="test", passed=True)

        engine.register_constraint(constraint)
        results = engine.validate(self._make_request())

        assert len(results) == 1
        assert results[0].constraint_name == "test"
        assert results[0].passed is True

    def test_unregister_constraint(self) -> None:
        engine = ConstraintEngine()
        constraint = DummyPipelineConstraint(name="remove", passed=True)

        engine.register_constraint(constraint)
        engine.unregister_constraint(constraint)
        results = engine.validate(self._make_request())

        assert results == []

    def test_execution_order(self) -> None:
        engine = ConstraintEngine()
        first = DummyPipelineConstraint(name="first", passed=True)
        second = DummyPipelineConstraint(name="second", passed=True)

        engine.register_constraint(first)
        engine.register_constraint(second)
        results = engine.validate(self._make_request())

        assert [result.constraint_name for result in results] == ["first", "second"]

    def test_multiple_constraints(self) -> None:
        engine = ConstraintEngine()
        constraint_a = DummyPipelineConstraint(name="a", passed=True)
        constraint_b = DummyPipelineConstraint(name="b", passed=False, errors=("failed",))

        engine.register_constraint(constraint_a)
        engine.register_constraint(constraint_b)
        results = engine.validate(self._make_request())

        assert len(results) == 2
        assert results[1].has_errors() is True

    def test_warning_aggregation(self) -> None:
        engine = ConstraintEngine()
        constraint_a = DummyPipelineConstraint(name="a", passed=True, warnings=("warn1",))
        constraint_b = DummyPipelineConstraint(name="b", passed=True, warnings=("warn2",))

        engine.register_constraint(constraint_a)
        engine.register_constraint(constraint_b)
        results = engine.validate(self._make_request())

        assert results[0].has_warnings() is True
        assert results[1].has_warnings() is True

    def test_error_aggregation(self) -> None:
        engine = ConstraintEngine()
        constraint_a = DummyPipelineConstraint(name="a", passed=False, errors=("error1",))
        constraint_b = DummyPipelineConstraint(name="b", passed=False, errors=("error2",))

        engine.register_constraint(constraint_a)
        engine.register_constraint(constraint_b)
        results = engine.validate(self._make_request())

        assert results[0].has_errors() is True
        assert results[1].has_errors() is True

    def test_empty_engine_behavior(self) -> None:
        engine = ConstraintEngine()
        results = engine.validate(self._make_request())

        assert results == []
