"""Distance calculations for Building Model v2.

Provides distance functions between geometry types:
- Point2D to Point2D
- Point2D to LineString
- LineString to Point2D
- Polygon to Point2D
- BoundingBox to Point2D

All functions return distances in the same unit as the input coordinates.
"""

from __future__ import annotations

from typing import Union

from shapely.geometry import LineString, Point, Polygon

from ..base import BoundingBox, Point2D


def distance_point_to_point(a: Point2D, b: Point2D) -> float:
    """Calculate Euclidean distance between two 2D points.
    
    Args:
        a: First point.
        b: Second point.
        
    Returns:
        Euclidean distance between the two points.
    """
    dx = b.x - a.x
    dy = b.y - a.y
    return (dx * dx + dy * dy) ** 0.5


def distance_point_to_line(point: Point2D, line: LineString) -> float:
    """Calculate minimum distance from a point to a line.
    
    Args:
        point: The point to measure from.
        line: The line to measure to.
        
    Returns:
        Minimum distance from the point to the line.
    """
    if line.is_empty:
        return float('inf')
    shapely_point = Point(point.x, point.y)
    return float(line.distance(shapely_point))


def distance_line_to_point(line: LineString, point: Point2D) -> float:
    """Calculate minimum distance from a line to a point.
    
    This is a convenience wrapper for distance_point_to_line.
    
    Args:
        line: The line to measure from.
        point: The point to measure to.
        
    Returns:
        Minimum distance from the line to the point.
    """
    return distance_point_to_line(point, line)


def distance_point_to_polygon(point: Point2D, polygon: Polygon) -> float:
    """Calculate minimum distance from a point to a polygon.
    
    If the point is inside the polygon, the distance is 0.
    
    Args:
        point: The point to measure from.
        polygon: The polygon to measure to.
        
    Returns:
        Minimum distance from the point to the polygon boundary.
        Returns 0.0 if the point is inside the polygon.
    """
    if polygon.is_empty:
        return float('inf')
    shapely_point = Point(point.x, point.y)
    if polygon.contains(shapely_point):
        return 0.0
    return float(polygon.boundary.distance(shapely_point))


def distance_polygon_to_point(polygon: Polygon, point: Point2D) -> float:
    """Calculate minimum distance from a polygon to a point.
    
    This is a convenience wrapper for distance_point_to_polygon.
    
    Args:
        polygon: The polygon to measure from.
        point: The point to measure to.
        
    Returns:
        Minimum distance from the polygon to the point.
    """
    return distance_point_to_polygon(point, polygon)


def distance_point_to_bbox(point: Point2D, bbox: BoundingBox) -> float:
    """Calculate minimum distance from a point to a bounding box.
    
    If the point is inside the bounding box, the distance is 0.
    
    Args:
        point: The point to measure from.
        bbox: The bounding box to measure to.
        
    Returns:
        Minimum distance from the point to the bounding box.
        Returns 0.0 if the point is inside the box.
    """
    # Check if point is inside the bounding box
    if bbox.min_x <= point.x <= bbox.max_x and bbox.min_y <= point.y <= bbox.max_y:
        return 0.0
    
    # Calculate distance to nearest edge
    dx = max(bbox.min_x - point.x, 0, point.x - bbox.max_x)
    dy = max(bbox.min_y - point.y, 0, point.y - bbox.max_y)
    return (dx * dx + dy * dy) ** 0.5


def distance_bbox_to_point(bbox: BoundingBox, point: Point2D) -> float:
    """Calculate minimum distance from a bounding box to a point.
    
    This is a convenience wrapper for distance_point_to_bbox.
    
    Args:
        bbox: The bounding box to measure from.
        point: The point to measure to.
        
    Returns:
        Minimum distance from the bounding box to the point.
    """
    return distance_point_to_bbox(point, bbox)


def distance(a: Union[Point2D, LineString, Polygon, BoundingBox],
             b: Union[Point2D, LineString, Polygon, BoundingBox]) -> float:
    """Calculate minimum distance between two geometry objects.
    
    This is a convenience function that dispatches to the appropriate
    distance function based on the input types.
    
    Supported combinations:
        - Point2D to Point2D
        - Point2D to LineString
        - LineString to Point2D
        - Point2D to Polygon
        - Polygon to Point2D
        - Point2D to BoundingBox
        - BoundingBox to Point2D
    
    Args:
        a: First geometry object.
        b: Second geometry object.
        
    Returns:
        Minimum distance between the two objects.
        
    Raises:
        TypeError: If the combination of types is not supported.
    """
    if isinstance(a, Point2D) and isinstance(b, Point2D):
        return distance_point_to_point(a, b)
    elif isinstance(a, Point2D) and isinstance(b, LineString):
        return distance_point_to_line(a, b)
    elif isinstance(a, LineString) and isinstance(b, Point2D):
        return distance_line_to_point(a, b)
    elif isinstance(a, Point2D) and isinstance(b, Polygon):
        return distance_point_to_polygon(a, b)
    elif isinstance(a, Polygon) and isinstance(b, Point2D):
        return distance_polygon_to_point(a, b)
    elif isinstance(a, Point2D) and isinstance(b, BoundingBox):
        return distance_point_to_bbox(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, Point2D):
        return distance_bbox_to_point(a, b)
    else:
        raise TypeError(
            f"Unsupported distance calculation between {type(a).__name__} "
            f"and {type(b).__name__}"
        )