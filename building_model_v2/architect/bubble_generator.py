"""Bubble diagram generator.

Converts a SpaceProgram into a BubbleDiagram using deterministic
architectural relationship rules.
"""
from __future__ import annotations

from typing import Any

from ..ai.room_program import FloorPreference, PrivacyLevel
from ..ai.space_program import SpaceProgram
from ..types import RoomType
from .bubble_connection import BubbleConnection
from .bubble_diagram import BubbleDiagram
from .bubble_node import BubbleNode


class BubbleGenerator:
    """Generates a BubbleDiagram from a SpaceProgram.

    Uses deterministic architectural relationship rules to create
    connections between rooms based on their types.
    """

    # Connection rules: (source_type, target_type, weight, required)
    # Required adjacency = weight 1.0
    # Preferred adjacency = weight 0.8
    # Optional adjacency = weight 0.5
    _CONNECTION_RULES: tuple[tuple[RoomType, RoomType, float, bool], ...] = (
        # Living <-> Dining (required)
        (RoomType.LIVING, RoomType.DINING, 1.0, True),
        # Dining <-> Kitchen (required)
        (RoomType.DINING, RoomType.KITCHEN, 1.0, True),
        # Kitchen <-> Utility (preferred)
        (RoomType.KITCHEN, RoomType.UTILITY, 0.8, False),
        # Entrance (Corridor) <-> Living (required)
        (RoomType.CORRIDOR, RoomType.LIVING, 1.0, True),
        # Master Bedroom <-> Master Bathroom (required)
        (RoomType.BEDROOM, RoomType.BATHROOM, 1.0, True),
        # Bedroom <-> Common Bathroom (preferred)
        (RoomType.BEDROOM, RoomType.BATHROOM, 0.8, False),
        # Living <-> Stair (preferred, multi-floor)
        (RoomType.LIVING, RoomType.STAIRCASE, 0.8, False),
        # Parking (Storage) <-> Entrance (Corridor) (preferred)
        (RoomType.STORAGE, RoomType.CORRIDOR, 0.8, False),
        # Balcony <-> Living (preferred)
        (RoomType.BALCONY, RoomType.LIVING, 0.8, False),
        # Office (Bedroom) <-> Living (preferred)
        (RoomType.BEDROOM, RoomType.LIVING, 0.8, False),
        # Pooja (Bedroom) <-> Living (preferred)
        (RoomType.BEDROOM, RoomType.LIVING, 0.8, False),
        # Utility <-> Parking (Storage) (optional)
        (RoomType.UTILITY, RoomType.STORAGE, 0.5, False),
    )

    def generate(self, program: SpaceProgram) -> BubbleDiagram:
        """Generate a BubbleDiagram from a SpaceProgram.

        Args:
            program: The space program to convert.

        Returns:
            A BubbleDiagram with nodes and connections.
        """
        nodes = self._create_nodes(program)
        connections = self._create_connections(program, nodes)
        return BubbleDiagram(
            nodes=nodes,
            connections=connections,
            metadata=dict(program.metadata),
        )

    def _create_nodes(self, program: SpaceProgram) -> tuple[BubbleNode, ...]:
        """Create BubbleNodes from RoomPrograms.

        Args:
            program: The space program containing room programs.

        Returns:
            Tuple of BubbleNode objects.
        """
        nodes: list[BubbleNode] = []
        for room in program.rooms:
            node = BubbleNode(
                id=room.id,
                room_type=self._map_room_type(room.room_type),
                name=room.name if room.name else room.room_type,
                target_area=room.target_area if room.target_area else 0.0,
                privacy_level=room.privacy_level,
                preferred_floor=room.floor_preference,
                metadata=dict(room.metadata),
            )
            nodes.append(node)
        return tuple(nodes)

    def _create_connections(
        self,
        program: SpaceProgram,
        nodes: tuple[BubbleNode, ...],
    ) -> tuple[BubbleConnection, ...]:
        """Create BubbleConnections based on architectural rules.

        Args:
            program: The space program.
            nodes: The created bubble nodes.

        Returns:
            Tuple of BubbleConnection objects.
        """
        # Build a mapping from room type to node ids
        type_to_ids: dict[RoomType, list[str]] = {}
        for node in nodes:
            if node.room_type not in type_to_ids:
                type_to_ids[node.room_type] = []
            type_to_ids[node.room_type].append(node.id)

        # Build a mapping from node id to floor for multi-floor stair connections
        id_to_floor: dict[str, FloorPreference] = {}
        for room_program, node in zip(program.rooms, nodes):
            id_to_floor[node.id] = room_program.floor_preference

        connections: list[BubbleConnection] = []
        created_edges: set[tuple[str, str]] = set()

        for source_type, target_type, weight, required in self._CONNECTION_RULES:
            source_ids = type_to_ids.get(source_type, [])
            target_ids = type_to_ids.get(target_type, [])

            for source_id in source_ids:
                for target_id in target_ids:
                    if source_id == target_id:
                        continue

                    # For stair connections, only connect if multi-floor
                    if source_type == RoomType.STAIRCASE or target_type == RoomType.STAIRCASE:
                        source_floor = id_to_floor.get(source_id, FloorPreference.ANY)
                        target_floor = id_to_floor.get(target_id, FloorPreference.ANY)
                        # Only add stair connection if rooms are on different floors
                        # or if one is explicitly multi-floor
                        if (
                            source_floor == target_floor
                            and source_floor != FloorPreference.ANY
                        ):
                            continue

                    # Create canonical edge key for deduplication
                    edge_key = (min(source_id, target_id), max(source_id, target_id))
                    if edge_key in created_edges:
                        continue

                    created_edges.add(edge_key)
                    connections.append(
                        BubbleConnection(
                            source_id=source_id,
                            target_id=target_id,
                            weight=weight,
                            required=required,
                        )
                    )

        return tuple(connections)

    def _map_room_type(self, room_type: str) -> RoomType:
        """Map a string room type to RoomType enum.

        Args:
            room_type: The string room type from RoomProgram.

        Returns:
            The corresponding RoomType enum value.
        """
        mapping: dict[str, RoomType] = {
            "living": RoomType.LIVING,
            "bedroom": RoomType.BEDROOM,
            "master_bedroom": RoomType.BEDROOM,
            "kitchen": RoomType.KITCHEN,
            "dining": RoomType.DINING,
            "toilet": RoomType.TOILET,
            "bathroom": RoomType.BATHROOM,
            "master_bathroom": RoomType.BATHROOM,
            "common_bathroom": RoomType.BATHROOM,
            "storage": RoomType.STORAGE,
            "corridor": RoomType.CORRIDOR,
            "stair": RoomType.STAIRCASE,
            "staircase": RoomType.STAIRCASE,
            "balcony": RoomType.BALCONY,
            "utility": RoomType.UTILITY,
            "entrance": RoomType.CORRIDOR,
            "parking": RoomType.STORAGE,
            "office": RoomType.BEDROOM,
            "pooja": RoomType.BEDROOM,
        }
        return mapping.get(room_type.lower(), RoomType.UNKNOWN)