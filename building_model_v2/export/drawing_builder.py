"""DrawingBuilder - converts BuildingModel into DrawingModel."""
from __future__ import annotations
from typing import Any
from ..validation.cross_entity_validator import BuildingModel
from .drawing_entities import (
    ArcEntity, CircleEntity, DimensionEntity, HatchEntity,
    LineEntity, PolygonEntity, PolylineEntity, TextEntity,
)
from .drawing_model import DrawingBounds, DrawingLayer, DrawingModel
from .svg_styles import *
DrawingEntity = (
    LineEntity | PolylineEntity | PolygonEntity | CircleEntity |
    ArcEntity | TextEntity | DimensionEntity | HatchEntity
)

def _compute_bounds(model):
    mn_x, mn_y = float('inf'), float('inf')
    mx_x, mx_y = float('-inf'), float('-inf')
    for room in model.rooms.values():
        if not room.polygon.is_empty:
            b = room.polygon.bounds
            mn_x, mn_y = min(mn_x, b[0]), min(mn_y, b[1])
            mx_x, mx_y = max(mx_x, b[2]), max(mx_y, b[3])
    if mn_x == float('inf'): return DrawingBounds(-10.0, -10.0, 10.0, 10.0)
    return DrawingBounds(mn_x, mn_y, mx_x, mx_y)

def _build_layers():
    return (
        DrawingLayer('A-WALL', COLOR_WALL), DrawingLayer('A-DOOR', COLOR_DOOR),
        DrawingLayer('A-WINDOW', COLOR_WINDOW), DrawingLayer('A-COLUMN', COLOR_COLUMN),
        DrawingLayer('A-STAIR', COLOR_STAIR), DrawingLayer('A-TEXT', COLOR_TEXT),
        DrawingLayer('A-DIMS', COLOR_DIM), DrawingLayer('A-GRID', COLOR_GRID),
        DrawingLayer('A-TITLE', COLOR_TITLE),
    )

def _build_room_entities(model):
    ents = []
    for room in model.rooms.values():
        if room.polygon.is_empty: continue
        coords = list(room.polygon.exterior.coords)
        pts = tuple((float(x), float(y)) for x, y in coords)
        fill = room_fill_color(room.room_type.value)
        ents.append(PolygonEntity(pts, 'A-HATCH', fill, COLOR_WALL, STROKE_WALL*0.5, OPACITY_ROOM_FILL))
        ents.append(PolylineEntity(pts, LAYER_WALL, COLOR_WALL, STROKE_BUILDING_OUTLINE, True))
        c = room.centroid
        ents.append(TextEntity(c.x, c.y+0.2, room.room_type.value, FONT_SIZE_ROOM_LABEL, LAYER_TEXT, COLOR_TEXT, 0.0, 'middle'))
        ents.append(TextEntity(c.x, c.y-0.3, '{:.0f} sqft'.format(room.area), FONT_SIZE_ROOM_AREA, LAYER_TEXT, COLOR_DIM, 0.0, 'middle'))
    return ents

def _build_wall_entities(model):
    ents = []
    for wall in model.walls.values():
        if wall.geometry.is_empty: continue
        coords = list(wall.geometry.coords)
        for i in range(len(coords)-1):
            ents.append(LineEntity(float(coords[i][0]),float(coords[i][1]),float(coords[i+1][0]),float(coords[i+1][1]),LAYER_WALL, COLOR_WALL, STROKE_WALL))
    return ents

def _build_door_entities(model):
    ents = []
    for d in model.doors.values():
        if d.location is None: continue
        ents.append(CircleEntity(d.location.x, d.location.y, max(d.width/2,0.3), LAYER_DOOR, COLOR_DOOR, COLOR_DOOR, STROKE_DOOR, 0.3))
    return ents

def _build_window_entities(model):
    ents = []
    for w in model.windows.values():
        if w.location is None: continue
        ents.append(CircleEntity(w.location.x, w.location.y, max(w.width/2,0.3), LAYER_WINDOW, COLOR_WINDOW, COLOR_WINDOW, STROKE_WINDOW, 0.3))
    return ents

def _build_column_entities(model):
    ents = []
    for col in model.columns.values():
        if col.geometry is None: continue
        ents.append(CircleEntity(col.geometry.x, col.geometry.y, max(col.size/2,0.5), LAYER_COLUMN, COLOR_COLUMN, COLOR_COLUMN, STROKE_COLUMN, OPACITY_COLUMN_FILL))
    return ents

def _build_stair_entities(model):
    ents = []
    for s in model.stairs.values():
        if s.geometry.is_empty: continue
        coords = list(s.geometry.coords)
        pts = tuple((float(x), float(y)) for x, y in coords)
        ents.append(PolylineEntity(pts, LAYER_STAIR, COLOR_STAIR, STROKE_STAIR, False))
    return ents

def _build_grid_entities(bounds):
    ents = []
    sp = 10.0
    x = float(int(bounds.min_x/sp)*int(sp))
    while x <= bounds.max_x:
        ents.append(LineEntity(x, bounds.min_y, x, bounds.max_y, LAYER_GRID, COLOR_GRID, STROKE_GRID))
        x += sp
    y = float(int(bounds.min_y/sp)*int(sp))
    while y <= bounds.max_y:
        ents.append(LineEntity(bounds.min_x, y, bounds.max_x, y, LAYER_GRID, COLOR_GRID, STROKE_GRID))
        y += sp
    return ents

def _build_dimension_entities(bounds):
    o = 5.0
    return [
        DimensionEntity(bounds.min_x, bounds.min_y, bounds.max_x, bounds.min_y, bounds.min_y-o, '{:.0f} ft'.format(bounds.width), LAYER_DIM, COLOR_DIM, FONT_SIZE_DIM),
        DimensionEntity(bounds.min_x, bounds.min_y, bounds.min_x, bounds.max_y, bounds.min_x-o, '{:.0f} ft'.format(bounds.height), LAYER_DIM, COLOR_DIM, FONT_SIZE_DIM),
    ]

def _build_north_arrow_entities(bounds):
    cx, cy = bounds.max_x+15.0, bounds.max_y-15.0
    pts = ((cx,cy-10),(cx-5,cy+5),(cx,cy+2),(cx+5,cy+5),(cx,cy-10))
    return [PolygonEntity(pts, LAYER_TITLE, COLOR_NORTH_ARROW, COLOR_NORTH_ARROW, STROKE_NORTH_ARROW, 1.0),
            TextEntity(cx, cy+8, 'N', FONT_SIZE_NORTH, LAYER_TITLE, COLOR_NORTH_ARROW, 0.0, 'middle')]

def _build_scale_bar_entities(bounds):
    bl, bh = 10.0, 1.0
    xs = bounds.max_x - bl - 5.0
    yp = bounds.min_y - 15.0
    return [PolylineEntity(((xs,yp),(xs+bl,yp),(xs+bl,yp+bh),(xs,yp+bh),(xs,yp)), LAYER_TITLE, COLOR_SCALE_BAR, STROKE_SCALE_BAR, True),
            TextEntity(xs+bl/2, yp-1.5, '10 ft', FONT_SIZE_SCALE, LAYER_TITLE, COLOR_SCALE_BAR, 0.0, 'middle')]

def _build_title_block_entities(bounds, model):
    w, h = 40.0, 15.0
    bx = bounds.max_x - w - 5.0
    by = bounds.min_y - 35.0
    name = ''
    if model.building is not None: name = model.building.name or 'Untitled'
    return [
        PolylineEntity(((bx,by),(bx+w,by),(bx+w,by+h),(bx,by+h),(bx,by)), LAYER_TITLE, COLOR_TITLE, STROKE_SCALE_BAR, True),
        TextEntity(bx+1, by+h-2, 'Project: {}'.format(name), FONT_SIZE_TITLE, LAYER_TITLE, COLOR_TITLE, 0.0, 'start'),
        TextEntity(bx+1, by+h-4, 'Scale: 1/4" = 1\'-0"', FONT_SIZE_TITLE, LAYER_TITLE, COLOR_TITLE, 0.0, 'start'),
        TextEntity(bx+1, by+h-6, 'Drawn by: Craftshood AI', FONT_SIZE_TITLE, LAYER_TITLE, COLOR_TITLE, 0.0, 'start'),
    ]

def build_drawing_model(model, *, include_grid=False, include_dimensions=True,
                          include_north_arrow=True, include_scale_bar=True, include_title_block=True):
    bounds = _compute_bounds(model)
    layers = _build_layers()
    entities = []
    entities.extend(_build_room_entities(model))
    entities.extend(_build_wall_entities(model))
    entities.extend(_build_door_entities(model))
    entities.extend(_build_window_entities(model))
    entities.extend(_build_column_entities(model))
    entities.extend(_build_stair_entities(model))
    if include_grid: entities.extend(_build_grid_entities(bounds))
    if include_dimensions: entities.extend(_build_dimension_entities(bounds))
    if include_north_arrow: entities.extend(_build_north_arrow_entities(bounds))
    if include_scale_bar: entities.extend(_build_scale_bar_entities(bounds))
    if include_title_block: entities.extend(_build_title_block_entities(bounds, model))
    metadata = {'source': 'BuildingModel', 'room_count': len(model.rooms),
        'wall_count': len(model.walls), 'door_count': len(model.doors),
        'window_count': len(model.windows), 'column_count': len(model.columns),
        'stair_count': len(model.stairs)}
    if model.building is not None:
        metadata['building_name'] = model.building.name
        metadata['project_number'] = model.building.project_number
    return DrawingModel(layers=layers, entities=tuple(entities), bounds=bounds, metadata=metadata)
