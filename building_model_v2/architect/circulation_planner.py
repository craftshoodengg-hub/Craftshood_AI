"""Circulation planner for architectural circulation analysis.

Converts an ArchitectResult into a CirculationResult by transforming
bubble diagram connections into a circulation graph.
"""
from __future__ import annotations

from typing import Any

from .architect_result import ArchitectResult
from .circulation_edge import CirculationEdge
from .circulation_graph import CirculationGraph
from .circulation_node import CirculationNode
from .circulation_result import CirculationResult


class CirculationPlanner:
    """Deterministic planner that converts architect results into circulation graphs.

    Takes an ArchitectResult containing a BubbleDiagram and produces
    a CirculationResult containing a CirculationGraph.
    """

    def __init__(self) -> None:
        """Initialize the circulation planner."""
        pass

    def plan(self, result: ArchitectResult) -> CirculationResult:
        """Generate a circulation graph from an architect result.

        Converts bubble diagram nodes into circulation nodes and
        bubble diagram connections into circulation edges.

        Args:
            result: The architect result containing a bubble diagram.

        Returns:
            A CirculationResult containing the generated circulation graph.

        Raises:
            ValueError: If the bubble diagram is empty or connections are invalid.
        """
        bubble_diagram = result.bubble_diagram

        if bubble_diagram.room_count == 0:
            return CirculationResult(
                circulation_graph=CirculationGraph(),
                total_length=0.0,
                entry_count=0,
                exit_count=0,
                metadata={"source": "circulation_planner"},
            )

        # Step 1: Convert bubble nodes to circulation nodes
        circulation_nodes: list[CirculationNode] = []
        for bubble_node in bubble_diagram.nodes:
            node = CirculationNode(
                id=bubble_node.id,
                name=bubble_node.name,
                space_id=bubble_node.id,
                width=self._compute_node_width(bubble_node.target_area),
                is_entry_exit=False,
            )
            circulation_nodes.append(node)

        # Step 2: Convert bubble connections to circulation edges
        circulation_edges: list[CirculationEdge] = []
        seen_pairs: set[tuple[str, str]] = set()
        for conn in bubble_diagram.connections:
            # Avoid duplicate edges in either direction
            pair = (conn.source_id, conn.target_id)
            reverse_pair = (conn.target_id, conn.source_id)
            if pair in seen_pairs or reverse_pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            edge = CirculationEdge(
                source_id=conn.source_id,
                target_id=conn.target_id,
                length=self._compute_edge_length(conn.weight),
                width=1.2,
                bidirectional=conn.bidirectional,
                is_accessible=True,
            )
            circulation_edges.append(edge)

        # Step 3: Identify entry and exit nodes
        entry_exit_ids = self._find_entry_exit_nodes(
            circulation_nodes, circulation_edges
        )

        # Mark entry/exit nodes
        updated_nodes: list[CirculationNode] = []
        for node in circulation_nodes:
            if node.id in entry_exit_ids:
                updated_nodes.append(
                    CirculationNode(
                        id=node.id,
                        name=node.name,
                        space_id=node.space_id,
                        width=node.width,
                        is_entry_exit=True,
                        metadata=node.metadata,
                    )
                )
            else:
                updated_nodes.append(node)

        # Step 4: Build graph and compute totals
        graph = CirculationGraph(
            nodes=tuple(updated_nodes),
            edges=tuple(circulation_edges),
        )

        total_length = graph.total_path_length()
        entry_count = len(graph.entry_exit_nodes())

        metadata: dict[str, Any] = {
            "source": "circulation_planner",
            "bubble_room_count": bubble_diagram.room_count,
            "bubble_connection_count": bubble_diagram.connection_count,
        }

        return CirculationResult(
            circulation_graph=graph,
            total_length=total_length,
            entry_count=entry_count,
            exit_count=entry_count,
            metadata=metadata,
        )

    def _compute_node_width(self, target_area: float) -> float:
        """Compute a circulation node width based on room area.

        Larger rooms imply wider connecting corridors.
        Clamps between 0.9 and 3.0 meters.

        Args:
            target_area: Target area of the room in square feet.

        Returns:
            Computed width in meters.
        """
        # Default width for unknown areas
        if target_area <= 0:
            return 1.2
        # Scale: larger rooms have wider connections
        width = 0.9 + (target_area / 500.0) * 1.5
        return max(0.9, min(3.0, width))

    def _compute_edge_length(self, weight: float) -> float:
        """Compute an edge length based on connection weight.

        Higher weight connections are shorter (closer rooms).
        Maps weight [0, 1] to length [1.0, 10.0] meters.

        Args:
            weight: Connection weight between 0.0 and 1.0.

        Returns:
            Computed length in meters.
        """
        # Clamp weight to valid range
        clamped_weight = max(0.0, min(1.0, weight))
        # Higher weight = shorter distance
        return 1.0 + (1.0 - clamped_weight) * 9.0

    def _find_entry_exit_nodes(
        self,
        nodes: list[CirculationNode],
        edges: list[CirculationEdge],
    ) -> set[str]:
        """Identify nodes that serve as entry or exit points.

        A node is considered an entry/exit if it has fewer
        than 2 connections (degree < 2), indicating it is
        at the edge of the circulation network.

        Args:
            nodes: List of circulation nodes.
            edges: List of circulation edges.

        Returns:
            Set of node IDs that are entry or exit points.
        """
        degree: dict[str, int] = {}
        for node in nodes:
            degree[node.id] = 0

        for edge in edges:
            degree[edge.source_id] = degree.get(edge.source_id, 0) + 1
            if edge.bidirectional:
                degree[edge.target_id] = degree.get(edge.target_id, 0) + 1
            else:
                degree[edge.target_id] = degree.get(edge.target_id, 0) + 1

        # Nodes with degree < 2 are entry/exit points
        return {node_id for node_id, deg in degree.items() if deg < 2}