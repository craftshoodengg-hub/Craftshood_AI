# Room Detection Engine — Design Document

**Date:** 2026-06-26  
**Status:** Pending Approved  
**Author:** OWL (AI Assistant)

---

## 1. Executive Summary

The current room detection pipeline requires pre-identified room center points (from text labels) and uses radial ray casting to find room boundaries. This approach fails when:
- Room labels are missing or ambiguous
- Rooms have irregular shapes
- Rooms contain holes (courtyards, columns)
- Small enclosed regions (closets, shafts) should be ignored

This document designs a **production-ready Room Detection Engine** that addresses these limitations.

---

## 2. Current Implementation Analysis

### 2.1 Current Pipeline

```
Room Labels (text) → RoomCenter points
                          ↓
LogicalWalls → BoundaryFinder (radial ray casting)
                          ↓
                    BoundaryIntersection points
                          ↓
                    PolygonBuilder (clockwise sort)
                          ↓
                    RoomGraphResult (polygon + metrics)
```

### 2.2 Limitations

| Limitation | Impact | Current Workaround |
|------------|--------|-------------------|
| Requires room labels | Cannot detect unlabeled rooms | None |
| Fixed 360 rays | Misses thin walls, creates sparse boundaries | None |
| No hole support | Cannot handle courtyards | None |
| No minimum area filter | Detects tiny regions as rooms | Manual post-processing |
| No shape validation | Produces invalid polygons | `buffer(0)` fix |
| Single center point | Cannot detect non-convex rooms | None |

### 3. Current Data Flow

```
DXF → LineReader → LineEntity[]
     → ParallelDetector → ParallelPair[]
     → WallClassifier → WallSegment[]
     → WallMerger → LogicalWall[]
     → TextExtractor → TextEntity[]
     → RoomDetector → Detection[] → RoomCenter[]
     → BoundaryFinder → BoundaryIntersection[]
     → PolygonBuilder → Polygon
     → AreaCalculator → RoomMetrics
     → RoomGraphResult
```

---

## 4. Proposed Architecture

### 4.1 New Pipeline

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    ROOM DETECTION ENGINE                    │
                    └─────────────────────────────────────────────────────────────┘
                                              │
        ┌─────────────────────────────────────┼─────────────────────────────────────┐
        ▼                                     ▼                                     ▼
┌───────────────┐                   ┌───────────────────┐               ┌───────────────────┐
│  Geometry     │                   │  Room Detection   │               │  Room Refinement  │
│  Analysis     │                   │  Algorithm        │               │  & Validation     │
└───────────────┘                   └───────────────────┘               └───────────────────┘
        │                                     │                                     │
        ▼                                     ▼                                     ▼
┌───────────────┐                   ┌───────────────────┐               ┌───────────────────┐
│ LogicalWalls  │                   │  Polygon          │               │  Validated Room   │
│ (from         │──────────────────▶│  Candidates       │──────────────▶│  Polygons         │
│  geometry     │                   │                   │               │                   │
│  engine)      │                   │                   │               │                   │
└───────────────┘                   └───────────────────┘               └───────────────────┘
```

### 4.2 Module Structure

```
room_detection/
├── __init__.py                 # Public API exports
├── detector.py                 # Main orchestrator
├── geometry_analyzer.py        # Wall loop detection
├── polygon_extractor.py       # Polygon extraction from wall loops
├── room_validator.py          # Room validation and filtering
├── room_metrics.py            # Area, perimeter, centroid, orientation
├── room_namer.py              # Room naming (from labels or inference)
├── config.py                  # Configuration dataclass
└── types.py                   # Shared type definitions
```

---

## 5. Algorithm Design

### 5.1 Phase 1: Wall Loop Detection

**Algorithm:** Find closed loops in the wall graph

**Approach:**
1. Build a graph from wall endpoints
2. Find all minimal cycles (loops) using Johnson's algorithm or DFS-based cycle detection
3. Filter loops by area and shape characteristics

**Data Structures:**

```python
@dataclass(frozen=True, slots=True)
class WallGraphNode:
    """A point where walls meet or end."""
    point: Point2D
    wall_ids: frozenset[str]

@dataclass(frozen=True, slots=True)
class WallGraphEdge:
    """A wall segment connecting two nodes."""
    start: WallGraphNode
    end: WallGraphNode
    wall_id: str
    geometry: LineString

@dataclass(frozen=True, slots=True)
class WallLoop:
    """A closed loop of wall segments forming a potential room."""
    nodes: tuple[WallGraphNode, ...]
    edges: tuple[WallGraphEdge, ...]
    polygon: Polygon
    area: float
    perimeter: float
```

**Algorithm: DFS-Based Cycle Detection**

```python
def find_wall_loops(
    walls: Sequence[LogicalWall],
    *,
    min_area: float = 1.0,
    max_area: float = 100000.0,
    tolerance: float = 0.01,
) -> list[WallLoop]:
    """
    Find all closed loops in the wall graph.
    
    Algorithm:
    1. Build adjacency list from wall endpoints
    2. For each node, perform DFS to find cycles
    3. Track visited edges to avoid duplicates
    4. Validate cycle area and shape
    5. Return sorted by area (largest first)
    
    Complexity: O(V + E) for graph construction + O(V * C) for cycle detection
    where V = vertices, E = edges, C = cycles
    """
```

**Complexity Analysis:**
- Graph construction: O(n) where n = number of wall segments
- Cycle detection: O(V * C) where V = vertices, C = cycles
- Overall: O(n + V * C) — typically O(n²) worst case for dense wall graphs

### 5.2 Phase 2: Polygon Extraction

**Algorithm:** Convert wall loops to valid Shapely polygons

**Steps:**
1. Extract ordered points from loop edges
2. Create Shapely Polygon
3. Validate polygon (non-empty, valid geometry)
4. Apply buffer(0) to fix self-intersections
5. Simplify polygon to remove redundant points

**Data Structures:**

```python
@dataclass(frozen=True, slots=True)
class PolygonCandidate:
    """A potential room polygon before validation."""
    polygon: Polygon
    source_wall_ids: frozenset[str]
    source_loop: WallLoop
    confidence: float  # 0.0 to 1.0 based on loop quality
```

### 5.3 Phase 3: Room Validation and Filtering

**Validation Rules:**

| Rule | Description | Config Parameter |
|------|-------------|------------------|
| Minimum area | Ignore tiny enclosed regions | `min_room_area: float = 4.0` |
| Maximum area | Ignore unreasonably large regions | `max_room_area: float = 100000.0` |
| Minimum perimeter | Ignore degenerate shapes | `min_perimeter: float = 8.0` |
| Aspect ratio | Ignore extremely elongated shapes | `max_aspect_ratio: float = 10.0` |
| Wall coverage | Room must be mostly enclosed | `min_wall_coverage: float = 0.7` |
| Polygon validity | Must be valid Shapely polygon | — |

**Implementation:**

```python
def validate_room(
    candidate: PolygonCandidate,
    config: RoomDetectionConfig,
) -> bool:
    """
    Validate a polygon candidate against room criteria.
    
    Returns True if the candidate passes all validation rules.
    """
    polygon = candidate.polygon
    
    # Area check
    if polygon.area < config.min_room_area:
        return False
    if polygon.area > config.max_room_area:
        return False
    
    # Perimeter check
    if polygon.length < config.min_perimeter:
        return False
    
    # Aspect ratio check
    bounds = polygon.bounds  # (minx, miny, maxx, maxy)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if width > 0 and height > 0:
        aspect = max(width, height) / min(width, height)
        if aspect > config.max_aspect_ratio:
            return False
    
    # Wall coverage check
    if candidate.source_wall_ids:
        wall_coverage = _calculate_wall_coverage(polygon, candidate.source_wall_ids)
        if wall_coverage < config.min_wall_coverage:
            return False
    
    return True
```

### 5.4 Phase 4: Room Metrics Calculation

**Metrics:**

| Metric | Description | Method |
|--------|-------------|--------|
| Area | Room floor area | `polygon.area` |
| Perimeter | Total boundary length | `polygon.length` |
| Centroid | Geometric center | `polygon.centroid` |
| Orientation | Principal axis angle | PCA on polygon points |
| Bounding box | Axis-aligned extents | `polygon.bounds` |
| Convex hull | Convex envelope | `polygon.convex_hull` |
| Solidity | Area / convex hull area | `polygon.area / convex_hull.area` |

**Orientation Calculation:**

```python
def calculate_orientation(polygon: Polygon) -> float:
    """
    Calculate the principal orientation of a room in degrees.
    
    Uses PCA on the polygon exterior coordinates to find
    the dominant direction.
    
    Returns: Angle in degrees (0-180)
    """
    coords = np.array(polygon.exterior.coords)
    centered = coords - coords.mean(axis=0)
    cov = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    principal = eigenvectors[:, np.argmax(eigenvalues)]
    angle = np.degrees(np.arctan2(principal[1], principal[0]))
    return angle % 180.0
```

### 5.5 Phase 5: Room Naming

**Strategy:**
1. If room label exists inside polygon, use it
2. If multiple labels, use the one closest to centroid
3. If no label, assign generic name based on size/position

```python
def assign_room_name(
    polygon: Polygon,
    detections: Sequence[Detection],
    room_index: int,
) -> str:
    """
    Assign a name to a room based on available label detections.
    
    Priority:
    1. Label inside polygon (closest to centroid)
    2. Generic name "Room-N"
    """
    centroid = polygon.centroid
    candidates = [
        detection for detection in detections
        if polygon.contains(Point(detection.x, detection.y))
    ]
    
    if candidates:
        best = min(candidates, key=lambda d: centroid.distance(Point(d.x, d.y)))
        return best.label
    
    return f"Room-{room_index + 1}"
```

---

## 6. Data Structures

### 6.1 Core Types

```python
# types.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shapely.geometry import Polygon

from geometry_engine import LogicalWall
from backend.cad_intelligence.room_detector import Detection


@dataclass(frozen=True, slots=True)
class RoomDetectionConfig:
    """Configuration for room detection."""
    
    # Filtering thresholds
    min_room_area: float = 4.0
    max_room_area: float = 100000.0
    min_perimeter: float = 8.0
    max_aspect_ratio: float = 10.0
    min_wall_coverage: float = 0.7
    
    # Geometry tolerance
    tolerance: float = 0.01
    buffer_distance: float = 0.001
    
    # Naming
    use_label_detection: bool = True
    generic_name_prefix: str = "Room"


@dataclass(frozen=True, slots=True)
class DetectedRoom:
    """A detected room with complete metadata."""
    
    room_id: str
    room_name: str
    polygon: Polygon
    area: float
    perimeter: float
    centroid: Point2D
    orientation_degrees: float
    bounding_box: tuple[float, float, float, float]
    wall_ids: frozenset[str]
    label_detection: Detection | None
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "polygon": [[x, y] for x, y in self.polygon.exterior.coords],
            "area": self.area,
            "perimeter": self.perimeter,
            "centroid": {"x": self.centroid.x, "y": self.centroid.y},
            "orientation_degrees": self.orientation_degrees,
            "bounding_box": list(self.bounding_box),
            "wall_ids": sorted(self.wall_ids),
            "label": self.label_detection.label if self.label_detection else None,
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class RoomDetectionResult:
    """Complete result of room detection."""
    
    rooms: tuple[DetectedRoom, ...]
    unlabeled_rooms: int
    total_wall_loops: int
    filtered_loops: int
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "rooms": [room.to_dict() for room in self.rooms],
            "statistics": {
                "total_rooms": len(self.rooms),
                "unlabeled_rooms": self.unlabeled_rooms,
                "total_wall_loops": self.total_wall_loops,
                "filtered_loops": self.filtered_loops,
            },
        }
```

---

## 7. Edge Cases

### 7.1 Handling Irregular Shapes

| Shape | Challenge | Solution |
|-------|-----------|----------|
| L-shaped room | Non-convex polygon | Natural result of wall loop detection |
| Room with alcove | Concave regions | Wall loop captures full boundary |
| Curved walls | ARC entities not supported | Approximate with line segments |
| Non-rectangular room | Complex boundary | Wall loop handles arbitrary shapes |

### 7.2 Handling Holes (Rooms with Courtyards)

**Current:** Not supported  
**Solution:** Detect inner loops as holes

```python
def detect_rooms_with_holes(
    outer_loop: WallLoop,
    inner_loops: list[WallLoop],
) -> Polygon:
    """
    Create a polygon with holes from outer and inner loops.
    """
    outer_polygon = outer_loop.polygon
    holes = [loop.polygon for loop in inner_loops if outer_polygon.contains(loop.polygon)]
    return Polygon(outer_polygon.exterior, [hole.exterior for hole in holes])
```

### 7.3 Handling Touching Rooms

**Challenge:** Two rooms share a common wall  
**Solution:** Each room is a separate loop; shared wall appears in both

### 7.4 Handling Small Enclosed Regions

**Challenge:** Closets, shafts, or noise create tiny loops  
**Solution:** Filter by `min_room_area` threshold

### 7.5 Handling Missing Labels

**Challenge:** Rooms without text labels  
**Solution:** Assign generic names; flag for manual review

### 7.6 Handling Overlapping Detections

**Challenge:** Multiple loops may overlap  
**Solution:** Keep largest loop; remove contained smaller loops

---

## 8. Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Graph construction | O(n) | O(n) |
| Cycle detection | O(V * C) | O(V + C) |
| Polygon validation | O(k) per polygon | O(k) |
| Metrics calculation | O(k) per polygon | O(1) |
| Room naming | O(r * d) | O(r) |
| **Total** | **O(n + V*C + r*k)** | **O(n + r)** |

Where:
- n = number of wall segments
- V = number of vertices in wall graph
- C = number of cycles
- k = average points per polygon
- r = number of detected rooms
- d = number of label detections

---

## 9. Required Files

### 9.1 New Files

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `room_detection/__init__.py` | Public API | 20 |
| `room_detection/config.py` | Configuration | 40 |
| `room_detection/types.py` | Data structures | 80 |
| `room_detection/geometry_analyzer.py` | Wall loop detection | 150 |
| `room_detection/polygon_extractor.py` | Polygon extraction | 80 |
| `room_detection/room_validator.py` | Validation logic | 100 |
| `room_detection/room_metrics.py` | Metrics calculation | 80 |
| `room_detection/room_namer.py` | Room naming | 60 |
| `room_detection/detector.py` | Main orchestrator | 120 |
| `tests/test_room_detection.py` | Unit tests | 200 |

**Total new code:** ~930 lines

### 9.2 Modified Files

| File | Change |
|------|--------|
| `room_graph/__init__.py` | Add backward-compatible exports |
| `building_model/models.py` | Add `DetectedRoom` reference |

---

## 10. Integration Points

### 10.1 Input Interfaces

```python
# From geometry_engine
from geometry_engine import LogicalWall

# From backend/cad_intelligence
from backend.cad_intelligence.room_detector import Detection
```

### 10.2 Output Interfaces

```python
# To building_model
from room_detection import DetectedRoom, RoomDetectionResult
```

### 10.3 Backward Compatibility

The new engine will be additive. The existing `room_graph` module remains unchanged:

```python
# Old approach (still works)
from room_graph import RoomGraphBuilder
result = builder.build_room(room_name, center, walls)

# New approach
from room_detection import RoomDetectionEngine
engine = RoomDetectionEngine()
result = engine.detect_rooms(walls, detections)
```

---

## 11. Acceptance Criteria

### 11.1 Functional Requirements

- [ ] Detect rooms from wall geometry without requiring labels
- [ ] Handle irregular room shapes (L-shaped, non-convex)
- [ ] Filter out tiny enclosed regions below minimum area
- [ ] Calculate accurate area, perimeter, and centroid
- [ ] Generate valid Shapely polygons
- [ ] Assign unique room IDs
- [ ] Compute room orientation (0-180 degrees)
- [ ] Support room naming from existing labels
- [ ] Handle rooms with holes (future enhancement)

### 11.2 Performance Requirements

- [ ] Process 100 walls in <1 second
- [ ] Process 1000 walls in <5 seconds
- [ ] Process 5000 walls in <30 seconds
- [ ] Memory usage <500MB for 5000 walls

### 11.3 Quality Requirements

- [ ] Test coverage >85%
- [ ] All edge cases handled
- [ ] No unhandled exceptions
- [ ] Clear error messages
- [ ] Documentation complete

---

## 12. Implementation Phases

### Phase 1: Core Detection (Week 1-2)

1. Create `types.py` with data structures
2. Create `config.py` with configuration
3. Implement `geometry_analyzer.py` (wall loop detection)
4. Implement `polygon_extractor.py`
5. Write unit tests

### Phase 2: Validation & Metrics (Week 3)

1. Implement `room_validator.py`
2. Implement `room_metrics.py`
3. Implement `room_namer.py`
4. Write unit tests

### Phase 3: Integration (Week 4)

1. Implement `detector.py` (main orchestrator)
2. Create `__init__.py` with public API
3. Integration tests
4. Documentation

---

## 13. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cycle detection fails on complex drawings | Medium | High | Fallback to ray casting |
| Performance unacceptable for large drawings | Low | Medium | Optimize with spatial indexing |
| Polygon validation too strict | Medium | Medium | Configurable thresholds |
| Breaking existing room_graph module | Very Low | High | Additive changes only |

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Next Review:** After approval