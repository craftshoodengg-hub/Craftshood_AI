"""Wall entity for Building Model v2.

Represents a wall with geometry, relationships to adjacent rooms,
and containment of doors and windows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

import numpy as np
from shapely.geometry import LineString

from .base import BaseEntity, BoundingBox, Point2D, generate_uuid
from .types import WallType


@dataclass(frozen=True, slots=True)
class Wall(BaseEntity):
    """A wall entity with geometry and relationships.
    
    Walls separate rooms and can contain doors and windows.
    The geometry is stored as a centerline LineString.
    
    Attributes:
        wall_type: Classification of the wall (exterior, interior, etc.).
        geometry: Centerline geometry as a Shapely LineString.
        width: Wall thickness in feet.
        height: Wall height in feet (optional).
        polygon: Full wall polygon including thickness (optional).
        room_ids: Set of room IDs that this wall borders.
        floor_id: ID of the floor this wall belongs to (optional).
        door_ids: Set of door IDs contained in this wall.
        window_ids: Set of window IDs contained in this wall.
        is_load_bearing: Whether this wall is load-bearing.
        metadata: Extensible key-value metadata.
    
    Future IFC Mapping:
        Maps to IfcWall or IfcWallStandardCase.
    
    Future Flutter Rendering:
        geometry.centerline provides line coordinates for canvas drawing.
        width determines line thickness.
    
    Future AI Reasoning:
        room_ids enables adjacency traversal.
        wall_type enables structural analysis.
    """
    
    wall_type: WallType = WallType.UNKNOWN
    geometry: LineString = field(default_factory=lambda: LineString())
    width: float = 0.0
    height: float | None = None
    polygon: Any = None  # Shapely Polygon | None - avoided circular import
    room_ids: frozenset[str] = field(default_factory=frozenset)
    floor_id: str | None = None
    door_ids: frozenset[str] = field(default_factory=frozenset)
    window_ids: frozenset[str] = field(default_factory=frozenset)
    is_load_bearing: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def length(self) -> float:
        """Calculate the length of the wall centerline.
        
        Returns:
            Length in feet.
        """
        return float(self.geometry.length)
    
    @property
    def bounding_box(self) -> BoundingBox:
        """Calculate bounding box from the centerline geometry.
        
        Returns:
            Axis-aligned bounding box.
        """
        bounds = self.geometry.bounds
        return BoundingBox(
            min_x=bounds[0],
            min_y=bounds[1],
            max_x=bounds[2],
            max_y=bounds[3],
        )
    
    @property
    def orientation_degrees(self) -> float:
        """Calculate the orientation of the wall.
        
        Uses the start and end points to determine the dominant direction.
        
        Returns:
            Angle in degrees (0-180).
        """
        coords = list(self.geometry.coords)
        if len(coords) < 2:
            return 0.0
        start = np.array(coords[0])
        end = np.array(coords[-1])
        vector = end - start
        angle = np.degrees(np.arctan2(vector[1], vector[0]))
        return angle % 180.0
    
    @property
    def start_point(self) -> Point2D:
        """Get the start point of the wall.
        
        Returns:
            Point2D at the start of the centerline.
        """
        coords = list(self.geometry.coords)
        if not coords:
            return Point2D(x=0.0, y=0.0)
        return Point2D(x=float(coords[0][0]), y=float(coords[0][1]))
    
    @property
    def end_point(self) -> Point2D:
        """Get the end point of the wall.
        
        Returns:
            Point2D at the end of the centerline.
        """
        coords = list(self.geometry.coords)
        if not coords:
            return Point2D(x=0.0, y=0.0)
        return Point2D(x=float(coords[-1][0]), y=float(coords[-1][1]))
    
    @property
    def is_exterior(self) -> bool:
        """Check if this is an exterior wall.
        
        Returns:
            True if wall_type is EXTERIOR.
        """
        return self.wall_type == WallType.EXTERIOR
    
    @property
    def has_openings(self) -> bool:
        """Check if this wall has any doors or windows.
        
        Returns:
            True if door_ids or window_ids is non-empty.
        """
        return bool(self.door_ids or self.window_ids)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the wall.
        """
        base = super().to_dict()
        base.update({
            "wall_type": self.wall_type.value,
            "geometry": {
                "centerline": [[x, y] for x, y in self.geometry.coords],
                "bounding_box": self.bounding_box.to_dict(),
                "length": self.length,
                "orientation_degrees": self.orientation_degrees,
            },
            "width": self.width,
            "height": self.height,
            "room_ids": sorted(self.room_ids),
            "floor_id": self.floor_id,
            "door_ids": sorted(self.door_ids),
            "window_ids": sorted(self.window_ids),
            "is_load_bearing": self.is_load_bearing,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Wall from a dictionary.
        
        Args:
            payload: Dictionary with wall data.
            
        Returns:
            New Wall instance.
        """
        base = BaseEntity.from_dict(payload)
        coords = [(float(x), float(y)) for x, y in payload.get("geometry", {}).get("centerline", [])]
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            wall_type=WallType(payload.get("wall_type", "Unknown")),
            geometry=LineString(coords) if coords else LineString(),
            width=float(payload.get("width", 0.0)),
            height=payload.get("height"),
            room_ids=frozenset(payload.get("room_ids", [])),
            floor_id=payload.get("floor_id"),
            door_ids=frozenset(payload.get("door_ids", [])),
            window_ids=frozenset(payload.get("window_ids", [])),
            is_load_bearing=bool(payload.get("is_load_bearing", False)),
        )
    
    @classmethod
    def create(
        cls,
        *,
        start: tuple[float, float],
        end: tuple[float, float],
        width: float = 0.5,
        height: float | None = None,
        wall_type: WallType = WallType.UNKNOWN,
        room_ids: frozenset[str] | None = None,
        floor_id: str | None = None,
        is_load_bearing: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> Wall:
        """Factory method to create a Wall from start and end points.
        
        Args:
            start: (x, y) start point.
            end: (x, y) end point.
            width: Wall thickness in feet.
            height: Wall height in feet.
            wall_type: Wall classification.
            room_ids: Adjacent room IDs.
            floor_id: Parent floor ID.
            is_load_bearing: Whether load-bearing.
            metadata: Additional metadata.
            
        Returns:
            New Wall instance.
        """
        return cls(
            geometry=LineString([start, end]),
            width=width,
            height=height,
            wall_type=wall_type,
            room_ids=room_ids or frozenset(),
            floor_id=floor_id,
            is_load_bearing=is_load_bearing,
            metadata=metadata or {},
        )