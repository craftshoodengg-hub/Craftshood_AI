"""Annotation engine - generates professional annotations."""
from __future__ import annotations
from typing import Any
from ..validation.cross_entity_validator import BuildingModel
from .annotation_entities import (
    RoomTag, DoorTag, WindowTag, GridBubble, NorthArrow, ScaleBar,
    TitleNote, LeaderNote, RevisionCloud,
)
from .annotation_settings import AnnotationSettings
from .dimension_engine import generate_all_dimensions


def generate_room_tags(model, settings):
    tags = []
    room_idx = 1
    for room_id in sorted(model.rooms.keys()):
        room = model.rooms[room_id]
        if room.polygon.is_empty:
            continue
        c = room.centroid
        tags.append(RoomTag(
            x=c.x, y=c.y + 0.2, room_name=room.room_type.value,
            room_number='R{:02d}'.format(room_idx),
            area=room.area, floor=room.floor_id or '',
            font_size=settings.text_height))
        if settings.show_room_areas:
            tags.append(RoomTag(
                x=c.x, y=c.y - 0.3, room_name='{:.0f} sqft'.format(room.area),
                font_size=settings.text_height * 0.7))
        room_idx += 1
    return tags


def generate_door_tags(model, settings):
    tags = []
    door_idx = 1
    for door in model.doors.values():
        if door.location is None:
            continue
        tags.append(DoorTag(
            x=door.location.x, y=door.location.y,
            door_number='D{:02d}'.format(door_idx), width=door.width,
            font_size=settings.text_height * 0.7))
        door_idx += 1
    return tags


def generate_window_tags(model, settings):
    tags = []
    win_idx = 1
    for win in model.windows.values():
        if win.location is None:
            continue
        tags.append(WindowTag(
            x=win.location.x, y=win.location.y,
            window_number='W{:02d}'.format(win_idx), width=win.width,
            font_size=settings.text_height * 0.7))
        win_idx += 1
    return tags


def generate_grid_bubbles(model, settings):
    bubbles = []
    if not settings.show_grid_labels:
        return bubbles
    bounds = _get_bounds(model)
    spacing = settings.grid_spacing
    x = float(int(bounds[0]/spacing)*int(spacing))
    col_idx = 1
    while x <= bounds[2]:
        bubbles.append(GridBubble(
            x=x, y=bounds[3] + 3, label=str(col_idx),
            direction='horizontal'))
        x += spacing
        col_idx += 1
    y = float(int(bounds[1]/spacing)*int(spacing))
    row_idx = 1
    while y <= bounds[3]:
        bubbles.append(GridBubble(
            x=bounds[0] - 3, y=y, label=chr(64 + row_idx),
            direction='vertical'))
        y += spacing
        row_idx += 1
    return bubbles


def generate_north_arrow(model, settings):
    if not settings.show_north_arrow:
        return []
    bounds = _get_bounds(model)
    return [NorthArrow(
        x=bounds[2] + 15, y=bounds[3] - 15,
        size=settings.scale_bar_size)]


def generate_scale_bar(model, settings):
    if not settings.show_scale_bar:
        return []
    bounds = _get_bounds(model)
    return [ScaleBar(
        x=bounds[2] - settings.scale_bar_size - 5,
        y=bounds[1] - 15, length=settings.scale_bar_size,
        label='{:.0f} ft'.format(settings.scale_bar_size))]


def generate_title_note(model, settings):
    if not settings.show_title:
        return []
    bounds = _get_bounds(model)
    building_name = ''
    if model.building is not None:
        building_name = model.building.name
    return [TitleNote(
        x=(bounds[0] + bounds[2]) / 2, y=bounds[3] + 10,
        text=building_name or 'Untitled',
        font_size=settings.text_height * 1.4)]


def generate_all_annotations(model, settings=None):
    if settings is None:
        settings = AnnotationSettings.default()
    annotations = []
    if settings.show_room_labels:
        annotations.extend(generate_room_tags(model, settings))
    if settings.show_door_numbers:
        annotations.extend(generate_door_tags(model, settings))
    if settings.show_window_numbers:
        annotations.extend(generate_window_tags(model, settings))
    annotations.extend(generate_grid_bubbles(model, settings))
    annotations.extend(generate_north_arrow(model, settings))
    annotations.extend(generate_scale_bar(model, settings))
    annotations.extend(generate_title_note(model, settings))
    annotations.extend(generate_all_dimensions(model, settings))
    return annotations


def _get_bounds(model):
    mn_x = mn_y = float('inf')
    mx_x = mx_y = float('-inf')
    for room in model.rooms.values():
        if not room.polygon.is_empty:
            b = room.polygon.bounds
            mn_x, mn_y = min(mn_x, b[0]), min(mn_y, b[1])
            mx_x, mx_y = max(mx_x, b[2]), max(mx_y, b[3])
    if mn_x == float('inf'):
        return -10.0, -10.0, 10.0, 10.0
    return mn_x, mn_y, mx_x, mx_y
