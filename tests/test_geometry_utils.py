"""Tests for geometry_utils module."""

from __future__ import annotations

from shapely.geometry import GeometryCollection, LineString, MultiLineString

from geometry_utils import linear_length


class TestLinearLength:
    """Tests for the linear_length function."""

    def test_linestring_returns_length(self) -> None:
        """LineString returns its length."""
        line = LineString([(0, 0), (3, 4)])
        assert linear_length(line) == 5.0

    def test_multilinestring_returns_sum(self) -> None:
        """MultiLineString returns sum of all line lengths."""
        multi = MultiLineString([
            [(0, 0), (1, 0)],
            [(2, 0), (2, 1)],
            [(5, 5), (8, 9)],  # length = 5
        ])
        assert linear_length(multi) == 7.0

    def test_empty_linestring_returns_zero(self) -> None:
        """Empty LineString returns 0.0."""
        line = LineString()
        assert linear_length(line) == 0.0

    def test_empty_multilinestring_returns_zero(self) -> None:
        """Empty MultiLineString returns 0.0."""
        multi = MultiLineString([])
        assert linear_length(multi) == 0.0

    def test_geometry_collection_returns_sum(self) -> None:
        """GeometryCollection returns sum of component lengths."""
        line1 = LineString([(0, 0), (1, 0)])
        line2 = LineString([(2, 0), (2, 1)])
        collection = GeometryCollection([line1, line2])
        assert linear_length(collection) == 2.0

    def test_nested_geometry_collection(self) -> None:
        """Nested GeometryCollection is handled recursively."""
        inner = GeometryCollection([
            LineString([(0, 0), (1, 0)]),
            LineString([(2, 0), (3, 0)]),
        ])
        outer = GeometryCollection([
            inner,
            LineString([(5, 0), (5, 2)]),
        ])
        assert linear_length(outer) == 4.0

    def test_empty_geometry_collection_returns_zero(self) -> None:
        """Empty GeometryCollection returns 0.0."""
        collection = GeometryCollection([])
        assert linear_length(collection) == 0.0

    def test_returns_float_type(self) -> None:
        """Return type is always float."""
        line = LineString([(0, 0), (3, 4)])
        result = linear_length(line)
        assert isinstance(result, float)

    def test_zero_length_linestring(self) -> None:
        """Zero-length LineString returns 0.0."""
        line = LineString([(1, 1), (1, 1)])
        assert linear_length(line) == 0.0