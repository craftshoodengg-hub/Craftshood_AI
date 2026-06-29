"""Stair entity for Building Model v2.

Represents a stair with geometry, width, direction, and floor connections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from shapely.geometry import LineString, Polygon

from .base import BaseEntity, BoundingBox, Point2D
from .types import StairType


@dataclass(frozen=True, slots=True)
class Stair(BaseEntity):
    """A stair entity.
    
    Stairs connect different floors and provide vertical circulation.
    
    Attributes:
        stair_type: Type of stair (straight, L-shaped, spiral, etc.).
        geometry: LineString representing the stair centerline.
        width: Width of the stair in feet.
        direction: Direction of the stair ('up', 'down', 'both').
        connects_floors: Tuple of (from_floor_id, to_floor_id).
        num_steps: Number of steps (optional).
        floor_id: ID of the floor this stair starts from (optional).
        polygon: Polygon representing the stair footprint (optional).
        metadata: Extensible key-value metadata.
    
    Future IFC Mapping:
        Maps to IfcStair.
    
    Future Flutter Rendering:
        geometry provides centerline for rendering.
        width determines stair width.
    
    Future AI Reasoning:
        connects_floors enables vertical circulation analysis.
    """
    
    stair_type: StairType = StairType.UNKNOWN
    geometry: LineString = field(default_factory=lambda: LineString())
    width: float = 0.0
    direction: str = "both"
    connects_floors: tuple[str | None, str | None] = (None, None)
    num_steps: int | None = None
    floor_id: str | None = None
    polygon: Polygon | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def length(self) -> float:
        """Calculate the length of the stair centerline.
        
        Returns:
            Length in feet.
        """
        return float(self.geometry.length)
    
    @property
    def bounding_box(self) -> BoundingBox:
        """Calculate bounding box from geometry or polygon.
        
        Returns:
            Axis-aligned bounding box.
        """
        if self.polygon:
            return BoundingBox.from_polygon(self.polygon)
        bounds = self.geometry.bounds
        return BoundingBox(
            min_x=bounds[0],
            min_y=bounds[1],
            max_x=bounds[2],
            max_y=bounds[3],
        )
    
    @property
    def from_floor_id(self) -> str | None:
        """Get the floor ID this stair connects from.
        
        Returns:
            Floor ID or None.
        """
        return self.connects_floors[0]
    
    @property
    def to_floor_id(self) -> str | None:
        """Get the floor ID this stair connects to.
        
        Returns:
            Floor ID or None.
        """
        return self.connects_floors[1]
    
    @property
    def is_connected(self) -> bool:
        """Check if this stair connects two floors.
        
        Returns:
            True if both from_floor_id and to_floor_id are set.
        """
        return self.connects_floors[0] is not None and self.connects_floors[1] is not None
    
    @property
    def is_exterior(self) -> bool:
        """Check if this is an exterior stair.
        
        A stair is considered exterior if it's L-shaped, U-shaped, or spiral.
        
        Returns:
            True if the stair type suggests exterior placement.
        """
        return self.stair_type in (StairType.L_SHAPED, StairType.U_SHAPED, StairType.SPIRAL)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the stair.
        """
        base = super(Stair, self).to_dict()
        base.update({
            "stair_type": self.stair_type.value,
            "geometry": {
                "centerline": [[x, y] for x, y in self.geometry.coords],
                "bounding_box": self.bounding_box.to_dict(),
                "length": self.length,
            },
            "width": self.width,
            "direction": self.direction,
            "connects_floors": {
                "from_floor": self.connects_floors[0],
                "to_floor": self.connects_floors[1],
            },
            "num_steps": self.num_steps,
            "floor_id": self.floor_id,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Stair from a dictionary.
        
        Args:
            payload: Dictionary with stair data.
            
        Returns:
            New Stair instance.
        """
        base = BaseEntity.from_dict(payload)
        coords = [(float(x), float(y)) for x, y in payload.get("geometry", {}).get("centerline", [])]
        connects = payload.get("connects_floors", {})
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            stair_type=StairType(payload.get("stair_type", "Unknown")),
            geometry=LineString(coords) if coords else LineString(),
            width=float(payload.get("width", 0.0)),
            direction=str(payload.get("direction", "both")),
            connects_floors=(
                connects.get("from_floor"),
                connects.get("to_floor"),
            ),
            num_steps=payload.get("num_steps"),
            floor_id=payload.get("floor_id"),
        )
    
    @classmethod
    def create(
        cls,
        *,
        start: tuple[float, float],
        end: tuple[float, float],
        width: float = 3.0,
        direction: str = "both",
        connects_floors: tuple[str | None, str | None] = (None, None),
        num_steps: int | None = None,
        stair_type: StairType = StairType.STRAIGHT,
        floor_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Stair:
        """Factory method to create a Stair.
        
        Args:
            start: (x, y) start point of the stair.
            end: (x, y) end point of the stair.
            width: Width of the stair in feet (default 3.0).
            direction: Direction of the stair ('up', 'down', 'both').
            connects_floors: Tuple of (from_floor_id, to_floor_id).
            num_steps: Number of steps.
            stair_type: Type of stair.
            floor_id: ID of the floor this stair starts from.
            metadata: Additional metadata.
            
        Returns:
            New Stair instance.
        """
        return cls(
            geometry=LineString([start, end]),
            width=width,
            direction=direction,
            connects_floors=connects_floors,
            num_steps=num_steps,
            stair_type=stair_type,
            floor_id=floor_id,
            metadata=metadata or {},
        )