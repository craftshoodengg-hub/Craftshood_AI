"""Room entity for Building Model v2.

Represents a room with polygon geometry, type classification,
and relationships to walls, doors, and windows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

import numpy as np
from shapely.geometry import Point, Polygon

from .base import BaseEntity, BoundingBox, Point2D
from .types import RoomType


@dataclass(frozen=True, slots=True)
class Room(BaseEntity):
    """A room entity with polygon geometry.
    
    Rooms are enclosed spaces within a building, bounded by walls.
    
    Attributes:
        room_type: Classification of the room (living, bedroom, etc.).
        polygon: Shapely Polygon representing the room boundary.
        floor_id: ID of the floor this room belongs to (optional).
        wall_ids: Set of wall IDs that bound this room.
        door_ids: Set of door IDs in this room's walls.
        window_ids: Set of window IDs in this room's walls.
        ceiling_height: Height of the ceiling in feet (optional).
        metadata: Extensible key-value metadata.
    
    Future IFC Mapping:
        Maps to IfcSpace.
    
    Future Flutter Rendering:
        polygon provides vertices for canvas drawing.
    
    Future AI Reasoning:
        room_type enables space classification.
        wall_ids enables adjacency analysis.
    """
    
    room_type: RoomType = RoomType.UNKNOWN
    polygon: Polygon = field(default_factory=lambda: Polygon())
    floor_id: str | None = None
    wall_ids: frozenset[str] = field(default_factory=frozenset)
    door_ids: frozenset[str] = field(default_factory=frozenset)
    window_ids: frozenset[str] = field(default_factory=frozenset)
    ceiling_height: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def bounding_box(self) -> BoundingBox:
        """Calculate bounding box from polygon.
        
        Returns:
            Axis-aligned bounding box.
        """
        return BoundingBox.from_polygon(self.polygon)
    
    @property
    def centroid(self) -> Point2D:
        """Calculate centroid of the room.
        
        Returns:
            Point2D at the centroid.
        """
        c = self.polygon.centroid
        return Point2D(x=float(c.x), y=float(c.y))
    
    @property
    def orientation_degrees(self) -> float:
        """Calculate principal orientation using PCA.
        
        Returns:
            Angle in degrees (0-180).
        """
        coords = np.array(self.polygon.exterior.coords)
        if len(coords) < 2:
            return 0.0
        centered = coords[:-1] - coords[:-1].mean(axis=0)
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        principal = eigenvectors[:, np.argmax(eigenvalues)]
        angle = np.degrees(np.arctan2(principal[1], principal[0]))
        return angle % 180.0
    
    @property
    def area(self) -> float:
        """Calculate area of the room.
        
        Returns:
            Area in square feet.
        """
        return float(self.polygon.area)
    
    @property
    def perimeter(self) -> float:
        """Calculate perimeter of the room.
        
        Returns:
            Perimeter in feet.
        """
        return float(self.polygon.length)
    
    def contains(self, point: Point2D) -> bool:
        """Check if a point is inside the room.
        
        Args:
            point: Point2D to check.
            
        Returns:
            True if the point is inside the polygon.
        """
        return self.polygon.contains(Point(point.x, point.y))
    
    def has_window(self) -> bool:
        """Check if this room has any windows.
        
        Returns:
            True if window_ids is non-empty.
        """
        return bool(self.window_ids)
    
    def has_door(self) -> bool:
        """Check if this room has any doors.
        
        Returns:
            True if door_ids is non-empty.
        """
        return bool(self.door_ids)
    
    def is_exterior(self) -> bool:
        """Check if this room is on the exterior.
        
        A room is considered exterior if it has windows (simplified heuristic).
        
        Returns:
            True if the room has windows.
        """
        return self.has_window()
    
    def aspect_ratio(self) -> float:
        """Calculate the aspect ratio of the room.
        
        Uses the bounding box width/height ratio.
        
        Returns:
            Aspect ratio (width / height), >= 1.0.
        """
        bbox = self.bounding_box
        width = bbox.width
        height = bbox.height
        if height == 0:
            return float('inf')
        ratio = width / height
        return ratio if ratio >= 1.0 else 1.0 / ratio
    
    def compactness(self) -> float:
        """Calculate the compactness of the room.
        
        Compactness is the ratio of the area to the area of the bounding box.
        A value of 1.0 means the room perfectly fills its bounding box.
        
        Returns:
            Compactness ratio (0.0 to 1.0).
        """
        bbox = self.bounding_box
        bbox_area = bbox.area
        if bbox_area == 0:
            return 0.0
        return self.area / bbox_area
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the room.
        """
        base = super(Room, self).to_dict()
        base.update({
            "room_type": self.room_type.value,
            "geometry": {
                "polygon": [[x, y] for x, y in self.polygon.exterior.coords],
                "bounding_box": self.bounding_box.to_dict(),
                "area": self.area,
                "perimeter": self.perimeter,
                "centroid": self.centroid.to_dict(),
                "orientation_degrees": self.orientation_degrees,
            },
            "floor_id": self.floor_id,
            "wall_ids": sorted(self.wall_ids),
            "door_ids": sorted(self.door_ids),
            "window_ids": sorted(self.window_ids),
            "ceiling_height": self.ceiling_height,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Room from a dictionary.
        
        Args:
            payload: Dictionary with room data.
            
        Returns:
            New Room instance.
        """
        base = BaseEntity.from_dict(payload)
        coords = [(float(x), float(y)) for x, y in payload.get("geometry", {}).get("polygon", [])]
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            room_type=RoomType(payload.get("room_type", "Unknown")),
            polygon=Polygon(coords) if coords else Polygon(),
            floor_id=payload.get("floor_id"),
            wall_ids=frozenset(payload.get("wall_ids", [])),
            door_ids=frozenset(payload.get("door_ids", [])),
            window_ids=frozenset(payload.get("window_ids", [])),
            ceiling_height=payload.get("ceiling_height"),
        )
    
    @classmethod
    def create(
        cls,
        *,
        vertices: list[tuple[float, float]],
        room_type: RoomType = RoomType.UNKNOWN,
        floor_id: str | None = None,
        wall_ids: frozenset[str] | None = None,
        door_ids: frozenset[str] | None = None,
        window_ids: frozenset[str] | None = None,
        ceiling_height: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Room:
        """Factory method to create a Room from vertices.
        
        Args:
            vertices: List of (x, y) coordinates defining the room polygon.
            room_type: Type of room.
            floor_id: ID of the floor this room belongs to.
            wall_ids: IDs of walls bounding this room.
            door_ids: IDs of doors in this room.
            window_ids: IDs of windows in this room.
            ceiling_height: Height of the ceiling in feet.
            metadata: Additional metadata.
            
        Returns:
            New Room instance.
        """
        return cls(
            room_type=room_type,
            polygon=Polygon(vertices),
            floor_id=floor_id,
            wall_ids=wall_ids or frozenset(),
            door_ids=door_ids or frozenset(),
            window_ids=window_ids or frozenset(),
            ceiling_height=ceiling_height,
            metadata=metadata or {},
        )