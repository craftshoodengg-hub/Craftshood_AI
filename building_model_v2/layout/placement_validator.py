"""Placement validator.

Deterministic validation engine for room placement results.
"""
from __future__ import annotations

from typing import Any, List, Tuple

from .layout_grid import LayoutGrid
from .placed_room import PlacedRoom
from .placement_issue import PlacementIssue
from .placement_result import PlacementResult
from .placement_validation_result import PlacementValidationResult


class PlacementValidator:
    """Deterministic placement validation engine.

    Validates PlacementResult objects without modifying them.
    Detects overlaps, out-of-bounds, duplicate IDs, and zero-area rooms.
    """

    def validate(
        self,
        result: PlacementResult,
    ) -> PlacementValidationResult:
        """Validate a placement result.

        Args:
            result: The placement result to validate.

        Returns:
            PlacementValidationResult containing any issues found.
        """
        issues: List[PlacementIssue] = []

        if not result.placed_rooms and not result.unplaced_rooms:
            issues.append(PlacementIssue(
                issue_type="empty_placement",
                severity="warning",
                room_id=None,
                message="Placement result contains no rooms.",
            ))

        issues.extend(self._check_duplicate_ids(result.placed_rooms))
        issues.extend(self._check_out_of_bounds(result.placed_rooms, result.grid))
        issues.extend(self._check_zero_area(result.placed_rooms))
        issues.extend(self._check_overlaps(result.placed_rooms))
        issues.extend(self._check_grid_consistency(result))

        valid = not any(issue.severity == "error" for issue in issues)
        return PlacementValidationResult(
            valid=valid,
            issues=tuple(issues),
        )

    def _check_duplicate_ids(self, rooms: Tuple[PlacedRoom, ...]) -> List[PlacementIssue]:
        """Check for duplicate room IDs."""
        issues: List[PlacementIssue] = []
        seen = {}
        for room in rooms:
            if room.room_id in seen:
                issues.append(PlacementIssue(
                    issue_type="duplicate_id",
                    severity="error",
                    room_id=room.room_id,
                    message=f"Duplicate room_id '{room.room_id}' found.",
                ))
            else:
                seen[room.room_id] = room
        return issues

    def _check_out_of_bounds(
        self,
        rooms: Tuple[PlacedRoom, ...],
        grid: LayoutGrid,
    ) -> List[PlacementIssue]:
        """Check for rooms placed outside grid bounds."""
        issues: List[PlacementIssue] = []
        for room in rooms:
            if room.x < 0 or room.y < 0:
                issues.append(PlacementIssue(
                    issue_type="out_of_bounds",
                    severity="error",
                    room_id=room.room_id,
                    message=f"Room '{room.room_id}' has negative coordinates ({room.x}, {room.y}).",
                ))
            elif room.x + room.width > grid.width or room.y + room.height > grid.height:
                issues.append(PlacementIssue(
                    issue_type="out_of_bounds",
                    severity="error",
                    room_id=room.room_id,
                    message=f"Room '{room.room_id}' exceeds grid bounds.",
                ))
        return issues

    def _check_zero_area(self, rooms: Tuple[PlacedRoom, ...]) -> List[PlacementIssue]:
        """Check for zero-area rooms."""
        issues: List[PlacementIssue] = []
        for room in rooms:
            if room.width <= 0 or room.height <= 0:
                issues.append(PlacementIssue(
                    issue_type="zero_area",
                    severity="error",
                    room_id=room.room_id,
                    message=f"Room '{room.room_id}' has zero or negative area ({room.width}x{room.height}).",
                ))
        return issues

    def _check_overlaps(self, rooms: Tuple[PlacedRoom, ...]) -> List[PlacementIssue]:
        """Check for overlapping rooms."""
        issues: List[PlacementIssue] = []
        for i in range(len(rooms)):
            for j in range(i + 1, len(rooms)):
                r1 = rooms[i]
                r2 = rooms[j]
                if r1.overlaps(r2):
                    issues.append(PlacementIssue(
                        issue_type="overlap",
                        severity="error",
                        room_id=r1.room_id,
                        message=f"Room '{r1.room_id}' overlaps with '{r2.room_id}'.",
                    ))
        return issues

    def _check_grid_consistency(self, result: PlacementResult) -> List[PlacementIssue]:
        """Check grid occupancy consistency."""
        issues: List[PlacementIssue] = []
        grid = result.grid

        if grid.area() == 0:
            issues.append(PlacementIssue(
                issue_type="empty_grid",
                severity="warning",
                room_id=None,
                message="Grid has zero area.",
            ))

        for room in result.unplaced_rooms:
            issues.append(PlacementIssue(
                issue_type="unplaced_room",
                severity="warning",
                room_id=room.room_id,
                message=f"Room '{room.room_id}' could not be placed.",
            ))

        return issues