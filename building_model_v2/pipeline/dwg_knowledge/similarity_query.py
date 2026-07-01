"""Domain models for DWG similarity queries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .dwg_reference import DwgReference


@dataclass(frozen=True, slots=True)
class SimilarityQuery:
    """Query used to search DWG references by similarity."""

    project_type: Optional[str] = None
    plot_width: Optional[float] = None
    plot_depth: Optional[float] = None
    floors: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    orientation: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    max_results: int = 10

    def __post_init__(self) -> None:
        if self.max_results < 1 or self.max_results > 100:
            raise ValueError("max_results must be between 1 and 100")
        if not isinstance(self.tags, list):
            object.__setattr__(self, "tags", list(self.tags))

    def area(self) -> Optional[float]:
        if self.plot_width is None or self.plot_depth is None:
            return None
        return self.plot_width * self.plot_depth

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_type": self.project_type,
            "plot_width": self.plot_width,
            "plot_depth": self.plot_depth,
            "floors": self.floors,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "orientation": self.orientation,
            "tags": list(self.tags),
            "max_results": self.max_results,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimilarityQuery":
        return cls(
            project_type=data.get("project_type"),
            plot_width=None if data.get("plot_width") is None else float(data["plot_width"]),
            plot_depth=None if data.get("plot_depth") is None else float(data["plot_depth"]),
            floors=None if data.get("floors") is None else int(data["floors"]),
            bedrooms=None if data.get("bedrooms") is None else int(data["bedrooms"]),
            bathrooms=None if data.get("bathrooms") is None else int(data["bathrooms"]),
            orientation=data.get("orientation"),
            tags=list(data.get("tags", [])),
            max_results=int(data.get("max_results", 10)),
        )


@dataclass(frozen=True, slots=True)
class SimilarityResult:
    """Similarity match result for a DWG reference."""

    reference: DwgReference
    score: float

    def __post_init__(self) -> None:
        if self.score < 0.0 or self.score > 1.0:
            raise ValueError("score must be between 0 and 1")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference": self.reference.to_dict(),
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimilarityResult":
        return cls(
            reference=DwgReference.from_dict(data["reference"]),
            score=float(data["score"]),
        )
