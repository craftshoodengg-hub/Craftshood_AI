"""Column entity for Building Model v2.

Represents a structural column with shape, geometry, and size properties.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from shapely.geometry import Point, Polygon

from .base import BaseEntity, BoundingBox, Point2D
from .types import ColumnType


@dataclass(frozen=True, slots=True)
class Column(BaseEntity):
    """A structural column entity.
    
    Columns are vertical structural elements that support loads.
    
    Attributes:
        column_type: Shape type of the column (rectangular, circular, etc.).
        geometry: Point location of the column center.
        size: Size of the column in feet (width for rectangular, diameter for circular).
        height: Height of the column in feet (optional).
        floor_id: ID of the floor this column belongs to (optional).
        polygon: Cross-section polygon of the column (optional).
        is_load_bearing: Whether this column is load-bearing.
        metadata: Extensible key-value metadata.
    
    Future IFC Mapping:
        Maps to IfcColumn.
    
    Future Flutter Rendering:
        geometry provides center point.
        size determines column footprint.
    
    Future AI Reasoning:
        column_type enables structural analysis.
    """
    
    column_type: ColumnType = ColumnType.UNKNOWN
    geometry: Point2D = field(default_factory=lambda: Point2D(x=0.0, y=0.0))
    size: float = 0.0
    height: float | None = None
    floor_id: str | None = None
    polygon: Polygon | None = None
    is_load_bearing: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def bounding_box(self) -> BoundingBox:
        """Calculate bounding box from geometry and size.
        
        Returns:
            Axis-aligned bounding box.
        """
        if self.polygon:
            return BoundingBox.from_polygon(self.polygon)
        half_size = self.size / 2
        return BoundingBox(
            min_x=self.geometry.x - half_size,
            min_y=self.geometry.y - half_size,
            max_x=self.geometry.x + half_size,
            max_y=self.geometry.y + half_size,
        )
    
    @property
    def cross_section_area(self) -> float:
        """Calculate the cross-sectional area of the column.
        
        Returns:
            Cross-sectional area in square feet.
        """
        if self.polygon:
            return float(self.polygon.area)
        if self.column_type == ColumnType.CIRCULAR:
            import math
            radius = self.size / 2
            return math.pi * radius * radius
        # Rectangular or square
        return self.size * self.size
    
    @property
    def is_circular(self) -> bool:
        """Check if this is a circular column.
        
        Returns:
            True if column_type is CIRCULAR.
        """
        return self.column_type == ColumnType.CIRCULAR
    
    @property
    def is_rectangular(self) -> bool:
        """Check if this is a rectangular column.
        
        Returns:
            True if column_type is RECTANGULAR or SQUARE.
        """
        return self.column_type in (ColumnType.RECTANGULAR, ColumnType.SQUARE)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the column.
        """
        base = super(Column, self).to_dict()
        base.update({
            "column_type": self.column_type.value,
            "geometry": self.geometry.to_dict(),
            "size": self.size,
            "height": self.height,
            "floor_id": self.floor_id,
            "is_load_bearing": self.is_load_bearing,
            "cross_section_area": self.cross_section_area,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Column from a dictionary.
        
        Args:
            payload: Dictionary with column data.
            
        Returns:
            New Column instance.
        """
        base = BaseEntity.from_dict(payload)
        geometry_data = payload.get("geometry", {})
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            column_type=ColumnType(payload.get("column_type", "Unknown")),
            geometry=Point2D.from_dict(geometry_data) if geometry_data else Point2D(x=0.0, y=0.0),
            size=float(payload.get("size", 0.0)),
            height=payload.get("height"),
            floor_id=payload.get("floor_id"),
            is_load_bearing=bool(payload.get("is_load_bearing", True)),
        )
    
    @classmethod
    def create(
        cls,
        *,
        location: Point2D | tuple[float, float],
        size: float = 1.0,
        height: float | None = None,
        column_type: ColumnType = ColumnType.RECTANGULAR,
        floor_id: str | None = None,
        is_load_bearing: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> Column:
        """Factory method to create a Column.
        
        Args:
            location: Center point of the column.
            size: Size of the column in feet (width or diameter).
            height: Height of the column in feet.
            column_type: Shape type of the column.
            floor_id: ID of the floor this column belongs to.
            is_load_bearing: Whether this column is load-bearing.
            metadata: Additional metadata.
            
        Returns:
            New Column instance.
        """
        if isinstance(location, tuple):
            location = Point2D(x=location[0], y=location[1])
        return cls(
            geometry=location,
            size=size,
            height=height,
            column_type=column_type,
            floor_id=floor_id,
            is_load_bearing=is_load_bearing,
            metadata=metadata or {},
        )