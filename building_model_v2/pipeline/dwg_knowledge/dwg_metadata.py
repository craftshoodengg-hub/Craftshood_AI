"""DWG knowledge base metadata domain model."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True, slots=True)
class DwgMetadata:
    """Metadata for a DWG reference design."""

    file_path: str
    project_type: str
    plot_width: Optional[float] = None
    plot_depth: Optional[float] = None
    floors: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    room_count: Optional[int] = None
    total_area: Optional[float] = None
    orientation: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "project_type": self.project_type,
            "plot_width": self.plot_width,
            "plot_depth": self.plot_depth,
            "floors": self.floors,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "room_count": self.room_count,
            "total_area": self.total_area,
            "orientation": self.orientation,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DwgMetadata":
        return cls(
            file_path=str(data["file_path"]),
            project_type=str(data["project_type"]),
            plot_width=None if data.get("plot_width") is None else float(data["plot_width"]),
            plot_depth=None if data.get("plot_depth") is None else float(data["plot_depth"]),
            floors=None if data.get("floors") is None else int(data["floors"]),
            bedrooms=None if data.get("bedrooms") is None else int(data["bedrooms"]),
            bathrooms=None if data.get("bathrooms") is None else int(data["bathrooms"]),
            room_count=None if data.get("room_count") is None else int(data["room_count"]),
            total_area=None if data.get("total_area") is None else float(data["total_area"]),
            orientation=None if data.get("orientation") is None else str(data["orientation"]),
            tags=list(data.get("tags", [])),
        )
