"""Architect result model.

Immutable dataclass containing the result of architect analysis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .bubble_diagram import BubbleDiagram
from .zoning_result import ZoningResult


@dataclass(frozen=True, slots=True)
class ArchitectResult:
    """Immutable result of architect analysis.

    Attributes:
        bubble_diagram: The generated bubble diagram.
        zoning_result: The zoning analysis result.
        metadata: Additional metadata about the analysis.
    """

    bubble_diagram: BubbleDiagram
    zoning_result: ZoningResult
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def room_count(self) -> int:
        """Total number of rooms in the diagram."""
        return self.bubble_diagram.room_count

    @property
    def connection_count(self) -> int:
        """Total number of connections in the diagram."""
        return self.bubble_diagram.connection_count

    @property
    def zone_count(self) -> int:
        """Total number of zones."""
        return self.zoning_result.total_zone_count

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "bubble_diagram": self.bubble_diagram.to_dict(),
            "zoning_result": self.zoning_result.to_dict(),
            "metadata": dict(self.metadata),
            "room_count": self.room_count,
            "connection_count": self.connection_count,
            "zone_count": self.zone_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ArchitectResult:
        """Deserialize from dictionary."""
        bubble_diagram = BubbleDiagram.from_dict(data["bubble_diagram"])
        zoning_result = ZoningResult.from_dict(data["zoning_result"])
        metadata = dict(data.get("metadata", {}))
        return cls(
            bubble_diagram=bubble_diagram,
            zoning_result=zoning_result,
            metadata=metadata,
        )