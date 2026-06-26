# Craftshood_AI — Processing Pipeline

## Overview

The Craftshood_AI processing pipeline transforms raw DXF floor plan drawings into structured building intelligence. The pipeline consists of 7 sequential stages, each producing well-defined outputs that feed into the next stage.

## Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE PROCESSING PIPELINE                          │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │          │    │              │    │              │    │              │
  │   DXF    │───▶│    Stage 1   │───▶│   Stage 2    │───▶│   Stage 3    │
  │  Input   │    │ Normalization│    │  Geometry    │    │    Room      │
  │          │    │              │    │  Extraction  │    │  Detection   │
  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                │
                                                                ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │          │    │              │    │              │    │              │
  │  Flutter │◀───│   Stage 7    │◀───│   Stage 6    │◀───│   Stage 5    │
  │   App    │    │     API      │    │   Analysis   │    │   Building   │
  │          │    │              │    │              │    │    Model     │
  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                       ▲
                                       │
                                 ┌──────────────┐
                                 │              │
                                 │   Stage 4    │
                                 │  Intelligence│
                                 │              │
                                 └──────────────┘
```

---

## Stage 1: Input (DXF File)

### Description
The pipeline begins with a DXF (Drawing Exchange Format) file, the standard CAD format for 2D architectural drawings.

### Input Format
- **File Format:** DXF (AutoCAD Drawing Exchange Format)
- **Versions Supported:** AutoCAD 2000 and later
- **Entity Types:** LINE, POLYLINE, ARC, CIRCLE, TEXT, MTEXT, INSERT (blocks)

### DXF Structure
```
DXF File
├── HEADER (variables, units, extents)
├── CLASSES (application-defined classes)
├── TABLES (layers, linetypes, text styles)
├── BLOCKS (reusable block definitions)
├── ENTITIES (geometric and text entities)
└── OBJECTS (non-graphical objects)
```

### Entity Types Used

| Entity Type | Description | Usage in Pipeline |
|-------------|-------------|-------------------|
| LINE | Straight line segment | Wall detection |
| POLYLINE | Connected line segments | Wall detection (future) |
| LWPOLYLINE | Lightweight polyline | Wall detection (future) |
| ARC | Arc segment | Wall detection (future) |
| CIRCLE | Circle/column | Column detection (future) |
| TEXT | Single-line text | Room labels |
| MTEXT | Multi-line text | Room labels, notes |
| INSERT | Block reference | Doors, windows, furniture |

### Example DXF Entities
```python
# LINE entity
{
    "dxftype": "LINE",
    "layer": "A-WALL",
    "start": (0.0, 0.0),
    "end": (100.0, 0.0)
}

# TEXT entity
{
    "dxftype": "TEXT",
    "layer": "A-TEXT",
    "text": "Living Room",
    "insert": (50.0, 50.0),
    "height": 2.5
}
```

---

## Stage 2: Normalization

### Description
Raw CAD data contains inconsistent naming conventions, units, and formats. The normalization stage standardizes all extracted data into consistent enums and units.

### Modules
- `normalizer/layer_normalizer.py`
- `normalizer/block_normalizer.py`
- `normalizer/text_normalizer.py`
- `normalizer/unit_normalizer.py`

### Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     NORMALIZATION PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │   Layer     │    │    Block    │    │    Text     │
  │  Names      │    │    Names    │    │   Labels    │
  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
         │                  │                  │
         ▼                  ▼                  ▼
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  Layer      │    │   Layer     │    │   Room      │
  │  Category   │    │  Category   │    │    Name     │
  │   Enum      │    │    Enum     │    │    Enum     │
  └─────────────┘    └─────────────┘    └─────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
                   ┌─────────────┐
                   │  Dimension  │
                   │  Strings    │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Decimal    │
                   │   Feet      │
                   └─────────────┘
```

### Layer Normalization

**Input:** Raw layer names from DXF (e.g., "A-WALL", "wall", "WALLS", "masonry")

**Output:** `LayerCategory` enum

| Raw Layer Name | Normalized Category |
|----------------|---------------------|
| A-WALL, wall, WALLS, masonry | `WALL` |
| A-DOOR, door, doors, shutter | `DOOR` |
| A-WINDOW, window, glazing | `WINDOW` |
| A-TEXT, text, anno, label | `TEXT` |
| A-DIM, dim, dimension | `DIMENSION` |
| furniture, fixture, sofa | `FURNITURE` |
| column, col, pillar | `COLUMN` |
| stair, staircase, steps | `STAIR` |
| (unknown) | `UNKNOWN` |

### Block Normalization

**Input:** Block names from DXF (e.g., "door-1", "bed", "A-DOOR")

**Output:** `LayerCategory` enum

Extends layer mappings with block-specific aliases:
- "d", "dr" → `DOOR`
- "w", "win" → `WINDOW`
- "bed", "chair", "wardrobe", "wc" → `FURNITURE`

### Text Normalization

**Input:** Room label text (e.g., "living room", "MASTER BEDROOM", "kit")

**Output:** `RoomName` enum

| Raw Text | Normalized Name |
|----------|-----------------|
| living, hall, liv | `Living` |
| master bedroom, MBR | `M.bed room` |
| bedroom, BR | `Bed room` |
| kitchen, kit | `Kitchen` |
| dining, din | `Dining` |
| toilet, wc, bath | `Toilet` |
| sit out, sitout | `Sitout` |
| portico, porch | `Portico` |

### Unit Normalization

**Input:** Dimension strings (e.g., "10'-6\"", "10 ft 6 in", "3.048 m", "126 in")

**Output:** `Dimension` dataclass with decimal feet

| Input Format | Parsed Value (feet) |
|--------------|---------------------|
| 10'-6" | 10.5 |
| 10 ft 6 in | 10.5 |
| 126 in | 10.5 |
| 3.048 m | 10.0 |
| 304.8 mm | 10.0 |

---

## Stage 3: Geometry Extraction

### Description
Extract wall geometry from DXF LINE entities. This stage identifies parallel line pairs that represent walls and merges them into logical wall segments.

### Module
- `geometry_engine/`

### Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    GEOMETRY EXTRACTION PIPELINE                  │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  LINE       │    │  Parallel   │    │    Wall     │    │  Logical    │
  │  Reading    │───▶│   Pair      │───▶│Classification│───▶│   Wall      │
  │             │    │  Detection  │    │             │    │   Merging   │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Step 3.1: Line Reading

**Input:** DXF file path

**Output:** `list[LineEntity]`

```python
@dataclass(frozen=True, slots=True)
class LineEntity:
    id: str              # Unique identifier (layout:handle)
    start: Point2D       # Start point (x, y)
    end: Point2D         # End point (x, y)
    length: float        # Line length
    angle: float         # Angle in degrees (0-180)
    layer: str           # Layer name
    space: str           # Layout or block name
```

### Step 3.2: Parallel Pair Detection

**Input:** `list[LineEntity]`

**Output:** `list[ParallelPair]`

**Algorithm:** O(n²) pairwise comparison with filters:
1. Angle difference ≤ `angle_tolerance_degrees` (default: 1.0°)
2. Perpendicular distance ≤ `max_perpendicular_distance` (default: 1.0)
3. Perpendicular distance ≥ `min_perpendicular_distance` (default: 1e-6)
4. Projection overlap ≥ `min_overlap_length` (default: 1e-6)

```python
@dataclass(frozen=True, slots=True)
class ParallelPair:
    id: str                          # Pair identifier
    line_a: LineEntity               # First line
    line_b: LineEntity               # Second line
    angle_difference: float          # Angle difference in degrees
    perpendicular_distance: float    # Distance between lines
```

### Step 3.3: Wall Classification

**Input:** `list[ParallelPair]`

**Output:** `list[WallSegment]`

**Algorithm:** Match perpendicular distance against known wall types

| Wall Type | Expected Width | Tolerance |
|-----------|---------------|-----------|
| 9 inch brick wall | 0.75 ft | ±0.05 ft |
| 4.5 inch brick wall | 0.375 ft | ±0.05 ft |

```python
@dataclass(frozen=True, slots=True)
class WallSegment:
    id: str                    # Segment identifier
    wall_type: WallType        # Classified wall type
    width: float               # Expected width
    measured_width: float      # Measured width
    source_pair: ParallelPair  # Source parallel pair
```

### Step 3.4: Wall Merging

**Input:** `list[WallSegment]`

**Output:** `list[LogicalWall]`

**Algorithm:** DFS-based connected components
1. Group segments with same `wall_type` and `width`
2. Merge segments whose source lines are within `connection_tolerance`

```python
@dataclass(frozen=True, slots=True)
class LogicalWall:
    id: str                          # Logical wall identifier
    wall_type: WallType              # Wall type
    width: float                     # Wall width
    segment_ids: tuple[str, ...]     # Component segment IDs
    line_ids: tuple[str, ...]        # Source line IDs
    source_lines: tuple[LineEntity, ...]  # Source line entities
```

---

## Stage 4: Room Detection

### Description
Build room boundary polygons by casting radial rays from room center points and finding wall intersections.

### Module
- `room_graph/`

### Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ROOM DETECTION PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │    Room     │    │  Boundary   │    │  Polygon    │    │    Room     │
  │   Center    │───▶│   Finder    │───▶│  Builder    │───▶│   Graph     │
  │   Point     │    │(Ray Casting)│    │             │    │   Result    │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Step 4.1: Room Center Detection

**Input:** Text entities from `cad_intelligence/`

**Output:** `list[RoomCenter]`

Room centers are detected from text labels matching known room names.

```python
@dataclass(frozen=True, slots=True)
class RoomCenter:
    x: float    # X coordinate
    y: float    # Y coordinate
```

### Step 4.2: Boundary Finding (Radial Ray Casting)

**Input:** `RoomCenter`, `list[LogicalWall]`

**Output:** `list[BoundaryIntersection]`

**Algorithm:**
1. Cast 360 radial rays from room center (configurable)
2. For each ray, find nearest wall intersection
3. Deduplicate by rounded coordinates

```python
@dataclass(frozen=True, slots=True)
class BoundaryIntersection:
    angle_degrees: float    # Ray angle
    point: RoomCenter       # Intersection point
    distance: float         # Distance from center
    wall_id: str            # Wall that was hit
```

### Step 4.3: Polygon Building

**Input:** `RoomCenter`, `list[BoundaryIntersection]`

**Output:** Shapely `Polygon`

**Algorithm:**
1. Sort intersection points clockwise around center
2. Build polygon from sorted points
3. Validate and repair if needed (buffer(0))

### Step 4.4: Room Graph Result

**Input:** Room name, polygon, intersections

**Output:** `RoomGraphResult`

```python
@dataclass(frozen=True, slots=True)
class RoomGraphResult:
    room_name: str                          # Room name
    polygon: Polygon                        # Room boundary polygon
    area: float                             # Area in square units
    perimeter: float                        # Perimeter length
    centroid: RoomCenter                    # Polygon centroid
    boundary_wall_ids: tuple[str, ...]      # Walls touching this room
    intersections: tuple[BoundaryIntersection, ...]  # All intersections
```

---

## Stage 5: Building Intelligence

### Description
Aggregate all detected data into a unified building model and compute statistics.

### Module
- `building_model/`

### Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   BUILDING INTELLIGENCE PIPELINE                 │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │   Module    │    │  Building   │    │  Statistics │    │ Validation  │
  │   Outputs   │───▶│   Model     │───▶│ Calculation │───▶│   Report    │
  │             │    │   Builder   │    │             │    │             │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Building Model

```python
@dataclass(frozen=True, slots=True)
class BuildingModel:
    metadata: JsonMapping                    # File metadata
    plot: JsonMapping | None                 # Plot information
    walls: Sequence[JsonMapping]             # Detected walls
    doors: Sequence[JsonMapping]             # Detected doors
    windows: Sequence[JsonMapping]           # Detected windows
    rooms: Sequence[JsonMapping]            # Detected rooms
    adjacency_graph: Sequence[JsonMapping]   # Room adjacency
    connectivity_graph: Sequence[JsonMapping] # Room connectivity
    facing_information: JsonMapping | None   # Road-facing info
    zoning: Sequence[JsonMapping]            # Room zoning
    confidence: Sequence[JsonMapping]        # Confidence scores
    statistics: BuildingStatistics           # Computed statistics
```

### Statistics

```python
@dataclass(frozen=True, slots=True)
class BuildingStatistics:
    room_count: int = 0
    wall_count: int = 0
    door_count: int = 0
    window_count: int = 0
    total_room_area: float = 0.0
    average_room_area: float = 0.0
    total_room_perimeter: float = 0.0
    adjacency_edge_count: int = 0
    connectivity_edge_count: int = 0
    front_room_count: int = 0
    average_confidence: float = 0.0
    zones: Mapping[str, int] = field(default_factory=dict)
```

### Validation

The `BuildingModelValidator` checks:
- Metadata presence
- At least one room exists
- Unique room IDs
- Graph references point to valid rooms
- Room-scoped records reference valid rooms

---

## Stage 6: Analysis Modules

### Description
Compute advanced spatial relationships and classifications from the building model.

### Modules
- `adjacency.py`
- `connectivity.py`
- `facing.py`
- `zoning.py`
- `confidence.py`

### Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ANALYSIS PIPELINE                           │
└─────────────────────────────────────────────────────────────────┘

                       ┌─────────────┐
                       │  Building   │
                       │   Model     │
                       └──────┬──────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  ┌───────────┐       ┌───────────┐       ┌───────────┐
  │ Adjacency │       │Connectivity│       │  Facing   │
  │  Analysis │       │  Analysis  │       │ Analysis  │
  └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
        │                     │                     │
        │                     ▼                     │
        │               ┌───────────┐               │
        │               │  Zoning   │               │
        │               │Classification            │
        │               └─────┬─────┘               │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Confidence      │
                    │    Scoring        │
                    └───────────────────┘
```

### 6.1 Adjacency Analysis

**Input:** `list[RoomPolygon]`

**Output:** Adjacency graph

**Algorithm:** O(n²) pairwise comparison
- Compute shared boundary length between room pairs
- Filter by `minimum_shared_wall_length`
- Build bidirectional adjacency records

```python
@dataclass(frozen=True, slots=True)
class RoomAdjacency:
    room_id: str
    room_name: str
    adjacent_rooms: tuple[str, ...]
    shared_boundary_length: Mapping[str, float]
```

### 6.2 Connectivity Analysis

**Input:** `list[RoomPolygon]`, adjacency graph, `list[DoorPoint]`

**Output:** Connectivity graph

**Algorithm:**
- For each adjacent room pair, check if a door lies on shared boundary
- Mark as connected only if door is found

```python
@dataclass(frozen=True, slots=True)
class RoomConnectivity:
    room_id: str
    connected_rooms: tuple[ConnectedRoom, ...]
```

### 6.3 Facing Analysis

**Input:** `list[RoomPolygon]`, `list[ExteriorWall]`, road location

**Output:** Facing information

**Algorithm:**
- Find nearest exterior wall to road text
- Identify rooms touching the front wall
- Determine cardinal direction

```python
@dataclass(frozen=True, slots=True)
class FacingResult:
    road_side: RoadSide
    front_wall_id: str | None
    front_rooms: tuple[str, ...]
```

### 6.4 Zoning Classification

**Input:** Room ID, room name

**Output:** Zoning classification

**Algorithm:** Rule-based lookup from `ZoningRuleBook`

| Room | Zone | Privacy | Preferred Neighbors | Avoid Neighbors |
|------|------|---------|---------------------|-----------------|
| Living | Public | Public | Dining, Sitout | Toilet |
| M.bed room | Private | Private | Toilet | Kitchen, Portico |
| Kitchen | Service | Semi-Private | Dining, Utility | Bedroom |
| Toilet | Service | Private | Bed room | Kitchen, Dining |

```python
@dataclass(frozen=True, slots=True)
class RoomZoning:
    room_id: str
    room_name: str
    zone: str
    privacy: str
    preferred_neighbors: tuple[str, ...]
    avoid_neighbors: tuple[str, ...]
    requires_exterior_wall: bool
    requires_ventilation: bool
    minimum_area: float | None
    maximum_area: float | None
```

### 6.5 Confidence Scoring

**Input:** Room polygon, adjacency, connectivity, facing, metadata

**Output:** Confidence score (0.0–1.0)

**Algorithm:** Weighted scoring

| Factor | Weight | Condition |
|--------|--------|-----------|
| Closed polygon | 0.20 | Polygon is closed |
| Valid geometry | 0.25 | Polygon is valid and non-empty |
| Known room name | 0.15 | Name matches known room types |
| Adjacency available | 0.15 | Adjacency data exists |
| Connectivity available | 0.15 | Connectivity data exists |
| Facing available | 0.10 | Facing data exists |

```python
@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    room_id: str
    confidence: float          # 0.0 to 1.0
    quality: QualityLabel      # Excellent/Good/Fair/Poor
    breakdown: Mapping[str, bool]
```

---

## Stage 7: API & Flutter Integration

### Description
Serve analysis results via REST API and display in Flutter mobile app.

### API Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │   Upload    │    │   Status    │    │   Results   │
  │  Endpoint   │    │  Endpoint   │    │  Endpoint   │
  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   Pipeline      │
                   │  Orchestrator   │
                   └─────────────────┘
```

### Flutter App

```
┌─────────────────────────────────────────────────────────────────┐
│                       FLUTTER APP                                │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │   Upload    │    │  Interactive│    │   Export    │
  │    Screen   │    │ Floor Plan  │    │   Screen    │
  │             │    │   Viewer    │    │             │
  └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Data Flow Summary

```
DXF File
    │
    ▼
[1] Read LINE entities → list[LineEntity]
    │
    ▼
[2] Find parallel pairs → list[ParallelPair]
    │
    ▼
[3] Classify wall widths → list[WallSegment]
    │
    ▼
[4] Merge connected walls → list[LogicalWall]
    │
    ▼
[5] Cast radial rays → list[BoundaryIntersection]
    │
    ▼
[6] Build polygons → list[RoomGraphResult]
    │
    ▼
[7] Compute adjacency → adjacency graph
    │
    ▼
[8] Compute connectivity → connectivity graph
    │
    ▼
[9] Detect facing → facing information
    │
    ▼
[10] Classify zoning → zoning per room
    │
    ▼
[11] Score confidence → confidence per room
    │
    ▼
[12] Aggregate → BuildingModel
    │
    ▼
[13] Serialize → JSON
    │
    ▼
[14] Serve via API → Flutter App
```

---

## Performance Characteristics

| Stage | Time Complexity | Typical Duration |
|-------|-----------------|------------------|
| Line Reading | O(n) | <1s |
| Parallel Detection | O(n²) | 1-5s |
| Wall Classification | O(p) | <1s |
| Wall Merging | O(p) | <1s |
| Boundary Finding | O(r × w × 360) | 2-10s |
| Polygon Building | O(k log k) | <1s |
| Adjacency Analysis | O(r²) | 1-3s |
| Connectivity Analysis | O(r² × d) | <1s |
| Facing Analysis | O(r × w) | <1s |
| Zoning Classification | O(r) | <1s |
| Confidence Scoring | O(r) | <1s |

**Total typical duration: 10-30 seconds per floor plan**

Where:
- n = number of LINE entities
- p = number of parallel pairs
- r = number of rooms
- w = number of walls
- d = number of doors
- k = number of boundary points