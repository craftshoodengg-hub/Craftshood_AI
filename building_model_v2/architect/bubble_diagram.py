"""Bubble diagram for architectural analysis.

Represents a complete bubble diagram containing nodes (rooms) and
connections (relationships) between them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .bubble_connection import BubbleConnection
from .bubble_node import BubbleNode


@dataclass(frozen=True, slots=True)
class BubbleDiagram:
    """Immutable bubble diagram containing nodes and connections.

    Represents a complete architectural bubble diagram with rooms
    as nodes and relationships as connections.

    Attributes:
        nodes: Tuple of bubble nodes (rooms).
        connections: Tuple of bubble connections (relationships).
        metadata: Additional key-value metadata.
    """

    nodes: tuple[BubbleNode, ...] = ()
    connections: tuple[BubbleConnection, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate diagram integrity after initialization."""
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node ids must be unique")

        node_id_set = set(node_ids)
        for conn in self.connections:
            if conn.source_id not in node_id_set:
                raise ValueError(f"connection source '{conn.source_id}' does not exist")
            if conn.target_id not in node_id_set:
                raise ValueError(f"connection target '{conn.target_id}' does not exist")

    @property
    def room_count(self) -> int:
        """Number of rooms (nodes) in the diagram."""
        return len(self.nodes)

    @property
    def connection_count(self) -> int:
        """Number of connections in the diagram."""
        return len(self.connections)

    @property
    def room_ids(self) -> tuple[str, ...]:
        """Tuple of all room IDs in deterministic order."""
        return tuple(node.id for node in self.nodes)

    def get_node(self, node_id: str) -> BubbleNode | None:
        """Get a node by its ID.

        Args:
            node_id: The ID of the node to find.

        Returns:
            The BubbleNode if found, None otherwise.
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def neighbors(self, node_id: str) -> tuple[BubbleNode, ...]:
        """Get all neighboring nodes for a given node.

        Respects bidirectional flag. Returns nodes in deterministic order.

        Args:
            node_id: The ID of the node to find neighbors for.

        Returns:
            Tuple of neighboring BubbleNode objects.
        """
        neighbor_ids: list[str] = []
        for conn in self.connections:
            if conn.source_id == node_id:
                if conn.target_id not in neighbor_ids:
                    neighbor_ids.append(conn.target_id)
            elif conn.target_id == node_id and conn.bidirectional:
                if conn.source_id not in neighbor_ids:
                    neighbor_ids.append(conn.source_id)

        result: list[BubbleNode] = []
        for nid in neighbor_ids:
            node = self.get_node(nid)
            if node is not None:
                result.append(node)
        return tuple(result)

    def adjacency_matrix(self) -> dict[str, dict[str, float]]:
        """Build adjacency matrix representation.

        Returns:
            Dictionary mapping source_id to dict of target_id to weight.
            All rooms are included as keys, even if they have no connections.
        """
        matrix: dict[str, dict[str, float]] = {}
        for node in self.nodes:
            matrix[node.id] = {}

        for conn in self.connections:
            matrix[conn.source_id][conn.target_id] = conn.weight
            if conn.bidirectional:
                matrix[conn.target_id][conn.source_id] = conn.weight

        return matrix

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "connections": [conn.to_dict() for conn in self.connections],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> BubbleDiagram:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing bubble diagram data.

        Returns:
            New BubbleDiagram instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        nodes = tuple(
            BubbleNode.from_dict(node_data)
            for node_data in data.get("nodes", [])
        )
        connections = tuple(
            BubbleConnection.from_dict(conn_data)
            for conn_data in data.get("connections", [])
        )
        return cls(
            nodes=nodes,
            connections=connections,
            metadata=dict(data.get("metadata", {})),
        )