"""Zoning engine for architectural analysis.

Converts a BubbleDiagram into logical architectural zones
using deterministic rules based on room types.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..types import RoomType
from .bubble_diagram import BubbleDiagram
from .bubble_node import BubbleNode
from .zone import Zone
from .zoning_result import ZoningResult


class ZoningEngine:
    """Deterministic zoning engine.

    Converts a BubbleDiagram into logical architectural zones
    based on room types.
    """

    # Default mapping from RoomType value to zone type
    _ZONE_TYPE_MAP: Dict[str, str] = {
        # PUBLIC zone
        "Living": "PUBLIC",
        "Dining": "PUBLIC",
        "Corridor": "PUBLIC",  # Entrance
        # SEMI_PRIVATE zone
        "Kitchen": "SEMI_PRIVATE",
        "Bedroom": "SEMI_PRIVATE",  # Office, Pooja, Master Bedroom, Bedroom
        # PRIVATE zone
        "Bathroom": "PRIVATE",
        "Toilet": "PRIVATE",
        # SERVICE zone
        "Storage": "SERVICE",  # Parking
        "Utility": "SERVICE",
        # VERTICAL zone
        "Staircase": "VERTICAL",  # Stair
        # OUTDOOR zone
        "Balcony": "OUTDOOR",
    }

    # Zone display names
    _ZONE_NAMES: Dict[str, str] = {
        "PUBLIC": "Public Zone",
        "SEMI_PRIVATE": "Semi-Private Zone",
        "PRIVATE": "Private Zone",
        "SERVICE": "Service Zone",
        "VERTICAL": "Vertical Circulation Zone",
        "OUTDOOR": "Outdoor Zone",
    }

    def analyze(self, diagram: BubbleDiagram) -> ZoningResult:
        """Analyze a BubbleDiagram and produce zoning results.

        Args:
            diagram: The bubble diagram to analyze.

        Returns:
            A ZoningResult containing zones and unassigned rooms.
        """
        # Group rooms by zone type
        zone_rooms: Dict[str, List[BubbleNode]] = {}
        unassigned: List[str] = []

        for node in diagram.nodes:
            zone_type = self._get_zone_type(node)
            if zone_type is None:
                unassigned.append(node.id)
                continue
            if zone_type not in zone_rooms:
                zone_rooms[zone_type] = []
            zone_rooms[zone_type].append(node)

        # Create Zone objects (sorted by zone type for determinism)
        zones: List[Zone] = []
        for zone_type in sorted(zone_rooms.keys()):
            rooms = zone_rooms[zone_type]
            # Sort rooms by ID for deterministic ordering
            sorted_rooms = tuple(sorted(rooms, key=lambda r: r.id))
            zone_name = self._ZONE_NAMES.get(zone_type, f"{zone_type} Zone")
            zones.append(Zone(
                name=zone_name,
                zone_type=zone_type,
                rooms=sorted_rooms,
            ))

        return ZoningResult(
            zones=tuple(zones),
            unassigned_rooms=tuple(sorted(unassigned)),
            metadata={
                "source": "zoning_engine",
                "total_rooms": diagram.room_count,
            },
        )

    def _get_zone_type(self, node: BubbleNode) -> str | None:
        """Determine zone type for a node based on room type.

        Args:
            node: The bubble node to classify.

        Returns:
            Zone type string or None if unassignable.
        """
        room_type_value = node.room_type.value
        return self._ZONE_TYPE_MAP.get(room_type_value)