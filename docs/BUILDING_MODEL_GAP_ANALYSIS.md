# Building Model — Gap Analysis & Implementation Plan

**Date:** 2026-06-26  
**Status:** Pending Approval  
**Author:** OWL (AI Assistant)

---

## 1. Current Implementation Review

### 1.1 What Already Exists

| Component | Current State | Location |
|-----------|---------------|----------|
| **BuildingModel** | Exists as frozen dataclass | `models.py` (line 47) |
| **BuildingStatistics** | Exists as frozen dataclass | `models.py` (line 13) |
| **ValidationIssue** | Exists as frozen dataclass | `models.py` (line 81) |
| **ValidationReport** | Exists as frozen dataclass | `models.py` (line 97) |
| **BuildingModelBuilder** | Exists as builder class | `builder.py` (line 30) |
| **BuildingModelSerializer** | Exists with JSON support | `serializer.py` (line 17) |
| **BuildingModelValidator** | Exists with graph validation | `validator.py` (line 11) |
| **BuildingStatisticsCalculator** | Exists with calculation logic | `statistics.py` (line 12) |
| **ModuleOutputs** | Exists as input container | `builder.py` (line 13) |

### 1.2 Current Data Model

```
BuildingModel
├── metadata: Mapping[str, Any]
├── plot: Mapping[str, Any] | None
├── walls: Sequence[Mapping[str, Any]]      ← Generic dicts
├── doors: Sequence[Mapping[str, Any]]
├── windows: Sequence[Mapping[str, Any]]
├── rooms: Sequence[Mapping[str, Any]]
├── adjacency_graph: Sequence[Mapping[str, Any]]
├── connectivity_graph: Sequence[Mapping[str, Any]]
├── facing_information: Mapping[str, Any] | None
├── zoning: Sequence[Mapping[str, Any]]
├── confidence: Sequence[Mapping[str, Any]]
└── statistics: BuildingStatistics
```

---

## 2. Gap Analysis: Target vs. Current

### 2.1 Entity-by-Entity Comparison

| Target Entity | Current State | Gap |
|---------------|---------------|-----|
| **Building** | Exists as `BuildingModel` | Missing: floors, building_type, address, year_built, building_orientation |
| **Floor** | ❌ Not supported | Missing entirely |
| **Room** | ❌ Generic dict | Missing: id, name, room_type, polygon, height, label_position, area, perimeter, centroid, orientation |
| **Wall** | ❌ Generic dict | Missing: id, wall_type, geometry, width, height, polygon, room_ids, length, orientation |
| **Door** | ❌ Generic dict | Missing: id, door_type, geometry, width, height, is_exterior, swing_direction, room_ids, wall_id |
| **Window** | ❌ Generic dict | Missing: id, window_type, geometry, width, height, sill_height, is_exterior, room_ids, wall_id |
| **Column** | ❌ Not supported | Missing entirely |
| **Stair** | ❌ Not supported | Missing entirely |
| **Opening** | ❌ Not supported | Missing as abstraction (doors/windows are separate dicts) |

### 2.2 Feature-by-Feature Comparison

| Feature | Current State | Gap |
|---------|---------------|-----|
| **UUID Identification** | ❌ None | No entity has unique ID |
| **Type Safety** | ❌ Generic dicts | All entities are `Mapping[str, Any]` |
| **Geometry Objects** | ❌ None | No Shapely geometry stored |
| **Bounding Box** | ❌ None | Not calculated or stored |
| **Area** | ✅ In statistics only | Not available per-entity |
| **Perimeter** | ✅ In statistics only | Not available per-entity |
| **Centroid** | ❌ None | Not calculated |
| **Orientation** | ❌ None | Not calculated |
| **Relationships** | ❌ Implicit only | No explicit links between entities |
| **Floor Organization** | ❌ Flat structure | No floor-based hierarchy |
| **Room Types** | ❌ None | No classification |
| **Wall Types** | ❌ None | No classification |
| **Opening Types** | ❌ None | No classification |
| **Metadata** | ✅ Building-level only | Not available per-entity |

---

## 3. What Should Be Redesigned

### 3.1 BuildingModel → Building

**Current Issues:**
- Flat structure (no floors)
- Generic dicts for all entity collections
- No building-level metadata (type, address, year)
- No building orientation

**Redesign:**
```python
@dataclass(frozen=True, slots=True)
class Building:
    id: str
    name: str
    floors: tuple[Floor, ...]          # New: floor-based hierarchy
    building_type: str | None
    address: str | None
    year_built: int | None
    metadata: dict[str, Any]
    
    # Computed properties
    @property
    def total_area(self) -> float: ...
    @property
    def number_of_rooms(self) -> int: ...
    @property
    def building_orientation(self) -> Orientation: ...
```

### 3.2 Floor (New Entity)

**Why Needed:**
- Real buildings have multiple floors
- Room detection produces floor-level results
- Stairs connect floors
- Vastu analysis is floor-based

```python
@dataclass(frozen=True, slots=True)
class Floor:
    id: str
    name: str
    level: float
    height: float
    rooms: tuple[Room, ...]
    walls: tuple[Wall, ...]
    doors: tuple[Door, ...]
    windows: tuple[Window, ...]
    columns: tuple[Column, ...]
    stairs: tuple[Stair, ...]
    metadata: dict[str, Any]
```

### 3.3 Room (Strongly Typed)

**Current Issues:**
- Generic `Mapping[str, Any]`
- No geometry object
- No computed properties
- No type classification

**Redesign:**
```python
@dataclass(frozen=True, slots=True)
class Room:
    id: str
    name: str
    room_type: RoomType
    floor_id: str
    polygon: Polygon                    # Shapely geometry
    height: float | None
    label_text: str | None
    label_position: Point2D | None
    metadata: dict[str, Any]
    
    # Computed from polygon
    @property
    def area(self) -> float: ...
    @property
    def perimeter(self) -> float: ...
    @property
    def centroid(self) -> Point2D: ...
    @property
    def orientation_degrees(self) -> float: ...
    @property
    def bounding_box(self) -> BoundingBox: ...
```

### 3.4 Wall (Strongly Typed)

**Current Issues:**
- Generic `Mapping[str, Any]`
- No geometry object
- No relationships to rooms
- No width/height

**Redesign:**
```python
@dataclass(frozen=True, slots=True)
class Wall:
    id: str
    wall_type: WallType
    geometry: LineString              # Centerline
    width: float
    height: float | None
    polygon: Polygon | None           # Full wall polygon
    room_ids: frozenset[str]          # Adjacent rooms
    floor_id: str | None
    metadata: dict[str, Any]
```

### 3.5 Door/Window → Opening Hierarchy

**Current Issues:**
- Separate generic dicts
- No common base class
- No relationship to wall or rooms

**Redesign:**
```python
@dataclass(frozen=True, slots=True)
class Opening:
    id: str
    opening_type: OpeningType
    geometry: Point | LineString
    width: float
    height: float | None
    room_ids: frozenset[str]
    wall_id: str | None
    floor_id: str | None
    metadata: dict[str, Any]

@dataclass(frozen=True, slots=True)
class Door(Opening):
    door_type: DoorType
    is_exterior: bool
    swing_direction: str | None

@dataclass(frozen=True, slots=True)
class Window(Opening):
    window_type: WindowType
    sill_height: float | None
    is_exterior: bool
```

### 3.6 Column (New Entity)

**Why Needed:**
- Structural elements in floor plans
- Affects room detection (obstacles)
- Required for BIM/IFC export

```python
@dataclass(frozen=True, slots=True)
class Column:
    id: str
    column_type: ColumnType
    geometry: Point | Polygon
    width: float
    height: float
    floor_id: str | None
    metadata: dict[str, Any]
```

### 3.7 Stair (New Entity)

**Why Needed:**
- Required for multi-floor support
- Affects room detection
- Required for egress analysis

```python
@dataclass(frozen=True, slots=True)
class Stair:
    id: str
    stair_type: StairType
    geometry: Polygon
    width: float
    floor_ids: frozenset[str]         # Connected floors
    direction: str | None
    floor_id: str | None
    metadata: dict[str, Any]
```

---

## 4. Migration Strategy

### 4.1 Non-Breaking Approach

The new model will be **additive** — existing code continues to work unchanged.

**Strategy:**
1. Create new package `building_model_v2/` alongside existing `building_model/`
2. New code uses new models
3. Adapter functions convert between old and new
4. Gradual migration of consumers

### 4.2 Adapter Functions

```python
# building_model_v2/adapters.py

def from_legacy_model(old_model: BuildingModel) -> Building:
    """Convert legacy BuildingModel to new Building."""
    # Create default floor from flat structure
    floor = Floor(
        id=_generate_uuid(),
        name="Ground Floor",
        level=0.0,
        height=10.0,
        rooms=_convert_rooms(old_model.rooms, floor.id),
        walls=_convert_walls(old_model.walls, floor.id),
        doors=_convert_doors(old_model.doors, floor.id),
        windows=_convert_windows(old_model.windows, floor.id),
    )
    return Building(
        id=_generate_uuid(),
        name="Building",
        floors=(floor,),
    )

def to_legacy_model(building: Building) -> BuildingModel:
    """Convert new Building to legacy BuildingModel."""
    # Flatten floors into single list
    all_rooms = [room for floor in building.floors for room in floor.rooms]
    all_walls = [wall for floor in building.floors for wall in floor.walls]
    # ... etc
    return BuildingModel(...)
```

### 4.3 Consumer Migration Order

| Priority | Consumer | Current Usage | Migration Effort |
|----------|----------|---------------|------------------|
| 1 | `adjacency.py` | Uses RoomPolygon dicts | Low — just change dict access to attributes |
| 2 | `connectivity.py` | Uses RoomPolygon dicts | Low |
| 3 | `facing.py` | Uses RoomPolygon dicts | Low |
| 4 | `zoning.py` | Uses room dicts | Medium |
| 5 | `confidence.py` | Uses room dicts | Medium |
| 6 | `backend/app.py` | Uses BuildingModel | Medium — needs adapter |

---

## 5. Implementation Plan

### Phase 1: Core Types and Base Classes

**Files to Create:**

| File | Purpose | Est. Lines |
|------|---------|------------|
| `building_model_v2/__init__.py` | Package init | 20 |
| `building_model_v2/types.py` | All enums | 80 |
| `building_model_v2/base.py` | BoundingBox, GeometryMixin | 100 |

**Dependencies:** None (standalone package)

### Phase 2: Entity Definitions

**Files to Create:**

| File | Purpose | Est. Lines |
|------|---------|------------|
| `building_model_v2/entities.py` | Room, Wall, Opening, Door, Window, Column, Stair | 350 |

**Dependencies:** Phase 1

### Phase 3: Building and Floor

**Files to Create:**

| File | Purpose | Est. Lines |
|------|---------|------------|
| `building_model_v2/building.py` | Building, Floor classes | 150 |

**Dependencies:** Phase 1, Phase 2

### Phase 4: Serialization and Validation

**Files to Create:**

| File | Purpose | Est. Lines |
|------|---------|------------|
| `building_model_v2/serializer.py` | JSON serialization | 100 |
| `building_model_v2/validator.py` | Validation logic | 120 |
| `building_model_v2/statistics.py` | Statistics calculation | 80 |

**Dependencies:** Phase 1, Phase 2, Phase 3

### Phase 5: Adapters and Integration

**Files to Create:**

| File | Purpose | Est. Lines |
|------|---------|------------|
| `building_model_v2/adapters.py` | Legacy conversion | 100 |
| `building_model_v2/builder.py` | Builder pattern | 80 |

**Dependencies:** All phases, existing `building_model/`

### Phase 6: Tests

**Files to Create:**

| File | Purpose | Est. Lines |
|------|---------|------------|
| `tests/test_building_model_v2.py` | Comprehensive tests | 300 |

**Dependencies:** All phases

---

## 6. File Summary

### 6.1 New Files

| File | Purpose | Est. Lines |
|------|---------|------------|
| `building_model_v2/__init__.py` | Package init | 20 |
| `building_model_v2/types.py` | Enums | 80 |
| `building_model_v2/base.py` | Base classes | 100 |
| `building_model_v2/entities.py` | Entity dataclasses | 350 |
| `building_model_v2/building.py` | Building, Floor | 150 |
| `building_model_v2/serializer.py` | JSON serialization | 100 |
| `building_model_v2/validator.py` | Validation | 120 |
| `building_model_v2/statistics.py` | Statistics | 80 |
| `building_model_v2/adapters.py` | Legacy adapters | 100 |
| `building_model_v2/builder.py` | Builder | 80 |
| `tests/test_building_model_v2.py` | Tests | 300 |

**Total new code:** ~1,480 lines

### 6.2 Existing Files (Unchanged)

| File | Reason |
|------|--------|
| `building_model/__init__.py` | Keep for backward compatibility |
| `building_model/models.py` | Keep for backward compatibility |
| `building_model/builder.py` | Keep for backward compatibility |
| `building_model/serializer.py` | Keep for backward compatibility |
| `building_model/statistics.py` | Keep for backward compatibility |
| `building_model/validator.py` | Keep for backward compatibility |

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Adapter conversion loses data | Low | High | Comprehensive tests for round-trip |
| Performance regression | Low | Medium | Lazy property evaluation |
| Breaking existing API | Very Low | High | New package, old package unchanged |
| UUID generation overhead | Very Low | Low | Generate once at creation |

---

## 8. Acceptance Criteria

- [ ] All 8 entity types implemented as frozen dataclasses
- [ ] Every entity has UUID-based `id` field
- [ ] Every entity has geometry (Polygon, LineString, or Point)
- [ ] Every entity has computed bounding_box, area, perimeter, centroid, orientation
- [ ] Building has floors, total_area, number_of_rooms, building_orientation
- [ ] JSON serialization/deserialization works for all entities
- [ ] Validation catches invalid models
- [ ] Adapter functions convert between old and new formats
- [ ] All existing tests pass unchanged
- [ ] New test coverage >90%

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Next Review:** After approval