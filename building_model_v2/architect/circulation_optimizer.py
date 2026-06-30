"""Circulation optimizer for architectural circulation analysis.

Deterministically optimizes circulation quality by improving
graph topology. Does NOT use AI or randomness.
"""
from __future__ import annotations

from typing import Any

from .architect_result import ArchitectResult
from .bubble_connection import BubbleConnection
from .bubble_diagram import BubbleDiagram
from .circulation_edge import CirculationEdge
from .circulation_evaluator import CirculationEvaluator
from .circulation_graph import CirculationGraph
from .circulation_optimization_result import CirculationOptimizationResult
from .circulation_planner import CirculationPlanner
from .circulation_result import CirculationResult


class CirculationOptimizer:
    """Deterministic optimizer for circulation quality.

    Improves circulation graphs by applying deterministic rules
    to remove duplicates, eliminate isolated rooms, and reduce dead ends.
    """

    def __init__(self) -> None:
        """Initialize the circulation optimizer."""
        self._evaluator = CirculationEvaluator()
        self._planner = CirculationPlanner()

    def optimize(self, architect_result: ArchitectResult) -> CirculationOptimizationResult:
        """Optimize circulation from an architect result.

        Args:
            architect_result: The architect result containing a bubble diagram.

        Returns:
            CirculationOptimizationResult with original and optimized scores.
        """
        # Step 1: Plan initial circulation
        original_circulation = self._planner.plan(architect_result)

        # Step 2: Evaluate original
        original_metrics, original_score = self._evaluator.evaluate(original_circulation)

        # Step 3: If perfect score, no optimization needed
        if original_score.overall_score >= 95.0 and original_metrics.connectivity_ratio >= 1.0:
            return CirculationOptimizationResult(
                original_score=original_score,
                optimized_score=original_score,
                improvements=("No optimization required - circulation is optimal",),
                modified_connections=(),
                iteration_count=0,
                circulation_result=original_circulation,
            )

        # Step 4: Optimize bubble diagram connections
        improved_diagram, modifications = self._optimize_bubble_diagram(
            architect_result.bubble_diagram
        )

        # Step 5: Replan with optimized diagram
        improved_architect = ArchitectResult(
            bubble_diagram=improved_diagram,
            zoning_result=architect_result.zoning_result,
            metadata=dict(architect_result.metadata),
        )
        optimized_circulation = self._planner.plan(improved_architect)

        # Step 6: Re-evaluate
        optimized_metrics, optimized_score = self._evaluator.evaluate(optimized_circulation)

        # Step 7: Build improvements list
        improvements: list[str] = []
        if optimized_metrics.connectivity_ratio > original_metrics.connectivity_ratio:
            improvements.append(
                f"Improved connectivity ratio from {original_metrics.connectivity_ratio:.2f} "
                f"to {optimized_metrics.connectivity_ratio:.2f}"
            )
        if optimized_metrics.isolated_room_count < original_metrics.isolated_room_count:
            improvements.append(
                f"Reduced isolated rooms from {original_metrics.isolated_room_count} "
                f"to {optimized_metrics.isolated_room_count}"
            )
        if optimized_metrics.dead_end_count < original_metrics.dead_end_count:
            improvements.append(
                f"Reduced dead ends from {original_metrics.dead_end_count} "
                f"to {optimized_metrics.dead_end_count}"
            )
        if optimized_metrics.total_path_length != original_metrics.total_path_length:
            improvements.append(
                f"Adjusted total path length from {original_metrics.total_path_length:.1f}m "
                f"to {optimized_metrics.total_path_length:.1f}m"
            )

        if not improvements:
            improvements.append("No improvements possible with current rules")

        return CirculationOptimizationResult(
            original_score=original_score,
            optimized_score=optimized_score,
            improvements=tuple(improvements),
            modified_connections=tuple(modifications),
            iteration_count=1,
            circulation_result=optimized_circulation,
        )

    def _optimize_bubble_diagram(
        self, diagram: BubbleDiagram
    ) -> tuple[BubbleDiagram, list[str]]:
        """Optimize a bubble diagram by improving connections.

        Args:
            diagram: The bubble diagram to optimize.

        Returns:
            Tuple of (optimized BubbleDiagram, list of modifications).
        """
        modifications: list[str] = []

        # Step 1: Remove duplicate connections
        deduped_connections, dup_count = self._deduplicate_connections(diagram.connections)
        if dup_count > 0:
            modifications.append(f"Removed {dup_count} duplicate connection(s)")

        # Step 2: Identify isolated nodes
        isolated_nodes = self._find_isolated_nodes(diagram.nodes, deduped_connections)

        # Step 3: Connect isolated nodes to nearest connected node
        improved_connections = list(deduped_connections)
        for node_id in isolated_nodes:
            target = self._find_connection_target(node_id, diagram.nodes, improved_connections)
            if target is not None:
                improved_connections.append(
                    BubbleConnection(
                        source_id=node_id,
                        target_id=target,
                        weight=0.5,
                        required=True,
                    )
                )
                modifications.append(f"Connected isolated node '{node_id}' to '{target}'")

        # Step 4: Try to reduce dead ends by connecting pairs
        reduced_connections, dead_end_mods = self._reduce_dead_ends(
            diagram.nodes, improved_connections
        )
        improved_connections = reduced_connections
        modifications.extend(dead_end_mods)

        # Build optimized diagram
        optimized_diagram = BubbleDiagram(
            nodes=diagram.nodes,
            connections=tuple(improved_connections),
        )

        return optimized_diagram, modifications

    def _deduplicate_connections(
        self,
        connections: tuple[BubbleConnection, ...],
    ) -> tuple[list[BubbleConnection], int]:
        """Remove duplicate connections.

        Args:
            connections: Original connections.

        Returns:
            Tuple of (deduplicated connections, number of duplicates removed).
        """
        seen: set[tuple[str, str]] = set()
        deduped: list[BubbleConnection] = []
        dup_count = 0

        for conn in connections:
            pair = (conn.source_id, conn.target_id)
            reverse = (conn.target_id, conn.source_id)
            if pair in seen or reverse in seen:
                dup_count += 1
                continue
            seen.add(pair)
            deduped.append(conn)

        return deduped, dup_count

    def _find_isolated_nodes(
        self,
        nodes: tuple[BubbleNode, ...],
        connections: list[BubbleConnection],
    ) -> list[str]:
        """Find nodes with no connections.

        Args:
            nodes: All nodes.
            connections: Current connections.

        Returns:
            List of isolated node IDs.
        """
        connected = set()
        for conn in connections:
            connected.add(conn.source_id)
            connected.add(conn.target_id)

        return [node.id for node in nodes if node.id not in connected]

    def _find_connection_target(
        self,
        isolated_id: str,
        all_nodes: tuple[BubbleNode, ...],
        existing_connections: list[BubbleConnection],
    ) -> str | None:
        """Find the best target to connect an isolated node to.

        Uses deterministic selection: first connected node by ID order.

        Args:
            isolated_id: The isolated node ID.
            all_nodes: All nodes in the diagram.
            existing_connections: Existing connections.

        Returns:
            Target node ID, or None if no target found.
        """
        connected = set()
        for conn in existing_connections:
            connected.add(conn.source_id)
            connected.add(conn.target_id)

        # Sort nodes by ID for deterministic selection
        sorted_nodes = sorted(all_nodes, key=lambda n: n.id)

        for node in sorted_nodes:
            if node.id != isolated_id and node.id in connected:
                return node.id

        # If no connected nodes, return first other node
        for node in sorted_nodes:
            if node.id != isolated_id:
                return node.id

        return None

    def _reduce_dead_ends(
        self,
        nodes: tuple[BubbleNode, ...],
        connections: list[BubbleConnection],
    ) -> tuple[list[BubbleConnection], list[str]]:
        """Try to reduce dead ends by connecting pairs.

        Args:
            nodes: All nodes.
            connections: Current connections.

        Returns:
            Tuple of (improved connections, list of modifications).
        """
        modifications: list[str] = []

        # Compute degrees
        degree: dict[str, int] = {node.id: 0 for node in nodes}
        for conn in connections:
            degree[conn.source_id] += 1
            degree[conn.target_id] += 1

        # Find dead ends (degree == 1)
        dead_ends = [nid for nid, deg in degree.items() if deg == 1]

        # Sort for deterministic pairing
        dead_ends_sorted = sorted(dead_ends)

        # Pair up dead ends
        added_connections = list(connections)
        i = 0
        while i < len(dead_ends_sorted) - 1:
            n1 = dead_ends_sorted[i]
            n2 = dead_ends_sorted[i + 1]

            # Check if already connected
            already = False
            for conn in added_connections:
                if (conn.source_id == n1 and conn.target_id == n2) or (
                    conn.source_id == n2 and conn.target_id == n1
                ):
                    already = True
                    break

            if not already:
                added_connections.append(
                    BubbleConnection(
                        source_id=n1,
                        target_id=n2,
                        weight=0.5,
                    )
                )
                modifications.append(f"Connected dead-end nodes '{n1}' and '{n2}'")

            i += 2

        return added_connections, modifications


# Alias for compatibility
CirculationOptimizationResult = CirculationOptimizationResult