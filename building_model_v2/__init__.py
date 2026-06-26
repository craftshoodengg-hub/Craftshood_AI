"""Building Model v2 — Core types and base classes.

This package provides strongly-typed, immutable data models for representing
building structures. It is designed for:

- Future BIM/IFC export
- AI reasoning and analysis
- Flutter mobile visualization
- Vastu compliance analysis

The models are organized in a hierarchy:
    Project → Building → Floor → (Room, Wall, Door, Window, Column, Stair)

All entities inherit from BaseEntity which provides UUID identification,
timestamps, and extensible metadata.
"""

from .base import (
    BaseEntity,
    BoundingBox,
    GeometryMixin,
    Point2D,
    ValidationIssue,
    ValidationReport,
)
from .entities_opening import (
    Door,
    Opening,
    Window,
)
from .entities_wall import (
    Wall,
)
from .types import (
    ColumnType,
    DoorType,
    FloorType,
    OpeningType,
    Orientation,
    RoomType,
    StairType,
    WallType,
    WindowType,
)

__all__ = [
    # Base
    "BaseEntity",
    "BoundingBox",
    "GeometryMixin",
    "Point2D",
    "ValidationIssue",
    "ValidationReport",
    # Entities
    "Wall",
    "Opening",
    "Door",
    "Window",
    # Enums
    "ColumnType",
    "DoorType",
    "FloorType",
    "OpeningType",
    "Orientation",
    "RoomType",
    "StairType",
    "WallType",
    "WindowType",
]

__version__ = "2.0.0"