"""Shared geometry utility functions for Craftshood_AI.

This module provides common geometry operations used across the
geometry_engine and analysis packages.
"""

from __future__ import annotations

from typing import Any

from shapely.geometry import GeometryCollection, LineString, MultiLineString


def linear_length(geometry: Any) -> float:
    """Return the total linear length of a Shapely geometry.

    Handles the following geometry types:
    - LineString: returns the line length
    - MultiLineString: returns the sum of all line lengths
    - GeometryCollection: returns the sum of all component lengths
    - Empty geometries: returns 0.0

    Args:
        geometry: A Shapely geometry object.

    Returns:
        The total linear length as a float. Returns 0.0 for empty
        or unsupported geometry types.

    Examples:
        >>> from shapely.geometry import LineString, MultiLineString
        >>> line = LineString([(0, 0), (3, 4)])
        >>> linear_length(line)
        5.0
        >>> multi = MultiLineString([[(0, 0), (1, 0)], [(2, 0), (2, 1)]])
        >>> linear_length(multi)
        2.0
    """
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(linear_length(part) for part in geometry.geoms)
    return 0.0
