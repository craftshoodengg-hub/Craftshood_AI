"""Layout Generator for Craftshood AI.

Deterministic heuristic generator that converts a SpaceProgram into a BuildingModel.
No AI. No randomness. Pure deterministic grid-based placement.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import box

from ..entities_building import Building
from ..entities_floor import Floor
from ..entities_room import Room
from ..types import RoomType
from ..validation.cross_entity_validator import BuildingModel
from .layout_generation_result import LayoutGenerationResult
from .placement_rules import GRID_MODULE_FT, assign_floor, get_priority
from .room_program import FloorPreference, RoomProgram
from .space_program import SpaceProgram


class LayoutGenerator:
    """Deterministic layout generator using grid-based heuristic placement."""

    def generate(self, space_program: SpaceProgram) -> LayoutGenerationResult:
        if not space_program.rooms:
            return LayoutGenerationResult(warnings=("No rooms in space program",), confidence=0.0)

        rooms = sorted(space_program.rooms, key=lambda r: get_priority(r.room_type))
        max_floors = space_program.floor_count

        floor_assignments: Dict[int, List[RoomProgram]] = {}
        for room in rooms:
            floor_idx = assign_floor(room.room_type, room.floor_preference, max_floors)
            floor_assignments.setdefault(floor_idx, []).append(room)

        floors: Dict[str, Floor] = {}
        all_rooms: Dict[str, Room] = {}
        placed: List[str] = []
        warnings: List[str] = []

        for floor_idx in range(max_floors):
            floor_rooms = floor_assignments.get(floor_idx, [])
            floor_id = f"floor_{floor_idx}"
            placed_ids = self._place_rooms_on_floor(floor_rooms, floor_id, all_rooms, floor_idx, warnings)
            for pid in placed_ids:
                placed.append(pid)
            room_ids = frozenset(r.id for r in all_rooms.values() if r.floor_id == floor_id)
            floor = Floor.create(name=f"Floor {floor_idx + 1}", level=floor_idx, room_ids=room_ids)
            floors[floor_id] = floor

        building = Building.create(name="Generated Building", floor_ids=tuple(floors.keys()))

        building_model = BuildingModel(
            building=building, floors=floors, rooms=all_rooms,
            walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[],
        )

        total_rooms = len(placed)
        confidence = 1.0 if total_rooms > 0 else 0.0

        return LayoutGenerationResult(
            building_model=building_model, placed_rooms=tuple(placed),
            warnings=tuple(warnings), confidence=confidence,
            metadata={"floor_count": max_floors, "total_rooms": len(rooms), "grid_module": GRID_MODULE_FT},
        )


    def _place_rooms_on_floor(
        self, rooms: List[RoomProgram], floor_id: str,
        all_rooms: Dict[str, Room], floor_idx: int, warnings: List[str],
    ) -> List[str]:
        """Place rooms on a single floor using grid-based layout."""
        placed: List[str] = []
        grid_y = 0
        row_height = 0
        max_cols = 3

        for i, room_program in enumerate(rooms):
            col = i % max_cols
            if col == 0 and i > 0:
                grid_y += row_height
                row_height = 0

            width, length = self._calculate_dimensions(room_program.target_area)
            x = col * GRID_MODULE_FT * 2
            y = grid_y
            polygon = box(x, y, x + width, y + length)
            room_type = self._map_room_type(room_program.room_type)

            room = Room.create(
                vertices=list(polygon.exterior.coords[:-1]),
                room_type=room_type, floor_id=floor_id,
                metadata={
                    "name": room_program.name,
                    "target_area": room_program.target_area,
                    "privacy_level": room_program.privacy_level.value,
                    "vastu_preference": room_program.vastu_preference,
                },
            )
            all_rooms[room_program.id] = room
            placed.append(room_program.id)
            row_height = max(row_height, length)

        return placed

    def _calculate_dimensions(self, target_area: float | None) -> Tuple[float, float]:
        """Calculate room width and length from target area."""
        if target_area is None or target_area <= 0:
            return GRID_MODULE_FT * 2, GRID_MODULE_FT * 2

        width = math.sqrt(target_area / 1.5)
        length = target_area / width
        module = GRID_MODULE_FT
        width = max(module, round(width / module) * module)
        length = max(module, round(length / module) * module)
        return width, length

    def _map_room_type(self, room_type: str) -> RoomType:
        """Map string room type to RoomType enum."""
        mapping = {
            "living": RoomType.LIVING, "dining": RoomType.DINING,
            "kitchen": RoomType.KITCHEN, "bedroom": RoomType.BEDROOM,
            "master_bedroom": RoomType.BEDROOM, "bathroom": RoomType.BATHROOM,
            "common_bathroom": RoomType.BATHROOM, "parking": RoomType.STORAGE,
            "utility": RoomType.UTILITY, "office": RoomType.STORAGE,
            "pooja": RoomType.STORAGE, "stair": RoomType.STAIRCASE,
            "balcony": RoomType.BALCONY, "entrance": RoomType.CORRIDOR,
            "corridor": RoomType.CORRIDOR, "store": RoomType.STORAGE,
        }
        return mapping.get(room_type, RoomType.UNKNOWN)
