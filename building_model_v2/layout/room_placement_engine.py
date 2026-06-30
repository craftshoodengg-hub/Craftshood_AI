"""Room placement engine.

Deterministic engine that places rooms onto a LayoutGrid.
"""
from __future__ import annotations

from typing import Tuple

from .layout_grid import LayoutGrid
from .placed_room import PlacedRoom
from .placement_result import PlacementResult


class RoomPlacementEngine:
    """Deterministic room placement engine.

    Places rooms onto a LayoutGrid using a simple scan strategy.
    No optimization, no AI, no randomness.
    """

    def place(
        self,
        architect_result: Any,
        grid: LayoutGrid,
    ) -> PlacementResult:
        """Place rooms from architect result onto the grid.

        Args:
            architect_result: Result from architect engine containing rooms.
            grid: The layout grid to place rooms on.

        Returns:
            PlacementResult with placed and unplaced rooms.
        """
        # Extract rooms from architect result's bubble diagram
        rooms: list[PlacedRoom] = []
        for bubble_node in architect_result.bubble_diagram.nodes:
            # Estimate width/height from target_area (assuming square-ish rooms)
            area = bubble_node.target_area
            width = max(1, int(area ** 0.5))
            height = max(1, int(area / width))
            rooms.append(
                PlacedRoom(
                    room_id=bubble_node.id,
                    room_type=bubble_node.room_type.value,
                    x=0,
                    y=0,
                    width=width,
                    height=height,
                )
            )

        # Sort: largest area first, then room_id
        rooms.sort(key=lambda r: (-r.area(), r.room_id))

        placed: list[PlacedRoom] = []
        unplaced: list[PlacedRoom] = []

        # Mark grid occupancy
        occupancy: list[list[bool]] = [
            [False] * grid.width for _ in range(grid.height)
        ]

        for room in rooms:
            position = self._find_position(room, grid, occupancy)
            if position is not None:
                x, y = position
                placed_room = PlacedRoom(
                    room_id=room.room_id,
                    room_type=room.room_type,
                    x=x,
                    y=y,
                    width=room.width,
                    height=room.height,
                )
                placed.append(placed_room)
                # Mark cells
                for cy in range(y, y + room.height):
                    for cx in range(x, x + room.width):
                        occupancy[cy][cx] = True
            else:
                unplaced.append(room)

        success = len(unplaced) == 0
        return PlacementResult(
            grid=grid,
            placed_rooms=tuple(placed),
            unplaced_rooms=tuple(unplaced),
            success=success,
        )

    def _find_position(
        self,
        room: PlacedRoom,
        grid: LayoutGrid,
        occupancy: list[list[bool]],
    ) -> Tuple[int, int] | None:
        """Find deterministic position for a room.

        Scan order: top to bottom, left to right.
        First valid location wins.

        Args:
            room: Room to place.
            grid: Layout grid.
            occupancy: Current occupancy grid.

        Returns:
            (x, y) if position found, None otherwise.
        """
        for y in range(grid.height):
            for x in range(grid.width):
                if self._fits(x, y, room.width, room.height, grid, occupancy):
                    return (x, y)
        return None

    def _fits(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        grid: LayoutGrid,
        occupancy: list[list[bool]],
    ) -> bool:
        """Check if room fits at position.

        Args:
            x: X coordinate.
            y: Y coordinate.
            width: Room width.
            height: Room height.
            grid: Layout grid.
            occupancy: Current occupancy grid.

        Returns:
            True if room fits without overlap or out-of-bounds.
        """
        if x + width > grid.width:
            return False
        if y + height > grid.height:
            return False
        for cy in range(y, y + height):
            for cx in range(x, x + width):
                if occupancy[cy][cx]:
                    return False
        return True