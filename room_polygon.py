"""Room polygon domain model used by adjacency, connectivity, facing, and validation."""

from __future__ import annotations

from dataclasses import dataclass
from shapely.geometry import Polygon


@dataclass(frozen=True, slots=True)
class RoomPolygon:
    """A detected room polygon with identifying metadata."""

    room_id: str
    room_name: str
    polygon: Polygon
