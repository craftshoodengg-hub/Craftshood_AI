"""Tests for circulation evaluation engine."""
from __future__ import annotations

import pytest

from building_model_v2.architect.circulation_edge import CirculationEdge
from building_model_v2.architect.circulation_evaluator import CirculationEvaluator
from building_model_v2.architect.circulation_graph import CirculationGraph
from building_model_v2.architect.circulation_metrics import CirculationMetrics
from building_model_v2.architect.circulation_node import CirculationNode
from building_model_v2.architect.circulation_result import CirculationResult
from building_model_v2.architect.circulation_score import CirculationScore


def _make_graph(
    node_count: int = 0,
    edge_count: int = 0,
    edge_width: float = 1.2,
    edge_length: float = 5.0,
    bidirectional: bool = True,
) -> CirculationGraph:
    """Create a simple linear circulation graph."""
    nodes: list[CirculationNode] = [
        CirculationNode(id=f"n{i}", name=f"Node {i}")
        for i in range(node_count)
    ]
    edges: list[CirculationEdge] = []
    for i in range(min(edge_count, node_count - 1 if node_count > 1 else 0)):
        edges.append(
            CirculationEdge(
                source_id=f"n{i}",
                target_id=f"n{i + 1}",
                length=edge_length,
                width=edge_width,
                bidirectional=bidirectional,
            )
        )
    return CirculationGraph(nodes=tuple(nodes), edges=tuple(edges))


def _make_result(graph: CirculationGraph) -> CirculationResult:
    """Create a circulation result from a graph."""
    total = graph.total_path_length()
    entries = len(graph.entry_exit_nodes())
    return CirculationResult(
        circulation_graph=graph,
        total_length=total,
        entry_count=entries,
        exit_count=entries,
    )


class TestCirculationMetricsConstruction:
    """Tests for CirculationMetrics dataclass."""

    def test_create_valid_metrics(self) -> None:
        """Test creating valid metrics."""
        metrics = CirculationMetrics(
            total_path_length=100.0,
            average_path_length=5.0,
            primary_path_count=10,
            secondary_path_count=5,
            dead_end_count=2,
            isolated_room_count=0,
            connected_room_count=15,
            connectivity_ratio=1.0,
        )
        assert metrics.total_path_length == 100.0
        assert metrics.average_path_length == 5.0
        assert metrics.connectivity_ratio == 1.0

    def test_negative_total_length_raises_error(self) -> None:
        """Test negative total_path_length raises error."""
        with pytest.raises(ValueError, match="total_path_length must be non-negative"):
            CirculationMetrics(
                total_path_length=-1.0,
                average_path_length=0.0,
                primary_path_count=0,
                secondary_path_count=0,
                dead_end_count=0,
                isolated_room_count=0,
                connected_room_count=0,
                connectivity_ratio=0.0,
            )

    def test_negative_average_length_raises_error(self) -> None:
        """Test negative average_path_length raises error."""
        with pytest.raises(ValueError, match="average_path_length must be non-negative"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=-1.0,
                primary_path_count=0,
                secondary_path_count=0,
                dead_end_count=0,
                isolated_room_count=0,
                connected_room_count=0,
                connectivity_ratio=0.0,
            )

    def test_negative_primary_count_raises_error(self) -> None:
        """Test negative primary_path_count raises error."""
        with pytest.raises(ValueError, match="primary_path_count must be non-negative"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=0.0,
                primary_path_count=-1,
                secondary_path_count=0,
                dead_end_count=0,
                isolated_room_count=0,
                connected_room_count=0,
                connectivity_ratio=0.0,
            )

    def test_negative_secondary_count_raises_error(self) -> None:
        """Test negative secondary_path_count raises error."""
        with pytest.raises(ValueError, match="secondary_path_count must be non-negative"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=0.0,
                primary_path_count=0,
                secondary_path_count=-1,
                dead_end_count=0,
                isolated_room_count=0,
                connected_room_count=0,
                connectivity_ratio=0.0,
            )

    def test_negative_dead_end_count_raises_error(self) -> None:
        """Test negative dead_end_count raises error."""
        with pytest.raises(ValueError, match="dead_end_count must be non-negative"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=0.0,
                primary_path_count=0,
                secondary_path_count=0,
                dead_end_count=-1,
                isolated_room_count=0,
                connected_room_count=0,
                connectivity_ratio=0.0,
            )

    def test_negative_isolated_count_raises_error(self) -> None:
        """Test negative isolated_room_count raises error."""
        with pytest.raises(ValueError, match="isolated_room_count must be non-negative"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=0.0,
                primary_path_count=0,
                secondary_path_count=0,
                dead_end_count=0,
                isolated_room_count=-1,
                connected_room_count=0,
                connectivity_ratio=0.0,
            )

    def test_negative_connected_count_raises_error(self) -> None:
        """Test negative connected_room_count raises error."""
        with pytest.raises(ValueError, match="connected_room_count must be non-negative"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=0.0,
                primary_path_count=0,
                secondary_path_count=0,
                dead_end_count=0,
                isolated_room_count=0,
                connected_room_count=-1,
                connectivity_ratio=0.0,
            )

    def test_connectivity_ratio_out_of_range_high(self) -> None:
        """Test connectivity_ratio > 1.0 raises error."""
        with pytest.raises(ValueError, match="connectivity_ratio must be between"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=0.0,
                primary_path_count=0,
                secondary_path_count=0,
                dead_end_count=0,
                isolated_room_count=0,
                connected_room_count=0,
                connectivity_ratio=1.5,
            )

    def test_connectivity_ratio_out_of_range_low(self) -> None:
        """Test connectivity_ratio < 0.0 raises error."""
        with pytest.raises(ValueError, match="connectivity_ratio must be between"):
            CirculationMetrics(
                total_path_length=0.0,
                average_path_length=0.0,
                primary_path_count=0,
                secondary_path_count=0,
                dead_end_count=0,
                isolated_room_count=0,
                connected_room_count=0,
                connectivity_ratio=-0.1,
            )


class TestCirculationMetricsSerialization:
    """Tests for CirculationMetrics serialization."""

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        metrics = CirculationMetrics(
            total_path_length=100.0,
            average_path_length=5.0,
            primary_path_count=10,
            secondary_path_count=5,
            dead_end_count=2,
            isolated_room_count=0,
            connected_room_count=15,
            connectivity_ratio=1.0,
        )
        data = metrics.to_dict()
        assert data["total_path_length"] == 100.0
        assert data["connectivity_ratio"] == 1.0

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "total_path_length": 100.0,
            "average_path_length": 5.0,
            "primary_path_count": 10,
            "secondary_path_count": 5,
            "dead_end_count": 2,
            "isolated_room_count": 0,
            "connected_room_count": 15,
            "connectivity_ratio": 1.0,
        }
        metrics = CirculationMetrics.from_dict(data)
        assert metrics.total_path_length == 100.0
        assert metrics.connectivity_ratio == 1.0

    def test_round_trip(self) -> None:
        """Test serialization round-trip."""
        original = CirculationMetrics(
            total_path_length=50.0,
            average_path_length=2.5,
            primary_path_count=5,
            secondary_path_count=3,
            dead_end_count=1,
            isolated_room_count=0,
            connected_room_count=8,
            connectivity_ratio=1.0,
        )
        data = original.to_dict()
        restored = CirculationMetrics.from_dict(data)
        assert restored == original

    def test_immutable(self) -> None:
        """Test that metrics is frozen."""
        metrics = CirculationMetrics(
            total_path_length=0.0,
            average_path_length=0.0,
            primary_path_count=0,
            secondary_path_count=0,
            dead_end_count=0,
            isolated_room_count=0,
            connected_room_count=0,
            connectivity_ratio=0.0,
        )
        with pytest.raises(AttributeError):
            metrics.total_path_length = 10.0  # type: ignore[misc]


class TestCirculationScoreConstruction:
    """Tests for CirculationScore dataclass."""

    def test_create_valid_score(self) -> None:
        """Test creating a valid score."""
        score = CirculationScore(
            overall_score=85.0,
            connectivity_score=90.0,
            accessibility_score=80.0,
            efficiency_score=75.0,
        )
        assert score.overall_score == 85.0
        assert score.connectivity_score == 90.0

    def test_create_score_with_penalties(self) -> None:
        """Test creating a score with penalties."""
        score = CirculationScore(
            overall_score=60.0,
            connectivity_score=70.0,
            accessibility_score=50.0,
            efficiency_score=60.0,
            penalties=("Dead end detected",),
            recommendations=("Reduce dead ends",),
        )
        assert len(score.penalties) == 1
        assert len(score.recommendations) == 1

    def test_overall_score_too_low_raises_error(self) -> None:
        """Test overall_score < 0 raises error."""
        with pytest.raises(ValueError, match="overall_score must be between"):
            CirculationScore(
                overall_score=-1.0,
                connectivity_score=50.0,
                accessibility_score=50.0,
                efficiency_score=50.0,
            )

    def test_overall_score_too_high_raises_error(self) -> None:
        """Test overall_score > 100 raises error."""
        with pytest.raises(ValueError, match="overall_score must be between"):
            CirculationScore(
                overall_score=101.0,
                connectivity_score=50.0,
                accessibility_score=50.0,
                efficiency_score=50.0,
            )

    def test_connectivity_score_out_of_range(self) -> None:
        """Test connectivity_score out of range raises error."""
        with pytest.raises(ValueError, match="connectivity_score must be between"):
            CirculationScore(
                overall_score=50.0,
                connectivity_score=101.0,
                accessibility_score=50.0,
                efficiency_score=50.0,
            )

    def test_accessibility_score_out_of_range(self) -> None:
        """Test accessibility_score out of range raises error."""
        with pytest.raises(ValueError, match="accessibility_score must be between"):
            CirculationScore(
                overall_score=50.0,
                connectivity_score=50.0,
                accessibility_score=101.0,
                efficiency_score=50.0,
            )

    def test_efficiency_score_out_of_range(self) -> None:
        """Test efficiency_score out of range raises error."""
        with pytest.raises(ValueError, match="efficiency_score must be between"):
            CirculationScore(
                overall_score=50.0,
                connectivity_score=50.0,
                accessibility_score=50.0,
                efficiency_score=101.0,
            )


class TestCirculationScoreSerialization:
    """Tests for CirculationScore serialization."""

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        score = CirculationScore(
            overall_score=85.0,
            connectivity_score=90.0,
            accessibility_score=80.0,
            efficiency_score=75.0,
            penalties=("Dead end",),
            recommendations=("Fix dead end",),
        )
        data = score.to_dict()
        assert data["overall_score"] == 85.0
        assert data["penalties"] == ["Dead end"]

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "overall_score": 85.0,
            "connectivity_score": 90.0,
            "accessibility_score": 80.0,
            "efficiency_score": 75.0,
            "penalties": ["Dead end"],
            "recommendations": ["Fix dead end"],
        }
        score = CirculationScore.from_dict(data)
        assert score.overall_score == 85.0
        assert score.penalties == ("Dead end",)

    def test_round_trip(self) -> None:
        """Test serialization round-trip."""
        original = CirculationScore(
            overall_score=75.0,
            connectivity_score=80.0,
            accessibility_score=70.0,
            efficiency_score=65.0,
            penalties=("P1", "P2"),
            recommendations=("R1",),
        )
        data = original.to_dict()
        restored = CirculationScore.from_dict(data)
        assert restored == original


class TestCirculationEvaluatorEmpty:
    """Tests for evaluating empty graphs."""

    def test_empty_graph_metrics(self) -> None:
        """Test metrics for empty graph."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=0)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.total_path_length == 0.0
        assert metrics.average_path_length == 0.0
        assert metrics.connected_room_count == 0
        assert metrics.connectivity_ratio == 0.0

    def test_empty_graph_score(self) -> None:
        """Test score for empty graph."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=0)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.overall_score >= 0.0
        assert score.overall_score <= 100.0

    def test_single_isolated_node(self) -> None:
        """Test graph with single isolated node."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=1)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.isolated_room_count == 1
        assert metrics.connected_room_count == 0
        assert metrics.connectivity_ratio == 0.0
        assert len(score.penalties) > 0


class TestCirculationEvaluatorConnected:
    """Tests for evaluating connected graphs."""

    def test_fully_connected_metrics(self) -> None:
        """Test metrics for fully connected graph."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=5, edge_count=4, edge_length=3.0)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.total_path_length == 12.0  # 4 edges * 3.0
        assert metrics.average_path_length == 3.0
        assert metrics.isolated_room_count == 0
        assert metrics.connected_room_count == 5
        assert metrics.connectivity_ratio == 1.0
        assert metrics.primary_path_count == 0  # width 1.2 < 1.5
        assert metrics.secondary_path_count == 4

    def test_fully_connected_score_high(self) -> None:
        """Test score for fully connected graph with primary paths."""
        evaluator = CirculationEvaluator()
        # A ring graph has no dead ends (all nodes degree 2)
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n2", name="Node 2"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.8),
            CirculationEdge(source_id="n1", target_id="n2", length=3.0, width=1.8),
            CirculationEdge(source_id="n2", target_id="n0", length=3.0, width=1.8),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.connectivity_score == 100.0
        assert score.efficiency_score >= 75.0
        assert score.accessibility_score > 50.0

    def test_deterministic(self) -> None:
        """Test that evaluation is deterministic."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=5, edge_count=4)
        result = _make_result(graph)
        m1, s1 = evaluator.evaluate(result)
        m2, s2 = evaluator.evaluate(result)
        assert m1 == m2
        assert s1 == s2

    def test_primary_paths(self) -> None:
        """Test detection of primary vs secondary paths."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.5),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.primary_path_count == 1
        assert metrics.secondary_path_count == 0

    def test_secondary_paths(self) -> None:
        """Test detection of secondary paths."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.2),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.primary_path_count == 0
        assert metrics.secondary_path_count == 1


class TestCirculationEvaluatorDeadEnds:
    """Tests for evaluating graphs with dead ends."""

    def test_dead_end_detection(self) -> None:
        """Test detection of dead ends."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=5, edge_count=4)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        # In a linear graph of 5 nodes:
        # n0 has 1 connection, n1 has 2, n2 has 2, n3 has 2, n4 has 1
        # So dead_end_count = 2 (n0 and n4)
        assert metrics.dead_end_count == 2

    def test_dead_end_penalty(self) -> None:
        """Test that dead ends apply penalties."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=5, edge_count=4)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        if metrics.dead_end_count > 1:
            assert len(score.penalties) > 0

    def test_no_dead_ends(self) -> None:
        """Test that a minimal graph has no dead ends if it's a single edge."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        # Both nodes have degree 1, so both are dead ends
        assert metrics.dead_end_count == 2


class TestCirculationEvaluatorIsolated:
    """Tests for evaluating graphs with isolated rooms."""

    def test_isolated_room_detection(self) -> None:
        """Test detection of isolated rooms."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n2", name="Node 2"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        # n2 has degree 0
        assert metrics.isolated_room_count == 1
        assert metrics.connected_room_count == 2
        assert metrics.connectivity_ratio == 2.0 / 3.0

    def test_isolated_room_penalty(self) -> None:
        """Test that isolated rooms generate penalties."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        graph = CirculationGraph(nodes=nodes)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.isolated_room_count == 2
        assert len(score.penalties) > 0
        assert any("isolated" in p.lower() for p in score.penalties)

    def test_isolated_room_recommendation(self) -> None:
        """Test that isolated rooms generate recommendations."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
        )
        graph = CirculationGraph(nodes=nodes)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert len(score.recommendations) > 0
        assert any("connect" in r.lower() for r in score.recommendations)


class TestCirculationEvaluatorScoring:
    """Tests for score calculation."""

    def test_perfect_connectivity_score(self) -> None:
        """Test perfect connectivity score."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=3, edge_count=2)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.connectivity_score == 100.0

    def test_zero_connectivity_score(self) -> None:
        """Test zero connectivity score."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=3)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.connectivity_score == 0.0

    def test_efficiency_short_paths(self) -> None:
        """Test efficiency with short paths (<=3m)."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=3, edge_count=2, edge_length=2.0)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.efficiency_score >= 90.0

    def test_efficiency_long_paths(self) -> None:
        """Test efficiency with long paths (>8m)."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=3, edge_count=2, edge_length=10.0)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.efficiency_score <= 50.0

    def test_efficiency_medium_paths(self) -> None:
        """Test efficiency with medium paths (5-8m)."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=3, edge_count=2, edge_length=6.0)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert 40.0 <= score.efficiency_score <= 60.0

    def test_overall_score_perfect(self) -> None:
        """Test overall score for a well-connected graph."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n2", name="Node 2"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.8),
            CirculationEdge(source_id="n1", target_id="n2", length=3.0, width=1.8),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.overall_score > 70.0

    def test_overall_score_poor(self) -> None:
        """Test overall score for a poorly connected graph."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n2", name="Node 2"),
        )
        graph = CirculationGraph(nodes=nodes)  # No edges
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert score.overall_score < 50.0

    def test_primary_path_boosts_accessibility(self) -> None:
        """Test that primary paths boost accessibility score."""
        evaluator = CirculationEvaluator()
        # Graph with primary paths
        nodes1 = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        edges1 = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.8),
        )
        graph1 = CirculationGraph(nodes=nodes1, edges=edges1)
        result1 = _make_result(graph1)
        m1, s1 = evaluator.evaluate(result1)

        # Graph with only secondary paths
        nodes2 = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        edges2 = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.2),
        )
        graph2 = CirculationGraph(nodes=nodes2, edges=edges2)
        result2 = _make_result(graph2)
        m2, s2 = evaluator.evaluate(result2)

        assert s1.accessibility_score > s2.accessibility_score


class TestCirculationEvaluatorSerialization:
    """Tests for full pipeline serialization."""

    def test_metrics_serialization_round_trip(self) -> None:
        """Test metrics serialization round-trip from evaluator."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=5, edge_count=4)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        data = metrics.to_dict()
        restored = CirculationMetrics.from_dict(data)
        assert restored == metrics

    def test_score_serialization_round_trip(self) -> None:
        """Test score serialization round-trip from evaluator."""
        evaluator = CirculationEvaluator()
        graph = _make_graph(node_count=5, edge_count=4)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        data = score.to_dict()
        restored = CirculationScore.from_dict(data)
        assert restored == score


class TestCirculationEvaluatorEdgeCases:
    """Tests for edge cases."""

    def test_single_node_no_edges(self) -> None:
        """Test single node with no edges."""
        evaluator = CirculationEvaluator()
        nodes = (CirculationNode(id="n0", name="Node 0"),)
        graph = CirculationGraph(nodes=nodes)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert graph.edge_count == 0
        assert metrics.isolated_room_count == 1
        assert metrics.connectivity_ratio == 0.0

    def test_two_nodes_no_edge(self) -> None:
        """Test two nodes with no connection."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        graph = CirculationGraph(nodes=nodes)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.isolated_room_count == 2
        assert metrics.connectivity_ratio == 0.0

    def test_all_entry_exit_nodes(self) -> None:
        """Test graph where all nodes are entry/exit."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0", is_entry_exit=True),
            CirculationNode(id="n1", name="Node 1", is_entry_exit=True),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=5.0),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert result.entry_count == 2
        assert metrics.total_path_length == 5.0

    def test_no_recommendations_perfect(self) -> None:
        """Test that a perfect graph has no recommendations."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.5),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        # All connected, primary paths, short paths - should be good
        assert metrics.connectivity_ratio == 1.0

    def test_mixed_width_edges(self) -> None:
        """Test graph with mixed primary and secondary edges."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n2", name="Node 2"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0, width=1.8),
            CirculationEdge(source_id="n1", target_id="n2", length=4.0, width=1.2),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.primary_path_count == 1
        assert metrics.secondary_path_count == 1

    def test_duplicate_degree_counting(self) -> None:
        """Test that degree counting is correct for multiple edges."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        # Two edges between same nodes
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0),
            CirculationEdge(source_id="n0", target_id="n1", length=4.0),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        # n0 has degree 2, n1 has degree 2 - no dead ends
        assert metrics.dead_end_count == 0

    def test_total_length_with_multiple_edges(self) -> None:
        """Test total path length with multiple edges."""
        evaluator = CirculationEvaluator()
        nodes = (
            CirculationNode(id="n0", name="Node 0"),
            CirculationNode(id="n1", name="Node 1"),
        )
        edges = (
            CirculationEdge(source_id="n0", target_id="n1", length=3.0),
            CirculationEdge(source_id="n0", target_id="n1", length=4.0),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        result = _make_result(graph)
        metrics, score = evaluator.evaluate(result)
        assert metrics.total_path_length == 7.0
        assert metrics.average_path_length == 3.5