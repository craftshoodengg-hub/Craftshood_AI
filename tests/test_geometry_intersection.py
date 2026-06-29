"""Unit tests for geometry intersection predicates."""

from __future__ import annotations

import pytest
from shapely.geometry import LineString, Polygon

from building_model_v2 import (
    BoundingBox,
    Point2D,
    contains,
    crosses,
    intersects,
    touches,
)


class TestIntersectsPointToPoint:
    """Tests for intersects_point_to_point."""
    
    def test_identical_points(self) -> None:
        a = Point2D(x=5.0, y=3.0)
        b = Point2D(x=5.0, y=3.0)
        assert intersects(a, b) is True
    
    def test_different_points(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=1.0, y=1.0)
        assert intersects(a, b) is False
    
    def test_same_x_different_y(self) -> None:
        a = Point2D(x=3.0, y=1.0)
        b = Point2D(x=3.0, y=2.0)
        assert intersects(a, b) is False
    
    def test_same_y_different_x(self) -> None:
        a = Point2D(x=1.0, y=3.0)
        b = Point2D(x=2.0, y=3.0)
        assert intersects(a, b) is False
    
    def test_origin_points(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=0.0, y=0.0)
        assert intersects(a, b) is True


class TestIntersectsPointToLine:
    """Tests for intersects_point_to_line."""
    
    def test_point_on_line(self) -> None:
        point = Point2D(x=2.0, y=0.0)
        line = LineString([(0.0, 0.0), (4.0, 0.0)])
        assert intersects(point, line) is True
    
    def test_point_off_line(self) -> None:
        point = Point2D(x=2.0, y=3.0)
        line = LineString([(0.0, 0.0), (4.0, 0.0)])
        assert intersects(point, line) is False
    
    def test_point_at_line_endpoint(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        line = LineString([(0.0, 0.0), (4.0, 0.0)])
        assert intersects(point, line) is True
    
    def test_point_on_diagonal_line(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        line = LineString([(0.0, 0.0), (2.0, 2.0)])
        assert intersects(point, line) is True
    
    def test_empty_line(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        line = LineString()
        assert intersects(point, line) is False


class TestIntersectsPointToPolygon:
    """Tests for intersects_point_to_polygon."""
    
    def test_point_inside_polygon(self) -> None:
        point = Point2D(x=0.5, y=0.5)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(point, polygon) is True
    
    def test_point_outside_polygon(self) -> None:
        point = Point2D(x=2.0, y=2.0)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(point, polygon) is False
    
    def test_point_on_polygon_edge(self) -> None:
        point = Point2D(x=0.5, y=0.0)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(point, polygon) is True
    
    def test_point_at_polygon_vertex(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(point, polygon) is True
    
    def test_empty_polygon(self) -> None:
        point = Point2D(x=1.0, y=1.0)
        polygon = Polygon()
        assert intersects(point, polygon) is False


class TestIntersectsLineToLine:
    """Tests for intersects_line_to_line."""
    
    def test_crossing_lines(self) -> None:
        a = LineString([(0.0, 0.0), (2.0, 2.0)])
        b = LineString([(0.0, 2.0), (2.0, 0.0)])
        assert intersects(a, b) is True
    
    def test_parallel_lines(self) -> None:
        a = LineString([(0.0, 0.0), (2.0, 0.0)])
        b = LineString([(0.0, 1.0), (2.0, 1.0)])
        assert intersects(a, b) is False
    
    def test_shared_endpoint(self) -> None:
        a = LineString([(0.0, 0.0), (1.0, 0.0)])
        b = LineString([(1.0, 0.0), (1.0, 1.0)])
        assert intersects(a, b) is True
    
    def test_collinear_overlapping(self) -> None:
        a = LineString([(0.0, 0.0), (2.0, 0.0)])
        b = LineString([(1.0, 0.0), (3.0, 0.0)])
        assert intersects(a, b) is True
    
    def test_empty_line(self) -> None:
        a = LineString([(0.0, 0.0), (1.0, 1.0)])
        b = LineString()
        assert intersects(a, b) is False


class TestIntersectsLineToPolygon:
    """Tests for intersects_line_to_polygon."""
    
    def test_line_crossing_polygon(self) -> None:
        line = LineString([(-1.0, 0.5), (2.0, 0.5)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(line, polygon) is True
    
    def test_line_outside_polygon(self) -> None:
        line = LineString([(2.0, 2.0), (3.0, 3.0)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(line, polygon) is False
    
    def test_line_touching_polygon_edge(self) -> None:
        line = LineString([(0.0, 0.0), (0.0, 1.0)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(line, polygon) is True
    
    def test_line_inside_polygon(self) -> None:
        line = LineString([(0.25, 0.25), (0.75, 0.75)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert intersects(line, polygon) is True
    
    def test_empty_polygon(self) -> None:
        line = LineString([(0.0, 0.0), (1.0, 1.0)])
        polygon = Polygon()
        assert intersects(line, polygon) is False


class TestIntersectsPolygonToPolygon:
    """Tests for intersects_polygon_to_polygon."""
    
    def test_overlapping_polygons(self) -> None:
        a = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        b = Polygon([(1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)])
        assert intersects(a, b) is True
    
    def test_disjoint_polygons(self) -> None:
        a = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        b = Polygon([(2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0)])
        assert intersects(a, b) is False
    
    def test_contained_polygon(self) -> None:
        a = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
        b = Polygon([(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)])
        assert intersects(a, b) is True
    
    def test_touching_edges(self) -> None:
        a = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        b = Polygon([(1.0, 0.0), (2.0, 0.0), (2.0, 1.0), (1.0, 1.0)])
        assert intersects(a, b) is True
    
    def test_empty_polygon(self) -> None:
        a = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        b = Polygon()
        assert intersects(a, b) is False


class TestIntersectsBboxToPoint:
    """Tests for intersects_bbox_to_point."""
    
    def test_point_inside_bbox(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=5.0, y=5.0)
        assert intersects(bbox, point) is True
    
    def test_point_outside_bbox(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=15.0, y=5.0)
        assert intersects(bbox, point) is False
    
    def test_point_on_edge(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=0.0, y=5.0)
        assert intersects(bbox, point) is True
    
    def test_point_at_corner(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=10.0, y=10.0)
        assert intersects(bbox, point) is True


class TestIntersectsBboxToBbox:
    """Tests for intersects_bbox_to_bbox."""
    
    def test_overlapping_boxes(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        b = BoundingBox(min_x=3.0, min_y=3.0, max_x=8.0, max_y=8.0)
        assert intersects(a, b) is True
    
    def test_disjoint_boxes(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        b = BoundingBox(min_x=2.0, min_y=2.0, max_x=3.0, max_y=3.0)
        assert intersects(a, b) is False
    
    def test_contained_box(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        b = BoundingBox(min_x=2.0, min_y=2.0, max_x=5.0, max_y=5.0)
        assert intersects(a, b) is True
    
    def test_touching_edges(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        b = BoundingBox(min_x=1.0, min_y=0.0, max_x=2.0, max_y=1.0)
        assert intersects(a, b) is True
    
    def test_identical_boxes(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        b = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        assert intersects(a, b) is True


class TestContains:
    """Tests for contains dispatcher."""
    
    def test_polygon_contains_point(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
        point = Point2D(x=2.0, y=2.0)
        assert contains(polygon, point) is True
    
    def test_polygon_does_not_contain_point(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        point = Point2D(x=5.0, y=5.0)
        assert contains(polygon, point) is False
    
    def test_bbox_contains_point(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=5.0, y=5.0)
        assert contains(bbox, point) is True
    
    def test_bbox_does_not_contain_point(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        point = Point2D(x=15.0, y=5.0)
        assert contains(bbox, point) is False
    
    def test_bbox_contains_bbox(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        b = BoundingBox(min_x=2.0, min_y=2.0, max_x=5.0, max_y=5.0)
        assert contains(a, b) is True
    
    def test_bbox_does_not_contain_bbox(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        b = BoundingBox(min_x=2.0, min_y=2.0, max_x=8.0, max_y=8.0)
        assert contains(a, b) is False
    
    def test_polygon_contains_polygon(self) -> None:
        a = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
        b = Polygon([(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)])
        assert contains(a, b) is True
    
    def test_polygon_does_not_contain_polygon(self) -> None:
        a = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        b = Polygon([(2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0)])
        assert contains(a, b) is False
    
    def test_point_cannot_contain_polygon(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert contains(point, polygon) is False
    
    def test_point_contains_identical_point(self) -> None:
        a = Point2D(x=3.0, y=4.0)
        b = Point2D(x=3.0, y=4.0)
        assert contains(a, b) is True
    
    def test_point_does_not_contain_different_point(self) -> None:
        a = Point2D(x=3.0, y=4.0)
        b = Point2D(x=3.0, y=5.0)
        assert contains(a, b) is False


class TestTouches:
    """Tests for touches dispatcher."""
    
    def test_identical_points_touch(self) -> None:
        a = Point2D(x=5.0, y=3.0)
        b = Point2D(x=5.0, y=3.0)
        assert touches(a, b) is True
    
    def test_different_points_do_not_touch(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=1.0, y=1.0)
        assert touches(a, b) is False
    
    def test_polygons_touching(self) -> None:
        a = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        b = Polygon([(1.0, 0.0), (2.0, 0.0), (2.0, 1.0), (1.0, 1.0)])
        assert touches(a, b) is True
    
    def test_polygons_overlapping_not_touching(self) -> None:
        a = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        b = Polygon([(1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)])
        assert touches(a, b) is False
    
    def test_bbox_touching_bbox(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        b = BoundingBox(min_x=1.0, min_y=0.0, max_x=2.0, max_y=1.0)
        assert touches(a, b) is True
    
    def test_bbox_overlapping_not_touching(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=2.0, max_y=2.0)
        b = BoundingBox(min_x=1.0, min_y=1.0, max_x=3.0, max_y=3.0)
        assert touches(a, b) is False
    
    def test_line_touches_polygon(self) -> None:
        line = LineString([(0.0, 0.0), (0.0, 1.0)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert touches(line, polygon) is True
    
    def test_line_crosses_polygon_not_touches(self) -> None:
        line = LineString([(-1.0, 0.5), (2.0, 0.5)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert touches(line, polygon) is False


class TestCrosses:
    """Tests for crosses dispatcher."""
    
    def test_lines_cross(self) -> None:
        a = LineString([(0.0, 0.0), (2.0, 2.0)])
        b = LineString([(0.0, 2.0), (2.0, 0.0)])
        assert crosses(a, b) is True
    
    def test_parallel_lines_do_not_cross(self) -> None:
        a = LineString([(0.0, 0.0), (2.0, 0.0)])
        b = LineString([(0.0, 1.0), (2.0, 1.0)])
        assert crosses(a, b) is False
    
    def test_lines_touching_do_not_cross(self) -> None:
        a = LineString([(0.0, 0.0), (1.0, 0.0)])
        b = LineString([(1.0, 0.0), (1.0, 1.0)])
        assert crosses(a, b) is False
    
    def test_polygons_cross(self) -> None:
        a = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        b = Polygon([(1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)])
        assert crosses(a, b) is True
    
    def test_polygons_contained_do_not_cross(self) -> None:
        a = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
        b = Polygon([(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)])
        assert crosses(a, b) is False
    
    def test_points_do_not_cross(self) -> None:
        a = Point2D(x=0.0, y=0.0)
        b = Point2D(x=1.0, y=1.0)
        assert crosses(a, b) is False
    
    def test_bbox_do_not_cross(self) -> None:
        a = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        b = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        assert crosses(a, b) is False
    
    def test_line_crosses_polygon(self) -> None:
        line = LineString([(-1.0, 0.5), (2.0, 0.5)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert crosses(line, polygon) is True
    
    def test_line_touches_polygon_does_not_cross(self) -> None:
        line = LineString([(0.0, 0.0), (0.0, 1.0)])
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert crosses(line, polygon) is False


class TestUnsupportedTypes:
    """Tests for unsupported type combinations."""
    
    def test_unsupported_line_to_bbox_raises(self) -> None:
        line = LineString([(0.0, 0.0), (1.0, 1.0)])
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        with pytest.raises(TypeError):
            intersects(line, bbox)
    
    def test_unsupported_polygon_to_bbox_raises(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
        with pytest.raises(TypeError):
            intersects(polygon, bbox)
    
    def test_unsupported_string_raises(self) -> None:
        with pytest.raises(TypeError):
            intersects("not_a_geometry", Point2D(x=0.0, y=0.0))  # type: ignore
    
    def test_unsupported_contains_raises(self) -> None:
        with pytest.raises(TypeError):
            contains("not_a_geometry", Point2D(x=0.0, y=0.0))  # type: ignore
    
    def test_unsupported_touches_raises(self) -> None:
        with pytest.raises(TypeError):
            touches("not_a_geometry", Point2D(x=0.0, y=0.0))  # type: ignore
    
    def test_unsupported_crosses_raises(self) -> None:
        with pytest.raises(TypeError):
            crosses("not_a_geometry", Point2D(x=0.0, y=0.0))  # type: ignore