"""Layout refinement engine.

Deterministic engine that refines an existing PlacementResult.
"""
from __future__ import annotations

from typing import List, Tuple

from .layout_grid import LayoutGrid
from .placed_room import PlacedRoom
from .placement_result import PlacementResult
from .placement_validator import PlacementValidator
from .layout_refinement_result import LayoutRefinementResult


class LayoutRefiner:
    """Deterministic layout refinement engine.

    Improves a PlacementResult by reducing empty gaps and
    improving occupancy ratio, while preserving all room properties.
    """

    def __init__(self) -> None:
        """Initialize the refiner with a validator."""
        self._validator = PlacementValidator()

    def refine(self, placement: PlacementResult) -> LayoutRefinementResult:
        """Refine a placement result.

        Args:
            placement: The placement result to refine.

        Returns:
            LayoutRefinementResult containing original and refined results.
        """
        original_result = placement
        rooms = list(placement.placed_rooms)
        grid = placement.grid

        score_before = placement.occupancy_ratio
        improvements: List[str] = []
        moved_rooms: List[str] = []

        # Sort rooms by current position (top-to-bottom, left-to-right)
        rooms.sort(key=lambda r: (r.y, r.x))

        occupied: List[List[bool]] = [
            [False] * grid.width for _ in range(grid.height)
        ]
        for room in rooms:
            for cy in range(room.y, room.y + room.height):
                for cx in range(room.x, room.x + room.width):
                    if 0 <= cy < grid.height and 0 <= cx < grid.width:
                        occupied[cy][cx] = True

        # Build occupancy excluding the current room being searched
        base_occupied: List[List[bool]] = [
            [False] * grid.width for _ in range(grid.height)
        ]
        for room in rooms:
            for cy in range(room.y, room.y + room.height):
                for cx in range(room.x, room.x + room.width):
                    if 0 <= cy < grid.height and 0 <= cx < grid.width:
                        base_occupied[cy][cx] = True

        # Try to move each room up and left
        refined_rooms: List[PlacedRoom] = []
        for room in rooms:
            # Clear this room from base occupancy for search
            for cy in range(room.y, room.y + room.height):
                for cx in range(room.x, room.x + room.width):
                    if 0 <= cy < grid.height and 0 <= cx < grid.width:
                        base_occupied[cy][cx] = False

            new_x, new_y = self._find_better_position(
                room, grid, base_occupied
            )
            if new_x != room.x or new_y != room.y:
                moved_rooms.append(room.room_id)
                improvements.append(
                    f"Moved room '{room.room_id}' from ({room.x}, {room.y}) to ({new_x}, {new_y})"
                )
                refined_room = PlacedRoom(
                    room_id=room.room_id,
                    room_type=room.room_type,
                    x=new_x,
                    y=new_y,
                    width=room.width,
                    height=room.height,
                )
                refined_rooms.append(refined_room)
                for cy in range(new_y, new_y + room.height):
                    for cx in range(new_x, new_x + room.width):
                        if 0 <= cy < grid.height and 0 <= cx < grid.width:
                            base_occupied[cy][cx] = True
            else:
                refined_rooms.append(room)
                for cy in range(room.y, room.y + room.height):
                    for cx in range(room.x, room.x + room.width):
                        if 0 <= cy < grid.height and 0 <= cx < grid.width:
                            base_occupied[cy][cx] = True

        refined_result = PlacementResult(
            grid=grid,
            placed_rooms=tuple(refined_rooms),
            unplaced_rooms=placement.unplaced_rooms,
            success=placement.success,
        )

        # Validate the refined result
        validation = self._validator.validate(refined_result)
        if not validation.valid:
            # Return original if refinement produces invalid layout
            return LayoutRefinementResult(
                original_result=original_result,
                refined_result=original_result,
                improvements=(),
                moved_rooms=(),
                score_before=score_before,
                score_after=score_before,
            )

        score_after = refined_result.occupancy_ratio

        return LayoutRefinementResult(
            original_result=original_result,
            refined_result=refined_result,
            improvements=tuple(improvements),
            moved_rooms=tuple(moved_rooms),
            score_before=score_before,
            score_after=score_after,
        )

    def _find_better_position(
        self,
        room: PlacedRoom,
        grid: LayoutGrid,
        occupied: List[List[bool]],
    ) -> Tuple[int, int]:
        """Find the best position (farthest up-left) for a room.

        Args:
            room: Room to reposition.
            grid: Layout grid.
            occupied: Current occupancy grid.

        Returns:
            (x, y) of the best position found.
        """
        best_x = room.x
        best_y = room.y

        # Try moving up as far as possible
        for y in range(room.y - 1, -1, -1):
            if self._fits(room.x, y, room.width, room.height, grid, occupied):
                best_y = y
            else:
                break

        # Try moving left as far as possible
        for x in range(room.x - 1, -1, -1):
            if self._fits(x, best_y, room.width, room.height, grid, occupied):
                best_x = x
            else:
                break

        return best_x, best_y

    def _fits(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        grid: LayoutGrid,
        occupied: List[List[bool]],
    ) -> bool:
        """Check if room fits at position without overlap.

        Args:
            x: X coordinate.
            y: Y coordinate.
            width: Room width.
            height: Room height.
            grid: Layout grid.
            occupied: Current occupancy grid.

        Returns:
            True if room fits without overlap or out-of-bounds.
        """
        if x + width > grid.width:
            return False
        if y + height > grid.height:
            return False
        for cy in range(y, y + height):
            for cx in range(x, x + width):
                if occupied[cy][cx]:
                    return False
        return True