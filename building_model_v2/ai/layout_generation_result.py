"""Layout Generation Result for Craftshood AI.

Immutable dataclass representing the result of generating an initial layout.
No AI. Pure deterministic heuristic output.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..validation.cross_entity_validator import BuildingModel


@dataclass(frozen=True, slots=True)
class LayoutGenerationResult:
    """Result of generating an initial building layout."""

    building_model: BuildingModel | None = None
    placed_rooms: Tuple[str, ...] = ()
    unplaced_rooms: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.building_model is not None and len(self.placed_rooms) > 0

    @property
    def placement_ratio(self) -> float:
        total = len(self.placed_rooms) + len(self.unplaced_rooms)
        return len(self.placed_rooms) / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "placed_rooms": list(self.placed_rooms),
            "unplaced_rooms": list(self.unplaced_rooms),
            "warnings": list(self.warnings),
            "confidence": self.confidence,
            "placement_ratio": self.placement_ratio,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LayoutGenerationResult:
        return cls(
            building_model=None,  # Cannot deserialize BuildingModel from dict
            placed_rooms=tuple(data.get("placed_rooms", [])),
            unplaced_rooms=tuple(data.get("unplaced_rooms", [])),
            warnings=tuple(data.get("warnings", [])),
            confidence=data.get("confidence", 0.0),
            metadata=dict(data.get("metadata", {})),
        )
