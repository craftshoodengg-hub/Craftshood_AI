"""Room polygon metric calculations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from shapely.geometry import Polygon

from .boundary_finder import RoomCenter


@dataclass(frozen=True, slots=True)
class RoomMetrics:
    """Calculated room polygon metrics."""

    area: float
    perimeter: float
    centroid: RoomCenter

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["centroid"] = self.centroid.to_dict()
        return payload


class AreaCalculator:
    """Calculate area, perimeter, and centroid from a Shapely polygon."""

    def calculate(self, polygon: Polygon) -> RoomMetrics:
        if polygon.is_empty:
            raise ValueError("Cannot calculate metrics for an empty polygon")
        centroid = polygon.centroid
        return RoomMetrics(
            area=float(polygon.area),
            perimeter=float(polygon.length),
            centroid=RoomCenter(x=float(centroid.x), y=float(centroid.y)),
        )
