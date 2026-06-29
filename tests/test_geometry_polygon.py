"""Unit tests for polygon geometry utilities."""

from __future__ import annotations

import math

import pytest
from shapely.geometry import Polygon

from building_model_v2 import (
    BoundingBox,
    Point2D,
    area,
    aspect_ratio,
    bounding_box,
    bounds,
    compactness,
    is_clockwise,
    is_counter_clockwise,
    is_convex,
    is_rectangular,
    is_square,
    is_triangle,
    orientation,
    perimeter,
    vertex_count,
)


class TestArea:
    """Tests for area function."""
    
    def test_unit_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert area(polygon) == pytest.approx(1.0)
    
    def test_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)])
        assert area(polygon) == pytest.approx(12.0)
    
    def test_triangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (2.0, 3.0)])
        assert area(polygon) == pytest.approx(6.0)
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert area(polygon) == 0.0
    
    def test_large_polygon(self) -> None:
        polygon = Polygon([(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)])
        assert area(polygon) == pytest.approx(10000.0)
    
    def test_negative_coordinates(self) -> None:
        polygon = Polygon([(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0)])
        assert area(polygon) == pytest.approx(16.0)
    
    def test_concave_polygon(self) -> None:
        # L-shaped polygon
        polygon = Polygon([
            (0.0, 0.0), (4.0, 0.0), (4.0, 2.0),
            (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)
        ])
        assert area(polygon) == pytest.approx(12.0)


class TestPerimeter:
    """Tests for perimeter function."""
    
    def test_unit_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert perimeter(polygon) == pytest.approx(4.0)
    
    def test_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)])
        assert perimeter(polygon) == pytest.approx(14.0)
    
    def test_triangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (2.0, 3.0)])
        expected = 4.0 + 2 * math.sqrt(4 + 9)
        assert perimeter(polygon) == pytest.approx(expected, rel=1e-9)
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert perimeter(polygon) == 0.0


class TestCentroid:
    """Tests for centroid function (via bounding_box)."""
    
    def test_centroid_via_bounding_box(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
        bbox = bounding_box(polygon)
        assert bbox is not None
        assert bbox.center == Point2D(x=2.0, y=2.0)
    
    def test_centroid_offset(self) -> None:
        polygon = Polygon([(1.0, 1.0), (5.0, 1.0), (5.0, 3.0), (1.0, 3.0)])
        bbox = bounding_box(polygon)
        assert bbox is not None
        assert bbox.center == Point2D(x=3.0, y=2.0)
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert bounding_box(polygon) is None


class TestBoundingBox:
    """Tests for bounding_box function."""
    
    def test_unit_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        bbox = bounding_box(polygon)
        assert bbox == BoundingBox(min_x=0.0, min_y=0.0, max_x=1.0, max_y=1.0)
    
    def test_offset_rectangle(self) -> None:
        polygon = Polygon([(2.0, 3.0), (6.0, 3.0), (6.0, 7.0), (2.0, 7.0)])
        bbox = bounding_box(polygon)
        assert bbox == BoundingBox(min_x=2.0, min_y=3.0, max_x=6.0, max_y=7.0)
    
    def test_negative_coordinates(self) -> None:
        polygon = Polygon([(-3.0, -2.0), (1.0, -2.0), (1.0, 4.0), (-3.0, 4.0)])
        bbox = bounding_box(polygon)
        assert bbox == BoundingBox(min_x=-3.0, min_y=-2.0, max_x=1.0, max_y=4.0)
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert bounding_box(polygon) is None
    
    def test_triangle_bbox(self) -> None:
        polygon = Polygon([(1.0, 2.0), (5.0, 2.0), (3.0, 6.0)])
        bbox = bounding_box(polygon)
        assert bbox == BoundingBox(min_x=1.0, min_y=2.0, max_x=5.0, max_y=6.0)


class TestBounds:
    """Tests for bounds function."""
    
    def test_unit_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert bounds(polygon) == (0.0, 0.0, 1.0, 1.0)
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert bounds(polygon) == (0.0, 0.0, 0.0, 0.0)
    
    def test_offset_polygon(self) -> None:
        polygon = Polygon([(2.0, 3.0), (5.0, 3.0), (5.0, 7.0), (2.0, 7.0)])
        assert bounds(polygon) == (2.0, 3.0, 5.0, 7.0)


class TestOrientation:
    """Tests for orientation function."""
    
    def test_horizontal_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (0.0, 2.0)])
        # Horizontal rectangle should have orientation near 0 or 90 degrees
        orient = orientation(polygon)
        assert orient == pytest.approx(0.0) or orient == pytest.approx(90.0)
    
    def test_vertical_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 4.0), (0.0, 4.0)])
        # Vertical rectangle should have orientation near 0 or 90 degrees
        orient = orientation(polygon)
        assert orient == pytest.approx(0.0) or orient == pytest.approx(90.0)
    
    def test_square(self) -> None:
        # For a square, orientation is ambiguous - just verify it returns a valid value
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        orient = orientation(polygon)
        assert 0.0 <= orient <= 180.0
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert orientation(polygon) == 0.0
    
    def test_rotated_rectangle(self) -> None:
        # 45-degree rotated square - orientation should be around 45 or 135 degrees
        polygon = Polygon([
            (1.0, 0.0), (2.0, 1.0), (1.0, 2.0), (0.0, 1.0)
        ])
        orient = orientation(polygon)
        # The orientation could be 45 or 135 depending on which edge is longest
        assert abs(orient - 45.0) <= 1.0 or abs(orient - 135.0) <= 1.0


class TestAspectRatio:
    """Tests for aspect_ratio function."""
    
    def test_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        assert aspect_ratio(polygon) == pytest.approx(1.0)
    
    def test_horizontal_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (0.0, 2.0)])
        assert aspect_ratio(polygon) == pytest.approx(0.5)
    
    def test_vertical_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 4.0), (0.0, 4.0)])
        assert aspect_ratio(polygon) == pytest.approx(0.5)
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert aspect_ratio(polygon) == 0.0
    
    def test_wide_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (10.0, 0.0), (10.0, 1.0), (0.0, 1.0)])
        assert aspect_ratio(polygon) == pytest.approx(0.1)


class TestCompactness:
    """Tests for compactness function."""
    
    def test_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        expected = math.pi / 4  # ≈ 0.785
        assert compactness(polygon) == pytest.approx(expected, rel=1e-9)
    
    def test_rectangle_less_compact(self) -> None:
        square = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        rectangle = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 1.0), (0.0, 1.0)])
        assert compactness(rectangle) < compactness(square)
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert compactness(polygon) == 0.0
    
    def test_degenerate_polygon(self) -> None:
        # Line-like polygon (zero area)
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)])
        assert compactness(polygon) == 0.0


class TestIsClockwise:
    """Tests for is_clockwise function."""
    
    def test_clockwise_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)])
        assert is_clockwise(polygon) is True
    
    def test_counter_clockwise_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert is_clockwise(polygon) is False
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert is_clockwise(polygon) is False


class TestIsCounterClockwise:
    """Tests for is_counter_clockwise function."""
    
    def test_counter_clockwise(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert is_counter_clockwise(polygon) is True
    
    def test_clockwise_not(self) -> None:
        polygon = Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)])
        assert is_counter_clockwise(polygon) is False
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert is_counter_clockwise(polygon) is False


class TestIsConvex:
    """Tests for is_convex function."""
    
    def test_convex_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert is_convex(polygon) is True
    
    def test_convex_triangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)])
        assert is_convex(polygon) is True
    
    def test_concave_l_shape(self) -> None:
        polygon = Polygon([
            (0.0, 0.0), (2.0, 0.0), (2.0, 1.0),
            (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)
        ])
        assert is_convex(polygon) is False
    
    def test_convex_pentagon(self) -> None:
        polygon = Polygon([
            (1.0, 0.0), (2.0, 1.0), (1.5, 2.0),
            (0.5, 2.0), (0.0, 1.0)
        ])
        assert is_convex(polygon) is True
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert is_convex(polygon) is False
    
    def test_degenerate_polygon(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)])
        assert is_convex(polygon) is False


class TestIsRectangular:
    """Tests for is_rectangular function."""
    
    def test_perfect_rectangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)])
        assert is_rectangular(polygon) is True
    
    def test_square_is_rectangular(self) -> None:
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        assert is_rectangular(polygon) is True
    
    def test_triangle_not_rectangular(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (2.0, 3.0)])
        assert is_rectangular(polygon) is False
    
    def test_l_shape_not_rectangular(self) -> None:
        polygon = Polygon([
            (0.0, 0.0), (2.0, 0.0), (2.0, 1.0),
            (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)
        ])
        assert is_rectangular(polygon) is False
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert is_rectangular(polygon) is False
    
    def test_degenerate_polygon(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)])
        assert is_rectangular(polygon) is False


class TestIsSquare:
    """Tests for is_square function."""
    
    def test_perfect_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)])
        assert is_square(polygon) is True
    
    def test_rectangle_not_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (0.0, 2.0)])
        assert is_square(polygon) is False
    
    def test_triangle_not_square(self) -> None:
        polygon = Polygon([(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)])
        assert is_square(polygon) is False
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert is_square(polygon) is False


class TestVertexCount:
    """Tests for vertex_count function."""
    
    def test_triangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)])
        assert vertex_count(polygon) == 3
    
    def test_quadrilateral(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert vertex_count(polygon) == 4
    
    def test_pentagon(self) -> None:
        polygon = Polygon([
            (1.0, 0.0), (2.0, 1.0), (1.5, 2.0), (0.5, 2.0), (0.0, 1.0)
        ])
        assert vertex_count(polygon) == 5
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert vertex_count(polygon) == 0


class TestIsTriangle:
    """Tests for is_triangle function."""
    
    def test_triangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (4.0, 0.0), (2.0, 3.0)])
        assert is_triangle(polygon) is True
    
    def test_quadrilateral_not_triangle(self) -> None:
        polygon = Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        assert is_triangle(polygon) is False
    
    def test_empty_polygon(self) -> None:
        polygon = Polygon()
        assert is_triangle(polygon) is False


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_floating_point_precision(self) -> None:
        polygon = Polygon([
            (0.1, 0.1), (1.1, 0.1), (1.1, 1.1), (0.1, 1.1)
        ])
        assert area(polygon) == pytest.approx(1.0, rel=1e-9)
    
    def test_very_small_polygon(self) -> None:
        polygon = Polygon([
            (0.0, 0.0), (0.001, 0.0), (0.001, 0.001), (0.0, 0.001)
        ])
        assert area(polygon) == pytest.approx(1e-6, rel=1e-6)
    
    def test_very_large_polygon(self) -> None:
        polygon = Polygon([
            (0.0, 0.0), (10000.0, 0.0), (10000.0, 10000.0), (0.0, 10000.0)
        ])
        assert area(polygon) == pytest.approx(1e8, rel=1e-9)
    
    def test_irregular_polygon(self) -> None:
        polygon = Polygon([
            (0.0, 0.0), (3.0, 1.0), (2.0, 3.0), (0.0, 2.0)
        ])
        assert area(polygon) > 0
        assert perimeter(polygon) > 0
        assert vertex_count(polygon) == 4
    
    def test_compactness_range(self) -> None:
        """Compactness should be between 0 and 1."""
        polygons = [
            Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]),
            Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 1.0), (0.0, 1.0)]),
            Polygon([(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)]),
        ]
        for poly in polygons:
            c = compactness(poly)
            assert 0.0 <= c <= 1.0
    
    def test_aspect_ratio_range(self) -> None:
        """Aspect ratio should be between 0 and 1."""
        polygons = [
            Polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]),
            Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 1.0), (0.0, 1.0)]),
            Polygon([(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)]),
        ]
        for poly in polygons:
            ar = aspect_ratio(poly)
            assert 0.0 <= ar <= 1.0