"""Annotation settings for the annotation engine."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Self


@dataclass(frozen=True, slots=True)
class AnnotationSettings:
    """Settings controlling annotation generation."""
    text_height: float = 0.5
    dimension_text_height: float = 0.35
    arrow_size: float = 0.5
    dimension_offset: float = 5.0
    grid_spacing: float = 10.0
    scale_bar_size: float = 10.0
    label_precision: int = 0
    show_room_labels: bool = True
    show_room_areas: bool = True
    show_room_numbers: bool = True
    show_door_numbers: bool = True
    show_window_numbers: bool = True
    show_dimensions: bool = True
    show_north_arrow: bool = True
    show_scale_bar: bool = True
    show_grid_labels: bool = True
    show_title: bool = True
    show_revisions: bool = True
    units: str = 'feet'
    font_family: str = 'Arial'

    def to_dict(self):
        return {
            'text_height': self.text_height,
            'dimension_text_height': self.dimension_text_height,
            'arrow_size': self.arrow_size, 'dimension_offset': self.dimension_offset,
            'grid_spacing': self.grid_spacing, 'scale_bar_size': self.scale_bar_size,
            'label_precision': self.label_precision, 'show_room_labels': self.show_room_labels,
            'show_room_areas': self.show_room_areas, 'show_room_numbers': self.show_room_numbers,
            'show_door_numbers': self.show_door_numbers, 'show_window_numbers': self.show_window_numbers,
            'show_dimensions': self.show_dimensions, 'show_north_arrow': self.show_north_arrow,
            'show_scale_bar': self.show_scale_bar, 'show_grid_labels': self.show_grid_labels,
            'show_title': self.show_title, 'show_revisions': self.show_revisions,
            'units': self.units, 'font_family': self.font_family,
        }

    @classmethod
    def from_dict(cls, payload):
        return cls(
            text_height=float(payload.get('text_height', 0.5)),
            dimension_text_height=float(payload.get('dimension_text_height', 0.35)),
            arrow_size=float(payload.get('arrow_size', 0.5)),
            dimension_offset=float(payload.get('dimension_offset', 5.0)),
            grid_spacing=float(payload.get('grid_spacing', 10.0)),
            scale_bar_size=float(payload.get('scale_bar_size', 10.0)),
            label_precision=int(payload.get('label_precision', 0)),
            show_room_labels=bool(payload.get('show_room_labels', True)),
            show_room_areas=bool(payload.get('show_room_areas', True)),
            show_room_numbers=bool(payload.get('show_room_numbers', True)),
            show_door_numbers=bool(payload.get('show_door_numbers', True)),
            show_window_numbers=bool(payload.get('show_window_numbers', True)),
            show_dimensions=bool(payload.get('show_dimensions', True)),
            show_north_arrow=bool(payload.get('show_north_arrow', True)),
            show_scale_bar=bool(payload.get('show_scale_bar', True)),
            show_grid_labels=bool(payload.get('show_grid_labels', True)),
            show_title=bool(payload.get('show_title', True)),
            show_revisions=bool(payload.get('show_revisions', True)),
            units=str(payload.get('units', 'feet')),
            font_family=str(payload.get('font_family', 'Arial')),
        )

    @classmethod
    def default(cls):
        return cls()
