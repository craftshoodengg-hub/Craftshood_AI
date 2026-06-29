"""Building entity for Building Model v2.

Represents a complete building, aggregating all floors and serving as the
primary entry point for AI reasoning, serialization, Flutter rendering,
IFC export, and future Vastu analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from .base import BaseEntity, Point2D


@dataclass(frozen=True, slots=True)
class Building(BaseEntity):
    """A building entity representing the complete structure.
    
    Buildings are the root entities in the model hierarchy, containing
    all floors, which in turn contain rooms, walls, columns, stairs, etc.
    
    Attributes:
        name: Human-readable name of the building.
        project_number: Unique project identifier.
        description: Description of the building.
        site_name: Name of the building site.
        site_address: Physical address of the building site.
        north_direction: North direction in degrees (0-360).
        units: Unit system used ('imperial' or 'metric').
        floor_ids: Set of floor IDs in this building, ordered by level.
        metadata: Extensible key-value metadata.
    
    Future IFC Mapping:
        Maps to IfcBuilding.
    
    Future Flutter Rendering:
        Provides root context for rendering all floors.
    
    Future AI Reasoning:
        floor_ids enable vertical circulation analysis.
        north_direction enables orientation-based analysis.
    """
    
    name: str = ""
    project_number: str = ""
    description: str = ""
    site_name: str = ""
    site_address: str = ""
    north_direction: float = 0.0
    units: str = "imperial"
    floor_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def floor_count(self) -> int:
        """Get the number of floors in this building.
        
        Returns:
            Count of floor IDs.
        """
        return len(self.floor_ids)
    
    @property
    def has_multiple_floors(self) -> bool:
        """Check if this building has multiple floors.
        
        Returns:
            True if floor_count > 1.
        """
        return self.floor_count > 1
    
    @property
    def is_single_floor(self) -> bool:
        """Check if this building has only one floor.
        
        Returns:
            True if floor_count == 1.
        """
        return self.floor_count == 1
    
    @property
    def is_empty(self) -> bool:
        """Check if this building has no floors.
        
        Returns:
            True if floor_count == 0.
        """
        return self.floor_count == 0
    
    @property
    def ground_floor_id(self) -> str | None:
        """Get the ID of the ground floor.
        
        Returns the first floor ID as a placeholder. In a full implementation,
        this would look up the floor with level == 0.
        
        Returns:
            Floor ID if floors exist, None otherwise.
        """
        if self.floor_ids:
            return self.floor_ids[0]
        return None
    
    @property
    def top_floor_id(self) -> str | None:
        """Get the ID of the top floor.
        
        Returns the last floor ID as a placeholder. In a full implementation,
        this would look up the floor with the highest level.
        
        Returns:
            Floor ID if floors exist, None otherwise.
        """
        if self.floor_ids:
            return self.floor_ids[-1]
        return None
    
    @property
    def has_metric_units(self) -> bool:
        """Check if this building uses metric units.
        
        Returns:
            True if units is 'metric'.
        """
        return self.units == "metric"
    
    @property
    def has_imperial_units(self) -> bool:
        """Check if this building uses imperial units.
        
        Returns:
            True if units is 'imperial'.
        """
        return self.units == "imperial"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the building.
        """
        base = super(Building, self).to_dict()
        base.update({
            "name": self.name,
            "project_number": self.project_number,
            "description": self.description,
            "site_name": self.site_name,
            "site_address": self.site_address,
            "north_direction": self.north_direction,
            "units": self.units,
            "floor_ids": list(self.floor_ids),
            "computed": {
                "floor_count": self.floor_count,
                "has_multiple_floors": self.has_multiple_floors,
                "ground_floor_id": self.ground_floor_id,
                "top_floor_id": self.top_floor_id,
            },
        })
        return base
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create a Building from a dictionary.
        
        Args:
            payload: Dictionary with building data.
            
        Returns:
            New Building instance.
        """
        base = BaseEntity.from_dict(payload)
        floor_ids = payload.get("floor_ids", [])
        return cls(
            id=base.id,
            created_at=base.created_at,
            updated_at=base.updated_at,
            metadata=base.metadata,
            name=str(payload.get("name", "")),
            project_number=str(payload.get("project_number", "")),
            description=str(payload.get("description", "")),
            site_name=str(payload.get("site_name", "")),
            site_address=str(payload.get("site_address", "")),
            north_direction=float(payload.get("north_direction", 0.0)),
            units=str(payload.get("units", "imperial")),
            floor_ids=tuple(floor_ids),
        )
    
    @classmethod
    def create(
        cls,
        *,
        name: str = "",
        project_number: str = "",
        description: str = "",
        site_name: str = "",
        site_address: str = "",
        north_direction: float = 0.0,
        units: str = "imperial",
        floor_ids: tuple[str, ...] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Building:
        """Factory method to create a Building.
        
        Args:
            name: Human-readable name of the building.
            project_number: Unique project identifier.
            description: Description of the building.
            site_name: Name of the building site.
            site_address: Physical address of the building site.
            north_direction: North direction in degrees (0-360).
            units: Unit system ('imperial' or 'metric').
            floor_ids: IDs of floors in this building, ordered by level.
            metadata: Additional metadata.
            
        Returns:
            New Building instance.
        """
        return cls(
            name=name,
            project_number=project_number,
            description=description,
            site_name=site_name,
            site_address=site_address,
            north_direction=north_direction,
            units=units,
            floor_ids=floor_ids or (),
            metadata=metadata or {},
        )