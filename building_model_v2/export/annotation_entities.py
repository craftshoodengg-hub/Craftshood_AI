"""Annotation entities for the annotation engine."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Self

@dataclass(frozen=True, slots=True)
class LinearDimension:
    x1: float
    y1: float
    x2: float
    y2: float
    offset: float = 5.0
    label: str = ''
    layer: str = 'A-DIMS'
    color: str = '#808080'
    font_size: float = 0.35
    precision: int = 0
    def to_dict(self):
        return {'type': 'linear_dim', 'x1': self.x1, 'y1': self.y1,
                'x2': self.x2, 'y2': self.y2, 'offset': self.offset,
                'label': self.label, 'layer': self.layer, 'color': self.color,
                'font_size': self.font_size, 'precision': self.precision}
    @classmethod
    def from_dict(cls, payload):
        return cls(x1=float(payload.get('x1', 0)), y1=float(payload.get('y1', 0)),
                   x2=float(payload.get('x2', 0)), y2=float(payload.get('y2', 0)),
                   offset=float(payload.get('offset', 5)),
                   label=str(payload.get('label', '')),
                   layer=str(payload.get('layer', 'A-DIMS')),
                   color=str(payload.get('color', '#808080')),
                   font_size=float(payload.get('font_size', 0.35)),
                   precision=int(payload.get('precision', 0)))

@dataclass(frozen=True, slots=True)
class AlignedDimension:
    x1: float
    y1: float
    x2: float
    y2: float
    offset: float = 5.0
    label: str = ''
    layer: str = 'A-DIMS'
    color: str = '#808080'
    font_size: float = 0.35
    def to_dict(self):
        return {'type': 'aligned_dim', 'x1': self.x1, 'y1': self.y1,
                'x2': self.x2, 'y2': self.y2, 'offset': self.offset,
                'label': self.label, 'layer': self.layer, 'color': self.color,
                'font_size': self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x1=float(payload.get('x1', 0)), y1=float(payload.get('y1', 0)),
                   x2=float(payload.get('x2', 0)), y2=float(payload.get('y2', 0)),
                   offset=float(payload.get('offset', 5)),
                   label=str(payload.get('label', '')),
                   layer=str(payload.get('layer', 'A-DIMS')),
                   color=str(payload.get('color', '#808080')),
                   font_size=float(payload.get('font_size', 0.35)))

@dataclass(frozen=True, slots=True)
class AngularDimension:
    cx: float
    cy: float
    radius: float
    start_angle: float
    end_angle: float
    label: str = ''
    layer: str = 'A-DIMS'
    color: str = '#808080'
    font_size: float = 0.35
    def to_dict(self):
        return {'type': 'angular_dim', 'cx': self.cx, 'cy': self.cy,
                'radius': self.radius, 'start_angle': self.start_angle,
                'end_angle': self.end_angle, 'label': self.label,
                'layer': self.layer, 'color': self.color,
                'font_size': self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(cx=float(payload.get('cx', 0)), cy=float(payload.get('cy', 0)),
                   radius=float(payload.get('radius', 1)),
                   start_angle=float(payload.get('start_angle', 0)),
                   end_angle=float(payload.get('end_angle', 90)),
                   label=str(payload.get('label', '')),
                   layer=str(payload.get('layer', 'A-DIMS')),
                   color=str(payload.get('color', '#808080')),
                   font_size=float(payload.get('font_size', 0.35)))

@dataclass(frozen=True, slots=True)
class LeaderNote:
    x: float
    y: float
    text: str
    target_x: float = 0.0
    target_y: float = 0.0
    layer: str = 'A-TEXT'
    color: str = '#000000'
    font_size: float = 0.5
    arrow_size: float = 0.5
    def to_dict(self):
        return {'type': 'leader', 'x': self.x, 'y': self.y, 'text': self.text,
                'target_x': self.target_x, 'target_y': self.target_y,
                'layer': self.layer, 'color': self.color,
                'font_size': self.font_size, 'arrow_size': self.arrow_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   text=str(payload.get('text', '')),
                   target_x=float(payload.get('target_x', 0)),
                   target_y=float(payload.get('target_y', 0)),
                   layer=str(payload.get('layer', 'A-TEXT')),
                   color=str(payload.get('color', '#000000')),
                   font_size=float(payload.get('font_size', 0.5)),
                   arrow_size=float(payload.get('arrow_size', 0.5)))

@dataclass(frozen=True, slots=True)
class RoomTag:
    x: float
    y: float
    room_name: str
    room_number: str = ''
    area: float = 0.0
    floor: str = ''
    layer: str = 'A-TEXT'
    color: str = '#000000'
    font_size: float = 0.5
    def to_dict(self):
        return {'type': 'room_tag', 'x': self.x, 'y': self.y,
                'room_name': self.room_name, 'room_number': self.room_number,
                'area': self.area, 'floor': self.floor,
                'layer': self.layer, 'color': self.color,
                'font_size': self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   room_name=str(payload.get('room_name', '')),
                   room_number=str(payload.get('room_number', '')),
                   area=float(payload.get('area', 0)),
                   floor=str(payload.get('floor', '')),
                   layer=str(payload.get('layer', 'A-TEXT')),
                   color=str(payload.get('color', '#000000')),
                   font_size=float(payload.get('font_size', 0.5)))

@dataclass(frozen=True, slots=True)
class DoorTag:
    x: float
    y: float
    door_number: str
    width: float = 3.0
    layer: str = 'A-DOOR'
    color: str = '#0000FF'
    font_size: float = 0.35
    def to_dict(self):
        return {'type': 'door_tag', 'x': self.x, 'y': self.y,
                'door_number': self.door_number, 'width': self.width,
                'layer': self.layer, 'color': self.color,
                'font_size': self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   door_number=str(payload.get('door_number', '')),
                   width=float(payload.get('width', 3)),
                   layer=str(payload.get('layer', 'A-DOOR')),
                   color=str(payload.get('color', '#0000FF')),
                   font_size=float(payload.get('font_size', 0.35)))

@dataclass(frozen=True, slots=True)
class WindowTag:
    x: float
    y: float
    window_number: str
    width: float = 4.0
    layer: str = 'A-WINDOW'
    color: str = '#0080FF'
    font_size: float = 0.35
    def to_dict(self):
        return {'type': 'window_tag', 'x': self.x, 'y': self.y,
                'window_number': self.window_number, 'width': self.width,
                'layer': self.layer, 'color': self.color,
                'font_size': self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   window_number=str(payload.get('window_number', '')),
                   width=float(payload.get('width', 4)),
                   layer=str(payload.get('layer', 'A-WINDOW')),
                   color=str(payload.get('color', '#0080FF')),
                   font_size=float(payload.get('font_size', 0.35)))

@dataclass(frozen=True, slots=True)
class GridBubble:
    x: float
    y: float
    label: str
    radius: float = 1.5
    direction: str = 'horizontal'
    layer: str = 'A-GRID'
    color: str = '#000000'
    font_size: float = 0.5
    def to_dict(self):
        return {'type': 'grid_bubble', 'x': self.x, 'y': self.y,
                'label': self.label, 'radius': self.radius,
                'direction': self.direction, 'layer': self.layer,
                'color': self.color, 'font_size': self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   label=str(payload.get('label', '')),
                   radius=float(payload.get('radius', 1.5)),
                   direction=str(payload.get('direction', 'horizontal')),
                   layer=str(payload.get('layer', 'A-GRID')),
                   color=str(payload.get('color', '#000000')),
                   font_size=float(payload.get('font_size', 0.5)))

@dataclass(frozen=True, slots=True)
class NorthArrow:
    x: float
    y: float
    size: float = 10.0
    rotation: float = 0.0
    layer: str = 'A-TITLE'
    color: str = '#000000'
    def to_dict(self):
        return {'type': 'north_arrow', 'x': self.x, 'y': self.y,
                'size': self.size, 'rotation': self.rotation,
                'layer': self.layer, 'color': self.color}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   size=float(payload.get('size', 10)),
                   rotation=float(payload.get('rotation', 0)),
                   layer=str(payload.get('layer', 'A-TITLE')),
                   color=str(payload.get('color', '#000000')))

@dataclass(frozen=True, slots=True)
class ScaleBar:
    x: float
    y: float
    length: float = 10.0
    height: float = 1.0
    label: str = '10 ft'
    layer: str = 'A-TITLE'
    color: str = '#000000'
    font_size: float = 0.35
    def to_dict(self):
        return {'type': 'scale_bar', 'x': self.x, 'y': self.y,
                'length': self.length, 'height': self.height,
                'label': self.label, 'layer': self.layer,
                'color': self.color, 'font_size': self.font_size}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   length=float(payload.get('length', 10)),
                   height=float(payload.get('height', 1)),
                   label=str(payload.get('label', '10 ft')),
                   layer=str(payload.get('layer', 'A-TITLE')),
                   color=str(payload.get('color', '#000000')),
                   font_size=float(payload.get('font_size', 0.35)))

@dataclass(frozen=True, slots=True)
class TitleNote:
    x: float
    y: float
    text: str
    font_size: float = 0.7
    layer: str = 'A-TITLE'
    color: str = '#000000'
    anchor: str = 'middle'
    def to_dict(self):
        return {'type': 'title_note', 'x': self.x, 'y': self.y, 'text': self.text,
                'font_size': self.font_size, 'layer': self.layer,
                'color': self.color, 'anchor': self.anchor}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   text=str(payload.get('text', '')),
                   font_size=float(payload.get('font_size', 0.7)),
                   layer=str(payload.get('layer', 'A-TITLE')),
                   color=str(payload.get('color', '#000000')),
                   anchor=str(payload.get('anchor', 'middle')))

@dataclass(frozen=True, slots=True)
class RevisionCloud:
    x: float
    y: float
    radius: float = 5.0
    revision: str = 'A'
    date: str = ''
    description: str = ''
    layer: str = 'A-TITLE'
    color: str = '#FF0000'
    def to_dict(self):
        return {'type': 'revision_cloud', 'x': self.x, 'y': self.y,
                'radius': self.radius, 'revision': self.revision,
                'date': self.date, 'description': self.description,
                'layer': self.layer, 'color': self.color}
    @classmethod
    def from_dict(cls, payload):
        return cls(x=float(payload.get('x', 0)), y=float(payload.get('y', 0)),
                   radius=float(payload.get('radius', 5)),
                   revision=str(payload.get('revision', 'A')),
                   date=str(payload.get('date', '')),
                   description=str(payload.get('description', '')),
                   layer=str(payload.get('layer', 'A-TITLE')),
                   color=str(payload.get('color', '#FF0000')))

_ANNOTATION_TYPES: dict[str, type] = {
    'linear_dim': LinearDimension, 'aligned_dim': AlignedDimension,
    'angular_dim': AngularDimension, 'leader': LeaderNote,
    'room_tag': RoomTag, 'door_tag': DoorTag, 'window_tag': WindowTag,
    'grid_bubble': GridBubble, 'north_arrow': NorthArrow,
    'scale_bar': ScaleBar, 'title_note': TitleNote,
    'revision_cloud': RevisionCloud,
}


def annotation_to_dict(entity: Any) -> dict[str, Any]:
    if hasattr(entity, 'to_dict'):
        return entity.to_dict()
    raise TypeError(f'Cannot serialize {type(entity).__name__}')


def annotation_from_dict(payload: dict[str, Any]) -> Any:
    type_key = payload.get('type', '')
    cls = _ANNOTATION_TYPES.get(type_key)
    if cls is None:
        raise ValueError(f'Unknown annotation type: {type_key!r}')
    return cls.from_dict(payload)
