"""Relationship graph layer for Building Model v2.

Defines immutable relationship objects that describe how building entities
connect. These relationships support AI reasoning, navigation, validation,
and future BIM/IFC export.

This module defines the data model only. Graph traversal algorithms,
adjacency lookup, and validation logic are implemented in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Self

from .base import BaseEntity, generate_uuid


class RelationshipType(Enum):
    """Types of relationships between building entities.
    
    Each type describes a specific kind of connection between two entities
    in the building model.
    """
    
    ROOM_TO_WALL = "room_to_wall"
    ROOM_TO_DOOR = "room_to_door"
    ROOM_TO_WINDOW = "room_to_window"
    ROOM_TO_ROOM = "room_to_room"
    WALL_TO_WINDOW = "wall_to_window"
    WALL_TO_DOOR = "wall_to_door"
    FLOOR_TO_ROOM = "floor_to_room"
    FLOOR_TO_STAIR = "floor_to_stair"
    BUILDING_TO_FLOOR = "building_to_floor"
    STAIR_TO_FLOOR = "stair_to_floor"
    
    @property
    def is_bidirectional(self) -> bool:
        """Check if this relationship type is bidirectional.
        
        Bidirectional relationships imply that if A relates to B,
        then B also relates to A in the same way.
        
        Returns:
            True if the relationship is bidirectional.
        """
        return self in _BIDIRECTIONAL_TYPES
    
    @property
    def is_hierarchical(self) -> bool:
        """Check if this relationship type is hierarchical.
        
        Hierarchical relationships imply a parent-child containment
        relationship (e.g., building contains floor).
        
        Returns:
            True if the relationship is hierarchical.
        """
        return self in _HIERARCHICAL_TYPES


# Set of relationship types that are bidirectional
_BIDIRECTIONAL_TYPES: frozenset[RelationshipType] = frozenset({
    RelationshipType.ROOM_TO_ROOM,
})

# Set of relationship types that are hierarchical (parent-child)
_HIERARCHICAL_TYPES: frozenset[RelationshipType] = frozenset({
    RelationshipType.FLOOR_TO_ROOM,
    RelationshipType.FLOOR_TO_STAIR,
    RelationshipType.BUILDING_TO_FLOOR,
})


@dataclass(frozen=True, slots=True)
class Relationship(BaseEntity):
    """A relationship between two building entities.
    
    Relationships describe how entities in the building model connect
    to each other. They form the edges in the building graph.
    
    Attributes:
        relationship_type: The type of relationship.
        source_id: ID of the source entity.
        target_id: ID of the target entity.
        metadata: Extensible key-value metadata.
    
    Future Graph Traversal:
        Relationships enable graph-based queries like adjacency lookup,
        pathfinding, and connectivity analysis.
    
    Future AI Reasoning:
        relationship_type enables semantic reasoning about connections.
        source_id/target_id enable graph traversal.
    """
    
    relationship_type: RelationshipType = RelationshipType.ROOM_TO_ROOM
    source_id: str = ""
    target_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_bidirectional(self) -> bool:
        """Check if this relationship is bidirectional.
        
        Returns:
            True if the relationship type is bidirectional.
        """
        return self.relationship_type.is_bidirectional
    
    @property
    def is_hierarchical(self) -> bool:
        """Check if this relationship is hierarchical.
        
        Returns:
            True if the relationship type is hierarchical.
        """
        return self.relationship_type.is_hierarchical
    
    @property
    def inverse(self) -> Relationship:
        """Get the inverse of this relationship.
        
        For bidirectional relationships, the inverse swaps source and target
        but keeps the same type. For unidirectional relationships, the
        inverse may have a different type.
        
        Returns:
            A new Relationship with source and target swapped.
        """
        return Relationship(
            relationship_type=self.relationship_type,
            source_id=self.target_id,
            target_id=self.source_id,
            metadata=dict(self.metadata),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the relationship.
        """
        base = super(Relationship, self).to_dict()
        base.update({
            "relationship_type": self.relationship_type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "is_bidirectional": self.is_bidirectional,
            "is_hierarchical": self.is_hierarchical,
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Relationship from a dictionary.
        
        Args:
            payload: Dictionary with relationship data.
            
        Returns:
            New Relationship instance.
        """
        base = BaseEntity.from_dict(payload)
        type_value = payload.get("relationship_type", "room_to_room")
        try:
            relationship_type = RelationshipType(type_value)
        except ValueError:
            relationship_type = RelationshipType.ROOM_TO_ROOM
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            relationship_type=relationship_type,
            source_id=str(payload.get("source_id", "")),
            target_id=str(payload.get("target_id", "")),
        )
    
    @classmethod
    def create(
        cls,
        *,
        relationship_type: RelationshipType,
        source_id: str,
        target_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> Relationship:
        """Factory method to create a Relationship.
        
        Args:
            relationship_type: The type of relationship.
            source_id: ID of the source entity.
            target_id: ID of the target entity.
            metadata: Additional metadata.
            
        Returns:
            New Relationship instance.
        """
        return cls(
            relationship_type=relationship_type,
            source_id=source_id,
            target_id=target_id,
            metadata=metadata or {},
        )