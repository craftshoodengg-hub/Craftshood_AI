"""Design request model for pipeline input requirements."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Tuple


@dataclass(frozen=True, slots=True)
class DesignRequest:
    """A structured design request representing user requirements.

    Attributes:
        project_type: The type of project, e.g. "residential" or "commercial".
        plot_width: Plot width in meters.
        plot_depth: Plot depth in meters.
        floors: Number of floors.
        bedrooms: Number of bedrooms.
        bathrooms: Number of bathrooms.
        parking: Number of parking spaces.
        kitchen_type: Kitchen type requirement.
        pooja_room: Whether a pooja room is requested.
        living_room: Whether a living room is requested.
        dining_room: Whether a dining room is requested.
        staircase: Whether a staircase is requested.
        orientation: Preferred orientation of the building.
        special_requirements: Additional free-form requirements.
    """

    project_type: str
    plot_width: float
    plot_depth: float
    floors: int
    bedrooms: int
    bathrooms: int
    parking: int
    kitchen_type: str
    pooja_room: bool
    living_room: bool
    dining_room: bool
    staircase: bool
    orientation: str
    special_requirements: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.plot_width <= 0:
            raise ValueError("plot_width must be positive")
        if self.plot_depth <= 0:
            raise ValueError("plot_depth must be positive")
        if self.floors < 1:
            raise ValueError("floors must be at least 1")
        if self.bedrooms < 0:
            raise ValueError("bedrooms must be non-negative")
        if self.bathrooms < 0:
            raise ValueError("bathrooms must be non-negative")

        if not isinstance(self.special_requirements, tuple):
            object.__setattr__(
                self,
                "special_requirements",
                tuple(str(item) for item in self.special_requirements),
            )

    def area(self) -> float:
        """Return the total plot area."""
        return self.plot_width * self.plot_depth

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the design request to a dictionary."""
        return {
            "project_type": self.project_type,
            "plot_width": self.plot_width,
            "plot_depth": self.plot_depth,
            "floors": self.floors,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "parking": self.parking,
            "kitchen_type": self.kitchen_type,
            "pooja_room": self.pooja_room,
            "living_room": self.living_room,
            "dining_room": self.dining_room,
            "staircase": self.staircase,
            "orientation": self.orientation,
            "special_requirements": list(self.special_requirements),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignRequest":
        """Create a DesignRequest from a dictionary."""
        return cls(
            project_type=data["project_type"],
            plot_width=float(data["plot_width"]),
            plot_depth=float(data["plot_depth"]),
            floors=int(data["floors"]),
            bedrooms=int(data["bedrooms"]),
            bathrooms=int(data["bathrooms"]),
            parking=int(data["parking"]),
            kitchen_type=data["kitchen_type"],
            pooja_room=bool(data["pooja_room"]),
            living_room=bool(data["living_room"]),
            dining_room=bool(data["dining_room"]),
            staircase=bool(data["staircase"]),
            orientation=data["orientation"],
            special_requirements=tuple(data.get("special_requirements", [])),
        )
