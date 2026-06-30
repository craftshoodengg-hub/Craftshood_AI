"""Circulation graph for architectural circulation analysis.

Represents a complete circulation network containing nodes (points/spaces)
and edges (paths/connections) between them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .circulation_edge import CirculationEdge
from .circulation_node import CirculationNode


@dataclass(frozen=True, slots=True)
class CirculationGraph:
    """Immutable circulation graph containing nodes and edges.

    Represents a complete architectural circulation network with
    circulation points as nodes and paths as edges.

    Attributes:
        nodes: Tuple of circulation nodes.
        edges: Tuple of circulation edges.
        metadata: Additional key-value metadata.
    """

    nodes: tuple[CirculationNode, ...] = ()
    edges: tuple[CirculationEdge, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        """Validate graph integrity after initialization."""
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node ids must be unique")

        node_id_set = set(node_ids)
        for edge in self.edges:
            if edge.source_id not in node_id_set:
                raise ValueError(f"edge source '{edge.source_id}' does not exist")
            if edge.target_id not in node_id_set:
                raise ValueError(f"edge target '{edge.target_id}' does not exist")

    @property
    def node_count(self) -> int:
        """Number of nodes in the graph."""
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Number of edges in the graph."""
        return len(self.edges)

    @property
    def node_ids(self) -> tuple[str, ...]:
        """Tuple of all node IDs in deterministic order."""
        return tuple(node.id for node in self.nodes)

    def get_node(self, node_id: str) -> CirculationNode | None:
        """Get a node by its ID.

        Args:
            node_id: The ID of the node to find.

        Returns:
            The CirculationNode if found, None otherwise.
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def neighbors(self, node_id: str) -> tuple[CirculationNode, ...]:
        """Get all neighboring nodes for a given node.

        Respects bidirectional flag. Returns nodes in deterministic order.

        Args:
            node_id: The ID of the node to find neighbors for.

        Returns:
            Tuple of neighboring CirculationNode objects.
        """
        neighbor_ids: list[str] = []
        for edge in self.edges:
            if edge.source_id == node_id:
                if edge.target_id not in neighbor_ids:
                    neighbor_ids.append(edge.target_id)
            elif edge.target_id == node_id and edge.bidirectional:
                if edge.source_id not in neighbor_ids:
                    neighbor_ids.append(edge.source_id)

        result: list[CirculationNode] = []
        for nid in neighbor_ids:
            node = self.get_node(nid)
            if node is not None:
                result.append(node)
        return tuple(result)

    def total_path_length(self) -> float:
        """Sum of all edge lengths in the graph.

        Returns:
            Total length of all path segments in meters.
        """
        return sum(edge.length for edge in self.edges)

    def entry_exit_nodes(self) -> tuple[CirculationNode, ...]:
        """Get all nodes that are entry or exit points.

        Returns:
            Tuple of entry/exit CirculationNode objects.
        """
        return tuple(
            node for node in self.nodes if node.is_entry_exit
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CirculationGraph:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing circulation graph data.

        Returns:
            New CirculationGraph instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        nodes = tuple(
            CirculationNode.from_dict(node_data)
            for node_data in data.get("nodes", [])
        )
        edges = tuple(
            CirculationEdge.from_dict(edge_data)
            for edge_data in data.get("edges", [])
        )
        return cls(
            nodes=nodes,
            edges=edges,
            metadata=dict(data.get("metadata", {})),
        )