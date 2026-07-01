"""Assign detected doors and windows to room polygons."""
from __future__ import annotations

from typing import Any

from shapely.geometry import Point, Polygon


class RoomOpeningAssigner:
    """Assign door and window detections to room polygons using Shapely geometry."""

    TOLERANCE = 0.5

    @classmethod
    def assign(
        cls,
        room_polygons: list[dict[str, Any]],
        door_window_information: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Return room dictionaries extended with their assigned doors and windows."""
        rooms: list[dict[str, Any]] = []

        for room in room_polygons:
            polygon = cls._to_polygon(room.get("polygon", []))
            if polygon is None:
                assigned_doors: list[dict[str, Any]] = []
                assigned_windows: list[dict[str, Any]] = []
            else:
                assigned_doors = cls._assign_openings(
                    polygon,
                    door_window_information.get("doors", []),
                )
                assigned_windows = cls._assign_openings(
                    polygon,
                    door_window_information.get("windows", []),
                )

            extended_room = dict(room)
            extended_room["doors"] = assigned_doors
            extended_room["windows"] = assigned_windows
            extended_room["door_count"] = len(assigned_doors)
            extended_room["window_count"] = len(assigned_windows)
            rooms.append(extended_room)

        return rooms

    @classmethod
    def _assign_openings(
        cls,
        polygon: Polygon,
        openings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        assigned: list[dict[str, Any]] = []
        for opening in openings:
            if cls._belongs_to_polygon(polygon, opening.get("position", (0.0, 0.0))):
                assigned.append(cls._copy_opening(opening))
        return assigned

    @classmethod
    def _belongs_to_polygon(cls, polygon: Polygon, position: tuple[float, float]) -> bool:
        point = Point(position)
        return polygon.covers(point) or polygon.distance(point) <= cls.TOLERANCE

    @classmethod
    def _to_polygon(cls, coordinates: list[Any]) -> Polygon | None:
        if not coordinates:
            return None

        try:
            polygon = Polygon(coordinates)
        except (TypeError, ValueError):
            return None

        if polygon.is_empty or not polygon.is_valid or polygon.area <= 0:
            return None

        return polygon

    @classmethod
    def _copy_opening(cls, opening: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": opening.get("type", ""),
            "name": opening.get("name", ""),
            "position": opening.get("position", (0.0, 0.0)),
            "layer": opening.get("layer", ""),
            "entity_type": opening.get("entity_type", ""),
        }
