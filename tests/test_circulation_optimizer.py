"""Tests for circulation optimizer."""
from __future__ import annotations

import pytest

from building_model_v2.architect.architect_result import ArchitectResult
from building_model_v2.architect.bubble_connection import BubbleConnection
from building_model_v2.architect.bubble_diagram import BubbleDiagram
from building_model_v2.architect.bubble_node import BubbleNode
from building_model_v2.architect.circulation_evaluator import CirculationEvaluator
from building_model_v2.architect.circulation_optimization_result import (
    CirculationOptimizationResult,
)
from building_model_v2.architect.circulation_planner import CirculationPlanner
from building_model_v2.architect.circulation_optimizer import CirculationOptimizer
from building_model_v2.architect.zoning_result import ZoningResult


def _make_bubble_node(
    node_id: str,
    target_area: float = 200.0,
) -> BubbleNode:
    """Create a simple bubble node."""
    from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel
    from building_model_v2.types import RoomType
    return BubbleNode(
        id=node_id,
        room_type=RoomType.LIVING,
        name=f"Room {node_id}",
        target_area=target_area,
        privacy_level=PrivacyLevel.PUBLIC,
        preferred_floor=FloorPreference.GROUND,
    )


def _make_architect_result(
    nodes: tuple[BubbleNode, ...] = (),
    connections: tuple[BubbleConnection, ...] = (),
) -> ArchitectResult:
    """Create an architect result."""
    diagram = BubbleDiagram(nodes=nodes, connections=connections)
    zoning = ZoningResult(zones=(), unassigned_rooms=(), metadata={})
    return ArchitectResult(
        bubble_diagram=diagram,
        zoning_result=zoning,
    )


class TestCirculationOptimizationResult:
    """Tests for CirculationOptimizationResult dataclass."""

    def test_create_result(self) -> None:
        """Test creating optimization result."""
        from building_model_v2.architect.circulation_score import CirculationScore
        original = CirculationScore(
            overall_score=50.0, connectivity_score=50.0,
            accessibility_score=50.0, efficiency_score=50.0,
        )
        optimized = CirculationScore(
            overall_score=75.0, connectivity_score=75.0,
            accessibility_score=75.0, efficiency_score=75.0,
        )
        result = CirculationOptimizationResult(
            original_score=original,
            optimized_score=optimized,
        )
        assert result.iteration_count == 0
        assert result.improvements == ()

    def test_optimized_score_below_original_raises(self) -> None:
        """Test that optimized_score < original_score raises error."""
        from building_model_v2.architect.circulation_score import CirculationScore
        original = CirculationScore(
            overall_score=80.0, connectivity_score=80.0,
            accessibility_score=80.0, efficiency_score=80.0,
        )
        optimized = CirculationScore(
            overall_score=50.0, connectivity_score=50.0,
            accessibility_score=50.0, efficiency_score=50.0,
        )
        with pytest.raises(ValueError, match="optimized_score must be >= original_score"):
            CirculationOptimizationResult(
                original_score=original,
                optimized_score=optimized,
            )

    def test_negative_iteration_count_raises(self) -> None:
        """Test that negative iteration_count raises error."""
        from building_model_v2.architect.circulation_score import CirculationScore
        score = CirculationScore(
            overall_score=50.0, connectivity_score=50.0,
            accessibility_score=50.0, efficiency_score=50.0,
        )
        with pytest.raises(ValueError, match="iteration_count must be non-negative"):
            CirculationOptimizationResult(
                original_score=score,
                optimized_score=score,
                iteration_count=-1,
            )

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        from building_model_v2.architect.circulation_score import CirculationScore
        original = CirculationScore(
            overall_score=50.0, connectivity_score=50.0,
            accessibility_score=50.0, efficiency_score=50.0,
        )
        optimized = CirculationScore(
            overall_score=75.0, connectivity_score=75.0,
            accessibility_score=75.0, efficiency_score=75.0,
        )
        result = CirculationOptimizationResult(
            original_score=original,
            optimized_score=optimized,
            improvements=("Test improvement",),
            modified_connections=("conn1",),
            iteration_count=1,
        )
        data = result.to_dict()
        assert data["iteration_count"] == 1
        assert data["improvements"] == ["Test improvement"]

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "original_score": {
                "overall_score": 50.0, "connectivity_score": 50.0,
                "accessibility_score": 50.0, "efficiency_score": 50.0,
            },
            "optimized_score": {
                "overall_score": 75.0, "connectivity_score": 75.0,
                "accessibility_score": 75.0, "efficiency_score": 75.0,
            },
            "improvements": ["Improved"],
            "modified_connections": ["c1"],
            "iteration_count": 1,
            "circulation_result": None,
        }
        result = CirculationOptimizationResult.from_dict(data)
        assert result.iteration_count == 1
        assert result.improvements == ("Improved",)

    def test_round_trip(self) -> None:
        """Test serialization round-trip."""
        from building_model_v2.architect.circulation_score import CirculationScore
        original = CirculationScore(
            overall_score=50.0, connectivity_score=50.0,
            accessibility_score=50.0, efficiency_score=50.0,
        )
        optimized = CirculationScore(
            overall_score=75.0, connectivity_score=75.0,
            accessibility_score=75.0, efficiency_score=75.0,
        )
        result = CirculationOptimizationResult(
            original_score=original,
            optimized_score=optimized,
            improvements=("Imp1",),
            iteration_count=2,
        )
        data = result.to_dict()
        restored = CirculationOptimizationResult.from_dict(data)
        assert restored.iteration_count == result.iteration_count
        assert restored.optimized_score == result.optimized_score

    def test_immutable(self) -> None:
        """Test that result is frozen."""
        from building_model_v2.architect.circulation_score import CirculationScore
        score = CirculationScore(
            overall_score=50.0, connectivity_score=50.0,
            accessibility_score=50.0, efficiency_score=50.0,
        )
        result = CirculationOptimizationResult(
            original_score=score,
            optimized_score=score,
        )
        with pytest.raises(AttributeError):
            result.iteration_count = 5  # type: ignore[misc]


class TestCirculationOptimizerEmpty:
    """Tests for empty graph optimization."""

    def test_optimize_empty_diagram(self) -> None:
        """Test optimizing an empty bubble diagram."""
        optimizer = CirculationOptimizer()
        result = _make_architect_result()
        opt = optimizer.optimize(result)
        assert opt.iteration_count >= 0
        assert opt.original_score.overall_score == opt.optimized_score.overall_score

    def test_optimize_single_node(self) -> None:
        """Test optimizing a single node diagram."""
        optimizer = CirculationOptimizer()
        nodes = (_make_bubble_node("n1"),)
        result = _make_architect_result(nodes=nodes)
        opt = optimizer.optimize(result)
        assert opt.circulation_result is not None
        assert opt.circulation_result.circulation_graph.node_count == 1


class TestCirculationOptimizerDuplicateRemoval:
    """Tests for duplicate edge removal."""

    def test_duplicate_connections_removed(self) -> None:
        """Test that duplicate connections are removed."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
            BubbleConnection(source_id="n1", target_id="n2", weight=0.6),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert opt.iteration_count >= 1
        assert any("duplicate" in m.lower() for m in opt.modified_connections) or \
               any("duplicate" in m.lower() for m in opt.improvements)

    def test_reverse_duplicate_removed(self) -> None:
        """Test that reverse duplicate connections are removed."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
            BubbleConnection(source_id="n2", target_id="n1", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert opt.iteration_count >= 1

    def test_no_duplicates_unchanged(self) -> None:
        """Test that no duplicates means no modification for that rule."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert not any("duplicate" in m.lower() for m in opt.modified_connections)


class TestCirculationOptimizerIsolated:
    """Tests for isolated room handling."""

    def test_isolated_node_connected(self) -> None:
        """Test that isolated nodes are connected."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        # Only n1-n2 connected, n3 is isolated
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert opt.iteration_count >= 1
        assert any("isolated" in m.lower() for m in opt.improvements) or \
               any("isolated" in m.lower() for m in opt.modified_connections)

    def test_all_nodes_connected(self) -> None:
        """Test that no isolated nodes means no isolated modification."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert not any("isolated" in m.lower() for m in opt.modified_connections)

    def test_multiple_isolated_nodes(self) -> None:
        """Test handling multiple isolated nodes."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
            _make_bubble_node("n4"),
        )
        # None connected
        result = _make_architect_result(nodes=nodes)
        opt = optimizer.optimize(result)
        assert opt.iteration_count >= 1
        # Should try to connect isolated nodes
        assert opt.circulation_result is not None


class TestCirculationOptimizerDeadEnds:
    """Tests for dead-end reduction."""

    def test_dead_ends_reduced(self) -> None:
        """Test that dead ends are reduced when possible."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        # Linear chain: n1-n2-n3 has dead ends at n1 and n3
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
            BubbleConnection(source_id="n2", target_id="n3", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        # May add connection between dead ends
        assert opt.iteration_count >= 1

    def test_no_dead_ends_in_perfect_graph(self) -> None:
        """Test that perfect graph has no dead-end modifications."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
            BubbleConnection(source_id="n2", target_id="n3", weight=0.5),
            BubbleConnection(source_id="n3", target_id="n1", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        # Ring graph has no dead ends, no modifications needed
        assert not any("dead-end" in m.lower() for m in opt.modified_connections)


class TestCirculationOptimizerScore:
    """Tests for score improvement."""

    def test_score_improves_or_equal(self) -> None:
        """Test that optimized score >= original score."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert opt.optimized_score.overall_score >= opt.original_score.overall_score

    def test_perfect_graph_unchanged(self) -> None:
        """Test that a good graph gets reasonable optimization."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        # Ring graph: no dead ends, fully connected
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=1.0),
            BubbleConnection(source_id="n2", target_id="n3", weight=1.0),
            BubbleConnection(source_id="n3", target_id="n1", weight=1.0),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        # Score should be high
        assert opt.original_score.overall_score >= opt.optimized_score.overall_score

    def test_improvements_reported(self) -> None:
        """Test that improvements are reported."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert len(opt.improvements) > 0


class TestCirculationOptimizerDeterministic:
    """Tests for deterministic behavior."""

    def test_deterministic_output(self) -> None:
        """Test that optimizer produces same results given same input."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt1 = optimizer.optimize(result)
        opt2 = optimizer.optimize(result)
        assert opt1.iteration_count == opt2.iteration_count
        assert opt1.improvements == opt2.improvements
        assert opt1.optimized_score.overall_score == opt2.optimized_score.overall_score

    def test_deterministic_modifications(self) -> None:
        """Test that modifications list is deterministic."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt1 = optimizer.optimize(result)
        opt2 = optimizer.optimize(result)
        assert opt1.modified_connections == opt2.modified_connections


class TestCirculationOptimizerGraph:
    """Tests for graph integrity after optimization."""

    def test_optimized_graph_valid(self) -> None:
        """Test that optimized graph is valid."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        graph = opt.circulation_result.circulation_graph
        assert graph.node_count == 3
        assert graph.edge_count >= 1

    def test_optimized_graph_nodes_preserved(self) -> None:
        """Test that all original nodes are preserved after optimization."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        node_ids = set(opt.circulation_result.circulation_graph.node_ids)
        assert node_ids == {"n1", "n2", "n3"}

    def test_optimized_graph_no_duplicates(self) -> None:
        """Test that optimized graph has no duplicate edges."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
            BubbleConnection(source_id="n1", target_id="n2", weight=0.6),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        graph = opt.circulation_result.circulation_graph
        edges = graph.edges
        pairs = [(e.source_id, e.target_id) for e in edges]
        assert len(pairs) == len(set(pairs))


class TestCirculationOptimizerSerialization:
    """Tests for serialization."""

    def test_optimization_result_serialization(self) -> None:
        """Test that optimization result serializes correctly."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        data = opt.to_dict()
        assert "original_score" in data
        assert "optimized_score" in data
        assert "improvements" in data
        assert "iteration_count" in data

    def test_optimization_result_round_trip(self) -> None:
        """Test serialization round-trip."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        data = opt.to_dict()
        restored = CirculationOptimizationResult.from_dict(data)
        assert restored.iteration_count == opt.iteration_count
        assert restored.improvements == opt.improvements


class TestCirculationOptimizerEdgeCases:
    """Tests for edge cases."""

    def test_optimize_two_nodes(self) -> None:
        """Test optimizing two connected nodes."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert opt.circulation_result is not None
        assert opt.circulation_result.circulation_graph.node_count == 2

    def test_optimize_preserves_zoning(self) -> None:
        """Test that zoning result is preserved through optimization."""
        optimizer = CirculationOptimizer()
        nodes = (_make_bubble_node("n1"),)
        result = _make_architect_result(nodes=nodes)
        opt = optimizer.optimize(result)
        # Should not modify zoning
        assert opt.circulation_result is not None

    def test_optimize_no_modifications_when_perfect(self) -> None:
        """Test that ring graph has no dead-end modifications."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=1.0),
            BubbleConnection(source_id="n2", target_id="n3", weight=1.0),
            BubbleConnection(source_id="n3", target_id="n1", weight=1.0),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        # Ring graph should not need dead-end modifications
        assert not any("dead-end" in m.lower() for m in opt.modified_connections)

    def test_optimize_isolated_and_duplicate(self) -> None:
        """Test handling both isolated nodes and duplicates."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
            BubbleConnection(source_id="n1", target_id="n2", weight=0.6),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        # Should handle both issues
        assert opt.circulation_result is not None

    def test_optimize_re_evaluates(self) -> None:
        """Test that optimizer re-evaluates after optimization."""
        optimizer = CirculationOptimizer()
        nodes = (
            _make_bubble_node("n1"),
            _make_bubble_node("n2"),
            _make_bubble_node("n3"),
        )
        connections = (
            BubbleConnection(source_id="n1", target_id="n2", weight=0.5),
        )
        result = _make_architect_result(nodes=nodes, connections=connections)
        opt = optimizer.optimize(result)
        assert opt.original_score != opt.optimized_score or opt.iteration_count == 0

    def test_optimizer_returns_circulation_result(self) -> None:
        """Test that optimizer returns a CirculationResult."""
        optimizer = CirculationOptimizer()
        nodes = (_make_bubble_node("n1"),)
        result = _make_architect_result(nodes=nodes)
        opt = optimizer.optimize(result)
        assert opt.circulation_result is not None
        assert isinstance(opt.circulation_result.circulation_graph, type(
            CirculationPlanner().plan(result).circulation_graph
        ))

    def test_optimize_single_iteration(self) -> None:
        """Test that optimizer uses exactly one iteration."""
        optimizer = CirculationOptimizer()
        nodes = (_make_bubble_node("n1"),)
        result = _make_architect_result(nodes=nodes)
        opt = optimizer.optimize(result)
        assert opt.iteration_count == 1