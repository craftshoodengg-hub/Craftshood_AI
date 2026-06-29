"""Shared validation utilities for Craftshood_AI.

This module provides common validation functions used across the
analysis packages.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from adjacency import RoomPolygon


def validate_room_polygons(rooms: Sequence[RoomPolygon]) -> None:
    """Validate a sequence of room polygons.

    Checks that all rooms have unique non-empty IDs and valid non-empty
    polygons.

    Args:
        rooms: A sequence of RoomPolygon objects to validate.

    Raises:
        ValueError: If any room_id is empty, duplicated, or if any
            polygon is empty or invalid.
    """
    seen_ids: set[str] = set()
    for room in rooms:
        if not room.room_id:
            raise ValueError("room_id cannot be empty")
        if room.room_id in seen_ids:
            raise ValueError(f"Duplicate room_id: {room.room_id!r}")
        seen_ids.add(room.room_id)
        if room.polygon.is_empty:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is empty")
        if not room.polygon.is_valid:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is invalid")


def validate_room_polygons_iterable(rooms: Iterable[RoomPolygon]) -> None:
    """Validate an iterable of room polygons.

    Same as validate_room_polygons but accepts any iterable.

    Args:
        rooms: An iterable of RoomPolygon objects to validate.

    Raises:
        ValueError: If any room_id is empty, duplicated, or if any
            polygon is empty or invalid.
    """
    seen_ids: set[str] = set()
    for room in rooms:
        if not room.room_id:
            raise ValueError("room_id cannot be empty")
        if room.room_id in seen_ids:
            raise ValueError(f"Duplicate room_id: {room.room_id!r}")
        if room.polygon.is_empty:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is empty")
        if not room.polygon.is_valid:
            raise ValueError(f"Polygon for room_id {room.room_id!r} is invalid")
        seen_ids.add(room.room_id)
