"""Bubble connection for architectural bubble diagrams.

Represents a relationship between two rooms in the bubble diagram.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class BubbleConnection:
    """Immutable connection between two bubble nodes.

    Represents a relationship or adjacency between two rooms
    in the architectural bubble diagram.

    Attributes:
        source_id: ID of the source bubble node.
        target_id: ID of the target bubble node.
        weight: Connection strength from 0.0 to 1.0.
        required: Whether this connection is mandatory.
        bidirectional: Whether connection applies in both directions.
        metadata: Additional key-value metadata.
    """

    source_id: str
    target_id: str
    weight: float = 1.0
    required: bool = False
    bidirectional: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if not self.source_id:
            raise ValueError("source_id cannot be empty")
        if not self.target_id:
            raise ValueError("target_id cannot be empty")
        if self.source_id == self.target_id:
            raise ValueError("source_id and target_id must be different")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("weight must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "weight": self.weight,
            "required": self.required,
            "bidirectional": self.bidirectional,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> BubbleConnection:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing bubble connection data.

        Returns:
            New BubbleConnection instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            weight=data.get("weight", 1.0),
            required=data.get("required", False),
            bidirectional=data.get("bidirectional", True),
            metadata=dict(data.get("metadata", {})),
        )