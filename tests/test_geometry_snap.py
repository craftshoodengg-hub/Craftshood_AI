"""Unit tests for geometry snapping and vertex cleanup utilities."""

from __future__ import annotations

import math

import pytest
from shapely.geometry import LineString, Polygon

from building_model_v2 import (
    Point2D,
    merge_vertices,
    remove_duplicate_vertices,
    simplify_geometry,
    snap_line,
    snap_point,
    snap_polygon,
)


class TestSnapPoint:
    """Tests for snap_point function."""
    
    def test_snap_to_exact_target(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        targets = [Point2D(x=1.0, y=1.0)]
        result = snap_point(point, targets, 0.5)
        assert result == Point2D(x=1.0, y=1.0)
    
    def test_snap_within_tolerance(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        targets = [Point2D(x=1.3, y=1.3)]
        result = snap_point(point, targets, 0.5)
        assert result == Point2D(x=1.3, y=1.3)
    
    def test_no_snap_outside_tolerance(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        targets = [Point2D(x=2.0, y=2.0)]
        result = snap_point(point, targets, 0.5)
        assert result == Point2D(x=1.0, y=1.0)
    
    def test_snap_to_closest_target(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        targets = [
            Point2D(x=2.0, y=0.0),
            Point2D(x=0.5, y=0.0),
            Point2D(x=1.0, y=0.0),
        ]
        result = snap_point(point, targets, 1.0)
        assert result == Point2D(x=0.5, y=0.0)
    
    def test_empty_targets(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        result = snap_point(point, [], 1.0)
        assert result == Point2D(x=1.0, y=1.0)
    
    def test_zero_tolerance(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        targets = [Point2D(x=1.001, y=1.001)]
        result = snap_point(point, targets, 0.0)
        assert result == Point2D(x=1.0, y=1.0)
    
    def test_negative_tolerance(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        targets = [Point2D(x=1.5, y=1.5)]
        result = snap_point(point, targets, -1.0)
        assert result == Point2D(x=1.0, y=1.0)
    
    def test_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            snap_point("not a point", [Point2D(x=0.0, y=0.0)], 1.0)
    
    def test_preserves_original(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        snap_point(point, [Point2D(x=2.0, y=2.0)], 0.5)
        assert point == Point2D(x=1.0, y=1.0)


class TestSnapLine:
    """Tests for snap_line function."""
    
    def test_snap_line_vertices(self) -> None:
        line = LineString([(0.1, 0.1), (1.1, 1.1)])
        targets = [Point2D(x=0.0, y=0.0), Point2D(x=1.0, y=1.0)]
        result = snap_line(line, targets, 0.2)
        coords = list(result.coords)
        assert coords[0] == pytest.approx((0.0, 0.0))
        assert coords[1] == pytest.approx((1.0, 1.0))
    
    def test_snap_line_no_targets(self) -> None:
        line = LineString([(0.0, 0.0), (1.0, 1.0)])
        result = snap_line(line, [], 1.0)
        coords = list(result.coords)
        assert coords[0] == (0.0, 0.0)
        assert coords[1] == (1.0, 1.0)
    
    def test_snap_line_empty(self) -> None:
        line = LineString()
        result = snap_line(line, [Point2D(x=0.0, y=0.0)], 1.0)
        assert result.is_empty
    
    def test_snap_line_negative_tolerance(self) -> None:
        line = LineString([(0.1, 0.1), (1.1, 1.1)])
        targets = [Point2D(x=0.0, y=0.0)]
        result = snap_line(line, targets, -1.0)
        coords = list(result.coords)
        assert coords[0] == pytest.approx((0.1, 0.1))
    
    def test_snap_line_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            snap_line("not a line", [Point2D(x=0.0, y=0.0)], 1.0)
    
    def test_snap_line_preserves_original(self) -> None:
        line = LineString([(0.1, 0.1), (1.1, 1.1)])
        snap_line(line, [Point2D(x=0.0, y=0.0)], 0.5)
        coords = list(line.coords)
        assert coords[0] == pytest.approx((0.1, 0.1))


class TestSnapPolygon:
    """Tests for snap_polygon function."""
    
    def test_snap_polygon_vertices(self) -> None:
        poly = Polygon([(0.1, 0.1), (1.1, 0.1), (1.1, 1.1), (0.1, 1.1)])
        targets = [
            Point2D(x=0.0, y=0.0),
            Point2D(x=1.0, y=0.0),
            Point2D(x=1.0, y=1.0),
            Point2D(x=0.0, y=1.0),
        ]
        result = snap_polygon(poly, targets, 0.2)
        coords = list(result.exterior.coords)
        assert coords[0] == pytest.approx((0.0, 0.0))
        assert coords[1] == pytest.approx((1.0, 0.0))
        assert coords[2] == pytest.approx((1.0, 1.0))
        assert coords[3] == pytest.approx((0.0, 1.0))
    
    def test_snap_polygon_no_targets(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        result = snap_polygon(poly, [], 1.0)
        coords = list(result.exterior.coords)
        assert coords[0] == (0.0, 0.0)
    
    def test_snap_polygon_empty(self) -> None:
        poly = Polygon()
        result = snap_polygon(poly, [Point2D(x=0.0, y=0.0)], 1.0)
        assert result.is_empty
    
    def test_snap_polygon_negative_tolerance(self) -> None:
        poly = Polygon([(0.1, 0.1), (1.1, 0.1), (1.1, 1.1), (0.1, 1.1)])
        targets = [Point2D(x=0.0, y=0.0)]
        result = snap_polygon(poly, targets, -1.0)
        coords = list(result.exterior.coords)
        assert coords[0] == pytest.approx((0.1, 0.1))
    
    def test_snap_polygon_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            snap_polygon("not a poly", [Point2D(x=0.0, y=0.0)], 1.0)
    
    def test_snap_polygon_preserves_original(self) -> None:
        poly = Polygon([(0.1, 0.1), (1.1, 0.1), (1.1, 1.1), (0.1, 1.1)])
        snap_polygon(poly, [Point2D(x=0.0, y=0.0)], 0.5)
        coords = list(poly.exterior.coords)
        assert coords[0] == pytest.approx((0.1, 0.1))


class TestMergeVertices:
    """Tests for merge_vertices function."""
    
    def test_merge_close_vertices_line(self) -> None:
        line = LineString([(0.0, 0.0), (0.01, 0.01), (1.0, 1.0)])
        result = merge_vertices(line, 0.1)
        coords = list(result.coords)
        assert len(coords) == 2
        assert coords[0] == pytest.approx((0.0, 0.0))
        assert coords[1] == pytest.approx((1.0, 1.0))
    
    def test_merge_no_close_vertices(self) -> None:
        line = LineString([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)])
        result = merge_vertices(line, 0.1)
        coords = list(result.coords)
        assert len(coords) == 3
    
    def test_merge_polygon_vertices(self) -> None:
        poly = Polygon([
            (0.0, 0.0), (0.01, 0.01), (1.0, 0.0),
            (1.0, 1.0), (0.0, 1.0),
        ])
        result = merge_vertices(poly, 0.1)
        coords = list(result.exterior.coords)
        # Should have 4 unique vertices + closure
        assert len(coords) == 5
    
    def test_merge_empty_line(self) -> None:
        line = LineString()
        result = merge_vertices(line, 0.1)
        assert result.is_empty
    
    def test_merge_empty_polygon(self) -> None:
        poly = Polygon()
        result = merge_vertices(poly, 0.1)
        assert result.is_empty
    
    def test_merge_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            merge_vertices(Point2D(x=0.0, y=0.0), 0.1)
    
    def test_merge_preserves_original(self) -> None:
        line = LineString([(0.0, 0.0), (0.01, 0.01), (1.0, 1.0)])
        merge_vertices(line, 0.5)
        coords = list(line.coords)
        assert len(coords) == 3


class TestRemoveDuplicateVertices:
    """Tests for remove_duplicate_vertices function."""
    
    def test_remove_duplicates_line(self) -> None:
        line = LineString([(0.0, 0.0), (0.0, 0.0), (1.0, 1.0)])
        result = remove_duplicate_vertices(line)
        coords = list(result.coords)
        assert len(coords) == 2
    
    def test_remove_duplicates_polygon(self) -> None:
        poly = Polygon([
            (0.0, 0.0), (0.0, 0.0), (1.0, 0.0),
            (1.0, 1.0), (0.0, 1.0), (0.0, 0.0),
        ])
        result = remove_duplicate_vertices(poly)
        coords = list(result.exterior.coords)
        # Should have 4 unique vertices + closure
        assert len(coords) == 5
    
    def test_no_duplicates(self) -> None:
        line = LineString([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)])
        result = remove_duplicate_vertices(line)
        coords = list(result.coords)
        assert len(coords) == 3
    
    def test_empty_line(self) -> None:
        line = LineString()
        result = remove_duplicate_vertices(line)
        assert result.is_empty
    
    def test_empty_polygon(self) -> None:
        poly = Polygon()
        result = remove_duplicate_vertices(poly)
        assert result.is_empty
    
    def test_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            remove_duplicate_vertices(Point2D(x=0.0, y=0.0))
    
    def test_preserves_original(self) -> None:
        line = LineString([(0.0, 0.0), (0.0, 0.0), (1.0, 1.0)])
        remove_duplicate_vertices(line)
        coords = list(line.coords)
        assert len(coords) == 3
    
    def test_custom_tolerance(self) -> None:
        line = LineString([(0.0, 0.0), (0.001, 0.001), (1.0, 1.0)])
        result = remove_duplicate_vertices(line, tolerance=0.01)
        coords = list(result.coords)
        assert len(coords) == 2


class TestSimplifyGeometry:
    """Tests for simplify_geometry function."""
    
    def test_simplify_line(self) -> None:
        # Create a line with collinear points
        line = LineString([(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)])
        result = simplify_geometry(line, 0.1)
        coords = list(result.coords)
        assert len(coords) == 2
    
    def test_simplify_polygon(self) -> None:
        # Create a polygon with collinear points
        poly = Polygon([
            (0.0, 0.0), (0.5, 0.0), (1.0, 0.0),
            (1.0, 1.0), (0.0, 1.0),
        ])
        result = simplify_geometry(poly, 0.1)
        # Should simplify to 4 vertices
        assert len(list(result.exterior.coords)) <= 5
    
    def test_simplify_preserves_shape(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        result = simplify_geometry(poly, 0.1)
        # Area should be preserved for a square
        assert result.area == pytest.approx(1.0, abs=0.01)
    
    def test_simplify_empty_line(self) -> None:
        line = LineString()
        result = simplify_geometry(line, 0.1)
        assert result.is_empty
    
    def test_simplify_empty_polygon(self) -> None:
        poly = Polygon()
        result = simplify_geometry(poly, 0.1)
        assert result.is_empty
    
    def test_simplify_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            simplify_geometry(Point2D(x=0.0, y=0.0), 0.1)
    
    def test_simplify_preserves_original(self) -> None:
        line = LineString([(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)])
        simplify_geometry(line, 0.1)
        coords = list(line.coords)
        assert len(coords) == 3


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_snap_point_floating_point(self) -> None:
        point = Point2D(x=0.1 + 0.2, y=0.3)  # 0.30000000000000004
        targets = [Point2D(x=0.3, y=0.3)]
        result = snap_point(point, targets, 1e-9)
        assert result == Point2D(x=0.3, y=0.3)
    
    def test_large_tolerance_snap_all(self) -> None:
        point = Point2D(x=100.0, y=100.0)
        targets = [Point2D(x=0.0, y=0.0)]
        result = snap_point(point, targets, 1000.0)
        assert result == Point2D(x=0.0, y=0.0)
    
    def test_merge_all_vertices(self) -> None:
        line = LineString([(0.0, 0.0), (0.001, 0.001), (0.002, 0.002)])
        result = merge_vertices(line, 1.0)
        coords = list(result.coords)
        assert len(coords) == 2
    
    def test_simplify_complex_shape(self) -> None:
        # Create a more complex polygon
        poly = Polygon([
            (0.0, 0.0), (0.1, 0.0), (0.2, 0.0), (0.3, 0.0),
            (1.0, 0.0), (1.0, 1.0), (0.0, 1.0),
        ])
        result = simplify_geometry(poly, 0.05)
        # Should reduce vertex count
        assert len(list(result.exterior.coords)) < len(list(poly.exterior.coords))
    
    def test_snap_with_many_targets(self) -> None:
        point = Point2D(x=5.0, y=5.0)
        targets = [Point2D(x=float(i), y=float(i)) for i in range(10)]
        result = snap_point(point, targets, 0.1)
        assert result == Point2D(x=5.0, y=5.0)
    
    def test_remove_consecutive_duplicates(self) -> None:
        line = LineString([
            (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1.0, 1.0),
        ])
        result = remove_duplicate_vertices(line)
        coords = list(result.coords)
        assert len(coords) == 2