"""Unit tests for the Iteration Engine."""
from __future__ import annotations
import pytest
from building_model_v2.base import Point2D
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_opening import Door, Window
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.entities_wall import Wall
from building_model_v2.optimization.action_registry import ActionRegistry
from building_model_v2.optimization.design_iteration import DesignIteration
from building_model_v2.optimization.improvement_plan import ImprovementPlan
from building_model_v2.optimization.iteration_engine import (
    IterationEngine, IterationEngineConfig, StoppingReason,
)
from building_model_v2.optimization.iteration_history import IterationHistory
from building_model_v2.optimization.optimization_action import OptimizationAction
from building_model_v2.optimization.optimization_result import OptimizationResult
from building_model_v2.optimization.optimizer import Optimizer
from building_model_v2.optimization.recommendation_engine import RecommendationEngine
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel


@pytest.fixture
def sample_room():
    return Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING, ceiling_height=9.0)

@pytest.fixture
def sample_window():
    return Window.create(location=Point2D(x=5.0,y=0.0), width=4.0, height=4.0, sill_height=3.0)

@pytest.fixture
def sample_door():
    return Door.create(location=Point2D(x=3.0,y=0.0), width=3.0, height=7.0)

@pytest.fixture
def sample_stair():
    return Stair.create(start=(0.0,0.0), end=(10.0,0.0), width=3.0)

@pytest.fixture
def sample_building():
    return Building.create(name="Test Building", floor_ids=("floor_1",))

@pytest.fixture
def sample_floor():
    return Floor.create(name="Ground Floor", level=0, room_ids=frozenset(["room_1"]), wall_ids=frozenset(["wall_1"]), stair_ids=frozenset(["stair_1"]))

@pytest.fixture
def building_model(sample_building, sample_floor, sample_room, sample_window, sample_door, sample_stair):
    return BuildingModel(
        building=sample_building,
        floors={"floor_1": sample_floor},
        rooms={"room_1": sample_room},
        walls={"wall_1": Wall.create(start=(0,0), end=(10,0))},
        columns={}, stairs={"stair_1": sample_stair},
        doors={"door_1": sample_door}, windows={"window_1": sample_window},
        relationships=[],
    )

@pytest.fixture
def engine():
    return IterationEngine()

@pytest.fixture
def config():
    return IterationEngineConfig(max_iterations=5, minimum_score_gain=0.25)


class TestDesignIteration:
    def test_create_iteration(self, building_model):
        iteration = DesignIteration(
            iteration=0,
            building_model=building_model,
            score=50.0,
            elapsed_time=1.5,
        )
        assert iteration.iteration == 0
        assert iteration.score == 50.0
        assert iteration.elapsed_time == 1.5
        assert iteration.action_count == 0

    def test_improved_with_result(self, building_model):
        action = OptimizationAction(id="t", title="T", description="D", target_entity_id="r", target_entity_type="room")
        result = OptimizationResult(
            original_model=building_model,
            optimized_model=building_model,
            applied_actions=[action],
            before_score=50.0,
            after_score=70.0,
        )
        iteration = DesignIteration(iteration=0, building_model=building_model, optimization_result=result)
        assert iteration.improved is True
        assert iteration.action_count == 1
        assert iteration.score_delta == 20.0

    def test_not_improved(self, building_model):
        result = OptimizationResult(
            original_model=building_model,
            optimized_model=building_model,
            before_score=70.0,
            after_score=50.0,
        )
        iteration = DesignIteration(iteration=0, building_model=building_model, optimization_result=result)
        assert iteration.improved is False
        assert iteration.score_delta == -20.0

    def test_action_count_no_result(self, building_model):
        iteration = DesignIteration(iteration=0, building_model=building_model)
        assert iteration.action_count == 0
        assert iteration.score_delta == 0.0

    def test_serialization(self, building_model):
        iteration = DesignIteration(iteration=0, building_model=building_model, score=50.0, elapsed_time=1.0)
        d = iteration.to_dict()
        assert d["iteration"] == 0
        assert d["score"] == 50.0
        assert d["elapsed_time"] == 1.0
        assert d["action_count"] == 0

    def test_equality(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        i2 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        assert i1 == i2

    def test_hash(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        i2 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        assert hash(i1) == hash(i2)

    def test_metadata(self, building_model):
        iteration = DesignIteration(iteration=0, building_model=building_model, metadata={"key": "value"})
        assert iteration.metadata["key"] == "value"


class TestIterationHistory:
    def test_create_empty_history(self):
        history = IterationHistory()
        assert history.iteration_count == 0
        assert history.best_score == 0.0
        assert history.total_actions == 0
        assert history.converged is False
        assert history.stopping_reason == ""

    def test_history_with_iterations(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        i2 = DesignIteration(iteration=1, building_model=building_model, score=60.0)
        i3 = DesignIteration(iteration=2, building_model=building_model, score=55.0)
        history = IterationHistory(iterations=[i1, i2, i3], best_iteration=i2, stopping_reason="converged", converged=True)
        assert history.iteration_count == 3
        assert history.best_score == 60.0
        assert history.best_iteration == i2
        assert history.converged is True
        assert history.stopping_reason == "converged"

    def test_score_progression(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        i2 = DesignIteration(iteration=1, building_model=building_model, score=60.0)
        i3 = DesignIteration(iteration=2, building_model=building_model, score=70.0)
        history = IterationHistory(iterations=[i1, i2, i3])
        assert history.score_progression == [50.0, 60.0, 70.0]

    def test_average_improvement(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        i2 = DesignIteration(iteration=1, building_model=building_model, score=60.0)
        i3 = DesignIteration(iteration=2, building_model=building_model, score=70.0)
        history = IterationHistory(iterations=[i1, i2, i3])
        assert history.average_improvement == pytest.approx(10.0)

    def test_average_improvement_single(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        history = IterationHistory(iterations=[i1])
        assert history.average_improvement == 0.0

    def test_total_actions(self, building_model):
        result1 = OptimizationResult(original_model=building_model, optimized_model=building_model, applied_actions=[], before_score=50.0, after_score=50.0)
        result2 = OptimizationResult(original_model=building_model, optimized_model=building_model, applied_actions=[], before_score=50.0, after_score=50.0)
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0, optimization_result=result1)
        i2 = DesignIteration(iteration=1, building_model=building_model, score=50.0, optimization_result=result2)
        history = IterationHistory(iterations=[i1, i2])
        assert history.total_actions == 0

    def test_get_iteration(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        i2 = DesignIteration(iteration=1, building_model=building_model, score=60.0)
        history = IterationHistory(iterations=[i1, i2])
        assert history.get_iteration(0) == i1
        assert history.get_iteration(1) == i2
        assert history.get_iteration(2) is None
        assert history.get_iteration(-1) is None

    def test_get_score_at(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        i2 = DesignIteration(iteration=1, building_model=building_model, score=60.0)
        history = IterationHistory(iterations=[i1, i2])
        assert history.get_score_at(0) == 50.0
        assert history.get_score_at(1) == 60.0
        assert history.get_score_at(2) == 0.0

    def test_serialization(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        history = IterationHistory(iterations=[i1], stopping_reason="test", converged=False)
        d = history.to_dict()
        assert d["iteration_count"] == 1
        assert d["stopping_reason"] == "test"
        assert d["converged"] is False
        assert len(d["iterations"]) == 1

    def test_equality(self, building_model):
        i1 = DesignIteration(iteration=0, building_model=building_model, score=50.0)
        h1 = IterationHistory(iterations=[i1], stopping_reason="test")
        h2 = IterationHistory(iterations=[i1], stopping_reason="test")
        assert h1 == h2


class TestStoppingReason:
    def test_max_iterations(self):
        assert StoppingReason.MAX_ITERATIONS == "max_iterations"

    def test_no_improvement(self):
        assert StoppingReason.NO_IMPROVEMENT == "no_improvement"

    def test_no_actions(self):
        assert StoppingReason.NO_ACTIONS == "no_actions"

    def test_converged(self):
        assert StoppingReason.CONVERGED == "converged"


class TestIterationEngineConfig:
    def test_default_config(self):
        config = IterationEngineConfig()
        assert config.max_iterations == 10
        assert config.minimum_score_gain == 0.25
        assert config.stop_when_no_actions is True
        assert config.stop_when_no_improvement is True
        assert config.evaluation_config is None

    def test_custom_config(self):
        config = IterationEngineConfig(max_iterations=20, minimum_score_gain=0.5, stop_when_no_actions=False, stop_when_no_improvement=False)
        assert config.max_iterations == 20
        assert config.minimum_score_gain == 0.5
        assert config.stop_when_no_actions is False
        assert config.stop_when_no_improvement is False


class TestIterationEngineProperties:
    def test_properties(self):
        engine = IterationEngine()
        assert isinstance(engine.config, IterationEngineConfig)
        assert engine.evaluation_pipeline is not None
        assert engine.recommendation_engine is not None
        assert engine.optimizer is not None

    def test_custom_components(self):
        config = IterationEngineConfig(max_iterations=3)
        engine = IterationEngine(config=config)
        assert engine.config.max_iterations == 3


class TestIterationEngineRun:
    def test_run_returns_history(self, building_model, engine):
        history = engine.run(building_model)
        assert isinstance(history, IterationHistory)
        assert history.iteration_count > 0

    def test_run_respects_max_iterations(self, building_model):
        config = IterationEngineConfig(max_iterations=3)
        engine = IterationEngine(config=config)
        history = engine.run(building_model)
        assert history.iteration_count <= 3

    def test_run_stops_when_no_actions(self, building_model):
        config = IterationEngineConfig(max_iterations=10, stop_when_no_actions=True)
        engine = IterationEngine(config=config)
        history = engine.run(building_model)
        # Should stop at some point due to no actions
        assert history.iteration_count >= 1
        assert history.stopping_reason in [StoppingReason.NO_ACTIONS, StoppingReason.MAX_ITERATIONS, StoppingReason.NO_IMPROVEMENT, StoppingReason.CONVERGED]

    def test_run_original_model_unchanged(self, building_model, engine):
        original_model = building_model
        history = engine.run(building_model)
        assert history.iterations[0].building_model is original_model

    def test_run_has_best_iteration(self, building_model, engine):
        history = engine.run(building_model)
        assert history.best_iteration is not None
        assert history.best_score >= 0.0

    def test_run_timing_recorded(self, building_model, engine):
        history = engine.run(building_model)
        for iteration in history.iterations:
            assert iteration.elapsed_time >= 0.0

    def test_run_metadata_in_iterations(self, building_model, engine):
        history = engine.run(building_model)
        for iteration in history.iterations:
            assert "action_count" in iteration.metadata
            assert "score_delta" in iteration.metadata

    def test_run_convergence(self, building_model):
        config = IterationEngineConfig(max_iterations=100, minimum_score_gain=0.25)
        engine = IterationEngine(config=config)
        history = engine.run(building_model)
        # Should eventually converge or hit max iterations
        assert history.stopping_reason != ""


class TestIterationEngineEdgeCases:
    def test_run_with_empty_model(self):
        model = BuildingModel()
        engine = IterationEngine()
        history = engine.run(model)
        assert isinstance(history, IterationHistory)
        assert history.iteration_count >= 1

    def test_original_model_not_modified(self, building_model, engine):
        original_rooms = dict(building_model.rooms)
        original_floors = dict(building_model.floors)
        engine.run(building_model)
        assert dict(building_model.rooms) == original_rooms
        assert dict(building_model.floors) == original_floors

    def test_custom_optimizer(self, building_model):
        config = IterationEngineConfig(max_iterations=3)
        optimizer = Optimizer()
        engine = IterationEngine(config=config, optimizer=optimizer)
        history = engine.run(building_model)
        assert history.iteration_count >= 1

    def test_multiple_runs_same_model(self, building_model):
        config = IterationEngineConfig(max_iterations=3)
        engine = IterationEngine(config=config)
        h1 = engine.run(building_model)
        h2 = engine.run(building_model)
        assert h1.iteration_count == h2.iteration_count


class TestIntegrationWithEvaluationPipeline:
    def test_engine_uses_evaluation_pipeline(self, building_model):
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline, EvaluationPipelineConfig
        eval_pipeline = EvaluationPipeline()
        engine = IterationEngine(evaluation_pipeline=eval_pipeline)
        history = engine.run(building_model)
        assert history.iteration_count >= 1
        for iteration in history.iterations:
            assert iteration.evaluation_report is not None

    def test_engine_uses_recommendation_engine(self, building_model):
        rec_engine = RecommendationEngine()
        engine = IterationEngine(recommendation_engine=rec_engine)
        history = engine.run(building_model)
        assert history.iteration_count >= 1
        for iteration in history.iterations:
            assert iteration.improvement_plan is not None

    def test_engine_uses_optimizer(self, building_model):
        optimizer = Optimizer()
        engine = IterationEngine(optimizer=optimizer)
        history = engine.run(building_model)
        assert history.iteration_count >= 1
        for iteration in history.iterations:
            assert iteration.optimization_result is not None

    def test_full_pipeline_integration(self, building_model):
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
        config = IterationEngineConfig(max_iterations=2)
        eval_pipeline = EvaluationPipeline()
        rec_engine = RecommendationEngine()
        optimizer = Optimizer()
        engine = IterationEngine(
            config=config,
            evaluation_pipeline=eval_pipeline,
            recommendation_engine=rec_engine,
            optimizer=optimizer,
        )
        history = engine.run(building_model)
        assert isinstance(history, IterationHistory)
        assert history.iteration_count >= 1
        if history.iteration_count > 0:
            first = history.iterations[0]
            assert first.building_model is building_model
            assert first.evaluation_report is not None
            assert first.improvement_plan is not None
            assert first.optimization_result is not None

