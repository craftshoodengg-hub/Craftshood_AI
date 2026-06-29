"""Geometry transformations for Building Model v2.

Provides reusable transformation functions for translating, rotating,
scaling, mirroring, and offsetting geometric objects.

This module is independent from entities and contains no AI logic,
validation, or transformation operations.

All functions are pure - they never modify the original geometry.
"""

from __future__ import annotations

import math
from typing import Optional, Union

from shapely.geometry import LineString, Point, Polygon
from shapely.affinity import affine_transform

from ..base import BoundingBox, Point2D


def _to_shapely_point(point: Point2D) -> Point:
    """Convert a Point2D to a shapely Point.
    
    Args:
        point: The Point2D to convert.
        
    Returns:
        A shapely Point.
    """
    return Point(point.x, point.y)


def _from_shapely_point(point: Point) -> Point2D:
    """Convert a shapely Point to a Point2D.
    
    Args:
        point: The shapely Point to convert.
        
    Returns:
        A Point2D.
    """
    return Point2D(x=point.x, y=point.y)


def _get_centroid(geometry: Union[Point, LineString, Polygon, BoundingBox]) -> Point2D:
    """Get the centroid of a geometry.
    
    Args:
        geometry: The geometry to get centroid for.
        
    Returns:
        The centroid as a Point2D.
        
    Raises:
        TypeError: If the geometry type is not supported.
    """
    if isinstance(geometry, BoundingBox):
        return geometry.center
    elif isinstance(geometry, Point2D):
        return geometry
    elif isinstance(geometry, (LineString, Polygon)):
        if geometry.is_empty:
            raise ValueError("Cannot get centroid of empty geometry")
        c = geometry.centroid
        return Point2D(x=c.x, y=c.y)
    else:
        raise TypeError(f"Unsupported geometry type: {type(geometry).__name__}")


def translate(
    geometry: Union[Point2D, LineString, Polygon, BoundingBox],
    dx: float,
    dy: float,
) -> Union[Point2D, LineString, Polygon, BoundingBox]:
    """Translate a geometry by a displacement vector.
    
    Args:
        geometry: The geometry to translate.
        dx: Displacement in x direction.
        dy: Displacement in y direction.
        
    Returns:
        A new translated geometry.
        
    Raises:
        TypeError: If the geometry type is not supported.
    """
    if isinstance(geometry, Point2D):
        return Point2D(x=geometry.x + dx, y=geometry.y + dy)
    elif isinstance(geometry, BoundingBox):
        return BoundingBox(
            min_x=geometry.min_x + dx,
            min_y=geometry.min_y + dy,
            max_x=geometry.max_x + dx,
            max_y=geometry.max_y + dy,
        )
    elif isinstance(geometry, (LineString, Polygon)):
        if geometry.is_empty:
            return geometry
        return affine_transform(geometry, [1.0, 0.0, 0.0, 1.0, dx, dy])
    else:
        raise TypeError(f"Unsupported geometry type: {type(geometry).__name__}")


def rotate(
    geometry: Union[Point2D, LineString, Polygon, BoundingBox],
    angle_degrees: float,
    origin: Optional[Point2D] = None,
) -> Union[Point2D, LineString, Polygon, BoundingBox]:
    """Rotate a geometry around an origin point.
    
    Args:
        geometry: The geometry to rotate.
        angle_degrees: Rotation angle in degrees (counter-clockwise).
        origin: The origin point for rotation. Defaults to geometry centroid.
        
    Returns:
        A new rotated geometry.
        
    Raises:
        TypeError: If the geometry type is not supported.
    """
    if isinstance(geometry, Point2D):
        if origin is None:
            origin = geometry
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        dx = geometry.x - origin.x
        dy = geometry.y - origin.y
        new_x = origin.x + dx * cos_a - dy * sin_a
        new_y = origin.y + dx * sin_a + dy * cos_a
        return Point2D(x=new_x, y=new_y)
    
    elif isinstance(geometry, BoundingBox):
        if origin is None:
            origin = _get_centroid(geometry)
        corners = [
            Point2D(x=geometry.min_x, y=geometry.min_y),
            Point2D(x=geometry.max_x, y=geometry.min_y),
            Point2D(x=geometry.max_x, y=geometry.max_y),
            Point2D(x=geometry.min_x, y=geometry.max_y),
        ]
        rotated_corners = [rotate(c, angle_degrees, origin) for c in corners]
        xs = [c.x for c in rotated_corners]
        ys = [c.y for c in rotated_corners]
        return BoundingBox(
            min_x=min(xs),
            min_y=min(ys),
            max_x=max(xs),
            max_y=max(ys),
        )
    
    elif isinstance(geometry, (LineString, Polygon)):
        if geometry.is_empty:
            return geometry
        if origin is None:
            origin = _get_centroid(geometry)
        from shapely.affinity import rotate as shapely_rotate
        return shapely_rotate(geometry, angle_degrees, origin=(origin.x, origin.y))
    
    else:
        raise TypeError(f"Unsupported geometry type: {type(geometry).__name__}")


def scale(
    geometry: Union[Point2D, LineString, Polygon, BoundingBox],
    sx: float,
    sy: Optional[float] = None,
    origin: Optional[Point2D] = None,
) -> Union[Point2D, LineString, Polygon, BoundingBox]:
    """Scale a geometry by scale factors.
    
    Args:
        geometry: The geometry to scale.
        sx: Scale factor in x direction.
        sy: Scale factor in y direction. Defaults to sx (uniform scaling).
        origin: The origin point for scaling. Defaults to geometry centroid.
        
    Returns:
        A new scaled geometry.
        
    Raises:
        TypeError: If the geometry type is not supported.
    """
    if sy is None:
        sy = sx
    
    if isinstance(geometry, Point2D):
        if origin is None:
            origin = geometry
        new_x = origin.x + (geometry.x - origin.x) * sx
        new_y = origin.y + (geometry.y - origin.y) * sy
        return Point2D(x=new_x, y=new_y)
    
    elif isinstance(geometry, BoundingBox):
        if origin is None:
            origin = _get_centroid(geometry)
        new_min_x = origin.x + (geometry.min_x - origin.x) * sx
        new_min_y = origin.y + (geometry.min_y - origin.y) * sy
        new_max_x = origin.x + (geometry.max_x - origin.x) * sx
        new_max_y = origin.y + (geometry.max_y - origin.y) * sy
        
        if new_min_x > new_max_x:
            new_min_x, new_max_x = new_max_x, new_min_x
        if new_min_y > new_max_y:
            new_min_y, new_max_y = new_max_y, new_min_y
        
        return BoundingBox(
            min_x=new_min_x,
            min_y=new_min_y,
            max_x=new_max_x,
            max_y=new_max_y,
        )
    
    elif isinstance(geometry, (LineString, Polygon)):
        if geometry.is_empty:
            return geometry
        if origin is None:
            origin = _get_centroid(geometry)
        return affine_transform(geometry, [sx, 0.0, 0.0, sy, origin.x * (1 - sx), origin.y * (1 - sy)])
    
    else:
        raise TypeError(f"Unsupported geometry type: {type(geometry).__name__}")


def mirror(
    geometry: Union[Point2D, LineString, Polygon, BoundingBox],
    axis: str = "x",
) -> Union[Point2D, LineString, Polygon, BoundingBox]:
    """Mirror a geometry across an axis.
    
    Args:
        geometry: The geometry to mirror.
        axis: The axis to mirror across. "x" for x-axis, "y" for y-axis.
        
    Returns:
        A new mirrored geometry.
        
    Raises:
        TypeError: If the geometry type is not supported.
        ValueError: If axis is not "x" or "y".
    """
    if axis not in ("x", "y"):
        raise ValueError(f"Axis must be 'x' or 'y', got '{axis}'")
    
    if isinstance(geometry, Point2D):
        if axis == "x":
            return Point2D(x=geometry.x, y=-geometry.y)
        else:
            return Point2D(x=-geometry.x, y=geometry.y)
    
    elif isinstance(geometry, BoundingBox):
        if axis == "x":
            return BoundingBox(
                min_x=geometry.min_x,
                min_y=-geometry.max_y,
                max_x=geometry.max_x,
                max_y=-geometry.min_y,
            )
        else:
            return BoundingBox(
                min_x=-geometry.max_x,
                min_y=geometry.min_y,
                max_x=-geometry.min_x,
                max_y=geometry.max_y,
            )
    
    elif isinstance(geometry, (LineString, Polygon)):
        if geometry.is_empty:
            return geometry
        if axis == "x":
            return affine_transform(geometry, [1.0, 0.0, 0.0, -1.0, 0.0, 0.0])
        else:
            return affine_transform(geometry, [-1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
    
    else:
        raise TypeError(f"Unsupported geometry type: {type(geometry).__name__}")


def offset(
    geometry: Union[LineString, Polygon],
    distance: float,
) -> Union[LineString, Polygon]:
    """Offset a geometry by a distance.
    
    For Polygons, this creates an outward (positive) or inward (negative) offset.
    For LineStrings, this creates a parallel line offset.
    
    Args:
        geometry: The geometry to offset (LineString or Polygon).
        distance: The offset distance. Positive for outward, negative for inward.
        
    Returns:
        A new offset geometry.
        
    Raises:
        TypeError: If the geometry type is not supported.
    """
    if isinstance(geometry, (LineString, Polygon)):
        if geometry.is_empty:
            return geometry
        try:
            return geometry.buffer(distance, join_style=2)  # mitre join
        except Exception:
            return geometry
    else:
        raise TypeError(f"Unsupported geometry type: {type(geometry).__name__}")
