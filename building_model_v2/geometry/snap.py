"""Snapping and vertex cleanup utilities for Building Model v2.

Provides reusable snapping functions for aligning geometry to target
points and grids, plus vertex cleanup operations for simplifying
and deduplicating geometry vertices.

This module is independent from entities and contains no AI logic,
validation, or transformation operations.

All functions are pure - they never modify the original geometry.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Union

from shapely.geometry import LineString, Point, Polygon

from ..base import BoundingBox, Point2D


def _distance_sq(p1: Point2D, p2: Point2D) -> float:
    """Calculate squared distance between two points.
    
    Args:
        p1: First point.
        p2: Second point.
        
    Returns:
        Squared distance between the points.
    """
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return dx * dx + dy * dy


def _distance(p1: Point2D, p2: Point2D) -> float:
    """Calculate Euclidean distance between two points.
    
    Args:
        p1: First point.
        p2: Second point.
        
    Returns:
        Euclidean distance between the points.
    """
    return _distance_sq(p1, p2) ** 0.5


def _find_closest_target(point: Point2D, targets: Sequence[Point2D]) -> Optional[Point2D]:
    """Find the closest target point to a given point.
    
    Args:
        point: The source point.
        targets: Sequence of target points to search.
        
    Returns:
        The closest target point, or None if targets is empty.
    """
    if not targets:
        return None
    
    closest = None
    min_dist_sq = float("inf")
    
    for target in targets:
        dist_sq = _distance_sq(point, target)
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            closest = target
    
    return closest


def snap_point(
    point: Point2D,
    targets: Sequence[Point2D],
    tolerance: float,
) -> Point2D:
    """Snap a point to the nearest target within tolerance.
    
    If no target is within tolerance, the original point is returned.
    
    Args:
        point: The point to snap.
        targets: Target points to snap to.
        tolerance: Maximum distance to snap.
        
    Returns:
        The snapped point, or the original point if no target is within tolerance.
        
    Raises:
        TypeError: If point is not a Point2D.
    """
    if not isinstance(point, Point2D):
        raise TypeError(f"Expected Point2D, got {type(point).__name__}")
    
    if tolerance < 0:
        return point
    
    if not targets:
        return point
    
    closest = _find_closest_target(point, targets)
    if closest is None:
        return point
    
    if _distance(point, closest) <= tolerance:
        return closest
    
    return point


def snap_line(
    line: LineString,
    targets: Sequence[Point2D],
    tolerance: float,
) -> LineString:
    """Snap all vertices of a line to nearest targets within tolerance.
    
    Args:
        line: The line to snap.
        targets: Target points to snap to.
        tolerance: Maximum distance to snap.
        
    Returns:
        A new line with snapped vertices, or original if line is empty.
        
    Raises:
        TypeError: If line is not a LineString.
    """
    if not isinstance(line, LineString):
        raise TypeError(f"Expected LineString, got {type(line).__name__}")
    
    if line.is_empty or not targets or tolerance < 0:
        return line
    
    coords = list(line.coords)
    new_coords = []
    
    for coord in coords:
        point = Point2D(x=coord[0], y=coord[1])
        snapped = snap_point(point, targets, tolerance)
        new_coords.append((snapped.x, snapped.y))
    
    return LineString(new_coords)


def snap_polygon(
    polygon: Polygon,
    targets: Sequence[Point2D],
    tolerance: float,
) -> Polygon:
    """Snap all vertices of a polygon to nearest targets within tolerance.
    
    Args:
        polygon: The polygon to snap.
        targets: Target points to snap to.
        tolerance: Maximum distance to snap.
        
    Returns:
        A new polygon with snapped vertices, or original if polygon is empty.
        
    Raises:
        TypeError: If polygon is not a Polygon.
    """
    if not isinstance(polygon, Polygon):
        raise TypeError(f"Expected Polygon, got {type(polygon).__name__}")
    
    if polygon.is_empty or not targets or tolerance < 0:
        return polygon
    
    exterior_coords = list(polygon.exterior.coords)
    new_exterior = []
    
    for coord in exterior_coords:
        point = Point2D(x=coord[0], y=coord[1])
        snapped = snap_point(point, targets, tolerance)
        new_exterior.append((snapped.x, snapped.y))
    
    # Handle interior rings (holes)
    new_interiors = []
    for interior in polygon.interiors:
        interior_coords = list(interior.coords)
        new_interior = []
        for coord in interior_coords:
            point = Point2D(x=coord[0], y=coord[1])
            snapped = snap_point(point, targets, tolerance)
            new_interior.append((snapped.x, snapped.y))
        new_interiors.append(new_interior)
    
    return Polygon(new_exterior, new_interiors)


def merge_vertices(
    geometry: Union[LineString, Polygon],
    tolerance: float,
) -> Union[LineString, Polygon]:
    """Merge vertices that are within tolerance distance of each other.
    
    For polygons, this processes the exterior ring and all interior rings.
    
    Args:
        geometry: The geometry to process.
        tolerance: Minimum distance between vertices.
        
    Returns:
        A new geometry with merged vertices, or original if empty.
        
    Raises:
        TypeError: If geometry type is not supported.
    """
    if isinstance(geometry, LineString):
        if geometry.is_empty:
            return geometry
        return LineString(_merge_coords(list(geometry.coords), tolerance))
    
    elif isinstance(geometry, Polygon):
        if geometry.is_empty:
            return geometry
        
        exterior = list(geometry.exterior.coords)
        new_exterior = _merge_coords(exterior, tolerance)
        
        new_interiors = []
        for interior in geometry.interiors:
            interior_coords = list(interior.coords)
            new_interior = _merge_coords(interior_coords, tolerance)
            new_interiors.append(new_interior)
        
        return Polygon(new_exterior, new_interiors)
    
    else:
        raise TypeError(
            f"merge_vertices only supports LineString and Polygon, got {type(geometry).__name__}"
        )


def _merge_coords(
    coords: List[tuple],
    tolerance: float,
) -> List[tuple]:
    """Merge coordinate pairs that are within tolerance distance.
    
    Args:
        coords: List of coordinate tuples.
        tolerance: Minimum distance between vertices.
        
    Returns:
        List of merged coordinate tuples.
    """
    if len(coords) <= 2:
        return coords
    
    tolerance_sq = tolerance * tolerance
    result = [coords[0]]
    
    for i in range(1, len(coords)):
        prev = Point2D(x=result[-1][0], y=result[-1][1])
        curr = Point2D(x=coords[i][0], y=coords[i][1])
        
        if _distance_sq(prev, curr) >= tolerance_sq:
            result.append(coords[i])
    
    # Ensure we have at least 2 points for a valid geometry
    if len(result) == 1 and len(coords) > 1:
        # Find a point that's far enough from the first
        for i in range(1, len(coords)):
            first = Point2D(x=coords[0][0], y=coords[0][1])
            other = Point2D(x=coords[i][0], y=coords[i][1])
            if _distance_sq(first, other) >= tolerance_sq:
                result.append(coords[i])
                break
        # If still only 1 point, keep the last original point
        if len(result) == 1:
            result.append(coords[-1])
    
    # Ensure polygon closure is preserved (first == last)
    if len(coords) > 2 and coords[0] == coords[-1] and result[0] != result[-1]:
        result.append(result[0])
    
    return result


def remove_duplicate_vertices(
    geometry: Union[LineString, Polygon],
    tolerance: float = 1e-9,
) -> Union[LineString, Polygon]:
    """Remove duplicate vertices from a geometry.
    
    Args:
        geometry: The geometry to process.
        tolerance: Distance below which vertices are considered duplicates.
        
    Returns:
        A new geometry with duplicates removed, or original if empty.
        
    Raises:
        TypeError: If geometry type is not supported.
    """
    if isinstance(geometry, LineString):
        if geometry.is_empty:
            return geometry
        return LineString(_remove_duplicates(list(geometry.coords), tolerance))
    
    elif isinstance(geometry, Polygon):
        if geometry.is_empty:
            return geometry
        
        exterior = list(geometry.exterior.coords)
        new_exterior = _remove_duplicates(exterior, tolerance)
        
        new_interiors = []
        for interior in geometry.interiors:
            interior_coords = list(interior.coords)
            new_interior = _remove_duplicates(interior_coords, tolerance)
            new_interiors.append(new_interior)
        
        return Polygon(new_exterior, new_interiors)
    
    else:
        raise TypeError(
            f"remove_duplicate_vertices only supports LineString and Polygon, got {type(geometry).__name__}"
        )


def _remove_duplicates(
    coords: List[tuple],
    tolerance: float,
) -> List[tuple]:
    """Remove consecutive duplicate coordinates.
    
    Args:
        coords: List of coordinate tuples.
        tolerance: Distance below which vertices are considered duplicates.
        
    Returns:
        List of unique coordinate tuples.
    """
    if not coords:
        return coords
    
    tolerance_sq = tolerance * tolerance
    result = [coords[0]]
    
    for i in range(1, len(coords)):
        prev = Point2D(x=result[-1][0], y=result[-1][1])
        curr = Point2D(x=coords[i][0], y=coords[i][1])
        
        if _distance_sq(prev, curr) > tolerance_sq:
            result.append(coords[i])
    
    # Ensure polygon closure is preserved
    if len(coords) > 2 and coords[0] == coords[-1]:
        if result[0] != result[-1]:
            if len(result) > 1:
                first = Point2D(x=result[0][0], y=result[0][1])
                last = Point2D(x=result[-1][0], y=result[-1][1])
                if _distance_sq(first, last) <= tolerance_sq:
                    result[-1] = result[0]
                else:
                    result.append(result[0])
    
    return result


def simplify_geometry(
    geometry: Union[LineString, Polygon],
    tolerance: float,
) -> Union[LineString, Polygon]:
    """Simplify a geometry using the Douglas-Peucker algorithm.
    
    Args:
        geometry: The geometry to simplify.
        tolerance: Maximum allowed deviation from original.
        
    Returns:
        A simplified geometry, or original if empty.
        
    Raises:
        TypeError: If geometry type is not supported.
    """
    if isinstance(geometry, (LineString, Polygon)):
        if geometry.is_empty:
            return geometry
        return geometry.simplify(tolerance, preserve_topology=True)
    else:
        raise TypeError(
            f"simplify_geometry only supports LineString and Polygon, got {type(geometry).__name__}"
        )