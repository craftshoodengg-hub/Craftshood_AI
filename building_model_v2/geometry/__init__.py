"""Geometry Engine for Building Model v2.

Provides distance calculations, geometric utilities, polygon
operations, transformations, and snapping for building entities.
This module is independent from entities and contains no AI,
validation, or graph logic.

Modules:
    distance: Distance calculations between geometry types.
    intersection: Geometric intersection predicates.
    polygon: Polygon geometry utilities.
    transform: Geometry transformation functions.
    snap: Snapping and vertex cleanup utilities.
"""

from .distance import (
    distance,
    distance_bbox_to_point,
    distance_line_to_point,
    distance_point_to_bbox,
    distance_point_to_line,
    distance_point_to_point,
    distance_point_to_polygon,
    distance_polygon_to_point,
)
from .intersection import (
    contains,
    crosses,
    intersects,
    touches,
)
from .polygon import (
    area,
    aspect_ratio,
    bounding_box,
    bounds,
    compactness,
    is_clockwise,
    is_counter_clockwise,
    is_convex,
    is_rectangular,
    is_square,
    is_triangle,
    orientation,
    perimeter,
    vertex_count,
)
from .snap import (
    merge_vertices,
    remove_duplicate_vertices,
    simplify_geometry,
    snap_line,
    snap_point,
    snap_polygon,
)
from .transform import (
    mirror,
    offset,
    rotate,
    scale,
    translate,
)

__all__ = [
    # Distance
    "distance",
    "distance_point_to_point",
    "distance_point_to_line",
    "distance_line_to_point",
    "distance_point_to_polygon",
    "distance_polygon_to_point",
    "distance_point_to_bbox",
    "distance_bbox_to_point",
    # Intersection
    "intersects",
    "contains",
    "touches",
    "crosses",
    # Polygon
    "area",
    "perimeter",
    "bounding_box",
    "bounds",
    "orientation",
    "aspect_ratio",
    "compactness",
    "is_clockwise",
    "is_counter_clockwise",
    "is_convex",
    "is_rectangular",
    "is_square",
    "is_triangle",
    "vertex_count",
    # Transform
    "translate",
    "rotate",
    "scale",
    "mirror",
    "offset",
    # Snap
    "snap_point",
    "snap_line",
    "snap_polygon",
    "merge_vertices",
    "remove_duplicate_vertices",
    "simplify_geometry",
]