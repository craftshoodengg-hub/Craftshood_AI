"""Base classes and value objects for Building Model v2.

This module provides:
- BaseEntity: Abstract base class with UUID, timestamps, metadata
- Point2D: 2D point value object
- BoundingBox: Axis-aligned bounding box
- GeometryMixin: Mixin for polygon-based geometry operations
- ValidationIssue/ValidationReport: Validation result types
"""

from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Self

import numpy as np
from shapely.geometry import Polygon, box


# ==================== ID Generation ====================

def generate_uuid() -> str:
    """Generate a new UUID4 string.
    
    Returns:
        A unique UUID4 string in standard format (e.g., '12345678-1234-5678-1234-567812345678').
    """
    return str(uuid.uuid4())


def current_timestamp() -> str:
    """Get the current UTC timestamp in ISO 8601 format.
    
    Returns:
        ISO 8601 formatted timestamp string (e.g., '2026-06-26T13:21:00.000000+00:00').
    """
    return datetime.now(timezone.utc).isoformat()


# ==================== Point2D ====================

@dataclass(frozen=True, slots=True)
class Point2D:
    """A 2D point with x and y coordinates.
    
    Attributes:
        x: X coordinate (typically east-west).
        y: Y coordinate (typically north-south).
    """
    
    x: float
    y: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array.
        
        Returns:
            Numpy array [x, y].
        """
        return np.array([self.x, self.y], dtype=float)
    
    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary.
        
        Returns:
            Dictionary with 'x' and 'y' keys.
        """
        return {"x": self.x, "y": self.y}
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Point2D:
        """Create Point2D from dictionary.
        
        Args:
            payload: Dictionary with 'x' and 'y' keys.
            
        Returns:
            New Point2D instance.
        """
        return cls(x=float(payload["x"]), y=float(payload["y"]))
    
    def distance_to(self, other: Point2D) -> float:
        """Calculate Euclidean distance to another point.
        
        Args:
            other: The other point.
            
        Returns:
            Distance between the two points.
        """
        return float(np.linalg.norm(other.to_array() - self.to_array()))


# ==================== BoundingBox ====================

@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned bounding box.
    
    Attributes:
        min_x: Minimum x coordinate.
        min_y: Minimum y coordinate.
        max_x: Maximum x coordinate.
        max_y: Maximum y coordinate.
    """
    
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    
    @property
    def width(self) -> float:
        """Width of the bounding box."""
        return self.max_x - self.min_x
    
    @property
    def height(self) -> float:
        """Height of the bounding box."""
        return self.max_y - self.min_y
    
    @property
    def area(self) -> float:
        """Area of the bounding box."""
        return self.width * self.height
    
    @property
    def center(self) -> Point2D:
        """Center point of the bounding box."""
        return Point2D(
            x=(self.min_x + self.max_x) / 2,
            y=(self.min_y + self.max_y) / 2,
        )
    
    def to_shapely(self) -> Polygon:
        """Convert to Shapely polygon.
        
        Returns:
            Shapely Polygon representing the bounding box.
        """
        return box(self.min_x, self.min_y, self.max_x, self.max_y)
    
    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary.
        
        Returns:
            Dictionary with min_x, min_y, max_x, max_y keys.
        """
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> BoundingBox:
        """Create BoundingBox from dictionary.
        
        Args:
            payload: Dictionary with min_x, min_y, max_x, max_y keys.
            
        Returns:
            New BoundingBox instance.
        """
        return cls(
            min_x=float(payload["min_x"]),
            min_y=float(payload["min_y"]),
            max_x=float(payload["max_x"]),
            max_y=float(payload["max_y"]),
        )
    
    @classmethod
    def from_points(cls, points: list[Point2D]) -> BoundingBox:
        """Create BoundingBox from a list of points.
        
        Args:
            points: List of Point2D instances.
            
        Returns:
            New BoundingBox instance.
            
        Raises:
            ValueError: If points list is empty.
        """
        if not points:
            raise ValueError("Cannot create BoundingBox from empty points list")
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return cls(
            min_x=min(xs),
            min_y=min(ys),
            max_x=max(xs),
            max_y=max(ys),
        )
    
    @classmethod
    def from_polygon(cls, polygon: Polygon) -> BoundingBox:
        """Create BoundingBox from a Shapely polygon.
        
        Args:
            polygon: Shapely Polygon.
            
        Returns:
            New BoundingBox instance.
        """
        bounds = polygon.bounds
        return cls(
            min_x=bounds[0],
            min_y=bounds[1],
            max_x=bounds[2],
            max_y=bounds[3],
        )


# ==================== GeometryMixin ====================

@dataclass(frozen=True, slots=True)
class GeometryMixin:
    """Mixin providing geometry utilities for polygon-based entities.
    
    This mixin is used by Room, Stair, and other entities that have
    a polygon representation.
    """
    
    polygon: Polygon
    
    @property
    def bounding_box(self) -> BoundingBox:
        """Calculate bounding box from polygon."""
        return BoundingBox.from_polygon(self.polygon)
    
    @property
    def area(self) -> float:
        """Calculate area of the polygon."""
        return float(self.polygon.area)
    
    @property
    def perimeter(self) -> float:
        """Calculate perimeter of the polygon."""
        return float(self.polygon.length)
    
    @property
    def centroid(self) -> Point2D:
        """Calculate centroid of the polygon."""
        c = self.polygon.centroid
        return Point2D(x=float(c.x), y=float(c.y))
    
    @property
    def orientation_degrees(self) -> float:
        """Calculate principal orientation using PCA.
        
        Returns:
            Angle in degrees (0-180).
        """
        coords = np.array(self.polygon.exterior.coords)
        if len(coords) < 2:
            return 0.0
        centered = coords[:-1] - coords[:-1].mean(axis=0)
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        principal = eigenvectors[:, np.argmax(eigenvalues)]
        angle = np.degrees(np.arctan2(principal[1], principal[0]))
        return angle % 180.0
    
    @property
    def is_convex(self) -> bool:
        """Check if the polygon is convex."""
        return self.polygon.equals(self.polygon.convex_hull)
    
    @property
    def convex_hull_area(self) -> float:
        """Calculate area of the convex hull."""
        return float(self.polygon.convex_hull.area)
    
    @property
    def solidity(self) -> float:
        """Calculate solidity (ratio of area to convex hull area).
        
        Returns:
            Solidity ratio (0.0 to 1.0).
        """
        hull_area = self.polygon.convex_hull.area
        return float(self.polygon.area / hull_area) if hull_area > 0 else 0.0


# ==================== BaseEntity ====================

@dataclass(frozen=True, slots=True)
class BaseEntity(ABC):
    """Abstract base class for all building model entities.
    
    Provides:
    - UUID-based identification
    - Creation and update timestamps
    - Extensible metadata storage
    - Serialization support
    
    Attributes:
        id: Unique UUID4 identifier.
        created_at: ISO 8601 creation timestamp.
        updated_at: ISO 8601 last update timestamp.
        metadata: Extensible key-value metadata.
    """
    
    id: str = field(default_factory=generate_uuid)
    created_at: str = field(default_factory=current_timestamp)
    updated_at: str = field(default_factory=current_timestamp)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the entity.
        """
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Self:
        """Create entity from dictionary.
        
        Args:
            payload: Dictionary with entity data.
            
        Returns:
            New entity instance.
        """
        return cls(
            id=str(payload.get("id", generate_uuid())),
            created_at=str(payload.get("created_at", current_timestamp())),
            updated_at=str(payload.get("updated_at", current_timestamp())),
            metadata=dict(payload.get("metadata", {})),
        )


# ==================== Validation ====================

@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A validation issue found in a building model.
    
    Attributes:
        code: Machine-readable issue code.
        message: Human-readable issue description.
        severity: Issue severity ('error', 'warning', 'info').
    """
    
    code: str
    message: str
    severity: str = "error"
    
    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary.
        
        Returns:
            Dictionary with code, message, and severity.
        """
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ValidationIssue:
        """Create ValidationIssue from dictionary.
        
        Args:
            payload: Dictionary with issue data.
            
        Returns:
            New ValidationIssue instance.
        """
        return cls(
            code=str(payload["code"]),
            message=str(payload["message"]),
            severity=str(payload.get("severity", "error")),
        )


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Validation result for a building model.
    
    Attributes:
        valid: Whether the model passed validation.
        issues: List of validation issues found.
    """
    
    valid: bool
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary with valid flag and issues list.
        """
        return {
            "valid": self.valid,
            "issues": [issue.to_dict() for issue in self.issues],
        }
    
    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ValidationReport:
        """Create ValidationReport from dictionary.
        
        Args:
            payload: Dictionary with report data.
            
        Returns:
            New ValidationReport instance.
        """
        issues = tuple(
            ValidationIssue.from_dict(issue)
            for issue in payload.get("issues", [])
        )
        return cls(
            valid=bool(payload.get("valid", True)),
            issues=issues,
        )
    
    @classmethod
    def create_valid(cls) -> ValidationReport:
        """Create a valid report with no issues.
        
        Returns:
            New valid ValidationReport instance.
        """
        return cls(valid=True, issues=())