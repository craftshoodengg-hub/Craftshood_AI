"""Circulation result model.

Immutable dataclass containing the result of circulation analysis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .circulation_graph import CirculationGraph


@dataclass(frozen=True, slots=True)
class CirculationResult:
    """Immutable result of circulation planning.

    Attributes:
        circulation_graph: The generated circulation graph.
        total_length: Total circulation path length in meters.
        entry_count: Number of entry nodes identified.
        exit_count: Number of exit nodes identified.
        metadata: Additional metadata about the analysis.
    """

    circulation_graph: CirculationGraph
    total_length: float
    entry_count: int = 0
    exit_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if self.total_length < 0:
            raise ValueError("total_length must be non-negative")
        if self.entry_count < 0:
            raise ValueError("entry_count must be non-negative")
        if self.exit_count < 0:
            raise ValueError("exit_count must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "circulation_graph": self.circulation_graph.to_dict(),
            "total_length": self.total_length,
            "entry_count": self.entry_count,
            "exit_count": self.exit_count,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CirculationResult:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing circulation result data.

        Returns:
            New CirculationResult instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        circulation_graph = CirculationGraph.from_dict(data["circulation_graph"])
        return cls(
            circulation_graph=circulation_graph,
            total_length=data["total_length"],
            entry_count=data.get("entry_count", 0),
            exit_count=data.get("exit_count", 0),
            metadata=dict(data.get("metadata", {})),
        )