"""Optimization Actions for Building Model v2.

Deterministic pure functions that apply safe parameter changes to a copy
of a BuildingModel. Each action receives a BuildingModel and an
OptimizationAction and returns a NEW BuildingModel. Never modifies the input.

Initially implements only safe parameter changes:
    - expand_room
    - increase_window_size
    - increase_door_width
    - increase_stair_width
    - increase_ceiling_height
    - increase_room_height

Unknown or unsupported actions return the original copied model unchanged.

Future extension points (not implemented):
    - topology optimization
    - wall movement
    - room relocation
    - corridor optimization
    - furniture placement
"""

from __future__ import annotations

import dataclasses
from copy import deepcopy
from typing import Any

from .optimization_action import OptimizationAction


def _replace_entity(entity: Any, **changes: Any) -> Any:
    """Replace fields on a slotted or dict-based dataclass entity."""
    if dataclasses.is_dataclass(entity):
        return dataclasses.replace(entity, **changes)
    # Fallback for non-dataclass objects with __dict__
    kwargs = {**entity.__dict__, **changes}
    return entity.__class__(**kwargs)


# ============================================================================
# Room Actions
# ============================================================================


def expand_room(building_model: Any, action: OptimizationAction) -> Any:
    """Expand a room that is too small.

    Safely increases room polygon area by scaling around the centroid.
    Validates entity exists and values remain positive.
    Preserves immutable entities by creating replacements.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with expanded room.
    """
    model = deepcopy(building_model)

    # Validate entity exists
    if not hasattr(model, 'rooms'):
        return model

    target_id = action.target_entity_id
    if target_id not in model.rooms:
        return model

    room = model.rooms[target_id]

    # Scale polygon around centroid to increase area by ~21% (10% per axis)
    try:
        from shapely.affinity import scale

        centroid = room.polygon.centroid
        new_polygon = scale(
            room.polygon,
            xfact=1.1,
            yfact=1.1,
            origin=(centroid.x, centroid.y),
        )

        if not new_polygon.is_empty and new_polygon.area > 0:
            new_room = _replace_entity(room, polygon=new_polygon)
            model.rooms = {**model.rooms, target_id: new_room}
    except Exception:
        pass

    return model


# ============================================================================
# Window Actions
# ============================================================================


def increase_window_size(building_model: Any, action: OptimizationAction) -> Any:
    """Increase window size to improve window-to-floor ratio.

    Increases both width and height by 20%.
    Validates entity exists and values remain positive.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with increased window size.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'windows'):
        return model

    target_id = action.target_entity_id
    if target_id not in model.windows:
        return model

    window = model.windows[target_id]

    new_width = window.width * 1.2 if window.width > 0 else window.width
    new_height = window.height * 1.2 if window.height and window.height > 0 else window.height

    if new_width > 0 and (new_height is None or new_height > 0):
        changes = {'width': new_width}
        if new_height is not None:
            changes['height'] = new_height
        new_window = _replace_entity(window, **changes)
        model.windows = {**model.windows, target_id: new_window}

    return model


def increase_window_area(building_model: Any, action: OptimizationAction) -> Any:
    """Increase window area for better natural light.

    Delegates to increase_window_size (same effect).

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with increased window area.
    """
    return increase_window_size(building_model, action)


# ============================================================================
# Door Actions
# ============================================================================


def increase_door_width(building_model: Any, action: OptimizationAction) -> Any:
    """Increase door width for accessibility.

    Increases door width by 15%.
    Validates entity exists and values remain positive.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with increased door width.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'doors'):
        return model

    target_id = action.target_entity_id
    if target_id not in model.doors:
        return model

    door = model.doors[target_id]

    if door.width > 0:
        new_width = door.width * 1.15
        if new_width > 0:
            new_door = _replace_entity(door, width=new_width)
            model.doors = {**model.doors, target_id: new_door}

    return model


# ============================================================================
# Stair Actions
# ============================================================================


def increase_stair_width(building_model: Any, action: OptimizationAction) -> Any:
    """Increase stair width for safety and accessibility.

    Increases stair width by 10%.
    Validates entity exists and values remain positive.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with increased stair width.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'stairs'):
        return model

    target_id = action.target_entity_id
    if target_id not in model.stairs:
        return model

    stair = model.stairs[target_id]

    if stair.width > 0:
        new_width = stair.width * 1.1
        if new_width > 0:
            new_stair = _replace_entity(stair, width=new_width)
            model.stairs = {**model.stairs, target_id: new_stair}

    return model


# ============================================================================
# Ceiling / Room Height Actions
# ============================================================================


def increase_ceiling_height(building_model: Any, action: OptimizationAction) -> Any:
    """Increase ceiling height.

    Increases room ceiling_height by 10%.
    Validates entity exists and values remain positive.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with increased ceiling height.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'rooms'):
        return model

    target_id = action.target_entity_id
    if target_id not in model.rooms:
        return model

    room = model.rooms[target_id]

    if room.ceiling_height and room.ceiling_height > 0:
        new_height = room.ceiling_height * 1.1
        if new_height > 0:
            new_room = _replace_entity(room, ceiling_height=new_height)
            model.rooms = {**model.rooms, target_id: new_room}

    return model


def increase_room_height(building_model: Any, action: OptimizationAction) -> Any:
    """Increase room height (alias for ceiling height).

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with increased room height.
    """
    return increase_ceiling_height(building_model, action)


# ============================================================================
# Placeholder Actions (safe metadata-only changes)
# ============================================================================


def add_window_placeholder(building_model: Any, action: OptimizationAction) -> Any:
    """Add a window placeholder to a room without windows.

    This is a safe parameter change that marks the room for window addition.
    Actual window creation would require topology editing (future extension).

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with window placeholder metadata.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'rooms'):
        return model

    target_id = action.target_entity_id
    if target_id not in model.rooms:
        return model

    room = model.rooms[target_id]
    new_metadata = {**room.metadata, 'window_placeholder': True}
    new_room = _replace_entity(room, metadata=new_metadata)
    model.rooms = {**model.rooms, target_id: new_room}

    return model


def add_opposite_window_placeholder(building_model: Any, action: OptimizationAction) -> Any:
    """Add opposite window placeholder for cross ventilation.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with opposite window placeholder.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'rooms'):
        return model

    target_id = action.target_entity_id
    if target_id not in model.rooms:
        return model

    room = model.rooms[target_id]
    new_metadata = {**room.metadata, 'opposite_window_placeholder': True}
    new_room = _replace_entity(room, metadata=new_metadata)
    model.rooms = {**model.rooms, target_id: new_room}

    return model


def add_ramp_placeholder(building_model: Any, action: OptimizationAction) -> Any:
    """Add accessibility ramp placeholder.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with ramp placeholder metadata.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'building') or model.building is None:
        return model

    building = model.building
    new_metadata = {**building.metadata, 'ramp_placeholder': True}
    new_building = _replace_entity(building, metadata=new_metadata)
    model.building = new_building

    return model


def add_elevator_placeholder(building_model: Any, action: OptimizationAction) -> Any:
    """Add elevator placeholder for accessibility.

    Args:
        building_model: The building model to optimize.
        action: The optimization action with target entity info.

    Returns:
        New BuildingModel with elevator placeholder metadata.
    """
    model = deepcopy(building_model)

    if not hasattr(model, 'building') or model.building is None:
        return model

    building = model.building
    new_metadata = {**building.metadata, 'elevator_placeholder': True}
    new_building = _replace_entity(building, metadata=new_metadata)
    model.building = new_building

    return model
