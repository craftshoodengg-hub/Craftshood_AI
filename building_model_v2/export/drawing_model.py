"""Unified DrawingModel abstraction.

An immutable dataclass that serves as the intermediate representation
between BuildingModel and any exporter (DXF, SVG, PDF, etc.).

The DrawingModel contains:
- layers: ordered tuple of layer definitions
- entities: ordered tuple of drawing entities
- bounds: axis-aligned bounding box of all geometry
- metadata: key-value metadata for the drawing
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from .drawing_entities import (
    ArcEntity,
    CircleEntity,
    DimensionEntity,
    GroupEntity,
    HatchEntity,
    LineEntity,
    PolygonEntity,
    PolylineEntity,
    TextEntity,
    _entity_from_dict,
    _entity_to_dict,
)


@dataclass(frozen=True, slots=True)
class DrawingLayer:
    """Definition of a drawing layer.

    Attributes:
        name: Layer name (e.g., 'A-WALL').
        color: Default color for entities on this layer.
        visible: Whether the layer is visible.
        locked: Whether the layer is locked.
    """
    name: str
    color: str = "#000000"
    visible: bool = True
    locked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "color": self.color,
            "visible": self.visible,
            "locked": self.locked,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        return cls(
            name=str(payload["name"]),
            color=str(payload.get("color", "#000000")),
            visible=bool(payload.get("visible", True)),
            locked=bool(payload.get("locked", False)),
        )


@dataclass(frozen=True, slots=True)
class DrawingBounds:
    """Axis-aligned bounding box for the drawing.

    Attributes:
        min_x: Minimum x coordinate.
        min_y: Minimum y coordinate.
        max_x: Maximum x coordinate.
        max_y: Maximum y coordinate.
    """
    min_x: float = 0.0
    min_y: float = 0.0
    max_x: float = 0.0
    max_y: float = 0.0

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    def to_dict(self) -> dict[str, Any]:
        return {
            "min_x": self.min_x, "min_y": self.min_y,
            "max_x": self.max_x, "max_y": self.max_y,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        return cls(
            min_x=float(payload.get("min_x", 0.0)),
            min_y=float(payload.get("min_y", 0.0)),
            max_x=float(payload.get("max_x", 0.0)),
            max_y=float(payload.get("max_y", 0.0)),
        )


# Type alias for any drawing entity
DrawingEntity = (
    LineEntity | PolylineEntity | PolygonEntity | CircleEntity |
    ArcEntity | TextEntity | DimensionEntity | HatchEntity | GroupEntity
)


@dataclass(frozen=True, slots=True)
class DrawingModel:
    """Immutable drawing model — the unified intermediate representation.

    Attributes:
        layers: Ordered tuple of DrawingLayer definitions.
        entities: Ordered tuple of drawing entities.
        bounds: Axis-aligned bounding box of all geometry.
        metadata: Key-value metadata (title, author, scale, etc.).
    """
    layers: tuple[DrawingLayer, ...] = ()
    entities: tuple[DrawingEntity, ...] = ()
    bounds: DrawingBounds = field(default_factory=DrawingBounds)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "layers": [layer.to_dict() for layer in self.layers],
            "entities": [_entity_to_dict(e) for e in self.entities],
            "bounds": self.bounds.to_dict(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Deserialize from dictionary."""
        layers = tuple(
            DrawingLayer.from_dict(layer)
            for layer in payload.get("layers", [])
        )
        entities = tuple(
            _entity_from_dict(e) for e in payload.get("entities", [])
        )
        bounds = DrawingBounds.from_dict(payload.get("bounds", {}))
        metadata = dict(payload.get("metadata", {}))
        return cls(
            layers=layers,
            entities=entities,
            bounds=bounds,
            metadata=metadata,
        )

    @classmethod
    def empty(cls) -> Self:
        """Create an empty drawing model."""
        return cls()
