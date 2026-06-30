"""Building model converter.

Deterministic converter that transforms a LayoutRefinementResult into a BuildingModel.
"""
from __future__ import annotations

from typing import Any

from shapely.geometry import Polygon

from .layout_grid import LayoutGrid
from .layout_refinement_result import LayoutRefinementResult
from .placed_room import PlacedRoom
from .placement_result import PlacementResult
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType


class BuildingModelConverter:
    """Deterministic converter from layout placement to BuildingModel.

    Converts PlacedRoom entities into BuildingModel Room, Floor, and Building
    entities using deterministic ordering and polygon generation.
    """

    def convert(self, refinement: LayoutRefinementResult) -> Building:
        """Convert a layout refinement result into a BuildingModel.

        Args:
            refinement: The refined layout result.

        Returns:
            A Building entity containing all rooms and floors.
        """
        result = refinement.refined_result
        grid = result.grid
        placed_rooms = result.placed_rooms

        if not placed_rooms:
            return self._create_empty_building(grid)

        # Group rooms by their y position (floor level)
        floors: dict[int, list[PlacedRoom]] = {}
        for room in placed_rooms:
            floor_level = self._determine_floor_level(room, grid)
            floors.setdefault(floor_level, []).append(room)

        building_room_ids: list[str] = []
        building_floor_ids: list[str] = []
        floor_entities: list[Floor] = []
        room_entities: list[Room] = []

        for level in sorted(floors.keys()):
            rooms = floors[level]
            rooms_sorted = sorted(rooms, key=lambda r: (r.x, r.y))
            floor_room_ids: list[str] = []
            for room in rooms_sorted:
                room_id = room.room_id
                room_entity = self._create_room(room, grid)
                room_entities.append(room_entity)
                floor_room_ids.append(room_id)
                building_room_ids.append(room_id)

            floor_id = f"floor_{level}"
            floor_entity = Floor(
                id=floor_id,
                level=level,
                room_ids=tuple(floor_room_ids),
            )
            floor_entities.append(floor_entity)
            building_floor_ids.append(floor_id)

        building = Building(
            id="building_1",
            floor_ids=tuple(building_floor_ids),
            room_ids=tuple(building_room_ids),
        )

        return building

    def _create_empty_building(self, grid: LayoutGrid) -> Building:
        """Create an empty building."""
        return Building()

    def _determine_floor_level(self, room: PlacedRoom, grid: LayoutGrid) -> int:
        """Determine floor level from room position.

        Simple deterministic mapping based on y coordinate and grid height.
        """
        if grid.height <= 10:
            return 0
        return room.y // 10

    def _create_room(self, room: PlacedRoom, grid: LayoutGrid) -> Room:
        """Create a Room entity from a PlacedRoom."""
        polygon = self._create_room_polygon(room, grid)
        room_type = self._map_room_type(room.room_type)
        return Room(
            id=room.room_id,
            room_type=room_type,
            polygon=polygon,
            floor_id=self._determine_floor_level(room, grid),
            metadata={
                "x": room.x,
                "y": room.y,
                "width": room.width,
                "height": room.height,
                "grid_width": grid.width,
                "grid_height": grid.height,
            },
        )

    def _create_room_polygon(self, room: PlacedRoom, grid: LayoutGrid) -> Polygon:
        """Create a rectangular polygon for the room."""
        x1, y1 = room.x, room.y
        x2, y2 = room.x + room.width, room.y + room.height
        return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

    def _map_room_type(self, room_type_str: str) -> RoomType:
        """Map room type string to RoomType enum."""
        type_map = {
            "LIVING": RoomType.LIVING,
            "BEDROOM": RoomType.BEDROOM,
            "KITCHEN": RoomType.KITCHEN,
            "BATHROOM": RoomType.BATHROOM,
            "BALCONY": RoomType.BALCONY,
            "CORRIDOR": RoomType.CORRIDOR,
            "UTILITY": RoomType.UTILITY,
            "DINING": RoomType.DINING,
            "STORAGE": RoomType.STORAGE,
            "TOILET": RoomType.TOILET,
            "STAIRCASE": RoomType.STAIRCASE,
            "ROOM": RoomType.LIVING,
        }
        return type_map.get(room_type_str.upper(), RoomType.UNKNOWN)
