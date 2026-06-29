"""Design Requirements for Craftshood AI.

Immutable dataclasses representing structured architectural design specifications.
No AI. Pure deterministic data structures.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True, slots=True)
class PlotRequirements:
    width: float | None = None
    length: float | None = None
    area: float | None = None
    area_unit: str | None = None
    facing: str | None = None
    corner_plot: bool = False
    road_count: int | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "length": self.length,
            "area": self.area,
            "area_unit": self.area_unit,
            "facing": self.facing,
            "corner_plot": self.corner_plot,
            "road_count": self.road_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlotRequirements:
        return cls(
            width=data.get("width"),
            length=data.get("length"),
            area=data.get("area"),
            area_unit=data.get("area_unit"),
            facing=data.get("facing"),
            corner_plot=data.get("corner_plot", False),
            road_count=data.get("road_count"),
        )


@dataclass(frozen=True, slots=True)
class BuildingRequirements:
    building_type: str | None = None
    floors: int | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    parking: bool = False
    parking_count: int | None = None
    pooja: bool = False
    office: bool = False
    balcony: bool = False
    balcony_count: int | None = None
    utility: bool = False
    vastu_required: bool = False
    accessibility_required: bool = False
    duplex: bool = False
    apartment: bool = False
    villa: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "building_type": self.building_type,
            "floors": self.floors,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "parking": self.parking,
            "parking_count": self.parking_count,
            "pooja": self.pooja,
            "office": self.office,
            "balcony": self.balcony,
            "balcony_count": self.balcony_count,
            "utility": self.utility,
            "vastu_required": self.vastu_required,
            "accessibility_required": self.accessibility_required,
            "duplex": self.duplex,
            "apartment": self.apartment,
            "villa": self.villa,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BuildingRequirements:
        return cls(
            building_type=data.get("building_type"),
            floors=data.get("floors"),
            bedrooms=data.get("bedrooms"),
            bathrooms=data.get("bathrooms"),
            parking=data.get("parking", False),
            parking_count=data.get("parking_count"),
            pooja=data.get("pooja", False),
            office=data.get("office", False),
            balcony=data.get("balcony", False),
            balcony_count=data.get("balcony_count"),
            utility=data.get("utility", False),
            vastu_required=data.get("vastu_required", False),
            accessibility_required=data.get("accessibility_required", False),
            duplex=data.get("duplex", False),
            apartment=data.get("apartment", False),
            villa=data.get("villa", False),
        )


@dataclass(frozen=True, slots=True)
class DesignRequirements:
    plot: PlotRequirements = field(default_factory=PlotRequirements)
    building: BuildingRequirements = field(default_factory=BuildingRequirements)
    budget: float | None = None
    budget_unit: str | None = None
    style: str | None = None
    priorities: tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plot": self.plot.to_dict(),
            "building": self.building.to_dict(),
            "budget": self.budget,
            "budget_unit": self.budget_unit,
            "style": self.style,
            "priorities": list(self.priorities),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DesignRequirements:
        return cls(
            plot=PlotRequirements.from_dict(data.get("plot", {})),
            building=BuildingRequirements.from_dict(data.get("building", {})),
            budget=data.get("budget"),
            budget_unit=data.get("budget_unit"),
            style=data.get("style"),
            priorities=tuple(data.get("priorities", [])),
            metadata=dict(data.get("metadata", {})),
        )
