"""Geometric intersection checks for Building Model v2.

Provides reusable geometry predicates that determine whether two
geometric objects intersect, contain, touch, or cross each other.

This module is independent from entities and contains no AI logic,
validation, or transformation operations.
"""

from __future__ import annotations

from typing import Union

from shapely.geometry import LineString, Point, Polygon

from ..base import BoundingBox, Point2D


def _to_shapely_point(point: Point2D) -> Point:
    """Convert a Point2D to a shapely Point.
    
    Args:
        point: The Point2D to convert.
        
    Returns:
        A shapely Point.
    """
    return Point(point.x, point.y)


def intersects_point_to_point(a: Point2D, b: Point2D) -> bool:
    """Check if two points intersect (are identical).
    
    Args:
        a: First point.
        b: Second point.
        
    Returns:
        True if the points have the same coordinates.
    """
    return a.x == b.x and a.y == b.y


def intersects_point_to_line(point: Point2D, line: LineString) -> bool:
    """Check if a point intersects a line.
    
    Args:
        point: The point to check.
        line: The line to check.
        
    Returns:
        True if the point lies on the line.
    """
    if line.is_empty:
        return False
    shapely_point = _to_shapely_point(point)
    return line.distance(shapely_point) == 0.0


def intersects_point_to_polygon(point: Point2D, polygon: Polygon) -> bool:
    """Check if a point intersects a polygon (on boundary or inside).
    
    Args:
        point: The point to check.
        polygon: The polygon to check.
        
    Returns:
        True if the point is on the boundary or inside the polygon.
    """
    if polygon.is_empty:
        return False
    shapely_point = _to_shapely_point(point)
    return polygon.contains(shapely_point) or polygon.touches(shapely_point)


def intersects_line_to_line(a: LineString, b: LineString) -> bool:
    """Check if two lines intersect.
    
    Args:
        a: First line.
        b: Second line.
        
    Returns:
        True if the lines share any points.
    """
    if a.is_empty or b.is_empty:
        return False
    return a.intersects(b)


def intersects_line_to_polygon(line: LineString, polygon: Polygon) -> bool:
    """Check if a line intersects a polygon.
    
    Args:
        line: The line to check.
        polygon: The polygon to check.
        
    Returns:
        True if the line crosses or touches the polygon.
    """
    if line.is_empty or polygon.is_empty:
        return False
    return line.intersects(polygon)


def intersects_polygon_to_polygon(a: Polygon, b: Polygon) -> bool:
    """Check if two polygons intersect.
    
    Args:
        a: First polygon.
        b: Second polygon.
        
    Returns:
        True if the polygons share any area or boundary.
    """
    if a.is_empty or b.is_empty:
        return False
    return a.intersects(b)


def intersects_bbox_to_point(bbox: BoundingBox, point: Point2D) -> bool:
    """Check if a bounding box contains or touches a point.
    
    Args:
        bbox: The bounding box.
        point: The point to check.
        
    Returns:
        True if the point is inside or on the boundary of the box.
    """
    return bbox.min_x <= point.x <= bbox.max_x and bbox.min_y <= point.y <= bbox.max_y


def intersects_bbox_to_bbox(a: BoundingBox, b: BoundingBox) -> bool:
    """Check if two bounding boxes intersect.
    
    Args:
        a: First bounding box.
        b: Second bounding box.
        
    Returns:
        True if the boxes overlap or touch.
    """
    if a.max_x < b.min_x or b.max_x < a.min_x:
        return False
    if a.max_y < b.min_y or b.max_y < a.min_y:
        return False
    return True


def contains_point_to_point(a: Point2D, b: Point2D) -> bool:
    """Check if point a contains point b (identical coordinates).
    
    Args:
        a: First point.
        b: Second point.
        
    Returns:
        True if the points are identical.
    """
    return a.x == b.x and a.y == b.y


def contains_point_to_line(point: Point2D, line: LineString) -> bool:
    """Check if a point is on a line.
    
    Args:
        point: The point to check.
        line: The line to check.
        
    Returns:
        True if the point lies on the line.
    """
    return intersects_point_to_line(point, line)


def contains_point_to_polygon(point: Point2D, polygon: Polygon) -> bool:
    """Check if a polygon contains a point (strictly inside, not on boundary).
    
    Args:
        point: The point to check.
        polygon: The polygon to check.
        
    Returns:
        True if the point is strictly inside the polygon.
    """
    if polygon.is_empty:
        return False
    shapely_point = _to_shapely_point(point)
    return polygon.contains(shapely_point)


def contains_line_to_polygon(line: LineString, polygon: Polygon) -> bool:
    """Check if a polygon contains a line.
    
    Args:
        line: The line to check.
        polygon: The polygon to check.
        
    Returns:
        True if the entire line is inside the polygon.
    """
    if line.is_empty or polygon.is_empty:
        return False
    return polygon.contains(line)


def contains_polygon_to_polygon(a: Polygon, b: Polygon) -> bool:
    """Check if polygon a contains polygon b.
    
    Args:
        a: The containing polygon.
        b: The polygon to check.
        
    Returns:
        True if polygon b is entirely inside polygon a.
    """
    if a.is_empty or b.is_empty:
        return False
    return a.contains(b)


def contains_bbox_to_point(bbox: BoundingBox, point: Point2D) -> bool:
    """Check if a bounding box contains a point.
    
    Args:
        bbox: The bounding box.
        point: The point to check.
        
    Returns:
        True if the point is inside or on the boundary of the box.
    """
    return bbox.min_x <= point.x <= bbox.max_x and bbox.min_y <= point.y <= bbox.max_y


def contains_bbox_to_bbox(a: BoundingBox, b: BoundingBox) -> bool:
    """Check if bounding box a contains bounding box b.
    
    Args:
        a: The containing box.
        b: The box to check.
        
    Returns:
        True if box b is entirely inside or equal to box a.
    """
    return (a.min_x <= b.min_x and a.max_x >= b.max_x and
            a.min_y <= b.min_y and a.max_y >= b.max_y)


def touches_point_to_point(a: Point2D, b: Point2D) -> bool:
    """Check if two points touch (are identical).
    
    Args:
        a: First point.
        b: Second point.
        
    Returns:
        True if the points are identical.
    """
    return a.x == b.x and a.y == b.y


def touches_point_to_line(point: Point2D, line: LineString) -> bool:
    """Check if a point touches a line (lies on it).
    
    Args:
        point: The point to check.
        line: The line to check.
        
    Returns:
        True if the point lies on the line.
    """
    return intersects_point_to_line(point, line)


def touches_point_to_polygon(point: Point2D, polygon: Polygon) -> bool:
    """Check if a point touches a polygon (on boundary only).
    
    Args:
        point: The point to check.
        polygon: The polygon to check.
        
    Returns:
        True if the point is on the boundary of the polygon.
    """
    if polygon.is_empty:
        return False
    shapely_point = _to_shapely_point(point)
    return polygon.boundary.distance(shapely_point) == 0.0


def touches_line_to_line(a: LineString, b: LineString) -> bool:
    """Check if two lines touch (share at least one point).
    
    Args:
        a: First line.
        b: Second line.
        
    Returns:
        True if the lines share at least one point.
    """
    if a.is_empty or b.is_empty:
        return False
    return a.touches(b) or a.intersects(b)


def touches_line_to_polygon(line: LineString, polygon: Polygon) -> bool:
    """Check if a line touches a polygon (shares boundary but doesn't cross interior).
    
    Args:
        line: The line to check.
        polygon: The polygon to check.
        
    Returns:
        True if the line touches but doesn't cross into the polygon interior.
    """
    if line.is_empty or polygon.is_empty:
        return False
    if not line.intersects(polygon):
        return False
    # A line that crosses the polygon interior is not just touching
    # Use shapely's crosses to detect interior crossing
    return not line.crosses(polygon)


def touches_polygon_to_polygon(a: Polygon, b: Polygon) -> bool:
    """Check if two polygons touch (share boundary but not interior).
    
    Args:
        a: First polygon.
        b: Second polygon.
        
    Returns:
        True if the polygons share boundary but not interior area.
    """
    if a.is_empty or b.is_empty:
        return False
    return a.touches(b)


def touches_bbox_to_bbox(a: BoundingBox, b: BoundingBox) -> bool:
    """Check if two bounding boxes touch (share edge or corner).
    
    Args:
        a: First bounding box.
        b: Second bounding box.
        
    Returns:
        True if the boxes share at least one edge or corner but no interior.
    """
    if a.max_x < b.min_x or b.max_x < a.min_x:
        return False
    if a.max_y < b.min_y or b.max_y < a.min_y:
        return False
    # Check if they only touch (share edge/corner but no overlap)
    x_touch = (a.max_x == b.min_x or b.max_x == a.min_x)
    y_touch = (a.max_y == b.min_y or b.max_y == a.min_y)
    return x_touch or y_touch


def crosses_point_to_point(a: Point2D, b: Point2D) -> bool:
    """Check if two points cross (always False for points).
    
    Args:
        a: First point.
        b: Second point.
        
    Returns:
        Always False.
    """
    return False


def crosses_point_to_line(point: Point2D, line: LineString) -> bool:
    """Check if a point crosses a line (always False).
    
    Args:
        point: The point to check.
        line: The line to check.
        
    Returns:
        Always False.
    """
    return False


def crosses_point_to_polygon(point: Point2D, polygon: Polygon) -> bool:
    """Check if a point crosses a polygon (always False).
    
    Args:
        point: The point to check.
        polygon: The polygon to check.
        
    Returns:
        Always False.
    """
    return False


def crosses_line_to_line(a: LineString, b: LineString) -> bool:
    """Check if two lines cross (intersect at interior points).
    
    Args:
        a: First line.
        b: Second line.
        
    Returns:
        True if the lines cross at interior points (not just touch).
    """
    if a.is_empty or b.is_empty:
        return False
    return a.crosses(b)


def crosses_line_to_polygon(line: LineString, polygon: Polygon) -> bool:
    """Check if a line crosses a polygon (enters and exits).
    
    Args:
        line: The line to check.
        polygon: The polygon to check.
        
    Returns:
        True if the line crosses through the polygon interior.
    """
    if line.is_empty or polygon.is_empty:
        return False
    return line.crosses(polygon)


def crosses_polygon_to_polygon(a: Polygon, b: Polygon) -> bool:
    """Check if two polygons cross (overlap but neither contains the other).
    
    Args:
        a: First polygon.
        b: Second polygon.
        
    Returns:
        True if the polygons overlap but neither contains the other.
    """
    if a.is_empty or b.is_empty:
        return False
    # Polygons cross if they intersect but neither contains the other
    if not a.intersects(b):
        return False
    return not a.contains(b) and not b.contains(a)


def intersects(a: Union[Point2D, LineString, Polygon, BoundingBox],
             b: Union[Point2D, LineString, Polygon, BoundingBox]) -> bool:
    """Check if two geometry objects intersect.
    
    Args:
        a: First geometry object.
        b: Second geometry object.
        
    Returns:
        True if the objects share any points.
        
    Raises:
        TypeError: If the combination of types is not supported.
    """
    if isinstance(a, Point2D) and isinstance(b, Point2D):
        return intersects_point_to_point(a, b)
    elif isinstance(a, Point2D) and isinstance(b, LineString):
        return intersects_point_to_line(a, b)
    elif isinstance(a, Point2D) and isinstance(b, Polygon):
        return intersects_point_to_polygon(a, b)
    elif isinstance(a, Point2D) and isinstance(b, BoundingBox):
        return intersects_bbox_to_point(b, a)
    elif isinstance(a, LineString) and isinstance(b, Point2D):
        return intersects_point_to_line(b, a)
    elif isinstance(a, LineString) and isinstance(b, LineString):
        return intersects_line_to_line(a, b)
    elif isinstance(a, LineString) and isinstance(b, Polygon):
        return intersects_line_to_polygon(a, b)
    elif isinstance(a, Polygon) and isinstance(b, Point2D):
        return intersects_point_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, LineString):
        return intersects_line_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, Polygon):
        return intersects_polygon_to_polygon(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, Point2D):
        return intersects_bbox_to_point(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, BoundingBox):
        return intersects_bbox_to_bbox(a, b)
    else:
        raise TypeError(
            f"Unsupported intersection check between {type(a).__name__} "
            f"and {type(b).__name__}"
        )


def contains(a: Union[Point2D, LineString, Polygon, BoundingBox],
             b: Union[Point2D, LineString, Polygon, BoundingBox]) -> bool:
    """Check if geometry a contains geometry b.
    
    Args:
        a: The containing geometry.
        b: The geometry to check.
        
    Returns:
        True if b is entirely inside a.
        
    Raises:
        TypeError: If the combination of types is not supported.
    """
    if isinstance(a, Point2D) and isinstance(b, Point2D):
        return contains_point_to_point(a, b)
    elif isinstance(a, Point2D) and isinstance(b, LineString):
        return contains_point_to_line(a, b)
    elif isinstance(a, Point2D) and isinstance(b, Polygon):
        return False  # A point cannot contain a polygon
    elif isinstance(a, Point2D) and isinstance(b, BoundingBox):
        return False  # A point cannot contain a bounding box
    elif isinstance(a, LineString) and isinstance(b, Point2D):
        return contains_point_to_line(b, a)
    elif isinstance(a, LineString) and isinstance(b, LineString):
        return False  # Lines don't contain other lines
    elif isinstance(a, LineString) and isinstance(b, Polygon):
        return False  # Lines don't contain polygons
    elif isinstance(a, Polygon) and isinstance(b, Point2D):
        return contains_point_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, LineString):
        return contains_line_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, Polygon):
        return contains_polygon_to_polygon(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, Point2D):
        return contains_bbox_to_point(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, BoundingBox):
        return contains_bbox_to_bbox(a, b)
    else:
        raise TypeError(
            f"Unsupported contains check between {type(a).__name__} "
            f"and {type(b).__name__}"
        )


def touches(a: Union[Point2D, LineString, Polygon, BoundingBox],
            b: Union[Point2D, LineString, Polygon, BoundingBox]) -> bool:
    """Check if two geometry objects touch (share boundary only).
    
    Args:
        a: First geometry object.
        b: Second geometry object.
        
    Returns:
        True if the objects share boundary but not interior.
        
    Raises:
        TypeError: If the combination of types is not supported.
    """
    if isinstance(a, Point2D) and isinstance(b, Point2D):
        return touches_point_to_point(a, b)
    elif isinstance(a, Point2D) and isinstance(b, LineString):
        return touches_point_to_line(a, b)
    elif isinstance(a, Point2D) and isinstance(b, Polygon):
        return touches_point_to_polygon(a, b)
    elif isinstance(a, Point2D) and isinstance(b, BoundingBox):
        return intersects_bbox_to_point(b, a)
    elif isinstance(a, LineString) and isinstance(b, Point2D):
        return touches_point_to_line(b, a)
    elif isinstance(a, LineString) and isinstance(b, LineString):
        return touches_line_to_line(a, b)
    elif isinstance(a, LineString) and isinstance(b, Polygon):
        return touches_line_to_polygon(a, b)
    elif isinstance(a, Polygon) and isinstance(b, Point2D):
        return touches_point_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, LineString):
        return touches_line_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, Polygon):
        return touches_polygon_to_polygon(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, Point2D):
        return intersects_bbox_to_point(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, BoundingBox):
        return touches_bbox_to_bbox(a, b)
    else:
        raise TypeError(
            f"Unsupported touches check between {type(a).__name__} "
            f"and {type(b).__name__}"
        )


def crosses(a: Union[Point2D, LineString, Polygon, BoundingBox],
            b: Union[Point2D, LineString, Polygon, BoundingBox]) -> bool:
    """Check if two geometry objects cross.
    
    Args:
        a: First geometry object.
        b: Second geometry object.
        
    Returns:
        True if the objects cross (intersect at interior points).
        
    Raises:
        TypeError: If the combination of types is not supported.
    """
    if isinstance(a, Point2D) and isinstance(b, Point2D):
        return crosses_point_to_point(a, b)
    elif isinstance(a, Point2D) and isinstance(b, LineString):
        return crosses_point_to_line(a, b)
    elif isinstance(a, Point2D) and isinstance(b, Polygon):
        return crosses_point_to_polygon(a, b)
    elif isinstance(a, Point2D) and isinstance(b, BoundingBox):
        return False  # Points don't cross bounding boxes
    elif isinstance(a, LineString) and isinstance(b, Point2D):
        return crosses_point_to_line(b, a)
    elif isinstance(a, LineString) and isinstance(b, LineString):
        return crosses_line_to_line(a, b)
    elif isinstance(a, LineString) and isinstance(b, Polygon):
        return crosses_line_to_polygon(a, b)
    elif isinstance(a, Polygon) and isinstance(b, Point2D):
        return crosses_point_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, LineString):
        return crosses_line_to_polygon(b, a)
    elif isinstance(a, Polygon) and isinstance(b, Polygon):
        return crosses_polygon_to_polygon(a, b)
    elif isinstance(a, BoundingBox) and isinstance(b, Point2D):
        return False  # Bounding boxes don't cross points
    elif isinstance(a, BoundingBox) and isinstance(b, BoundingBox):
        return False  # Bounding boxes don't cross
    else:
        raise TypeError(
            f"Unsupported crosses check between {type(a).__name__} "
            f"and {type(b).__name__}"
        )