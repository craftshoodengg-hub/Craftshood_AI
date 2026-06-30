"""Circulation evaluator for architectural circulation analysis.

Deterministically computes circulation metrics and quality scores
from a CirculationResult. Does NOT modify or optimize layouts.
"""
from __future__ import annotations

from typing import Any

from .circulation_edge import CirculationEdge
from .circulation_graph import CirculationGraph
from .circulation_metrics import CirculationMetrics
from .circulation_result import CirculationResult
from .circulation_score import CirculationScore


class CirculationEvaluator:
    """Deterministic evaluator for circulation quality.

    Computes metrics and scores from a CirculationResult without
    modifying the underlying data.
    """

    _PRIMARY_WIDTH_THRESHOLD: float = 1.5

    def evaluate(
        self,
        circulation: CirculationResult,
    ) -> tuple[CirculationMetrics, CirculationScore]:
        """Evaluate a circulation result and produce metrics and scores.

        Computes connectivity, accessibility, and efficiency metrics
        from the circulation graph, then derives quality scores.

        Args:
            circulation: The circulation result to evaluate.

        Returns:
            Tuple of (CirculationMetrics, CirculationScore).
        """
        graph = circulation.circulation_graph

        metrics = self._compute_metrics(graph)
        score = self._compute_score(metrics)

        return metrics, score

    def _compute_metrics(self, graph: CirculationGraph) -> CirculationMetrics:
        """Compute metrics from a circulation graph.

        Args:
            graph: The circulation graph to analyze.

        Returns:
            Computed CirculationMetrics.
        """
        edges = graph.edges
        nodes = graph.nodes

        total_path_length = graph.total_path_length()

        edge_count = len(edges)
        average_path_length = total_path_length / edge_count if edge_count > 0 else 0.0

        primary_path_count = sum(
            1 for edge in edges if edge.width >= self._PRIMARY_WIDTH_THRESHOLD
        )
        secondary_path_count = edge_count - primary_path_count

        # Compute node degrees
        node_ids = list(graph.node_ids)
        degree: dict[str, int] = {nid: 0 for nid in node_ids}
        for edge in edges:
            degree[edge.source_id] += 1
            degree[edge.target_id] += 1

        dead_end_count = sum(1 for deg in degree.values() if deg == 1)
        isolated_room_count = sum(1 for deg in degree.values() if deg == 0)
        connected_room_count = len(nodes) - isolated_room_count

        connectivity_ratio = (
            connected_room_count / len(nodes) if len(nodes) > 0 else 0.0
        )

        return CirculationMetrics(
            total_path_length=total_path_length,
            average_path_length=average_path_length,
            primary_path_count=primary_path_count,
            secondary_path_count=secondary_path_count,
            dead_end_count=dead_end_count,
            isolated_room_count=isolated_room_count,
            connected_room_count=connected_room_count,
            connectivity_ratio=connectivity_ratio,
        )

    def _compute_score(self, metrics: CirculationMetrics) -> CirculationScore:
        """Compute quality scores from metrics.

        Scoring rules:
        - connectivity_score: Based on connectivity_ratio (100 * ratio)
        - accessibility_score: Based on primary paths vs dead ends
        - efficiency_score: Based on average path length relative to ideal
        - penalties: Applied for dead ends, isolated rooms, poor accessibility
        - overall_score: Weighted combination with penalties

        Args:
            metrics: The computed metrics.

        Returns:
            Computed CirculationScore with recommendations.
        """
        penalties: list[str] = []
        recommendations: list[str] = []

        # Connectivity score: perfect if all rooms connected
        connectivity_score = metrics.connectivity_ratio * 100.0

        if metrics.isolated_room_count > 0:
            penalties.append(
                f"{metrics.isolated_room_count} isolated room(s) with no connections"
            )
            recommendations.append(
                "Connect isolated rooms to the circulation network"
            )

        # Accessibility score: based on primary paths and dead ends
        total_paths = metrics.primary_path_count + metrics.secondary_path_count
        if total_paths > 0:
            primary_ratio = metrics.primary_path_count / total_paths
            accessibility_score = primary_ratio * 100.0
        else:
            accessibility_score = 0.0

        if metrics.dead_end_count > 0:
            dead_end_penalty = min(metrics.dead_end_count * 10.0, 30.0)
            accessibility_score = max(0.0, accessibility_score - dead_end_penalty)
            if metrics.dead_end_count > 1:
                penalties.append(
                    f"{metrics.dead_end_count} dead-end path(s) reduce accessibility"
                )
                recommendations.append(
                    "Reduce dead-end paths by creating loops in circulation"
                )

        # Efficiency score: based on average path length
        if metrics.average_path_length <= 0:
            efficiency_score = 100.0
        elif metrics.average_path_length <= 3.0:
            efficiency_score = 90.0
        elif metrics.average_path_length <= 5.0:
            efficiency_score = 75.0
        elif metrics.average_path_length <= 8.0:
            efficiency_score = 50.0
        else:
            efficiency_score = 25.0

        if efficiency_score < 50.0:
            penalties.append(
                f"Average path length of {metrics.average_path_length:.1f}m is inefficient"
            )
            recommendations.append(
                "Reduce circulation path lengths for better efficiency"
            )

        if metrics.secondary_path_count > 0 and metrics.primary_path_count == 0:
            if metrics.secondary_path_count > 0:
                penalties.append("No primary circulation paths found")
                recommendations.append(
                    "Widen corridors to create primary circulation paths (>= 1.5m)"
                )

        # Overall score: weighted combination minus penalties
        base_score = (
            connectivity_score * 0.4
            + accessibility_score * 0.35
            + efficiency_score * 0.25
        )
        penalty_total = len(penalties) * 5.0
        overall_score = max(0.0, min(100.0, base_score - penalty_total))

        return CirculationScore(
            overall_score=round(overall_score, 1),
            connectivity_score=round(connectivity_score, 1),
            accessibility_score=round(accessibility_score, 1),
            efficiency_score=round(efficiency_score, 1),
            penalties=tuple(penalties),
            recommendations=tuple(recommendations),
        )