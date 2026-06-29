"""Floor entity for Building Model v2.

Represents a floor level with its constituent rooms, walls, columns, and stairs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from .base import BaseEntity, BoundingBox, Point2D
from .types import FloorType


@dataclass(frozen=True, slots=True)
class Floor(BaseEntity):
    """A floor entity representing a building level.
    
    Floors are horizontal divisions of a building, containing rooms, walls,
    columns, and stairs at a specific elevation.
    
    Attributes:
        name: Human-readable name of the floor (e.g., "Ground Floor", "First Floor").
        level: Integer level number (0 for ground, -1 for basement, etc.).
        elevation: Elevation of the floor in feet relative to ground level.
        floor_height: Height of the floor in feet (floor-to-floor).
        slab_thickness: Thickness of the floor slab in feet.
        floor_type: Type of floor (ground, basement, roof, etc.).
        room_ids: Set of room IDs on this floor.
        wall_ids: Set of wall IDs on this floor.
        column_ids: Set of column IDs on this floor.
        stair_ids: Set of stair IDs on this floor.
        metadata: Extensible key-value metadata.
    
    Future IFC Mapping:
        Maps to IfcBuildingStorey.
    
    Future Flutter Rendering:
        elevation provides vertical position for floor plan stacking.
    
    Future AI Reasoning:
        level enables vertical circulation analysis.
        room_ids enable spatial adjacency analysis.
    """
    
    name: str = ""
    level: int = 0
    elevation: float = 0.0
    floor_height: float = 0.0
    slab_thickness: float = 0.0
    floor_type: FloorType = FloorType.UNKNOWN
    room_ids: frozenset[str] = field(default_factory=frozenset)
    wall_ids: frozenset[str] = field(default_factory=frozenset)
    column_ids: frozenset[str] = field(default_factory=frozenset)
    stair_ids: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def room_count(self) -> int:
        """Get the number of rooms on this floor.
        
        Returns:
            Count of room IDs.
        """
        return len(self.room_ids)
    
    @property
    def wall_count(self) -> int:
        """Get the number of walls on this floor.
        
        Returns:
            Count of wall IDs.
        """
        return len(self.wall_ids)
    
    @property
    def column_count(self) -> int:
        """Get the number of columns on this floor.
        
        Returns:
            Count of column IDs.
        """
        return len(self.column_ids)
    
    @property
    def stair_count(self) -> int:
        """Get the number of stairs on this floor.
        
        Returns:
            Count of stair IDs.
        """
        return len(self.stair_ids)
    
    @property
    def has_rooms(self) -> bool:
        """Check if this floor has any rooms.
        
        Returns:
            True if room_ids is non-empty.
        """
        return bool(self.room_ids)
    
    @property
    def has_columns(self) -> bool:
        """Check if this floor has any columns.
        
        Returns:
            True if column_ids is non-empty.
        """
        return bool(self.column_ids)
    
    @property
    def has_stairs(self) -> bool:
        """Check if this floor has any stairs.
        
        Returns:
            True if stair_ids is non-empty.
        """
        return bool(self.stair_ids)
    
    @property
    def is_ground_floor(self) -> bool:
        """Check if this is the ground floor.
        
        Returns:
            True if level is 0.
        """
        return self.level == 0
    
    @property
    def is_basement(self) -> bool:
        """Check if this is a basement floor.
        
        Returns:
            True if level is negative.
        """
        return self.level < 0
    
    @property
    def is_roof(self) -> bool:
        """Check if this is a roof level.
        
        Returns:
            True if floor_type is ROOF.
        """
        return self.floor_type == FloorType.ROOF
    
    def bounding_box(self) -> BoundingBox | None:
        """Calculate the bounding box of this floor.
        
        Placeholder for future implementation. Requires geometry data
        from associated rooms and walls to compute.
        
        Returns:
            Bounding box if computable, None otherwise.
        """
        # TODO: Implement when geometry aggregation is available
        # This would aggregate bounding boxes from all rooms on this floor
        return None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the floor.
        """
        base = super(Floor, self).to_dict()
        base.update({
            "name": self.name,
            "level": self.level,
            "elevation": self.elevation,
            "floor_height": self.floor_height,
            "slab_thickness": self.slab_thickness,
            "floor_type": self.floor_type.value,
            "room_ids": sorted(self.room_ids),
            "wall_ids": sorted(self.wall_ids),
            "column_ids": sorted(self.column_ids),
            "stair_ids": sorted(self.stair_ids),
            "counts": {
                "rooms": self.room_count,
                "walls": self.wall_count,
                "columns": self.column_count,
                "stairs": self.stair_count,
            },
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Floor from a dictionary.
        
        Args:
            payload: Dictionary with floor data.
            
        Returns:
            New Floor instance.
        """
        base = BaseEntity.from_dict(payload)
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            name=str(payload.get("name", "")),
            level=int(payload.get("level", 0)),
            elevation=float(payload.get("elevation", 0.0)),
            floor_height=float(payload.get("floor_height", 0.0)),
            slab_thickness=float(payload.get("slab_thickness", 0.0)),
            floor_type=FloorType(payload.get("floor_type", "Unknown")),
            room_ids=frozenset(payload.get("room_ids", [])),
            wall_ids=frozenset(payload.get("wall_ids", [])),
            column_ids=frozenset(payload.get("column_ids", [])),
            stair_ids=frozenset(payload.get("stair_ids", [])),
        )
    
    @classmethod
    def create(
        cls,
        *,
        name: str = "",
        level: int = 0,
        elevation: float = 0.0,
        floor_height: float = 10.0,
        slab_thickness: float = 0.5,
        floor_type: FloorType = FloorType.UNKNOWN,
        room_ids: frozenset[str] | None = None,
        wall_ids: frozenset[str] | None = None,
        column_ids: frozenset[str] | None = None,
        stair_ids: frozenset[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Floor:
        """Factory method to create a Floor.
        
        Args:
            name: Human-readable name of the floor.
            level: Integer level number (0 for ground, -1 for basement).
            elevation: Elevation in feet relative to ground level.
            floor_height: Height of the floor in feet.
            slab_thickness: Thickness of the floor slab in feet.
            floor_type: Type of floor.
            room_ids: IDs of rooms on this floor.
            wall_ids: IDs of walls on this floor.
            column_ids: IDs of columns on this floor.
            stair_ids: IDs of stairs on this floor.
            metadata: Additional metadata.
            
        Returns:
            New Floor instance.
        """
        return cls(
            name=name,
            level=level,
            elevation=elevation,
            floor_height=floor_height,
            slab_thickness=slab_thickness,
            floor_type=floor_type,
            room_ids=room_ids or frozenset(),
            wall_ids=wall_ids or frozenset(),
            column_ids=column_ids or frozenset(),
            stair_ids=stair_ids or frozenset(),
            metadata=metadata or {},
        )