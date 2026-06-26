"""Unit tests for Building Model v2 core types and base classes."""

from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from building_model_v2 import (
    BaseEntity,
    BoundingBox,
    GeometryMixin,
    Point2D,
    ValidationIssue,
    ValidationReport,
)
from building_model_v2.base import current_timestamp, generate_uuid


# ==================== Point2D Tests ====================

class TestPoint2D:
    """Tests for Point2D value object."""
    
    def test_create_with_coordinates(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        assert point.x == 1.0
        assert point.y == 2.0
    
    def test_to_array(self) -> None:
        point = Point2D(x=3.0, y=4.0)
        array = point.to_array()
        assert array[0] == 3.0
        assert array[1] == 4.0
    
    def test_to_dict(self) -> None:
        point = Point2D(x=5.0, y=6.0)
        result = point.to_dict()
        assert result == {"x": 5.0, "y": 6.0}
    
    def test_from_dict(self) -> None:
        payload = {"x": 7.0, "y": 8.0}
        point = Point2D.from_dict(payload)
        assert point.x == 7.0
        assert point.y == 8.0
    
    def test_distance_to(self) -> None:
        p1 = Point2D(x=0.0, y=0.0)
        p2 = Point2D(x=3.0, y=4.0)
        assert p1.distance_to(p2) == pytest.approx(5.0)
    
    def test_distance_to_same_point(self) -> None:
        p1 = Point2D(x=1.0, y=1.0)
        assert p1.distance_to(p1) == pytest.approx(0.0)
    
    def test_immutability(self) -> None:
        point = Point2D(x=1.0, y=2.0)
        with pytest.raises(AttributeError):
            point.x = 10.0  # type: ignore


# ==================== BoundingBox Tests ====================

class TestBoundingBox:
    """Tests for BoundingBox value object."""
    
    def test_create_with_coordinates(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        assert bbox.min_x == 0.0
        assert bbox.min_y == 0.0
        assert bbox.max_x == 10.0
        assert bbox.max_y == 5.0
    
    def test_width(self) -> None:
        bbox = BoundingBox(min_x=2.0, min_y=0.0, max_x=8.0, max_y=5.0)
        assert bbox.width == pytest.approx(6.0)
    
    def test_height(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=3.0, max_x=10.0, max_y=7.0)
        assert bbox.height == pytest.approx(4.0)
    
    def test_area(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        assert bbox.area == pytest.approx(50.0)
    
    def test_center(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        center = bbox.center
        assert center.x == pytest.approx(5.0)
        assert center.y == pytest.approx(5.0)
    
    def test_to_shapely(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=10.0)
        polygon = bbox.to_shapely()
        assert polygon.area == pytest.approx(100.0)
    
    def test_to_dict(self) -> None:
        bbox = BoundingBox(min_x=1.0, min_y=2.0, max_x=3.0, max_y=4.0)
        result = bbox.to_dict()
        assert result == {"min_x": 1.0, "min_y": 2.0, "max_x": 3.0, "max_y": 4.0}
    
    def test_from_dict(self) -> None:
        payload = {"min_x": 1.0, "min_y": 2.0, "max_x": 3.0, "max_y": 4.0}
        bbox = BoundingBox.from_dict(payload)
        assert bbox.min_x == 1.0
        assert bbox.min_y == 2.0
        assert bbox.max_x == 3.0
        assert bbox.max_y == 4.0
    
    def test_from_points(self) -> None:
        points = [Point2D(x=0.0, y=0.0), Point2D(x=10.0, y=5.0), Point2D(x=3.0, y=8.0)]
        bbox = BoundingBox.from_points(points)
        assert bbox.min_x == pytest.approx(0.0)
        assert bbox.min_y == pytest.approx(0.0)
        assert bbox.max_x == pytest.approx(10.0)
        assert bbox.max_y == pytest.approx(8.0)
    
    def test_from_points_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            BoundingBox.from_points([])
    
    def test_from_polygon(self) -> None:
        polygon = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        bbox = BoundingBox.from_polygon(polygon)
        assert bbox.min_x == pytest.approx(0.0)
        assert bbox.min_y == pytest.approx(0.0)
        assert bbox.max_x == pytest.approx(10.0)
        assert bbox.max_y == pytest.approx(5.0)
    
    def test_immutability(self) -> None:
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        with pytest.raises(AttributeError):
            bbox.min_x = 10.0  # type: ignore


# ==================== GeometryMixin Tests ====================

class TestGeometryMixin:
    """Tests for GeometryMixin."""
    
    def _create_mixin(self, coords: list[tuple[float, float]]) -> GeometryMixin:
        polygon = Polygon(coords)
        return GeometryMixin(polygon=polygon)
    
    def test_bounding_box(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 5), (0, 5)])
        bbox = mixin.bounding_box
        assert bbox.width == pytest.approx(10.0)
        assert bbox.height == pytest.approx(5.0)
    
    def test_area(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 5), (0, 5)])
        assert mixin.area == pytest.approx(50.0)
    
    def test_perimeter(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 5), (0, 5)])
        assert mixin.perimeter == pytest.approx(30.0)
    
    def test_centroid(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 10), (0, 10)])
        centroid = mixin.centroid
        assert centroid.x == pytest.approx(5.0)
        assert centroid.y == pytest.approx(5.0)
    
    def test_orientation_square(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 10), (0, 10)])
        orientation = mixin.orientation_degrees
        assert orientation == pytest.approx(0.0) or orientation == pytest.approx(90.0)
    
    def test_is_convex_true(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 10), (0, 10)])
        assert mixin.is_convex is True
    
    def test_is_convex_false(self) -> None:
        # L-shaped polygon (concave)
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 5), (5, 5), (5, 10), (0, 10)])
        assert mixin.is_convex is False
    
    def test_solidity_convex(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 10), (0, 10)])
        assert mixin.solidity == pytest.approx(1.0)
    
    def test_solidity_non_convex(self) -> None:
        # L-shaped polygon
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 5), (5, 5), (5, 10), (0, 10)])
        assert mixin.solidity < 1.0
    
    def test_convex_hull_area(self) -> None:
        mixin = self._create_mixin([(0, 0), (10, 0), (10, 5), (0, 5)])
        assert mixin.convex_hull_area == pytest.approx(50.0)


# ==================== BaseEntity Tests ====================

class TestBaseEntity:
    """Tests for BaseEntity abstract class."""
    
    def _create_entity(self, **kwargs: Any) -> BaseEntity:
        """Create a concrete subclass for testing."""
        entity = ConcreteTestEntity(**kwargs)
        return entity
    
    def test_generate_uuid(self) -> None:
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2
        assert len(uuid1) == 36  # Standard UUID format
    
    def test_current_timestamp(self) -> None:
        ts = current_timestamp()
        assert "T" in ts  # ISO 8601 format
    
    def test_default_id(self) -> None:
        entity = self._create_entity()
        assert len(entity.id) == 36
    
    def test_custom_id(self) -> None:
        entity = self._create_entity(id="custom-id")
        assert entity.id == "custom-id"
    
    def test_timestamps(self) -> None:
        entity = self._create_entity()
        assert entity.created_at is not None
        assert entity.updated_at is not None
    
    def test_metadata_default(self) -> None:
        entity = self._create_entity()
        assert entity.metadata == {}
    
    def test_metadata_custom(self) -> None:
        entity = self._create_entity(metadata={"key": "value"})
        assert entity.metadata == {"key": "value"}
    
    def test_to_dict(self) -> None:
        entity = self._create_entity(id="test-id")
        result = entity.to_dict()
        assert result["id"] == "test-id"
        assert "created_at" in result
        assert "updated_at" in result
        assert "metadata" in result
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "test-id",
            "created_at": "2026-06-26T12:00:00+00:00",
            "updated_at": "2026-06-26T12:00:00+00:00",
            "metadata": {"key": "value"},
        }
        entity = ConcreteTestEntity.from_dict(payload)
        assert entity.id == "test-id"
        assert entity.metadata == {"key": "value"}
    
    def test_from_dict_defaults(self) -> None:
        entity = ConcreteTestEntity.from_dict({})
        assert len(entity.id) == 36
        assert entity.metadata == {}
    
    def test_immutability(self) -> None:
        entity = self._create_entity()
        with pytest.raises(AttributeError):
            entity.id = "new-id"  # type: ignore


class ConcreteTestEntity(BaseEntity):
    """Concrete entity for testing BaseEntity."""
    
    def __init__(self, **kwargs: Any) -> None:
        object.__setattr__(self, 'id', kwargs.get('id', generate_uuid()))
        object.__setattr__(self, 'created_at', kwargs.get('created_at', current_timestamp()))
        object.__setattr__(self, 'updated_at', kwargs.get('updated_at', current_timestamp()))
        object.__setattr__(self, 'metadata', kwargs.get('metadata', {}))


# ==================== ValidationIssue Tests ====================

class TestValidationIssue:
    """Tests for ValidationIssue."""
    
    def test_create_with_defaults(self) -> None:
        issue = ValidationIssue(code="test_code", message="Test message")
        assert issue.code == "test_code"
        assert issue.message == "Test message"
        assert issue.severity == "error"
    
    def test_create_with_severity(self) -> None:
        issue = ValidationIssue(code="test_code", message="Test message", severity="warning")
        assert issue.severity == "warning"
    
    def test_to_dict(self) -> None:
        issue = ValidationIssue(code="test_code", message="Test message", severity="warning")
        result = issue.to_dict()
        assert result == {
            "code": "test_code",
            "message": "Test message",
            "severity": "warning",
        }
    
    def test_from_dict(self) -> None:
        payload = {"code": "test_code", "message": "Test message", "severity": "warning"}
        issue = ValidationIssue.from_dict(payload)
        assert issue.code == "test_code"
        assert issue.message == "Test message"
        assert issue.severity == "warning"
    
    def test_from_dict_default_severity(self) -> None:
        payload = {"code": "test_code", "message": "Test message"}
        issue = ValidationIssue.from_dict(payload)
        assert issue.severity == "error"
    
    def test_immutability(self) -> None:
        issue = ValidationIssue(code="test_code", message="Test message")
        with pytest.raises(AttributeError):
            issue.code = "new_code"  # type: ignore


# ==================== ValidationReport Tests ====================

class TestValidationReport:
    """Tests for ValidationReport."""
    
    def test_create_valid(self) -> None:
        report = ValidationReport(valid=True)
        assert report.valid is True
        assert report.issues == ()
    
    def test_create_invalid(self) -> None:
        issue = ValidationIssue(code="test", message="Test")
        report = ValidationReport(valid=False, issues=(issue,))
        assert report.valid is False
        assert len(report.issues) == 1
    
    def test_to_dict(self) -> None:
        issue = ValidationIssue(code="test", message="Test")
        report = ValidationReport(valid=False, issues=(issue,))
        result = report.to_dict()
        assert result["valid"] is False
        assert len(result["issues"]) == 1
    
    def test_from_dict(self) -> None:
        payload = {
            "valid": False,
            "issues": [{"code": "test", "message": "Test", "severity": "error"}],
        }
        report = ValidationReport.from_dict(payload)
        assert report.valid is False
        assert len(report.issues) == 1
    
    def test_create_valid_factory(self) -> None:
        report = ValidationReport.create_valid()
        assert report.valid is True
        assert report.issues == ()
    
    def test_immutability(self) -> None:
        report = ValidationReport(valid=True)
        with pytest.raises(AttributeError):
            report.valid = False  # type: ignore


# ==================== Enum Tests ====================

class TestEnums:
    """Tests for enumeration types."""
    
    def test_room_type_values(self) -> None:
        from building_model_v2 import RoomType
        assert RoomType.LIVING == "Living"
        assert RoomType.BEDROOM == "Bedroom"
        assert RoomType.KITCHEN == "Kitchen"
        assert RoomType.UNKNOWN == "Unknown"
    
    def test_wall_type_values(self) -> None:
        from building_model_v2 import WallType
        assert WallType.EXTERIOR == "Exterior"
        assert WallType.INTERIOR == "Interior"
        assert WallType.UNKNOWN == "Unknown"
    
    def test_orientation_values(self) -> None:
        from building_model_v2 import Orientation
        assert Orientation.NORTH == "North"
        assert Orientation.NORTHEAST == "Northeast"
        assert Orientation.CENTER == "Center"
        assert Orientation.UNKNOWN == "Unknown"
    
    def test_enum_serialization(self) -> None:
        """Enums should serialize to their string value."""
        from building_model_v2 import RoomType
        assert RoomType.LIVING.value == "Living"
        assert str(RoomType.LIVING) == "RoomType.LIVING" or RoomType.LIVING == "Living"
    
    def test_all_enum_values_unique(self) -> None:
        """Ensure all enum values are unique within each enum."""
        from building_model_v2 import RoomType
        values = [member.value for member in RoomType]
        assert len(values) == len(set(values))