"""Drawing entities for the unified drawing model."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Self

@dataclass(frozen=True, slots=True)
class LineEntity:
    x1: float
    y1: float
    x2: float
    y2: float
    layer: str = "0"
    color: str = "#000000"
    stroke_width: float = 0.25
    def to_dict(self):
        return {"type": "line", "x1": self.x1, "y1": self.y1,
                "x2": self.x2, "y2": self.y2, "layer": self.layer,
                "color": self.color, "stroke_width": self.stroke_width}
    @classmethod
    def from_dict(cls, payload):
        return cls(x1=float(payload["x1"]), y1=float(payload["y1"]),
                   x2=float(payload["x2"]), y2=float(payload["y2"]),
                   layer=str(payload.get("layer", "0")),
                   color=str(payload.get("color", "#000000")),
                   stroke_width=float(payload.get("stroke_width", 0.25)))

@dataclass(frozen=True, slots=True)
class PolylineEntity:
    points: tuple = ()
    layer: str = "0"
    color: str = "#000000"
    stroke_width: float = 0.25
    closed: bool = False
    def to_dict(self):
        return {"type": "polyline", "points": list(self.points),
                "layer": self.layer, "color": self.color,
                "stroke_width": self.stroke_width, "closed": self.closed}
    @classmethod
    def from_dict(cls, payload):
        pts = tuple((float(x), float(y)) for x, y in payload.get("points", []))
        return cls(points=pts, layer=str(payload.get("layer", "0")),
                   color=str(payload.get("color", "#000000")),
                   stroke_width=float(payload.get("stroke_width", 0.25)),
                   closed=bool(payload.get("closed", False)))

@dataclass(frozen=True, slots=True)
class PolygonEntity:
    points: tuple = ()
    layer: str = "0"
    fill_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: float = 0.25
    fill_opacity: float = 1.0
    def to_dict(self):
        return {"type": "polygon", "points": list(self.points),
                "layer": self.layer, "fill_color": self.fill_color,
                "stroke_color": self.stroke_color,
                "stroke_width": self.stroke_width,
                "fill_opacity": self.fill_opacity}
    @classmethod
    def from_dict(cls, payload):
        pts = tuple((float(x), float(y)) for x, y in payload.get("points", []))
        return cls(points=pts, layer=str(payload.get("layer", "0")),
                   fill_color=str(payload.get("fill_color", "#FFFFFF")),
                   stroke_color=str(payload.get("stroke_color", "#000000")),
                   stroke_width=float(payload.get("stroke_width", 0.25)),
                   fill_opacity=float(payload.get("fill_opacity", 1.0)))

@dataclass(frozen=True, slots=True)
class CircleEntity:
    cx: float = 0.0
    cy: float = 0.0
    radius: float = 1.0
    layer: str = "0"
    fill_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: float = 0.25
    fill_opacity: float = 1.0
    def to_dict(self):
        return {"type": "circle", "cx": self.cx, "cy": self.cy,
                "radius": self.radius, "layer": self.layer,
                "fill_color": self.fill_color, "stroke_color": self.stroke_color,
                "stroke_width": self.stroke_width, "fill_opacity": self.fill_opacity}
    @classmethod
    def from_dict(cls, payload):
        return cls(cx=float(payload.get("cx", 0.0)), cy=float(payload.get("cy", 0.0)),
                   radius=float(payload.get("radius", 1.0)),
                   layer=str(payload.get("layer", "0")),
                   fill_color=str(payload.get("fill_color", "#FFFFFF")),
                   stroke_color=str(payload.get("stroke_color", "#000000")),
                   stroke_width=float(payload.get("stroke_width", 0.25)),
                   fill_opacity=float(payload.get("fill_opacity", 1.0)))

@dataclass(frozen=True, slots=True)
class ArcEntity:
    cx: float = 0.0
    cy: float = 0.0
    radius: float = 1.0
    start_angle: float = 0.0
    end_angle: float = 90.0
    layer: str = "0"
    color: str = "#000000"
    stroke_width: float = 0.25
    def to_dict(self):
        return {"type": "arc", "cx": self.cx, "cy": self.cy,
                "radius": self.radius, "start_angle": self.start_angle,
                "end_angle": self.end_angle, "layer": self.layer,
                "color": self.color, "stroke_width": self.stroke_width}
    @classmethod
    def from_dict(cls, payload):
        return cls(cx=float(payload.get("cx", 0.0)), cy=float(payload.get("cy", 0.0)),
                   radius=float(payload.get("radius", 1.0)),
                   start_angle=float(payload.get("start_angle", 0.0)),
                   end_angle=float(payload.get("end_angle", 90.0)),
                   layer=str(payload.get("layer", "0")),
                   color=str(payload.get("color", "#000000")),
                   stroke_width=float(payload.get("stroke_width", 0.25)))

@dataclass(frozen=True, slots=True)
class TextEntity:
    x: float = 0.0
    y: float = 0.0
    text: str = ""
    font_size: float = 0.5
    layer: str = "0"
    color: str = "#000000"
    rotation: float = 0.0
    anchor: str = "middle"
    def to_dict(self):
        return {"type": "text", "x": self.x, "y": self.y,
                "text": self.text, "font_size": self.font_size,
                "layer": self.layer, "color": self.color,
                "rotation": self.rotation, "anchor": self.anchor}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get("x", 0.0)), y=float(payload.get("y", 0.0)),
                   text=str(payload.get("text", "")),
                   font_size=float(payload.get("font_size", 0.5)),
                   layer=str(payload.get("layer", "0")),
                   color=str(payload.get("color", "#000000")),
                   rotation=float(payload.get("rotation", 0.0)),
                   anchor=str(payload.get("anchor", "middle")))

@dataclass(frozen=True, slots=True)
class DimensionEntity:
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    offset_y: float = 0.0
    label: str = ""
    layer: str = "A-DIMS"
    color: str = "#808080"
    font_size: float = 0.35
    def to_dict(self):
        return {"type": "dimension", "x1": self.x1, "y1": self.y1,
                "x2": self.x2, "y2": self.y2, "offset_y": self.offset_y,
                "label": self.label, "layer": self.layer,
                "color": self.color, "font_size": self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x1=float(payload.get("x1", 0.0)), y1=float(payload.get("y1", 0.0)),
                   x2=float(payload.get("x2", 0.0)), y2=float(payload.get("y2", 0.0)),
                   offset_y=float(payload.get("offset_y", 0.0)),
                   label=str(payload.get("label", "")),
                   layer=str(payload.get("layer", "A-DIMS")),
                   color=str(payload.get("color", "#808080")),
                   font_size=float(payload.get("font_size", 0.35)))

@dataclass(frozen=True, slots=True)
class HatchEntity:
    points: tuple = ()
    pattern: str = "SOLID"
    layer: str = "A-HATCH"
    color: str = "#C0C0C0"
    scale: float = 1.0
    def to_dict(self):
        return {"type": "hatch", "points": list(self.points),
                "pattern": self.pattern, "layer": self.layer,
                "color": self.color, "scale": self.scale}
    @classmethod
    def from_dict(cls, payload):
        pts = tuple((float(x), float(y)) for x, y in payload.get("points", []))
        return cls(points=pts, pattern=str(payload.get("pattern", "SOLID")),
                   layer=str(payload.get("layer", "A-HATCH")),
                   color=str(payload.get("color", "#C0C0C0")),
                   scale=float(payload.get("scale", 1.0)))

@dataclass(frozen=True, slots=True)
class GroupEntity:
    name: str = ""
    entities: tuple = ()
    layer: str = "0"
    def to_dict(self):
        return {"type": "group", "name": self.name,
                "entities": [_entity_to_dict(e) for e in self.entities],
                "layer": self.layer}
    @classmethod
    def from_dict(cls, payload):
        children = tuple(_entity_from_dict(e) for e in payload.get("entities", []))
        return cls(name=str(payload.get("name", "")),
                   entities=children, layer=str(payload.get("layer", "0")))


_ENTITY_TYPES: dict[str, type] = {
    "line": LineEntity, "polyline": PolylineEntity, "polygon": PolygonEntity,
    "circle": CircleEntity, "arc": ArcEntity, "text": TextEntity,
    "dimension": DimensionEntity, "hatch": HatchEntity, "group": GroupEntity,
}


def _entity_to_dict(entity: Any) -> dict[str, Any]:
    if hasattr(entity, "to_dict"):
        return entity.to_dict()
    raise TypeError(f"Cannot serialize entity of type {type(entity).__name__}")


def _entity_from_dict(payload: dict[str, Any]) -> Any:
    type_key = payload.get("type", "")
    cls = _ENTITY_TYPES.get(type_key)
    if cls is None:
        raise ValueError(f"Unknown entity type: {type_key!r}")
    return cls.from_dict(payload)

