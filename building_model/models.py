"""Dataclasses for the aggregate building model."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


JsonMapping = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class BuildingStatistics:
    """Building-level computed metrics."""

    room_count: int = 0
    wall_count: int = 0
    door_count: int = 0
    window_count: int = 0
    total_room_area: float = 0.0
    average_room_area: float = 0.0
    total_room_perimeter: float = 0.0
    adjacency_edge_count: int = 0
    connectivity_edge_count: int = 0
    front_room_count: int = 0
    average_confidence: float = 0.0
    zones: Mapping[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_count": self.room_count,
            "wall_count": self.wall_count,
            "door_count": self.door_count,
            "window_count": self.window_count,
            "total_room_area": self.total_room_area,
            "average_room_area": self.average_room_area,
            "total_room_perimeter": self.total_room_perimeter,
            "adjacency_edge_count": self.adjacency_edge_count,
            "connectivity_edge_count": self.connectivity_edge_count,
            "front_room_count": self.front_room_count,
            "average_confidence": self.average_confidence,
            "zones": dict(self.zones),
        }


@dataclass(frozen=True, slots=True)
class BuildingModel:
    """Aggregated model for an analyzed building."""

    metadata: JsonMapping = field(default_factory=dict)
    plot: JsonMapping | None = None
    walls: Sequence[JsonMapping] = field(default_factory=tuple)
    doors: Sequence[JsonMapping] = field(default_factory=tuple)
    windows: Sequence[JsonMapping] = field(default_factory=tuple)
    rooms: Sequence[JsonMapping] = field(default_factory=tuple)
    adjacency_graph: Sequence[JsonMapping] = field(default_factory=tuple)
    connectivity_graph: Sequence[JsonMapping] = field(default_factory=tuple)
    facing_information: JsonMapping | None = None
    zoning: Sequence[JsonMapping] = field(default_factory=tuple)
    confidence: Sequence[JsonMapping] = field(default_factory=tuple)
    statistics: BuildingStatistics = field(default_factory=BuildingStatistics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": dict(self.metadata),
            "plot": self.plot,
            "walls": list(self.walls),
            "doors": list(self.doors),
            "windows": list(self.windows),
            "rooms": list(self.rooms),
            "adjacency_graph": list(self.adjacency_graph),
            "connectivity_graph": list(self.connectivity_graph),
            "facing_information": self.facing_information,
            "zoning": list(self.zoning),
            "confidence": list(self.confidence),
            "statistics": self.statistics.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A validation issue found in a building model."""

    code: str
    message: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Validation result for a building model."""

    valid: bool
    issues: Sequence[ValidationIssue] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [issue.to_dict() for issue in self.issues],
        }
