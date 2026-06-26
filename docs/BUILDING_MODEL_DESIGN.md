# Building Model — Design Document

**Date:** 2026-06-26  
**Status:** Pending Approval  
**Author:** OWL (AI Assistant)

---

## 1. Executive Summary

The current Building Model uses generic `JsonMapping` dictionaries for all entities, lacking type safety, relationships, and extensibility. This document designs a production-ready Building Model with strongly-typed entities, UUID-based identification, comprehensive geometry support, and future-proof architecture for BIM/IFC export, AI reasoning, Flutter visualization, and Vastu analysis.

---

## 2. Current Implementation Analysis

### 2.1 Current Architecture

```
BuildingModel
├── metadata: dict
├── plot: dict | None
├── walls: Sequence[dict]      ← Generic dictionaries
├── doors: Sequence[dict]
├── windows: Sequence[dict]
├── rooms: Sequence[dict]
├── adjacency_graph: Sequence[dict]
├── connectivity_graph: Sequence[dict]
├── facing_information: dict | None
├── zoning: Sequence[dict]
├── confidence: Sequence[dict]
└── statistics: BuildingStatistics
```

### 2.2 Limitations

| Limitation | Impact |
|------------|--------|
| No UUID-based identification | Cannot reference specific objects |
| Generic dicts for entities | No type safety, no IDE support |
| No relationships between objects | Cannot traverse building structure |
| No geometry objects | Cannot perform spatial queries |
| No bounding boxes | Cannot optimize rendering |
| No orientation | Cannot support Vastu analysis |
| Flat structure | No floor-based organization |
| No opening abstraction | Doors/windows treated differently |
| No column/stair support | Missing structural elements |

---

## 3. Proposed Architecture

### 3.1 Architecture Principles

1. **Immutable Models:** All entities use `frozen=True, slots=True` dataclasses
2. **UUID Identification:** Every entity has a unique `id: str` (UUID4)
3. **Type Safety:** Strong typing with `typing` module
4. **Geometry Integration:** Shapely geometries for spatial operations
5. **Relationship Graph:** Explicit relationships between entities
6. **Extensible Metadata:** `metadata: dict[str, Any]` for custom data
7. **Layered Design:** Core models → Analysis models → Export models

### 3.2 Entity Hierarchy

```
Building
├── floors: Sequence[Floor]
│   ├── rooms: Sequence[Room]
│   ├── walls: Sequence[Wall]
│   ├── doors: Sequence[Door]
│   ├── windows: Sequence[Window]
│   ├── columns: Sequence[Column]
│   ├── stairs: Sequence[Stair]
│   └── openings: Sequence[Opening]
├── statistics: BuildingStatistics
└── metadata: dict[str, Any]
```

### 3.3 Module Structure

```
building_model/
├── __init__.py           # Public API exports
├── types.py              # Shared type definitions (enums, constants)
├── base.py               # Base classes (BoundingBox, GeometryMixin)
├── entities.py           # Core entities (Room, Wall, Door, etc.)
├── building.py           # Building and Floor classes
├── statistics.py         # BuildingStatistics calculator
├── relationships.py      # Relationship graph
├── serializer.py         # JSON serialization/deserialization
├── validator.py          # Validation logic
└── utils.py              # Utility functions
```

---

## 4. Data Models

### 4.1 Base Types

```python
# types.py

from __future__ import annotations

from enum import StrEnum
from typing import Any


class RoomType(StrEnum):
    """Room classification types."""
    LIVING = "Living"
    BEDROOM = "Bedroom"
    KITCHEN = "Kitchen"
    DINING = "Dining"
    TOILET = "Toilet"
    BATHROOM = "Bathroom"
    STORAGE = "Storage"
    CORRIDOR = "Corridor"
    STAIRCASE = "Staircase"
    BALCONY = "Balcony"
    UTILITY = "Utility"
    UNKNOWN = "Unknown"


class WallType(StrEnum):
    """Wall classification types."""
    EXTERIOR = "Exterior"
    INTERIOR = "Interior"
    PARTITION = "Partition"
    BEARING = "Bearing"
    SHEAR = "Shear"
    UNKNOWN = "Unknown"


class OpeningType(StrEnum):
    """Opening classification types."""
    DOOR = "Door"
    WINDOW = "Window"
    VENTILATION = "Ventilation"
    ARCHWAY = "Archway"
    SLIDING_DOOR = "Sliding Door"
    FRENCH_DOOR = "French Door"
    UNKNOWN = "Unknown"


class DoorType(StrEnum):
    """Door classification types."""
    SINGLE_LEAF = "Single Leaf"
    DOUBLE_LEAF = "Double Leaf"
    SLIDING = "Sliding"
    FOLDING = "Folding"
    REVOLVING = "Revolving"
    UNKNOWN = "Unknown"


class WindowType(StrEnum):
    """Window classification types."""
    FIXED = "Fixed"
    CASEMENT = "Casement"
    SLIDING = "Sliding"
    AWNING = "Awning"
    BAY = "Bay"
    UNKNOWN = "Unknown"


class ColumnType(StrEnum):
    """Column classification types."""
    RECTANGULAR = "Rectangular"
    CIRCULAR = "Circular"
    SQUARE = "Square"
    STRUCTURAL = "Structural"
    UNKNOWN = "Unknown"


class StairType(StrEnum):
    """Stair classification types."""
    STRAIGHT = "Straight"
    L_SHAPED = "L-Shaped"
    U_SHAPED = "U-Shaped"
    SPIRAL = "Spiral"
    CURVED = "Curved"
    UNKNOWN = "Unknown"


class FloorType(StrEnum):
    """Floor classification types."""
    GROUND = "Ground"
    BASEMENT = "Basement"
    UPPER = "Upper"
    ROOF = "Roof"
    MEZZANINE = "Mezzanine"
    UNKNOWN = "Unknown"


class Orientation(StrEnum):
    """Cardinal directions for Vastu analysis."""
    NORTH = "North"
    NORTHEAST = "Northeast"
    EAST = "East"
    SOUTHEAST = "Southeast"
    SOUTH = "South"
    SOUTHWEST = "Southwest"
    WEST = "West"
    NORTHWEST = "Northwest"
    CENTER = "Center"
    UNKNOWN = "Unknown"
```

### 4.2 Base Classes

```python
# base.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from shapely.geometry import Polygon, box

from geometry_engine import Point2D


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned bounding box."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    
    @property
    def width(self) -> float:
        return self.max_x - self.min_x
    
    @property
    def height(self) -> float:
        return self.max_y - self.min_y
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def center(self) -> Point2D:
        return Point2D(
            x=(self.min_x + self.max_x) / 2,
            y=(self.min_y + self.max_y) / 2,
        )
    
    def to_shapely(self) -> Polygon:
        return box(self.min_x, self.min_y, self.max_x, self.max_y)
    
    def to_dict(self) -> dict[str, float]:
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }
    
    @classmethod
    def from_points(cls, points: Sequence[Point2D]) -> BoundingBox:
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return cls(
            min_x=min(xs),
            min_y=min(ys),
            max_x=max(xs),
            max_y=max(ys),
        )
    
    @classmethod
    def from_polygon(cls, polygon: Polygon) -> BoundingBox:
        bounds = polygon.bounds
        return cls(
            min_x=bounds[0],
            min_y=bounds[1],
            max_x=bounds[2],
            max_y=bounds[3],
        )


@dataclass(frozen=True, slots=True)
class GeometryMixin:
    """Mixin providing geometry utilities for entities."""
    
    polygon: Polygon
    
    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox.from_polygon(self.polygon)
    
    @property
    def area(self) -> float:
        return float(self.polygon.area)
    
    @property
    def perimeter(self) -> float:
        return float(self.polygon.length)
    
    @property
    def centroid(self) -> Point2D:
        c = self.polygon.centroid
        return Point2D(x=float(c.x), y=float(c.y))
    
    @property
    def orientation_degrees(self) -> float:
        """Calculate principal orientation using PCA."""
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
    def is_convex(self) -> bool:
        return self.polygon.equals(self.polygon.convex_hull)
    
    @property
    def convex_hull_area(self) -> float:
        return float(self.polygon.convex_hull.area)
    
    @property
    def solidity(self) -> float:
        """Ratio of area to convex hull area."""
        hull_area = self.polygon.convex_hull.area
        return float(self.polygon.area / hull_area) if hull_area > 0 else 0.0
```

### 4.3 Core Entities

```python
# entities.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shapely.geometry import LineString, Point, Polygon

from geometry_engine import Point2D, LineEntity

from .base import BoundingBox, GeometryMixin
from .types import (
    ColumnType,
    DoorType,
    OpeningType,
    Orientation,
    RoomType,
    StairType,
    WallType,
    WindowType,
)


@dataclass(frozen=True, slots=True)
class Room(GeometryMixin):
    """A room entity with complete metadata."""
    
    id: str  # UUID
    name: str
    room_type: RoomType
    floor_id: str  # Reference to parent floor
    polygon: Polygon
    height: float | None = None  # Ceiling height
    label_text: str | None = None  # Original label text
    label_position: Point2D | None = None  # Label location
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "room_type": self.room_type.value,
            "floor_id": self.floor_id,
            "geometry": {
                "polygon": [[x, y] for x, y in self.polygon.exterior.coords],
                "bounding_box": self.bounding_box.to_dict(),
                "area": self.area,
                "perimeter": self.perimeter,
                "centroid": {"x": self.centroid.x, "y": self.centroid.y},
                "orientation_degrees": self.orientation_degrees,
                "is_convex": self.is_convex,
                "solidity": self.solidity,
            },
            "height": self.height,
            "label_text": self.label_text,
            "label_position": self.label_position.to_dict() if self.label_position else None,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Wall:
    """A wall entity with geometry and relationships."""
    
    id: str  # UUID
    wall_type: WallType
    geometry: LineString  # Centerline
    width: float  # Wall thickness
    height: float | None = None  # Wall height
    polygon: Polygon | None = None  # Full wall polygon (including thickness)
    room_ids: frozenset[str] = field(default_factory=frozenset)  # Adjacent rooms
    floor_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def length(self) -> float:
        return float(self.geometry.length)
    
    @property
    def bounding_box(self) -> BoundingBox:
        bounds = self.geometry.bounds
        return BoundingBox(
            min_x=bounds[0], min_y=bounds[1],
            max_x=bounds[2], max_y=bounds[3],
        )
    
    @property
    def orientation_degrees(self) -> float:
        coords = list(self.geometry.coords)
        if len(coords) < 2:
            return 0.0
        start = np.array(coords[0])
        end = np.array(coords[-1])
        vector = end - start
        angle = np.degrees(np.arctan2(vector[1], vector[0]))
        return angle % 180.0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "wall_type": self.wall_type.value,
            "geometry": {
                "centerline": [[x, y] for x, y in self.geometry.coords],
                "bounding_box": self.bounding_box.to_dict(),
                "length": self.length,
                "orientation_degrees": self.orientation_degrees,
                "width": self.width,
                "height": self.height,
            },
            "room_ids": sorted(self.room_ids),
            "floor_id": self.floor_id,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Opening:
    """Base class for doors, windows, and other openings."""
    
    id: str  # UUID
    opening_type: OpeningType
    geometry: Point | LineString  # Point for location, LineString for frame
    width: float
    height: float | None = None
    room_ids: frozenset[str] = field(default_factory=frozenset)  # Adjacent rooms
    wall_id: str | None = None  # Wall this opening belongs to
    floor_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def location(self) -> Point2D:
        if isinstance(self.geometry, Point):
            return Point2D(x=float(self.geometry.x), y=float(self.geometry.y))
        centroid = self.geometry.centroid
        return Point2D(x=float(centroid.x), y=float(centroid.y))
    
    def to_dict(self) -> dict[str, Any]:
        if isinstance(self.geometry, Point):
            geom_data = {"x": float(self.geometry.x), "y": float(self.geometry.y)}
        else:
            geom_data = [[x, y] for x, y in self.geometry.coords]
        
        return {
            "id": self.id,
            "opening_type": self.opening_type.value,
            "geometry": geom_data,
            "width": self.width,
            "height": self.height,
            "room_ids": sorted(self.room_ids),
            "wall_id": self.wall_id,
            "floor_id": self.floor_id,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Door(Opening):
    """A door entity."""
    
    door_type: DoorType = DoorType.UNKNOWN
    is_exterior: bool = False
    swing_direction: str | None = None  # "left", "right", "sliding"
    
    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["door_type"] = self.door_type.value
        base["is_exterior"] = self.is_exterior
        base["swing_direction"] = self.swing_direction
        return base


@dataclass(frozen=True, slots=True)
class Window(Opening):
    """A window entity."""
    
    window_type: WindowType = WindowType.UNKNOWN
    sill_height: float | None = None
    is_exterior: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["window_type"] = self.window_type.value
        base["sill_height"] = self.sill_height
        base["is_exterior"] = self.is_exterior
        return base


@dataclass(frozen=True, slots=True)
class Column:
    """A structural column entity."""
    
    id: str  # UUID
    column_type: ColumnType
    geometry: Point | Polygon  # Point for location, Polygon for cross-section
    width: float
    height: float
    floor_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def location(self) -> Point2D:
        if isinstance(self.geometry, Point):
            return Point2D(x=float(self.geometry.x), y=float(self.geometry.y))
        centroid = self.geometry.centroid
        return Point2D(x=float(centroid.x), y=float(centroid.y))
    
    @property
    def bounding_box(self) -> BoundingBox:
        if isinstance(self.geometry, Point):
            return BoundingBox(
                min_x=self.geometry.x - self.width / 2,
                min_y=self.geometry.y - self.width / 2,
                max_x=self.geometry.x + self.width / 2,
                max_y=self.geometry.y + self.width / 2,
            )
        return BoundingBox.from_polygon(self.geometry)
    
    def to_dict(self) -> dict[str, Any]:
        if isinstance(self.geometry, Point):
            geom_data = {"x": float(self.geometry.x), "y": float(self.geometry.y)}
        else:
            geom_data = [[x, y] for x, y in self.geometry.exterior.coords]
        
        return {
            "id": self.id,
            "column_type": self.column_type.value,
            "geometry": geom_data,
            "width": self.width,
            "height": self.height,
            "bounding_box": self.bounding_box.to_dict(),
            "floor_id": self.floor_id,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Stair:
    """A staircase entity."""
    
    id: str  # UUID
    stair_type: StairType
    geometry: Polygon  # Footprint
    width: float
    floor_ids: frozenset[str] = field(default_factory=frozenset)  # Connected floors
    direction: str | None = None  # "up", "down", "both"
    floor_id: str | None = None  # Primary floor
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def area(self) -> float:
        return float(self.geometry.area)
    
    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox.from_polygon(self.geometry)
    
    @property
    def orientation_degrees(self) -> float:
        coords = np.array(self.geometry.exterior.coords)
        if len(coords) < 2:
            return 0.0
        centered = coords[:-1] - coords[:-1].mean(axis=0)
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        principal = eigenvectors[:, np.argmax(eigenvalues)]
        angle = np.degrees(np.arctan2(principal[1], principal[0]))
        return angle % 180.0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stair_type": self.stair_type.value,
            "geometry": {
                "polygon": [[x, y] for x, y in self.geometry.exterior.coords],
                "bounding_box": self.bounding_box.to_dict(),
                "area": self.area,
                "orientation_degrees": self.orientation_degrees,
                "width": self.width,
            },
            "floor_ids": sorted(self.floor_ids),
            "direction": self.direction,
            "floor_id": self.floor_id,
            "metadata": self.metadata,
        }
```

### 4.4 Building and Floor

```python
# building.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from shapely.geometry import MultiPolygon, Polygon

from .base import BoundingBox, Point2D
from .entities import Column, Door, Room, Stair, Wall, Window
from .types import Orientation


@dataclass(frozen=True, slots=True)
class Floor:
    """A floor level in a building."""
    
    id: str  # UUID
    name: str
    level: float  # Elevation in feet
    height: float  # Floor-to-floor height
    rooms: tuple[Room, ...] = field(default_factory=tuple)
    walls: tuple[Wall, ...] = field(default_factory=tuple)
    doors: tuple[Door, ...] = field(default_factory=tuple)
    windows: tuple[Window, ...] = field(default_factory=tuple)
    columns: tuple[Column, ...] = field(default_factory=tuple)
    stairs: tuple[Stair, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_area(self) -> float:
        return sum(room.area for room in self.rooms)
    
    @property
    def room_count(self) -> int:
        return len(self.rooms)
    
    @property
    def wall_count(self) -> int:
        return len(self.walls)
    
    @property
    def door_count(self) -> int:
        return len(self.doors)
    
    @property
    def window_count(self) -> int:
        return len(self.windows)
    
    @property
    def bounding_box(self) -> BoundingBox | None:
        if not self.rooms:
            return None
        polygons = [room.polygon for room in self.rooms]
        combined = MultiPolygon(polygons)
        return BoundingBox.from_polygon(combined.convex_hull)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "height": self.height,
            "statistics": {
                "total_area": self.total_area,
                "room_count": self.room_count,
                "wall_count": self.wall_count,
                "door_count": self.door_count,
                "window_count": self.window_count,
            },
            "rooms": [room.to_dict() for room in self.rooms],
            "walls": [wall.to_dict() for wall in self.walls],
            "doors": [door.to_dict() for door in self.doors],
            "windows": [window.to_dict() for window in self.windows],
            "columns": [column.to_dict() for column in self.columns],
            "stairs": [stair.to_dict() for stair in self.stairs],
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class Building:
    """Complete building model with all entities."""
    
    id: str  # UUID
    name: str
    floors: tuple[Floor, ...]
    building_type: str | None = None
    address: str | None = None
    year_built: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_area(self) -> float:
        return sum(floor.total_area for floor in self.floors)
    
    @property
    def built_up_area(self) -> float:
        """Total built-up area (same as total_area for now)."""
        return self.total_area
    
    @property
    def number_of_rooms(self) -> int:
        return sum(floor.room_count for floor in self.floors)
    
    @property
    def number_of_walls(self) -> int:
        return sum(floor.wall_count for floor in self.floors)
    
    @property
    def number_of_doors(self) -> int:
        return sum(floor.door_count for floor in self.floors)
    
    @property
    def number_of_windows(self) -> int:
        return sum(floor.window_count for floor in self.floors)
    
    @property
    def number_of_floors(self) -> int:
        return len(self.floors)
    
    @property
    def bounding_box(self) -> BoundingBox | None:
        if not self.floors:
            return None
        polygons = []
        for floor in self.floors:
            for room in floor.rooms:
                polygons.append(room.polygon)
        if not polygons:
            return None
        combined = MultiPolygon(polygons)
        return BoundingBox.from_polygon(combined.convex_hull)
    
    @property
    def building_orientation(self) -> Orientation:
        """Calculate building orientation from largest floor."""
        if not self.floors:
            return Orientation.UNKNOWN
        
        largest_floor = max(self.floors, key=lambda f: f.total_area)
        if not largest_floor.rooms:
            return Orientation.UNKNOWN
        
        # Use largest room for orientation
        largest_room = max(largest_floor.rooms, key=lambda r: r.area)
        angle = largest_room.orientation_degrees
        
        # Convert angle to cardinal direction
        return _angle_to_orientation(angle)
    
    def get_room_by_id(self, room_id: str) -> Room | None:
        for floor in self.floors:
            for room in floor.rooms:
                if room.id == room_id:
                    return room
        return None
    
    def get_floor_by_id(self, floor_id: str) -> Floor | None:
        for floor in self.floors:
            if floor.id == floor_id:
                return floor
        return None
    
    def get_adjacent_rooms(self, room_id: str) -> tuple[Room, ...]:
        """Get rooms that share a wall with the given room."""
        room = self.get_room_by_id(room_id)
        if not room:
            return ()
        
        adjacent: list[Room] = []
        for floor in self.floors:
            for wall in floor.walls:
                if room_id in wall.room_ids:
                    for adjacent_id in wall.room_ids:
                        if adjacent_id != room_id:
                            adj_room = self.get_room_by_id(adjacent_id)
                            if adj_room and adj_room not in adjacent:
                                adjacent.append(adj_room)
        return tuple(adjacent)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "building_type": self.building_type,
            "address": self.address,
            "year_built": self.year_built,
            "statistics": {
                "total_area": self.total_area,
                "built_up_area": self.built_up_area,
                "number_of_rooms": self.number_of_rooms,
                "number_of_walls": self.number_of_walls,
                "number_of_doors": self.number_of_doors,
                "number_of_windows": self.number_of_windows,
                "number_of_floors": self.number_of_floors,
                "building_orientation": self.building_orientation.value,
            },
            "floors": [floor.to_dict() for floor in self.floors],
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
            "metadata": self.metadata,
        }


def _angle_to_orientation(angle_degrees: float) -> Orientation:
    """Convert angle in degrees to cardinal orientation."""
    angle = angle_degrees % 360
    if 337.5 <= angle or angle < 22.5:
        return Orientation.NORTH
    elif 22.5 <= angle < 67.5:
        return Orientation.NORTHEAST
    elif 67.5 <= angle < 112.5:
        return Orientation.EAST
    elif 112.5 <= angle < 157.5:
        return Orientation.SOUTHEAST
    elif 157.5 <= angle < 202.5:
        return Orientation.SOUTH
    elif 202.5 <= angle < 247.5:
        return Orientation.SOUTHWEST
    elif 247.5 <= angle < 292.5:
        return Orientation.WEST
    elif 292.5 <= angle < 337.5:
        return Orientation.NORTHWEST
    return Orientation.UNKNOWN
```

---

## 5. Affected Files

### 5.1 New Files

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `building_model/types.py` | Enums and constants | 80 |
| `building_model/base.py` | Base classes | 100 |
| `building_model/entities.py` | Entity dataclasses | 350 |
| `building_model/building.py` | Building and Floor | 200 |
| `building_model/relationships.py` | Relationship graph | 100 |
| `building_model/utils.py` | Utility functions | 50 |

### 5.2 Modified Files

| File | Change |
|------|--------|
| `building_model/__init__.py` | Update exports |
| `building_model/serializer.py` | Rewrite for new models |
| `building_model/statistics.py` | Rewrite for new models |
| `building_model/validator.py` | Rewrite for new models |

### 5.3 Test Files

| File | Purpose |
|------|---------|
| `tests/test_building_model_v2.py` | Comprehensive tests |

---

## 6. Migration Plan

### 6.1 Phase 1: Foundation (No Breaking Changes)

1. Create `types.py` with all enums
2. Create `base.py` with BoundingBox and GeometryMixin
3. Create `entities.py` with all entity classes
4. Create `building.py` with Building and Floor
5. Write comprehensive tests

### 6.2 Phase 2: Serialization & Validation

1. Update `serializer.py` for new models
2. Update `validator.py` for new models
3. Update `statistics.py` for new models
4. Write integration tests

### 6.3 Phase 3: Integration

1. Update `__init__.py` with new exports
2. Create adapter functions for backward compatibility
3. Update downstream consumers (adjacency, connectivity, etc.)

### 6.4 Backward Compatibility

```python
# Adapter function to convert old dict format to new model
def from_legacy_model(old_model: BuildingModel) -> Building:
    """Convert legacy BuildingModel to new Building."""
    # Conversion logic here
    pass

# Adapter function to convert new model to old dict format
def to_legacy_model(building: Building) -> BuildingModel:
    """Convert new Building to legacy BuildingModel."""
    # Conversion logic here
    pass
```

---

## 7. Future-Proofing

### 7.1 BIM/IFC Export

The entity structure maps directly to IFC entities:

| Our Model | IFC Entity |
|-----------|------------|
| `Building` | `IfcBuilding` |
| `Floor` | `IfcBuildingStorey` |
| `Room` | `IfcSpace` |
| `Wall` | `IfcWall` |
| `Door` | `IfcDoor` |
| `Window` | `IfcWindow` |
| `Column` | `IfcColumn` |
| `Stair` | `IfcStair` |

### 7.2 AI Reasoning

The relationship graph and typed entities enable:
- Room classification by size/shape/position
- Pathfinding through adjacency
- Natural language queries ("Find all north-facing bedrooms")

### 7.3 Flutter Visualization

The `to_dict()` methods produce JSON directly consumable by Flutter:
- `geometry.polygon` → Canvas drawing data
- `bounding_box` → Viewport calculations
- `orientation_degrees` → Label rotation

### 7.4 Vastu Analysis

The `Orientation` enum and room positions enable:
- Zone identification (NE, SW, center)
- Room placement validation
- Compliance scoring

---

## 8. Acceptance Criteria

- [ ] All entities have UUID-based identification
- [ ] All entities have geometry, bounding box, area, perimeter, orientation
- [ ] Building exposes total area, room count, wall count, door count, window count
- [ ] Building exposes building orientation
- [ ] All models are immutable frozen dataclasses
- [ ] Type hints are comprehensive
- [ ] JSON serialization/deserialization works correctly
- [ ] Validation catches invalid models
- [ ] Backward compatibility maintained via adapters
- [ ] Test coverage >90%

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Next Review:** After approval