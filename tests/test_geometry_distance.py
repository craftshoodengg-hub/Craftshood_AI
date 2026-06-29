"""Unit tests for geometry distance calculations."""

from __future__ import annotations

import math

import pytest
from shapely.geometry import LineString, Point, Polygon

from building_model_v2 import (
    BoundingBox,
    Point2D,
    distance,
    distance_bbox_to_point,
    distance_line_to_point,
    distance_point_to_bbox,
    distance_point_to_line,
    distance_point_to_point,
    distance_point_to_polygon,
    distance_polygon_to_point,
)


class TestDistancePointToPoint:
    """Tests for distance_point_to_point."""
    
    def test_identical_points(self) -> None:
        p = Point2D(x=5.0, y=3.0)
        assert distance_point_to_point(p, p) == pytest.approx(0.0)
    
    def test_horizontal_distance(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=3.0, y=0.0)
        assert distance_point_to_point(a, b) == pytest.approx(3.0)
    
    def test_vertical_distance(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=0.0, y=4.0)
        assert distance_point_to_point(a, b) == pytest.approx(4.0)
    
    def test_diagonal_distance(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=3.0, y=4.0)
        assert distance_point_to_point(a, b) == pytest.approx(5.0)
    
    def test_negative_coordinates(self) -> None:
        a = Point2D(x=-1.0, y=-1.0)
        b = Point2D(x=2.0, y=3.0)
        assert distance_point_to_point(a, b) == pytest.approx(5.0)
    
    def test_symmetry(self) -> None:
        a = Point2D(x=1.0, y=2.0)
        b = Point2D(x=4.0, y=6.0)
        assert distance_point_to_point(a, b) == pytest.approx(distance_point_to_point(b, a))
    
    def test_floating_point_precision(self) -> None:
        a = Point2D(x=0.1, y=0.2)
        b = Point2D(x=0.3, y=0.4)
        expected = math.sqrt(0.04 + 0.04)
        assert distance_point_to_point(a, b) == pytest.approx(expected, rel=1e-9)
    
    def test_large_coordinates(self) -> None:
        a = Point2D(x=10000.0, y=20000.0)
        b = Point2D(x=10003.0, y=20004.0)
        assert distance_point_to_point(a, b) == pytest.approx(5.0)
    
    def test_unit_distance(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=1.0, y=0.0)
        assert distance_point_to_point(a, b) == pytest.approx(1.0)


class TestDistancePointToLine:
    """Tests for distance_point_to_line."""
    
    def test_point_on_line(self) -> None:
        point = Point2D(x=1.0, y=0.0)
        line = LineString([(0.0, 0.0), (2.0, 0.0)])
        assert distance_point_to_line(point, line) == pytest.approx(0.0)
    
    def test_horizontal_distance_to_horizontal_line(self) -> None:
        point = Point2D(x=1.0, y=3.0)
        line = LineString([(0.0, 0.0), (5.0, 0.0)])
        assert distance_point_to_line(point, line) == pytest.approx(3.0)
    
    def test_perpendicular_distance(self) -> None:
        point = Point2D(x=2.0, y=3.0)
        line = LineString([(0.0, 0.0), (5.0, 0.0)])
        assert distance_point_to_line(point, line) == pytest.approx(3.0)
    
    def test_distance_to_diagonal_line(self) -> None:
        point = Point2D(x=0.0, y=1.0)
        line = LineString([(0.0, 0.0), (1.0, 1.0)])
        expected = math.sqrt(2) / 2
        assert distance_point_to_line(point, line) == pytest.approx(expected, rel=1e-9)
    
    def test_empty_line(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        line = LineString()
        assert distance_point_to_line(point, line) == float('inf')
    
    def test_point_at_line_endpoint(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        line = LineString([(0.0, 0.0), (5.0, 0.0)])
        assert distance_point_to_line(point, line) == pytest.approx(0.0)
    
    def test_point_beyond_endpoint(self) -> None:
        point = Point2D(x=10.0, y=0.0)
        line = LineString([(0.0, 0.0), (5.0, 0.0)])
        assert distance_point_to_line(point, line) == pytest.approx(5.0)


class TestDistanceLineToPoint:
    """Tests for distance_line_to_point."""
    
    def test_symmetry_with_point_to_line(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        line = LineString([(0.0, 0.0), (6.0, 0.0)])
        assert distance_line_to_point(line, point) == pytest.approx(distance_point_to_line(point, line))
    
    def test_horizontal_line_to_point(self) -> None:
        line = LineString([(0.0, 0.0), (5.0, 0.0)])
        point = Point2D(x=2.0, y=3.0)
        assert distance_line_to_point(line, point) == pytest.approx(3.0)


class TestDistancePointToPolygon:
    """Tests for distance_point_to_polygon."""
    
    def test_point_inside_polygon(self) -> None:
        point = Point2D(x=0.5, y=0.5)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert distance_point_to_polygon(point, polygon) == pytest.approx(0.0)
    
    def test_point_at_polygon_vertex(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert distance_point_to_polygon(point, polygon) == pytest.approx(0.0)
    
    def test_point_at_polygon_edge(self) -> None:
        point = Point2D(x=0.5, y=0.0)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert distance_point_to_polygon(point, polygon) == pytest.approx(0.0)
    
    def test_point_outside_polygon(self) -> None:
        point = Point2D(x=2.0, y=0.5)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert distance_point_to_polygon(point, polygon) == pytest.approx(1.0)
    
    def test_point_diagonally_outside(self) -> None:
        point = Point2D(x=2.0, y=2.0)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        expected = math.sqrt(2)
        assert distance_point_to_polygon(point, polygon) == pytest.approx(expected, rel=1e-9)
    
    def test_empty_polygon(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        polygon = Polygon()
        assert distance_point_to_polygon(point, polygon) == float('inf')
    
    def test_point_inside_complex_polygon(self) -> None:
        # L-shaped polygon
        polygon = Polygon([
            (0.0, 0.0), (2.0, 0.0), (2.0, 1.0),
            (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)
        ])
        point = Point2D(x=0.5, y=0.5)
        assert distance_point_to_polygon(point, polygon) == pytest.approx(0.0)


class TestDistancePolygonToPoint:
    """Tests for distance_polygon_to_point."""
    
    def test_symmetry_with_point_to_polygon(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        assert distance_polygon_to_point(polygon, point) == pytest.approx(distance_point_to_polygon(point, polygon))
    
    def test_polygon_to_outside_point(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        point = Point2D(x=3.0, y=3.0)
        expected = math.sqrt(8)
        assert distance_polygon_to_point(polygon, point) == pytest.approx(expected, rel=1e-9)


class TestDistancePointToBbox:
    """Tests for distance_point_to_bbox."""
    
    def test_point_inside_bbox(self) -> None:
        point = Point2D(x=5.0, y=5.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        assert distance_point_to_bbox(point, bbox) == pytest.approx(0.0)
    
    def test_point_at_bbox_edge(self) -> None:
        point = Point2D(x=0.0, y=5.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        assert distance_point_to_bbox(point, bbox) == pytest.approx(0.0)
    
    def test_point_at_bbox_corner(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        assert distance_point_to_bbox(point, bbox) == pytest.approx(0.0)
    
    def test_point_outside_right(self) -> None:
        point = Point2D(x=15.0, y=5.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        assert distance_point_to_bbox(point, bbox) == pytest.approx(5.0)
    
    def test_point_outside_above(self) -> None:
        point = Point2D(x=5.0, y=15.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        assert distance_point_to_bbox(point, bbox) == pytest.approx(5.0)
    
    def test_point_outside_diagonal(self) -> None:
        point = Point2D(x=13.0, y=14.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        expected = math.sqrt(9 + 16)
        assert distance_point_to_bbox(point, bbox) == pytest.approx(expected)
    
    def test_point_outside_bottom_left(self) -> None:
        point = Point2D(x=-3.0, y=-4.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        expected = math.sqrt(9 + 16)
        assert distance_point_to_bbox(point, bbox) == pytest.approx(expected)


class TestDistanceBboxToPoint:
    """Tests for distance_bbox_to_point."""
    
    def test_symmetry_with_point_to_bbox(self) -> None:
        point = Point2D(x=15.0, y=20.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        assert distance_bbox_to_point(bbox, point) == pytest.approx(distance_point_to_bbox(point, bbox))
    
    def test_bbox_to_outside_point(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=13.0, y=14.0)
        expected = math.sqrt(9 + 16)
        assert distance_bbox_to_point(bbox, point) == pytest.approx(expected)


class TestDistanceDispatcher:
    """Tests for the distance dispatcher function."""
    
    def test_point_to_point(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=3.0, y=4.0)
        assert distance(a, b) == pytest.approx(5.0)
    
    def test_point_to_line(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        line = LineString([(0.0, 0.0), (6.0, 0.0)])
        assert distance(point, line) == pytest.approx(4.0)
    
    def test_line_to_point(self) -> None:
        line = LineString([(0.0, 0.0), (6.0, 0.0)])
        point = Point2D(x=3.0, y=4.0)
        assert distance(line, point) == pytest.approx(4.0)
    
    def test_point_to_polygon(self) -> None:
        point = Point2D(x=2.0, y=0.5)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert distance(point, polygon) == pytest.approx(1.0)
    
    def test_polygon_to_point(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        point = Point2D(x=2.0, y=0.5)
        assert distance(polygon, point) == pytest.approx(1.0)
    
    def test_point_to_bbox(self) -> None:
        point = Point2D(x=15.0, y=5.0)
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        assert distance(point, bbox) == pytest.approx(5.0)
    
    def test_bbox_to_point(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=15.0, y=5.0)
        assert distance(bbox, point) == pytest.approx(5.0)
    
    def test_unsupported_types_raises(self) -> None:
        with pytest.raises(TypeError):
            distance("not_a_geometry", Point2D(x=0.0, y=0.0))  # type: ignore
    
    def test_unsupported_line_to_line_raises(self) -> None:
        line1 = LineString([(0.0, 0.0), (1.0, 1.0)])
        line2 = LineString([(2.0, 2.0), (3.0, 3.0)])
        with pytest.raises(TypeError):
            distance(line1, line2)
    
    def test_unsupported_polygon_to_polygon_raises(self) -> None:
        poly1 = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)])
        poly2 = Polygon([(2.0, 2.0), (3.0, 2.0), (3.0, 3.0)])
        with pytest.raises(TypeError):
            distance(poly1, poly2)
    
    def test_unsupported_bbox_to_bbox_raises(self) -> None:
        bbox1 = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        bbox2 = BoundingBox(min_x=2.0, min_y=2.0, max_x=3.0, max_y=3.0)
        with pytest.raises(TypeError):
            distance(bbox1, bbox2)
    
    def test_unsupported_line_to_polygon_raises(self) -> None:
        line = LineString([(0.0, 0.0), (1.0, 1.0)])
        polygon = Polygon([(2.0, 2.0), (3.0, 2.0), (3.0, 3.0)])
        with pytest.raises(TypeError):
            distance(line, polygon)