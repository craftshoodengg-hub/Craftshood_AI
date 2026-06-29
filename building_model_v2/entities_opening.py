"""Opening, Door, and Window entities for Building Model v2.

Openings are abstract base entities that represent penetrations in walls.
Door and Window are concrete opening types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from shapely.geometry import LineString, Point

from .base import BaseEntity, Point2D
from .types import DoorType, OpeningType, WindowType


# ==================== Opening (Abstract) ====================

@dataclass(frozen=True, slots=True)
class Opening(BaseEntity):
    """Abstract base class for all openings (doors, windows, etc.).
    
    Openings are penetrations in walls that connect rooms or provide
    access to the exterior.
    
    This class cannot be instantiated directly. Use Door or Window instead.
    
    Attributes:
        opening_type: Type of opening (DOOR, WINDOW, etc.).
        width: Width of the opening in feet.
        height: Height of the opening in feet (optional).
        location: Point location of the opening center.
        wall_id: ID of the wall this opening belongs to (optional).
        room_ids: Set of room IDs this opening connects.
        floor_id: ID of the floor this opening belongs to (optional).
        is_exterior: Whether this opening leads to the exterior.
        metadata: Extensible key-value metadata.
    
    Future IFC Mapping:
        Door → IfcDoor
        Window → IfcWindow
    
    Future Flutter Rendering:
        location provides center point for rendering.
        width and height determine opening rectangle size.
    
    Future AI Reasoning:
        room_ids enables connectivity analysis.
        is_exterior enables egress analysis.
    """
    
    opening_type: OpeningType = OpeningType.UNKNOWN
    width: float = 0.0
    height: float | None = None
    location: Point2D = field(default_factory=lambda: Point2D(x=0.0, y=0.0))
    wall_id: str | None = None
    room_ids: frozenset[str] = field(default_factory=frozenset)
    floor_id: str | None = None
    is_exterior: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the opening.
        """
        base = super(Opening, self).to_dict()
        base.update({
            "opening_type": self.opening_type.value,
            "width": self.width,
            "height": self.height,
            "location": self.location.to_dict(),
            "wall_id": self.wall_id,
            "room_ids": sorted(self.room_ids),
            "floor_id": self.floor_id,
            "is_exterior": self.is_exterior,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create an Opening from a dictionary.
        
        Args:
            payload: Dictionary with opening data.
            
        Returns:
            New Opening instance.
        """
        base = BaseEntity.from_dict(payload)
        location_data = payload.get("location", {})
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            opening_type=OpeningType(payload.get("opening_type", "Unknown")),
            width=float(payload.get("width", 0.0)),
            height=payload.get("height"),
            location=Point2D.from_dict(location_data) if location_data else Point2D(x=0.0, y=0.0),
            wall_id=payload.get("wall_id"),
            room_ids=frozenset(payload.get("room_ids", [])),
            floor_id=payload.get("floor_id"),
            is_exterior=bool(payload.get("is_exterior", False)),
        )


# ==================== Door ====================

@dataclass(frozen=True, slots=True)
class Door(Opening):
    """A door entity.
    
    Doors provide access between rooms or to the exterior.
    
    Attributes:
        door_type: Type of door (single leaf, sliding, etc.).
        swing_direction: Direction the door swings ('left', 'right', 'sliding').
        opening_type: Always set to OpeningType.DOOR.
    
    Future IFC Mapping:
        Maps to IfcDoor.
    
    Future Flutter Rendering:
        location provides center point.
        swing_direction determines swing arc visualization.
    
    Future AI Reasoning:
        door_type enables accessibility analysis.
        room_ids enables pathfinding.
    """
    
    door_type: DoorType = DoorType.UNKNOWN
    swing_direction: str | None = None
    opening_type: OpeningType = field(default=OpeningType.DOOR, init=False)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the door.
        """
        base = super(Door, self).to_dict()
        base.update({
            "door_type": self.door_type.value,
            "swing_direction": self.swing_direction,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Door from a dictionary.
        
        Args:
            payload: Dictionary with door data.
            
        Returns:
            New Door instance.
        """
        base = BaseEntity.from_dict(payload)
        location_data = payload.get("location", {})
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            width=float(payload.get("width", 0.0)),
            height=payload.get("height"),
            location=Point2D.from_dict(location_data) if location_data else Point2D(x=0.0, y=0.0),
            wall_id=payload.get("wall_id"),
            room_ids=frozenset(payload.get("room_ids", [])),
            floor_id=payload.get("floor_id"),
            is_exterior=bool(payload.get("is_exterior", False)),
            door_type=DoorType(payload.get("door_type", "Unknown")),
            swing_direction=payload.get("swing_direction"),
        )
    
    @classmethod
    def create(
        cls,
        *,
        location: Point2D | tuple[float, float],
        width: float = 3.0,
        height: float | None = 7.0,
        door_type: DoorType = DoorType.SINGLE_LEAF,
        swing_direction: str | None = None,
        wall_id: str | None = None,
        room_ids: frozenset[str] | None = None,
        floor_id: str | None = None,
        is_exterior: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> Door:
        """Factory method to create a Door.
        
        Args:
            location: Center point of the door.
            width: Door width in feet (default 3.0).
            height: Door height in feet (default 7.0).
            door_type: Type of door.
            swing_direction: Direction the door swings.
            wall_id: ID of the wall containing this door.
            room_ids: IDs of rooms this door connects.
            floor_id: ID of the floor this door belongs to.
            is_exterior: Whether this is an exterior door.
            metadata: Additional metadata.
            
        Returns:
            New Door instance.
        """
        if isinstance(location, tuple):
            location = Point2D(x=location[0], y=location[1])
        return cls(
            width=width,
            height=height,
            location=location,
            wall_id=wall_id,
            room_ids=room_ids or frozenset(),
            floor_id=floor_id,
            is_exterior=is_exterior,
            door_type=door_type,
            swing_direction=swing_direction,
            metadata=metadata or {},
        )


# ==================== Window ====================

@dataclass(frozen=True, slots=True)
class Window(Opening):
    """A window entity.
    
    Windows provide natural light and ventilation.
    
    Attributes:
        window_type: Type of window (fixed, casement, etc.).
        sill_height: Height of the window sill from the floor in feet.
        opening_type: Always set to OpeningType.WINDOW.
    
    Future IFC Mapping:
        Maps to IfcWindow.
    
    Future Flutter Rendering:
        location provides center point.
        sill_height determines vertical position.
    
    Future AI Reasoning:
        window_type enables ventilation analysis.
        is_exterior enables daylight analysis.
    """
    
    window_type: WindowType = WindowType.UNKNOWN
    sill_height: float | None = None
    opening_type: OpeningType = field(default=OpeningType.WINDOW, init=False)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the window.
        """
        base = super(Window, self).to_dict()
        base.update({
            "window_type": self.window_type.value,
            "sill_height": self.sill_height,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Window from a dictionary.
        
        Args:
            payload: Dictionary with window data.
            
        Returns:
            New Window instance.
        """
        base = BaseEntity.from_dict(payload)
        location_data = payload.get("location", {})
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            width=float(payload.get("width", 0.0)),
            height=payload.get("height"),
            location=Point2D.from_dict(location_data) if location_data else Point2D(x=0.0, y=0.0),
            wall_id=payload.get("wall_id"),
            room_ids=frozenset(payload.get("room_ids", [])),
            floor_id=payload.get("floor_id"),
            is_exterior=bool(payload.get("is_exterior", False)),
            window_type=WindowType(payload.get("window_type", "Unknown")),
            sill_height=payload.get("sill_height"),
        )
    
    @classmethod
    def create(
        cls,
        *,
        location: Point2D | tuple[float, float],
        width: float = 4.0,
        height: float | None = 4.0,
        sill_height: float | None = 3.0,
        window_type: WindowType = WindowType.FIXED,
        wall_id: str | None = None,
        room_ids: frozenset[str] | None = None,
        floor_id: str | None = None,
        is_exterior: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> Window:
        """Factory method to create a Window.
        
        Args:
            location: Center point of the window.
            width: Window width in feet (default 4.0).
            height: Window height in feet (default 4.0).
            sill_height: Height of sill from floor in feet (default 3.0).
            window_type: Type of window.
            wall_id: ID of the wall containing this window.
            room_ids: IDs of rooms this window belongs to.
            floor_id: ID of the floor this window belongs to.
            is_exterior: Whether this is an exterior window.
            metadata: Additional metadata.
            
        Returns:
            New Window instance.
        """
        if isinstance(location, tuple):
            location = Point2D(x=location[0], y=location[1])
        return cls(
            width=width,
            height=height,
            sill_height=sill_height,
            location=location,
            wall_id=wall_id,
            room_ids=room_ids or frozenset(),
            floor_id=floor_id,
            is_exterior=is_exterior,
            window_type=window_type,
            metadata=metadata or {},
        )