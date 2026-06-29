"""Dimension engine - generates automatic dimensions."""
from __future__ import annotations
import math
from ..validation.cross_entity_validator import BuildingModel
from ..base import BoundingBox
from .annotation_entities import LinearDimension, AlignedDimension
from .annotation_settings import AnnotationSettings


def _format_length(value, precision=0):
    if precision == 0:
        return '{:.0f} ft'.format(value)
    return '{:.{}f} ft'.format(value, precision)


def generate_overall_dimensions(model, settings):
    if not model.rooms:
        return []
    bounds = _get_model_bounds(model)
    dims = []
    offset = settings.dimension_offset
    dims.append(LinearDimension(
        x1=bounds.min_x, y1=bounds.min_y, x2=bounds.max_x, y2=bounds.min_y,
        offset=offset, label=_format_length(bounds.width, settings.label_precision),
        font_size=settings.dimension_text_height))
    dims.append(LinearDimension(
        x1=bounds.min_x, y1=bounds.min_y, x2=bounds.min_x, y2=bounds.max_y,
        offset=offset, label=_format_length(bounds.height, settings.label_precision),
        font_size=settings.dimension_text_height))
    return dims


def generate_room_dimensions(model, settings):
    dims = []
    for room in model.rooms.values():
        if room.polygon.is_empty:
            continue
        b = room.polygon.bounds
        w = b[2] - b[0]
        h = b[3] - b[1]
        dims.append(AlignedDimension(
            x1=b[0], y1=b[1], x2=b[2], y2=b[1],
            offset=settings.dimension_offset * 0.6,
            label=_format_length(w, settings.label_precision)))
        dims.append(AlignedDimension(
            x1=b[0], y1=b[1], x2=b[0], y2=b[3],
            offset=settings.dimension_offset * 0.6,
            label=_format_length(h, settings.label_precision)))
    return dims


def generate_door_window_dimensions(model, settings):
    dims = []
    for door in model.doors.values():
        if door.location is None:
            continue
        dims.append(AlignedDimension(
            x1=door.location.x - door.width/2, y1=door.location.y,
            x2=door.location.x + door.width/2, y2=door.location.y,
            offset=settings.dimension_offset * 0.4,
            label=_format_length(door.width, settings.label_precision)))
    for win in model.windows.values():
        if win.location is None:
            continue
        dims.append(AlignedDimension(
            x1=win.location.x - win.width/2, y1=win.location.y,
            x2=win.location.x + win.width/2, y2=win.location.y,
            offset=settings.dimension_offset * 0.4,
            label=_format_length(win.width, settings.label_precision)))
    return dims


def generate_column_spacing_dimensions(model, settings):
    dims = []
    columns = list(model.columns.values())
    if len(columns) < 2:
        return dims
    sorted_cols = sorted(columns, key=lambda c: (c.geometry.x, c.geometry.y) if c.geometry else (0, 0))
    for i in range(len(sorted_cols) - 1):
        c1, c2 = sorted_cols[i], sorted_cols[i + 1]
        if c1.geometry is None or c2.geometry is None:
            continue
        dist = math.sqrt((c2.geometry.x - c1.geometry.x)**2 + (c2.geometry.y - c1.geometry.y)**2)
        dims.append(AlignedDimension(
            x1=c1.geometry.x, y1=c1.geometry.y, x2=c2.geometry.x, y2=c2.geometry.y,
            offset=settings.dimension_offset * 0.5,
            label=_format_length(dist, settings.label_precision)))
    return dims


def generate_wall_thickness_dimensions(model, settings):
    dims = []
    for wall in model.walls.values():
        if wall.geometry.is_empty or wall.width <= 0:
            continue
        coords = list(wall.geometry.coords)
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            if length > 0:
                dims.append(AlignedDimension(
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    offset=settings.dimension_offset * 0.3,
                    label=_format_length(length, settings.label_precision)))
    return dims


def generate_all_dimensions(model, settings=None):
    if settings is None:
        settings = AnnotationSettings.default()
    dims = []
    if settings.show_dimensions:
        dims.extend(generate_overall_dimensions(model, settings))
        dims.extend(generate_room_dimensions(model, settings))
        dims.extend(generate_door_window_dimensions(model, settings))
        dims.extend(generate_column_spacing_dimensions(model, settings))
        dims.extend(generate_wall_thickness_dimensions(model, settings))
    return dims


def _get_model_bounds(model):
    mn_x = mn_y = float('inf')
    mx_x = mx_y = float('-inf')
    for room in model.rooms.values():
        if not room.polygon.is_empty:
            b = room.polygon.bounds
            mn_x, mn_y = min(mn_x, b[0]), min(mn_y, b[1])
            mx_x, mx_y = max(mx_x, b[2]), max(mx_y, b[3])
    if mn_x == float('inf'):
        return BoundingBox(-10, -10, 10, 10)
    return BoundingBox(mn_x, mn_y, mx_x, mx_y)
