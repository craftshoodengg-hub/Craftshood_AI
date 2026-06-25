"""Room boundary graph utilities.

The package builds a room polygon from a known room center and logical walls.
It casts radial rays, finds nearest wall intersections, builds a Shapely
polygon, calculates metrics, and exports serializable room data. It does not
detect doors or windows and does not mutate wall geometry.
"""

from .area_calculator import AreaCalculator, RoomMetrics
from .boundary_finder import BoundaryFinder, BoundaryFinderConfig, BoundaryIntersection, RoomCenter
from .graph_builder import RoomGraphBuilder, RoomGraphResult
from .polygon_builder import PolygonBuilder, PolygonBuilderConfig
from .room_exporter import RoomExporter

__all__ = [
    "AreaCalculator",
    "BoundaryFinder",
    "BoundaryFinderConfig",
    "BoundaryIntersection",
    "PolygonBuilder",
    "PolygonBuilderConfig",
    "RoomCenter",
    "RoomExporter",
    "RoomGraphBuilder",
    "RoomGraphResult",
    "RoomMetrics",
]
