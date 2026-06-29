"""Polygon geometry utilities for Building Model v2.

Provides reusable polygon calculations for area, perimeter, centroid,
bounding box, orientation, aspect ratio, compactness, and winding order.

This module is independent from entities and contains no AI logic,
validation, or transformation operations.
"""

from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import Polygon

from ..base import BoundingBox, Point2D


def _ensure_polygon(polygon: Polygon) -> Polygon:
    """Ensure polygon is valid; return as-is if valid.
    
    If the polygon is invalid, attempt to fix it using buffer(0).
    
    Args:
        polygon: The polygon to validate.
        
    Returns:
        A valid polygon.
    """
    if not polygon.is_valid:
        return polygon.buffer(0)
    return polygon


def area(polygon: Polygon) -> float:
    """Calculate the area of a polygon.
    
    Args:
        polygon: The polygon to calculate area for.
        
    Returns:
        The area of the polygon. Returns 0.0 for empty or invalid polygons.
    """
    if polygon.is_empty:
        return 0.0
    return float(polygon.area)


def perimeter(polygon: Polygon) -> float:
    """Calculate the perimeter of a polygon.
    
    Args:
        polygon: The polygon to calculate perimeter for.
        
    Returns:
        The perimeter length. Returns 0.0 for empty polygons.
    """
    if polygon.is_empty:
        return 0.0
    return float(polygon.length)


def centroid(polygon: Polygon) -> Optional[Point2D]:
    """Calculate the centroid of a polygon.
    
    Args:
        polygon: The polygon to calculate centroid for.
        
    Returns:
        The centroid as a Point2D, or None if the polygon is empty.
    """
    if polygon.is_empty:
        return None
    c = polygon.centroid
    return Point2D(x=c.x, y=c.y)


def bounding_box(polygon: Polygon) -> Optional[BoundingBox]:
    """Calculate the bounding box of a polygon.
    
    Args:
        polygon: The polygon to calculate bounding box for.
        
    Returns:
        The bounding box, or None if the polygon is empty.
    """
    if polygon.is_empty:
        return None
    min_x, min_y, max_x, max_y = polygon.bounds
    return BoundingBox(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)


def orientation(polygon: Polygon) -> float:
    """Calculate the orientation angle of a polygon.
    
    Returns the angle (in degrees) of the minimum bounding rectangle
    relative to the x-axis. This indicates the primary direction
    the polygon is facing.
    
    Args:
        polygon: The polygon to calculate orientation for.
        
    Returns:
        The orientation angle in degrees (0-180). Returns 0.0 for
        empty or degenerate polygons.
    """
    if polygon.is_empty:
        return 0.0
    
    # Use minimum rotated rectangle to determine orientation
    min_rect = polygon.minimum_rotated_rectangle
    if min_rect.is_empty or min_rect.area == 0:
        return 0.0
    
    # Get the coordinates of the minimum rotated rectangle
    coords = list(min_rect.exterior.coords)
    if len(coords) < 3:
        return 0.0
    
    # Find the longest edge to determine primary orientation
    max_length = 0.0
    best_angle = 0.0
    
    for i in range(len(coords) - 1):
        p1 = coords[i]
        p2 = coords[i + 1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = (dx * dx + dy * dy) ** 0.5
        
        if length > max_length:
            max_length = length
            if dx == 0 and dy == 0:
                best_angle = 0.0
            else:
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)
                # Normalize to 0-180 range
                if angle_deg < 0:
                    angle_deg += 180
                if angle_deg >= 180:
                    angle_deg -= 180
                best_angle = angle_deg
    
    return best_angle


def aspect_ratio(polygon: Polygon) -> float:
    """Calculate the aspect ratio of a polygon.
    
    The aspect ratio is defined as the ratio of the shorter side
    to the longer side of the minimum bounding rectangle.
    A square has an aspect ratio of 1.0.
    
    Args:
        polygon: The polygon to calculate aspect ratio for.
        
    Returns:
        The aspect ratio (0.0 to 1.0). Returns 0.0 for empty or
        degenerate polygons.
    """
    if polygon.is_empty:
        return 0.0
    
    bbox = bounding_box(polygon)
    if bbox is None:
        return 0.0
    
    width = bbox.width
    height = bbox.height
    
    if width == 0 and height == 0:
        return 0.0
    
    longer = max(width, height)
    shorter = min(width, height)
    
    if longer == 0:
        return 0.0
    
    return shorter / longer


def compactness(polygon: Polygon) -> float:
    """Calculate the compactness of a polygon.
    
    Compactness is defined as (4 * pi * area) / (perimeter^2).
    A circle has the maximum compactness of 1.0.
    More irregular shapes have lower compactness values.
    
    Args:
        polygon: The polygon to calculate compactness for.
        
    Returns:
        The compactness value (0.0 to 1.0). Returns 0.0 for
        empty or degenerate polygons.
    """
    if polygon.is_empty:
        return 0.0
    
    poly_area = polygon.area
    poly_perimeter = polygon.length
    
    if poly_perimeter == 0:
        return 0.0
    
    return (4 * math.pi * poly_area) / (poly_perimeter * poly_perimeter)


def is_clockwise(polygon: Polygon) -> bool:
    """Check if a polygon's exterior ring is clockwise.
    
    Args:
        polygon: The polygon to check.
        
    Returns:
        True if the exterior ring is clockwise, False otherwise.
        Returns False for empty polygons.
    """
    if polygon.is_empty:
        return False
    
    # Use the signed area method
    # Negative signed area = clockwise, positive = counter-clockwise
    coords = list(polygon.exterior.coords)
    n = len(coords)
    
    if n < 4:  # Need at least 3 points (plus closing point)
        return False
    
    signed_area = 0.0
    for i in range(n - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]
        signed_area += (x2 - x1) * (y2 + y1)
    
    return signed_area > 0


def is_counter_clockwise(polygon: Polygon) -> bool:
    """Check if a polygon's exterior ring is counter-clockwise.
    
    Args:
        polygon: The polygon to check.
        
    Returns:
        True if the exterior ring is counter-clockwise, False otherwise.
        Returns False for empty polygons.
    """
    if polygon.is_empty:
        return False
    
    return not is_clockwise(polygon)


def is_convex(polygon: Polygon) -> bool:
    """Check if a polygon is convex.
    
    Args:
        polygon: The polygon to check.
        
    Returns:
        True if the polygon is convex, False otherwise.
        Returns False for empty polygons.
    """
    if polygon.is_empty:
        return False
    
    if polygon.area == 0:
        return False
    
    # A polygon is convex if its convex hull has the same area
    convex_hull = polygon.convex_hull
    return abs(polygon.area - convex_hull.area) < 1e-10


def is_rectangular(polygon: Polygon, tolerance: float = 1e-6) -> bool:
    """Check if a polygon is approximately rectangular.
    
    Args:
        polygon: The polygon to check.
        tolerance: Tolerance for area comparison.
        
    Returns:
        True if the polygon is approximately rectangular.
        Returns False for empty or degenerate polygons.
    """
    if polygon.is_empty:
        return False
    
    if polygon.area == 0:
        return False
    
    # A rectangular polygon should have 4 vertices (plus closing point)
    coords = list(polygon.exterior.coords)
    if len(coords) != 5:  # 4 vertices + closing point
        return False
    
    # Check if area matches bounding box area
    bbox = bounding_box(polygon)
    if bbox is None:
        return False
    
    bbox_area = bbox.width * bbox.height
    if bbox_area == 0:
        return False
    
    return abs(polygon.area - bbox_area) < tolerance


def is_square(polygon: Polygon, tolerance: float = 1e-6) -> bool:
    """Check if a polygon is approximately square.
    
    Args:
        polygon: The polygon to check.
        tolerance: Tolerance for side length comparison.
        
    Returns:
        True if the polygon is approximately square.
        Returns False for empty or degenerate polygons.
    """
    if not is_rectangular(polygon, tolerance):
        return False
    
    bbox = bounding_box(polygon)
    if bbox is None:
        return False
    
    return abs(bbox.width - bbox.height) < tolerance


def vertex_count(polygon: Polygon) -> int:
    """Count the number of vertices in a polygon.
    
    Args:
        polygon: The polygon to count vertices for.
        
    Returns:
        The number of vertices. Returns 0 for empty polygons.
    """
    if polygon.is_empty:
        return 0
    
    # Exterior ring includes closing point, so subtract 1
    return len(list(polygon.exterior.coords)) - 1


def is_triangle(polygon: Polygon) -> bool:
    """Check if a polygon is a triangle.
    
    Args:
        polygon: The polygon to check.
        
    Returns:
        True if the polygon has exactly 3 vertices.
    """
    return vertex_count(polygon) == 3


def bounds(polygon: Polygon) -> tuple[float, float, float, float]:
    """Get the bounds of a polygon.
    
    Args:
        polygon: The polygon to get bounds for.
        
    Returns:
        A tuple of (min_x, min_y, max_x, max_y).
        Returns (0.0, 0.0, 0.0, 0.0) for empty polygons.
    """
    if polygon.is_empty:
        return (0.0, 0.0, 0.0, 0.0)
    return polygon.bounds