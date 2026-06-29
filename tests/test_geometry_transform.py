"""Unit tests for geometry transformation functions."""

from __future__ import annotations

import math

import pytest
from shapely.geometry import LineString, Polygon

from building_model_v2 import (
    BoundingBox,
    Point2D,
    mirror,
    offset,
    rotate,
    scale,
    translate,
)


class TestTranslate:
    """Tests for translate function."""
    
    def test_translate_point_positive(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        result = translate(point, 3.0, 4.0)
        assert result == Point2D(x=4.0, y=6.0)
    
    def test_translate_point_negative(self) -> None:
        point = Point2D(x=5.0, y=5.0)
        result = translate(point, -2.0, -3.0)
        assert result == Point2D(x=3.0, y=2.0)
    
    def test_translate_point_zero(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        result = translate(point, 0.0, 0.0)
        assert result == Point2D(x=1.0, y=2.0)
    
    def test_translate_bbox(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=2.0, max_y=3.0)
        result = translate(bbox, 1.0, 2.0)
        assert result == BoundingBox(min_x=1.0, min_y=2.0, max_x=3.0, max_y=5.0)
    
    def test_translate_linestring(self) -> None:
        line = LineString([(0.0, 0.0), (1.0, 1.0)])
        result = translate(line, 2.0, 3.0)
        coords = list(result.coords)
        assert coords[0] == pytest.approx((2.0, 3.0))
        assert coords[1] == pytest.approx((3.0, 4.0))
    
    def test_translate_polygon(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        result = translate(poly, 2.0, 3.0)
        coords = list(result.exterior.coords)
        assert coords[0] == pytest.approx((2.0, 3.0))
        assert coords[1] == pytest.approx((3.0, 3.0))
    
    def test_translate_empty_polygon(self) -> None:
        poly = Polygon()
        result = translate(poly, 1.0, 1.0)
        assert result.is_empty
    
    def test_translate_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            translate("not a geometry", 1.0, 1.0)
    
    def test_translate_preserves_original(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        translate(point, 10.0, 20.0)
        assert point == Point2D(x=1.0, y=2.0)


class TestRotate:
    """Tests for rotate function."""
    
    def test_rotate_point_90_degrees(self) -> None:
        point = Point2D(x=1.0, y=0.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 90.0, origin)
        assert result.x == pytest.approx(0.0, abs=1e-10)
        assert result.y == pytest.approx(1.0, abs=1e-10)
    
    def test_rotate_point_180_degrees(self) -> None:
        point = Point2D(x=1.0, y=0.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 180.0, origin)
        assert result.x == pytest.approx(-1.0, abs=1e-10)
        assert result.y == pytest.approx(0.0, abs=1e-10)
    
    def test_rotate_point_270_degrees(self) -> None:
        point = Point2D(x=1.0, y=0.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 270.0, origin)
        assert result.x == pytest.approx(0.0, abs=1e-10)
        assert result.y == pytest.approx(-1.0, abs=1e-10)
    
    def test_rotate_point_360_degrees(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 360.0, origin)
        assert result.x == pytest.approx(1.0, abs=1e-10)
        assert result.y == pytest.approx(2.0, abs=1e-10)
    
    def test_rotate_point_0_degrees(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 0.0, origin)
        assert result.x == pytest.approx(1.0, abs=1e-10)
        assert result.y == pytest.approx(2.0, abs=1e-10)
    
    def test_rotate_point_45_degrees(self) -> None:
        point = Point2D(x=1.0, y=0.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 45.0, origin)
        assert result.x == pytest.approx(math.sqrt(2) / 2, abs=1e-10)
        assert result.y == pytest.approx(math.sqrt(2) / 2, abs=1e-10)
    
    def test_rotate_point_default_origin(self) -> None:
        point = Point2D(x=2.0, y=0.0)
        # Default origin is the point itself, so rotation should not change it
        result = rotate(point, 90.0)
        assert result.x == pytest.approx(2.0, abs=1e-10)
        assert result.y == pytest.approx(0.0, abs=1e-10)
    
    def test_rotate_bbox(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=2.0, max_y=2.0)
        origin = Point2D(x=1.0, y=1.0)
        result = rotate(bbox, 90.0, origin)
        # After 90 degree rotation around center, should be same square
        assert result.min_x == pytest.approx(0.0, abs=1e-10)
        assert result.min_y == pytest.approx(0.0, abs=1e-10)
        assert result.max_x == pytest.approx(2.0, abs=1e-10)
        assert result.max_y == pytest.approx(2.0, abs=1e-10)
    
    def test_rotate_polygon(self) -> None:
        poly = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        origin = Point2D(x=1.0, y=1.0)
        result = rotate(poly, 90.0, origin)
        # Area should be preserved
        assert result.area == pytest.approx(4.0, abs=1e-10)
    
    def test_rotate_empty_polygon(self) -> None:
        poly = Polygon()
        result = rotate(poly, 90.0)
        assert result.is_empty
    
    def test_rotate_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            rotate("not a geometry", 90.0)
    
    def test_rotate_preserves_original(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        rotate(point, 90.0)
        assert point == Point2D(x=1.0, y=2.0)


class TestScale:
    """Tests for scale function."""
    
    def test_scale_point_uniform(self) -> None:
        point = Point2D(x=2.0, y=3.0)
        origin = Point2D(x=0.0, y=0.0)
        result = scale(point, 2.0, origin=origin)
        assert result == Point2D(x=4.0, y=6.0)
    
    def test_scale_point_non_uniform(self) -> None:
        point = Point2D(x=2.0, y=3.0)
        origin = Point2D(x=0.0, y=0.0)
        result = scale(point, 2.0, 3.0, origin=origin)
        assert result == Point2D(x=4.0, y=9.0)
    
    def test_scale_point_default_origin(self) -> None:
        point = Point2D(x=2.0, y=4.0)
        # Default origin is the point itself, so scaling should not change it
        result = scale(point, 2.0)
        assert result == Point2D(x=2.0, y=4.0)
    
    def test_scale_bbox_uniform(self) -> None:
        bbox = BoundingBox(min_x=1.0, min_y=1.0, max_x=3.0, max_y=3.0)
        origin = Point2D(x=2.0, y=2.0)
        result = scale(bbox, 2.0, origin=origin)
        assert result == BoundingBox(min_x=0.0, min_y=0.0, max_x=4.0, max_y=4.0)
    
    def test_scale_bbox_non_uniform(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=2.0, max_y=3.0)
        origin = Point2D(x=0.0, y=0.0)
        result = scale(bbox, 2.0, 3.0, origin=origin)
        assert result == BoundingBox(min_x=0.0, min_y=0.0, max_x=4.0, max_y=9.0)
    
    def test_scale_polygon_uniform(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        origin = Point2D(x=0.0, y=0.0)
        result = scale(poly, 2.0, origin=origin)
        assert result.area == pytest.approx(4.0, abs=1e-10)
    
    def test_scale_polygon_non_uniform(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        origin = Point2D(x=0.0, y=0.0)
        result = scale(poly, 2.0, 3.0, origin=origin)
        assert result.area == pytest.approx(6.0, abs=1e-10)
    
    def test_scale_empty_polygon(self) -> None:
        poly = Polygon()
        result = scale(poly, 2.0)
        assert result.is_empty
    
    def test_scale_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            scale("not a geometry", 2.0)
    
    def test_scale_preserves_original(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        scale(point, 5.0)
        assert point == Point2D(x=1.0, y=2.0)


class TestMirror:
    """Tests for mirror function."""
    
    def test_mirror_point_x_axis(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        result = mirror(point, "x")
        assert result == Point2D(x=3.0, y=-4.0)
    
    def test_mirror_point_y_axis(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        result = mirror(point, "y")
        assert result == Point2D(x=-3.0, y=4.0)
    
    def test_mirror_point_origin(self) -> None:
        point = Point2D(x=0.0, y=0.0)
        result = mirror(point, "x")
        assert result == Point2D(x=0.0, y=0.0)
    
    def test_mirror_bbox_x_axis(self) -> None:
        bbox = BoundingBox(min_x=1.0, min_y=2.0, max_x=3.0, max_y=4.0)
        result = mirror(bbox, "x")
        assert result == BoundingBox(min_x=1.0, min_y=-4.0, max_x=3.0, max_y=-2.0)
    
    def test_mirror_bbox_y_axis(self) -> None:
        bbox = BoundingBox(min_x=1.0, min_y=2.0, max_x=3.0, max_y=4.0)
        result = mirror(bbox, "y")
        assert result == BoundingBox(min_x=-3.0, min_y=2.0, max_x=-1.0, max_y=4.0)
    
    def test_mirror_polygon_x_axis(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        result = mirror(poly, "x")
        coords = list(result.exterior.coords)
        assert coords[0] == pytest.approx((0.0, 0.0))
        assert coords[2] == pytest.approx((1.0, -1.0))
    
    def test_mirror_polygon_y_axis(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        result = mirror(poly, "y")
        coords = list(result.exterior.coords)
        assert coords[0] == pytest.approx((0.0, 0.0))
        assert coords[1] == pytest.approx((-1.0, 0.0))
    
    def test_mirror_empty_polygon(self) -> None:
        poly = Polygon()
        result = mirror(poly, "x")
        assert result.is_empty
    
    def test_mirror_invalid_axis(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        with pytest.raises(ValueError):
            mirror(point, "z")
    
    def test_mirror_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            mirror("not a geometry", "x")
    
    def test_mirror_preserves_original(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        mirror(point, "x")
        assert point == Point2D(x=1.0, y=2.0)


class TestOffset:
    """Tests for offset function."""
    
    def test_offset_polygon_positive(self) -> None:
        poly = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        result = offset(poly, 0.5)
        # Outward offset should increase area
        assert result.area > poly.area
    
    def test_offset_polygon_negative(self) -> None:
        poly = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
        result = offset(poly, -0.5)
        # Inward offset should decrease area
        assert result.area < poly.area
    
    def test_offset_linestring(self) -> None:
        line = LineString([(0.0, 0.0), (2.0, 0.0)])
        result = offset(line, 0.5)
        # Offset of a line should create a polygon
        assert result.area > 0
    
    def test_offset_empty_polygon(self) -> None:
        poly = Polygon()
        result = offset(poly, 1.0)
        assert result.is_empty
    
    def test_offset_unsupported_type(self) -> None:
        with pytest.raises(TypeError):
            offset("not a geometry", 1.0)
    
    def test_offset_point_unsupported(self) -> None:
        with pytest.raises(TypeError):
            offset(Point2D(x=0.0, y=0.0), 1.0)
    
    def test_offset_preserves_original(self) -> None:
        poly = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        original_area = poly.area
        offset(poly, 1.0)
        assert poly.area == original_area


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_translate_floating_point(self) -> None:
        point = Point2D(x=0.1, y=0.2)
        result = translate(point, 0.3, 0.4)
        assert result.x == pytest.approx(0.4, abs=1e-10)
        assert result.y == pytest.approx(0.6, abs=1e-10)
    
    def test_rotate_arbitrary_angle(self) -> None:
        point = Point2D(x=1.0, y=0.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 30.0, origin)
        expected_x = math.cos(math.radians(30))
        expected_y = math.sin(math.radians(30))
        assert result.x == pytest.approx(expected_x, abs=1e-10)
        assert result.y == pytest.approx(expected_y, abs=1e-10)
    
    def test_scale_negative(self) -> None:
        point = Point2D(x=2.0, y=3.0)
        origin = Point2D(x=0.0, y=0.0)
        result = scale(point, -1.0, origin=origin)
        assert result == Point2D(x=-2.0, y=-3.0)
    
    def test_scale_zero(self) -> None:
        point = Point2D(x=2.0, y=3.0)
        origin = Point2D(x=0.0, y=0.0)
        result = scale(point, 0.0, origin=origin)
        assert result == Point2D(x=0.0, y=0.0)
    
    def test_double_mirror_x(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        result = mirror(mirror(point, "x"), "x")
        assert result == point
    
    def test_double_mirror_y(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        result = mirror(mirror(point, "y"), "y")
        assert result == point
    
    def test_rotate_360_preserves_position(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        origin = Point2D(x=0.0, y=0.0)
        result = rotate(point, 360.0, origin)
        assert result.x == pytest.approx(3.0, abs=1e-10)
        assert result.y == pytest.approx(4.0, abs=1e-10)
    
    def test_translate_negative_coordinates(self) -> None:
        point = Point2D(x=-1.0, y=-2.0)
        result = translate(point, -3.0, -4.0)
        assert result == Point2D(x=-4.0, y=-6.0)