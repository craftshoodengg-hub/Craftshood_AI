"""Unit tests for the Optimization Engine."""
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
from building_model_v2.optimization.improvement_plan import ImprovementPlan
from building_model_v2.optimization.optimization_action import OptimizationAction
from building_model_v2.optimization.optimization_actions import (
    add_elevator_placeholder, add_opposite_window_placeholder,
    add_ramp_placeholder, add_window_placeholder,
    expand_room, increase_ceiling_height, increase_door_width,
    increase_room_height, increase_stair_width, increase_window_area,
    increase_window_size,
)
from building_model_v2.optimization.optimization_result import OptimizationResult
from building_model_v2.optimization.optimizer import Optimizer
from building_model_v2.optimization.recommendation_engine import RecommendationEngine
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel


@pytest.fixture
def sample_room():
    return Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING, ceiling_height=9.0, metadata={"source":"test"})

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
def optimizer():
    return Optimizer()

@pytest.fixture
def action_registry():
    return ActionRegistry()


class TestOptimizationResult:
    def test_create_result(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, applied_actions=[], before_score=50.0, after_score=70.0)
        assert r.before_score == 50.0
        assert r.after_score == 70.0
        assert r.action_count == 0

    def test_improved_true(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=70.0)
        assert r.improved is True

    def test_improved_false(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=70.0, after_score=50.0)
        assert r.improved is False

    def test_improved_equal(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=50.0)
        assert r.improved is False

    def test_score_delta(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=75.0)
        assert r.score_delta == pytest.approx(25.0)

    def test_score_delta_negative(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=75.0, after_score=50.0)
        assert r.score_delta == pytest.approx(-25.0)

    def test_improvement_percentage(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=75.0)
        assert r.improvement_percentage == pytest.approx(50.0)

    def test_improvement_pct_zero_before(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=0.0, after_score=50.0)
        assert r.improvement_percentage == pytest.approx(0.0)

    def test_action_count(self, building_model):
        a = OptimizationAction(id="t", title="T", description="D", target_entity_id="r", target_entity_type="room")
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, applied_actions=[a, a, a])
        assert r.action_count == 3

    def test_serialization(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=70.0)
        d = r.to_dict()
        assert d["before_score"] == 50.0
        assert d["after_score"] == 70.0
        assert d["improved"] is True
        assert d["score_delta"] == pytest.approx(20.0)

    def test_deserialization(self):
        d = {"applied_actions": [], "before_score": 50.0, "after_score": 70.0, "metadata": {}}
        r = OptimizationResult.from_dict(d)
        assert r.before_score == 50.0
        assert r.after_score == 70.0

    def test_equality(self, building_model):
        r1 = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=70.0)
        r2 = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=70.0)
        assert r1 == r2

    def test_hash(self, building_model):
        r1 = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=70.0)
        r2 = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=70.0)
        assert hash(r1) == hash(r2)

    def test_metadata(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, metadata={"key": "value"})
        assert r.metadata["key"] == "value"

    def test_immutability(self, building_model):
        r = OptimizationResult(original_model=building_model, optimized_model=building_model, before_score=50.0, after_score=70.0)
        with pytest.raises(AttributeError):
            r.before_score = 100.0


class TestActionRegistry:
    def test_default_registry_has_actions(self, action_registry):
        assert len(action_registry) > 0

    def test_registered_codes(self, action_registry):
        codes = action_registry.registered_codes
        assert "ROOM_TOO_SMALL" in codes
        assert "WINDOW_TO_FLOOR_RATIO_LOW" in codes
        assert "DOOR_TOO_NARROW" in codes

    def test_get_existing_action(self, action_registry):
        func = action_registry.get("ROOM_TOO_SMALL")
        assert func is not None
        assert callable(func)

    def test_get_nonexistent_action(self, action_registry):
        func = action_registry.get("NONEXISTENT_CODE")
        assert func is None

    def test_has_existing(self, action_registry):
        assert action_registry.has("ROOM_TOO_SMALL") is True

    def test_has_nonexistent(self, action_registry):
        assert action_registry.has("NONEXISTENT_CODE") is False

    def test_contains_operator(self, action_registry):
        assert "ROOM_TOO_SMALL" in action_registry
        assert "NONEXISTENT_CODE" not in action_registry

    def test_register_custom_action(self, action_registry):
        def custom_action(model, action):
            return model
        action_registry.register("CUSTOM_CODE", custom_action)
        assert action_registry.has("CUSTOM_CODE")
        assert action_registry.get("CUSTOM_CODE") is custom_action

    def test_all_default_mappings_exist(self, action_registry):
        expected = {"ROOM_AREA_BELOW_MINIMUM", "ROOM_TOO_SMALL", "ROOM_WITHOUT_WINDOW",
            "WINDOW_TO_FLOOR_RATIO_LOW", "NATURAL_LIGHT_INSUFFICIENT",
            "CROSS_VENTILATION_POSSIBLE", "DOOR_WIDTH_BELOW_MINIMUM",
            "DOOR_TOO_NARROW", "STAIR_WIDTH_BELOW_MINIMUM", "STAIR_TOO_NARROW",
            "CEILING_HEIGHT_BELOW_MINIMUM", "ROOM_HEIGHT_INSUFFICIENT",
            "ACCESSIBILITY_RAMP_MISSING", "ELEVATOR_MISSING"}
        for code in expected:
            assert code in action_registry, f"Missing mapping for {code}"

    def test_registered_codes_is_frozenset(self, action_registry):
        codes = action_registry.registered_codes
        assert isinstance(codes, frozenset)


class TestExpandRoom:
    def test_expand_room_increases_area(self, building_model):
        original_area = building_model.rooms["room_1"].area
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        result = expand_room(building_model, action)
        assert result.rooms["room_1"].area > original_area

    def test_expand_room_preserves_original(self, building_model):
        original_area = building_model.rooms["room_1"].area
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        expand_room(building_model, action)
        assert building_model.rooms["room_1"].area == original_area

    def test_expand_room_unknown_target(self, building_model):
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="nonexistent", target_entity_type="room")
        result = expand_room(building_model, action)
        assert result.rooms["room_1"].area == building_model.rooms["room_1"].area

    def test_expand_room_no_rooms_attr(self):
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        model = BuildingModel()
        result = expand_room(model, action)
        assert result is not None


class TestIncreaseWindowSize:
    def test_increase_window_width(self, building_model):
        original_width = building_model.windows["window_1"].width
        action = OptimizationAction(id="WINDOW_TO_FLOOR_RATIO_LOW", title="Bigger", description="Bigger", target_entity_id="window_1", target_entity_type="window")
        result = increase_window_size(building_model, action)
        assert result.windows["window_1"].width > original_width

    def test_increase_window_height(self, building_model):
        original_height = building_model.windows["window_1"].height
        action = OptimizationAction(id="WINDOW_TO_FLOOR_RATIO_LOW", title="Bigger", description="Bigger", target_entity_id="window_1", target_entity_type="window")
        result = increase_window_size(building_model, action)
        assert result.windows["window_1"].height > original_height

    def test_increase_window_preserves_original(self, building_model):
        original_width = building_model.windows["window_1"].width
        action = OptimizationAction(id="WINDOW_TO_FLOOR_RATIO_LOW", title="Bigger", description="Bigger", target_entity_id="window_1", target_entity_type="window")
        increase_window_size(building_model, action)
        assert building_model.windows["window_1"].width == original_width

    def test_increase_window_unknown_target(self, building_model):
        action = OptimizationAction(id="WINDOW_TO_FLOOR_RATIO_LOW", title="Bigger", description="Bigger", target_entity_id="nonexistent", target_entity_type="window")
        result = increase_window_size(building_model, action)
        assert result.windows["window_1"].width == building_model.windows["window_1"].width

    def test_increase_window_area_delegates(self, building_model):
        action = OptimizationAction(id="NATURAL_LIGHT_INSUFFICIENT", title="More light", description="More", target_entity_id="window_1", target_entity_type="window")
        result1 = increase_window_area(building_model, action)
        result2 = increase_window_size(building_model, action)
        assert result1.windows["window_1"].width == result2.windows["window_1"].width


class TestIncreaseDoorWidth:
    def test_increase_door_width(self, building_model):
        original_width = building_model.doors["door_1"].width
        action = OptimizationAction(id="DOOR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="door_1", target_entity_type="door")
        result = increase_door_width(building_model, action)
        assert result.doors["door_1"].width > original_width

    def test_increase_door_preserves_original(self, building_model):
        original_width = building_model.doors["door_1"].width
        action = OptimizationAction(id="DOOR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="door_1", target_entity_type="door")
        increase_door_width(building_model, action)
        assert building_model.doors["door_1"].width == original_width

    def test_increase_door_unknown_target(self, building_model):
        action = OptimizationAction(id="DOOR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="nonexistent", target_entity_type="door")
        result = increase_door_width(building_model, action)
        assert result.doors["door_1"].width == building_model.doors["door_1"].width


class TestIncreaseStairWidth:
    def test_increase_stair_width(self, building_model):
        original_width = building_model.stairs["stair_1"].width
        action = OptimizationAction(id="STAIR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="stair_1", target_entity_type="stair")
        result = increase_stair_width(building_model, action)
        assert result.stairs["stair_1"].width > original_width

    def test_increase_stair_preserves_original(self, building_model):
        original_width = building_model.stairs["stair_1"].width
        action = OptimizationAction(id="STAIR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="stair_1", target_entity_type="stair")
        increase_stair_width(building_model, action)
        assert building_model.stairs["stair_1"].width == original_width

    def test_increase_stair_unknown_target(self, building_model):
        action = OptimizationAction(id="STAIR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="nonexistent", target_entity_type="stair")
        result = increase_stair_width(building_model, action)
        assert result.stairs["stair_1"].width == building_model.stairs["stair_1"].width


class TestIncreaseCeilingHeight:
    def test_increase_ceiling_height(self, building_model):
        original_height = building_model.rooms["room_1"].ceiling_height
        action = OptimizationAction(id="CEILING_HEIGHT_BELOW_MINIMUM", title="Raise", description="Higher", target_entity_id="room_1", target_entity_type="room")
        result = increase_ceiling_height(building_model, action)
        assert result.rooms["room_1"].ceiling_height > original_height

    def test_increase_ceiling_preserves_original(self, building_model):
        original_height = building_model.rooms["room_1"].ceiling_height
        action = OptimizationAction(id="CEILING_HEIGHT_BELOW_MINIMUM", title="Raise", description="Higher", target_entity_id="room_1", target_entity_type="room")
        increase_ceiling_height(building_model, action)
        assert building_model.rooms["room_1"].ceiling_height == original_height

    def test_increase_room_height_delegates(self, building_model):
        action = OptimizationAction(id="ROOM_HEIGHT_INSUFFICIENT", title="Taller", description="Taller", target_entity_id="room_1", target_entity_type="room")
        result1 = increase_room_height(building_model, action)
        result2 = increase_ceiling_height(building_model, action)
        assert result1.rooms["room_1"].ceiling_height == result2.rooms["room_1"].ceiling_height


class TestPlaceholderActions:
    def test_add_window_placeholder(self, building_model):
        action = OptimizationAction(id="ROOM_WITHOUT_WINDOW", title="Add window", description="Placeholder", target_entity_id="room_1", target_entity_type="room")
        result = add_window_placeholder(building_model, action)
        assert result.rooms["room_1"].metadata.get("window_placeholder") is True

    def test_add_window_placeholder_preserves_original(self, building_model):
        action = OptimizationAction(id="ROOM_WITHOUT_WINDOW", title="Add window", description="Placeholder", target_entity_id="room_1", target_entity_type="room")
        add_window_placeholder(building_model, action)
        assert "window_placeholder" not in building_model.rooms["room_1"].metadata

    def test_add_opposite_window_placeholder(self, building_model):
        action = OptimizationAction(id="CROSS_VENTILATION_POSSIBLE", title="Opposite", description="Cross", target_entity_id="room_1", target_entity_type="room")
        result = add_opposite_window_placeholder(building_model, action)
        assert result.rooms["room_1"].metadata.get("opposite_window_placeholder") is True

    def test_add_ramp_placeholder(self, building_model):
        action = OptimizationAction(id="ACCESSIBILITY_RAMP_MISSING", title="Ramp", description="Ramp", target_entity_id="", target_entity_type="building")
        result = add_ramp_placeholder(building_model, action)
        assert result.building.metadata.get("ramp_placeholder") is True

    def test_add_ramp_placeholder_no_building(self):
        model = BuildingModel()
        action = OptimizationAction(id="ACCESSIBILITY_RAMP_MISSING", title="Ramp", description="Ramp", target_entity_id="", target_entity_type="building")
        result = add_ramp_placeholder(model, action)
        assert result.building is None

    def test_add_elevator_placeholder(self, building_model):
        action = OptimizationAction(id="ELEVATOR_MISSING", title="Elevator", description="Elevator", target_entity_id="", target_entity_type="building")
        result = add_elevator_placeholder(building_model, action)
        assert result.building.metadata.get("elevator_placeholder") is True


class TestOptimizer:
    def test_optimize_empty_plan(self, optimizer, building_model):
        plan = ImprovementPlan(actions=[])
        result = optimizer.optimize(building_model, plan)
        assert isinstance(result, OptimizationResult)
        assert result.action_count == 0
        assert result.original_model is building_model

    def test_optimize_preserves_original(self, optimizer, building_model):
        original_area = building_model.rooms["room_1"].area
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        optimizer.optimize(building_model, plan)
        assert building_model.rooms["room_1"].area == original_area

    def test_optimize_applies_action(self, optimizer, building_model):
        original_area = building_model.rooms["room_1"].area
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        result = optimizer.optimize(building_model, plan)
        assert result.optimized_model.rooms["room_1"].area > original_area

    def test_optimize_returns_applied_actions(self, optimizer, building_model):
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        result = optimizer.optimize(building_model, plan)
        assert result.action_count == 1
        assert result.applied_actions[0] == action

    def test_optimize_with_scores(self, optimizer, building_model):
        plan = ImprovementPlan(actions=[])
        result = optimizer.optimize(building_model, plan, before_score=50.0, after_score=70.0)
        assert result.before_score == 50.0
        assert result.after_score == 70.0
        assert result.improved is True

    def test_optimize_unknown_action(self, optimizer, building_model):
        action = OptimizationAction(id="TOTALLY_UNKNOWN", title="Unknown", description="Unknown", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        result = optimizer.optimize(building_model, plan)
        assert result.action_count == 1
        assert result.optimized_model.rooms["room_1"].area == building_model.rooms["room_1"].area

    def test_optimize_multiple_actions(self, optimizer, building_model):
        action1 = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        action2 = OptimizationAction(id="WINDOW_TO_FLOOR_RATIO_LOW", title="Bigger", description="Bigger", target_entity_id="window_1", target_entity_type="window")
        plan = ImprovementPlan(actions=[action1, action2])
        result = optimizer.optimize(building_model, plan)
        assert result.action_count == 2
        assert result.optimized_model.rooms["room_1"].area > building_model.rooms["room_1"].area
        assert result.optimized_model.windows["window_1"].width > building_model.windows["window_1"].width

    def test_optimize_deep_copy(self, optimizer, building_model):
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        result = optimizer.optimize(building_model, plan)
        assert result.optimized_model is not building_model

    def test_optimize_metadata(self, optimizer, building_model):
        plan = ImprovementPlan(actions=[])
        result = optimizer.optimize(building_model, plan)
        assert "optimizer_version" in result.metadata
        assert "action_count" in result.metadata

    def test_can_optimize(self, optimizer):
        assert optimizer.can_optimize("ROOM_TOO_SMALL") is True
        assert optimizer.can_optimize("NONEXISTENT") is False

    def test_available_actions(self, optimizer):
        actions = optimizer.available_actions
        assert isinstance(actions, frozenset)
        assert "ROOM_TOO_SMALL" in actions

    def test_registry_property(self, optimizer):
        assert isinstance(optimizer.registry, ActionRegistry)


class TestEdgeCases:
    def test_action_on_empty_model(self, optimizer):
        model = BuildingModel()
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        result = optimizer.optimize(model, plan)
        assert result.action_count == 1

    def test_action_on_model_without_building(self, optimizer):
        model = BuildingModel(rooms={"room_1": Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)])})
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        result = optimizer.optimize(model, plan)
        assert result.action_count == 1

    def test_multiple_actions_same_target(self, optimizer, building_model):
        original_width = building_model.doors["door_1"].width
        action1 = OptimizationAction(id="DOOR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="door_1", target_entity_type="door")
        action2 = OptimizationAction(id="DOOR_WIDTH_BELOW_MINIMUM", title="Widen more", description="Wider", target_entity_id="door_1", target_entity_type="door")
        plan = ImprovementPlan(actions=[action1, action2])
        result = optimizer.optimize(building_model, plan)
        expected_width = original_width * 1.15 * 1.15
        assert result.optimized_model.doors["door_1"].width == pytest.approx(expected_width)

    def test_zero_score_before(self, optimizer, building_model):
        plan = ImprovementPlan(actions=[])
        result = optimizer.optimize(building_model, plan, before_score=0.0, after_score=50.0)
        assert result.improvement_percentage == 0.0

    def test_equal_scores(self, optimizer, building_model):
        plan = ImprovementPlan(actions=[])
        result = optimizer.optimize(building_model, plan, before_score=50.0, after_score=50.0)
        assert result.improved is False
        assert result.score_delta == 0.0

    def test_negative_score_delta(self, optimizer, building_model):
        plan = ImprovementPlan(actions=[])
        result = optimizer.optimize(building_model, plan, before_score=70.0, after_score=50.0)
        assert result.score_delta == pytest.approx(-20.0)
        assert result.improved is False

    def test_deep_copy_isolation(self, optimizer, building_model):
        action = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room")
        plan = ImprovementPlan(actions=[action])
        result = optimizer.optimize(building_model, plan)
        assert result.original_model is building_model
        assert result.optimized_model is not building_model


class TestActionOrdering:
    def test_actions_applied_in_plan_order(self, optimizer, building_model):
        original_width = building_model.windows["window_1"].width
        action1 = OptimizationAction(id="WINDOW_TO_FLOOR_RATIO_LOW", title="Bigger", description="Bigger", target_entity_id="window_1", target_entity_type="window", priority=1)
        action2 = OptimizationAction(id="WINDOW_TO_FLOOR_RATIO_LOW", title="Bigger", description="Bigger", target_entity_id="window_1", target_entity_type="window", priority=2)
        plan = ImprovementPlan(actions=[action1, action2])
        result = optimizer.optimize(building_model, plan)
        expected_width = original_width * 1.2 * 1.2
        assert result.optimized_model.windows["window_1"].width == pytest.approx(expected_width)

    def test_action_order_preserved(self, optimizer, building_model):
        action1 = OptimizationAction(id="ROOM_TOO_SMALL", title="Expand", description="Bigger", target_entity_id="room_1", target_entity_type="room", priority=1)
        action2 = OptimizationAction(id="DOOR_TOO_NARROW", title="Widen", description="Wider", target_entity_id="door_1", target_entity_type="door", priority=2)
        plan = ImprovementPlan(actions=[action1, action2])
        result = optimizer.optimize(building_model, plan)
        assert result.applied_actions[0] == action1
        assert result.applied_actions[1] == action2


class TestIntegration:
    def test_end_to_end_optimization(self, building_model):
        """Test full pipeline: RecommendationEngine -> Optimizer."""
        engine = RecommendationEngine()
        from building_model_v2.evaluation.evaluation_report import EvaluationReport
        from building_model_v2.evaluation.evaluation_summary import EvaluationSummary
        from building_model_v2.constraints.scoring import ConstraintScore
        from building_model_v2.validation.validation_result import ValidationResult
        from building_model_v2.constraints.constraint_result import ConstraintResult
        validation_result = None
        constraint_result = None
        score = ConstraintScore(overall_score=50.0, category_scores={"structural": 60.0})
        summary = EvaluationSummary(overall_score=50.0, validation_result=validation_result, constraint_result=constraint_result, constraint_score=score)
        report = EvaluationReport(summary=summary, constraint_issues=[], validation_errors=[])
        plan = engine.generate(report)
        optimizer = Optimizer()
        result = optimizer.optimize(building_model, plan, before_score=50.0, after_score=55.0)
        assert result.original_model is building_model
        assert result.optimized_model is not building_model
        assert isinstance(result, OptimizationResult)

    def test_optimize_with_recommendation_plan(self, optimizer, building_model):
        """Test that optimizer can use a plan from RecommendationEngine."""
        engine = RecommendationEngine()
        from building_model_v2.evaluation.evaluation_report import EvaluationReport
        from building_model_v2.evaluation.evaluation_summary import EvaluationSummary
        from building_model_v2.constraints.scoring import ConstraintScore
        from building_model_v2.validation.validation_result import ValidationResult
        from building_model_v2.constraints.constraint_result import ConstraintResult
        validation_result = None
        constraint_result = None
        score = ConstraintScore(overall_score=50.0, category_scores={})
        summary = EvaluationSummary(overall_score=50.0, validation_result=validation_result, constraint_result=constraint_result, constraint_score=score)
        report = EvaluationReport(summary=summary, constraint_issues=[], validation_errors=[])
        plan = engine.generate(report)
        result = optimizer.optimize(building_model, plan)
        assert isinstance(result, OptimizationResult)
        assert result.before_score == 0.0


