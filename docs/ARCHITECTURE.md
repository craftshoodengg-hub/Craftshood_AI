# Craftshood_AI — Architecture Documentation

## 1. Overall Architecture

Craftshood_AI is an **AI-powered architectural floor plan understanding engine** that converts CAD/DXF floor plans into structured building intelligence. The system follows a **modular pipeline architecture** where each stage transforms data and passes it to the next stage.

The codebase is organized into:
- **Core pipeline packages** — `geometry_engine`, `normalizer`, `room_graph`, `building_model`
- **Analysis modules** — `adjacency`, `connectivity`, `facing`, `zoning`, `confidence`
- **Backend services** — `backend/` (API, DWG parsing, CAD intelligence)
- **Tests** — `tests/` (unit tests for all modules)

All data flows through the pipeline as **immutable frozen dataclasses** with `slots=True` for memory efficiency and type safety.

---

## 2. Complete Pipeline

```
DXF File
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Normalization (normalizer/)                       │
│  - Layer names → LayerCategory enum                         │
│  - Block names → LayerCategory enum                         │
│  - Room labels → RoomName enum                              │
│  - Dimension strings → decimal feet (Dimension)             │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: Geometry Extraction (geometry_engine/)            │
│  - Read LINE entities from DXF                              │
│  - Detect parallel line pairs                                │
│  - Classify wall-width pairs (brick wall types)              │
│  - Merge connected wall segments into logical walls          │
│  - Export to JSON                                            │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: Room Detection (room_graph/)                      │
│  - Cast radial rays from room center points                 │
│  - Find nearest wall intersections                          │
│  - Build Shapely polygons from boundary points              │
│  - Calculate area, perimeter, centroid                      │
│  - Export room graph JSON                                    │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: Building Model (building_model/)                  │
│  - Aggregate all module outputs                              │
│  - Build unified BuildingModel                              │
│  - Calculate statistics (room counts, areas, etc.)          │
│  - Validate model consistency                                │
│  - Serialize/deserialize JSON                                │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 5: Analysis Modules                                  │
│  5a. Adjacency (adjacency.py)                                │
│      - Detect room-to-room adjacency via shared boundaries   │
│  5b. Connectivity (connectivity.py)                          │
│      - Door-based room connectivity                          │
│  5c. Facing (facing.py)                                      │
│      - Road-facing wall and front-room detection             │
│  5d. Zoning (zoning.py + zoning_rules.py)                    │
│      - Room classification (Public/Private/Service zones)    │
│  5e. Confidence (confidence.py)                              │
│      - Weighted confidence scoring (0.0–1.0)                │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 6: API (backend/)                                    │
│  - FastAPI application (backend/app.py)                      │
│  - DWG parsing (backend/dwg_parser/)                         │
│  - CAD text intelligence (backend/cad_intelligence/)         │
│  - JSON export and serving                                   │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 7: Flutter App (not in this repository)              │
│  - Client consumer of the API                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Folder Residences

### `geometry_engine/`
**Responsibility:** LINE-based wall extraction from DXF files.

| Module | Purpose |
|--------|---------|
| `line_reader.py` | Read LINE entities from DXF, normalize into `LineEntity` objects |
| `parallel_detector.py` | Find candidate parallel line pairs with distance/overlap tolerances |
| `wall_classifier.py` | Classify parallel pairs as supported brick-wall widths |
| `wall_merger.py` | Merge connected wall segments into logical walls |
| `wall_exporter.py` | Orchestrate pipeline and export JSON |

### `normalizer/`
**Responsibility:** Normalize extracted CAD information (labels, dimensions) without mutating geometry.

| Module | Purpose |
|--------|---------|
| `normalizer.py` | High-level facade for all normalizers |
| `layer_normalizer.py` | Normalize layer names → `LayerCategory` enum |
| `block_normalizer.py` | Normalize block names → `LayerCategory` enum |
| `text_normalizer.py` | Normalize room labels → `RoomName` enum |
| `unit_normalizer.py` | Parse dimension strings → decimal feet |

### `room_graph/`
**Responsibility:** Build room boundary polygons from room centers and logical walls.

| Module | Purpose |
|--------|---------|
| `graph_builder.py` | Orchestrate room graph building |
| `boundary_finder.py` | Radial ray casting to find wall intersections |
| `polygon_builder.py` | Sort boundary points clockwise, build Shapely polygon |
| `area_calculator.py` | Calculate area, perimeter, centroid |
| `room_exporter.py` | Export room graph JSON |

### `building_model/`
**Responsibility:** Aggregate all module outputs into a unified building model.

| Module | Purpose |
|--------|---------|
| `builder.py` | Construct `BuildingModel` from upstream module outputs |
| `models.py` | Core dataclasses (`BuildingModel`, `BuildingStatistics`, `ValidationIssue`, etc.) |
| `serializer.py` | JSON serialization/deserialization |
| `statistics.py` | Calculate aggregate building metrics |
| `validator.py` | Validate model consistency and completeness |

### `backend/`
**Responsibility:** API, DWG parsing, and CAD text intelligence.

| Folder/File | Purpose |
|-------------|---------|
| `app.py` | FastAPI application entry point |
| `config.py` | Application configuration |
| `requirements.txt` | Python dependencies |
| `cad_intelligence/` | Rule-based CAD text extraction and analysis |
| `dwg_parser/` | DWG file parsing utilities |
| `Craftshood_AI/` | (Empty/placeholder directory) |
| `outputs/` | Output directory for analysis results |
| `test_files/` | Test DXF/DWG files |

### `tests/`
**Responsibility:** Unit tests for all modules.

| File | Tests |
|------|-------|
| `test_adjacency.py` | Adjacency graph construction |
| `test_building_model.py` | Building model, serializer, validator, statistics |
| `test_confidence.py` | Confidence scoring |
| `test_connectivity.py` | Connectivity graph construction |
| `test_facing.py` | Road-facing detection |
| `test_geometry_engine.py` | Line reader, parallel detector, wall classifier, merger |
| `test_normalizer.py` | Layer, block, text, unit normalization |
| `test_room_graph.py` | Boundary finder, polygon builder, area calculator |
| `test_zoning.py` | Zoning classification |

### Top-level scripts
**Responsibility:** Standalone analysis modules.

| File | Purpose |
|------|---------|
| `adjacency.py` | Room adjacency graph construction |
| `confidence.py` | Room confidence scoring |
| `connectivity.py` | Door-based room connectivity |
| `facing.py` | Road-facing wall detection |
| `zoning.py` | Room zoning classification |
| `zoning_rules.py` | Zoning rules and room type definitions |
| `zoning_exporter.py` | Zoning results JSON export |

---

## 4. Module Interactions

```
┌──────────────────────────────────────────────────────────────────────┐
│                           backend/app.py                             │
│                    (FastAPI orchestrator)                            │
└──────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ cad_intelligence│         │ geometry_engine │         │   normalizer    │
│               │         │                 │         │                 │
│ text_extractor│         │ line_reader     │         │ layer_normalizer│
│ room_detector │         │ parallel_detector│        │ block_normalizer│
│ plot_detector │         │ wall_classifier │         │ text_normalizer │
│ json_exporter │         │ wall_merger     │         │ unit_normalizer │
└───────────────┘         │ wall_exporter   │         └─────────────────┘
        │                 └─────────────────┘                  │
        │                           │                          │
        │                           ▼                          │
        │                 ┌─────────────────┐                  │
        │                 │   room_graph    │                  │
        │                 │                 │                  │
        │                 │ boundary_finder │                  │
        │                 │ polygon_builder │                  │
        │                 │ area_calculator │                  │
        │                 │ graph_builder   │                  │
        │                 │ room_exporter   │                  │
        │                 └─────────────────┘                  │
        │                           │                          │
        └───────────────────────────┼──────────────────────────┘
                                    ▼
                        ┌─────────────────────┐
                        │   building_model     │
                        │                     │
                        │ builder             │
                        │ models              │
                        │ serializer          │
                        │ statistics          │
                        │ validator           │
                        └─────────────────────┘
                                    │
        ┌───────────────┬───────────┼───────────┬───────────────┐
        ▼               ▼           ▼           ▼               ▼
   ┌─────────┐    ┌──────────┐ ┌────────┐ ┌────────┐    ┌──────────┐
   │adjacency│    │connectivity│ │facing  │ │zoning  │    │confidence│
   └─────────┘    └──────────┘ └────────┘ └────────┘    └──────────┘
```

**Key dependencies:**
- `geometry_engine` → `room_graph` (provides `LogicalWall`)
- `room_graph` → `building_model` (provides room polygons)
- `adjacency` → `connectivity` and `facing` (provides `RoomPolygon`)
- `normalizer` → used by all modules for label normalization
- `cad_intelligence` → provides room labels and text entities for room center points

---

## 5. Data Flow

### Primary Data Types

| Type | Package | Description |
|------|---------|-------------|
| `LineEntity` | geometry_engine | Normalized DXF LINE with id, start, end, length, angle, layer |
| `ParallelPair` | geometry_engine | Two parallel lines with perpendicular distance |
| `WallSegment` | geometry_engine | Classified wall with type and width |
| `LogicalWall` | geometry_engine | Merged connected wall segments |
| `RoomCenter` | room_graph | Known center point of a room label |
| `BoundaryIntersection` | room_graph | Nearest wall intersection for a radial ray |
| `RoomGraphResult` | room_graph | Complete room polygon with metrics |
| `RoomPolygon` | adjacency | Room polygon with id and name for graph analysis |
| `BuildingModel` | building_model | Aggregated model with all analysis results |
| `BuildingStatistics` | building_model | Computed metrics (counts, areas, averages) |
| `TextEntity` | cad_intelligence | Extracted TEXT/MTEXT from DXF |
| `Detection` | cad_intelligence | Detected label (room, floor, road, etc.) |

### Flow Example

```
DXF File
   │
   ▼
LineReader.read() → list[LineEntity]
   │
   ▼
ParallelDetector.find_pairs() → list[ParallelPair]
   │
   ▼
WallClassifier.classify() → list[WallSegment]
   │
   ▼
WallMerger.merge() → list[LogicalWall]
   │
   ▼
RoomGraphBuilder.build_room() → RoomGraphResult
   │
   ▼
AdjacencyBuilder.build() → adjacency graph
   │
   ▼
ConnectivityBuilder.build() → connectivity graph
   │
   ▼
FacingDetector.detect() → facing information
   │
   ▼
ZoningClassifier.classify() → zoning per room
   │
   ▼
ConfidenceScorer.score() → confidence per room
   │
   ▼
BuildingModelBuilder.build() → BuildingModel
   │
   ▼
BuildingModelSerializer.to_json() → JSON output
```

---

## 6. External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `ezdxf` | ≥1.3.0 | DXF file reading and entity extraction |
| `shapely` | ≥2.0.0 | Geometric operations (intersections, buffers, polygons) |
| `numpy` | latest | Vector math, array operations |
| `pandas` | latest | Data manipulation (used in backend) |
| `fastapi` | latest | REST API framework |
| `uvicorn` | latest | ASGI server for FastAPI |
| `orjson` | latest | Fast JSON serialization |
| `loguru` | latest | Logging |
| `python-dotenv` | latest | Environment variable loading |
| `pydantic` | latest | Data validation (FastAPI dependency) |
| `pytest` | latest | Testing framework |

---

## 7. Current Limitations

### Geometry Engine
- **LINE-only**: Only processes LINE entities; POLYLINE, LWPOLYLINE, and ARC are ignored
- **O(n²) parallel detection**: Brute-force pairwise comparison is slow for large drawings
- **Limited wall types**: Only supports 9" and 4.5" brick walls; no concrete, drywall, or custom types
- **Midpoint distance**: `perpendicular_distance()` uses only midpoint, not full carrier line distance

### Room Graph
- **Radial ray casting**: Fixed 360 rays may miss thin walls or create sparse boundaries
- **No door/window detection**: Room boundaries don't account for openings
- **Requires known room centers**: Cannot detect rooms without text labels

### Analysis Modules
- **Adjacency**: O(n²) pairwise comparison for room adjacency
- **Connectivity**: Requires pre-provided door locations; does not detect doors
- **Facing**: Requires pre-provided road text location and exterior wall geometry
- **Zoning**: Hardcoded rules; no support for custom zoning configurations
- **Confidence**: Fixed weights; no machine learning or adaptive scoring

### Backend
- **No authentication**: API has no security layer
- **No async processing**: Long-running analyses block the request
- **No caching**: Repeated analyses of the same file are not cached

### General
- **No database**: All data is in-memory or JSON files
- **No configuration file**: Settings are hardcoded or environment variables only
- **Limited test coverage**: Some modules lack comprehensive tests
- **No CI/CD**: No automated testing or deployment pipeline visible

---

## 8. Future Architecture

### Short-term Improvements
1. **Spatial indexing**: Replace O(n²) parallel detection with R-tree or KD-tree
2. **Extended entity support**: Add POLYLINE, LWPOLYLINE, ARC, and CIRCLE support
3. **Configurable wall types**: Load wall width definitions from JSON/YAML
4. **Async processing**: Use background tasks for long-running analyses
5. **Response caching**: Cache results by file hash

### Medium-term Improvements
1. **Door/window detection**: Detect openings from geometry or block references
2. **Machine learning**: Replace rule-based detection with trained models
3. **Database persistence**: Store analysis results in PostgreSQL/SQLite
4. **Plugin architecture**: Allow custom analysis modules
5. **WebSocket support**: Real-time progress updates for long analyses

### Long-term Vision
1. **Full BIM support**: Extend to IFC and Revit formats
2. **3D reconstruction**: Generate 3D building models from 2D plans
3. **Multi-floor support**: Handle staircases and vertical connections
4. **Collaborative editing**: Real-time multi-user analysis
5. **Mobile API**: Optimized API for Flutter mobile app

---

## Appendix: File Tree

```
craftshood_ai/
├── .gitignore
├── adjacency.py                    # Room adjacency graph
├── confidence.py                   # Room confidence scoring
├── connectivity.py                 # Door-based connectivity
├── facing.py                       # Road-facing detection
├── zoning.py                       # Room zoning classification
├── zoning_rules.py                 # Zoning rules and room types
├── zoning_exporter.py              # Zoning JSON export
├── backend/
│   ├── app.py                      # FastAPI application
│   ├── config.py                   # Configuration
│   ├── requirements.txt            # Dependencies
│   ├── cad_intelligence/
│   │   ├── __init__.py
│   │   ├── json_exporter.py        # DXF analysis export
│   │   ├── plot_detector.py        # Plot dimension detection
│   │   ├── room_detector.py        # Room label detection
│   │   └── text_extractor.py       # TEXT/MTEXT extraction
│   ├── dwg_parser/
│   │   ├── __init__.py
│   │   ├── entity_counter.py       # Entity counting
│   │   ├── exporter.py             # Export utilities
│   │   ├── layer_analyzer.py       # Layer analysis
│   │   └── reader.py               # DWG file reading
│   ├── Craftshood_AI/              # (Empty)
│   ├── outputs/                    # Analysis outputs
│   └── test_files/                 # Test DXF/DWG files
├── building_model/
│   ├── __init__.py
│   ├── builder.py                  # BuildingModel builder
│   ├── models.py                   # Core dataclasses
│   ├── serializer.py               # JSON serialization
│   ├── statistics.py               # Statistics calculation
│   └── validator.py                # Model validation
├── data/                           # Data files
├── geometry_engine/
│   ├── __init__.py
│   ├── line_reader.py              # DXF LINE reader
│   ├── parallel_detector.py        # Parallel pair detection
│   ├── wall_classifier.py          # Wall width classification
│   ├── wall_merger.py              # Logical wall merging
│   └── wall_exporter.py            # JSON export
├── normalizer/
│   ├── __init__.py
│   ├── block_normalizer.py         # Block name normalization
│   ├── layer_normalizer.py         # Layer name normalization
│   ├── normalizer.py               # High-level facade
│   ├── text_normalizer.py          # Room label normalization
│   └── unit_normalizer.py          # Dimension normalization
├── room_graph/
│   ├── __init__.py
│   ├── area_calculator.py          # Polygon metrics
│   ├── boundary_finder.py          # Radial ray casting
│   ├── graph_builder.py            # Room graph orchestration
│   ├── polygon_builder.py           # Polygon construction
│   └── room_exporter.py            # Room JSON export
├── tests/
│   ├── test_adjacency.py
│   ├── test_building_model.py
│   ├── test_confidence.py
│   ├── test_connectivity.py
│   ├── test_facing.py
│   ├── test_geometry_engine.py
│   ├── test_normalizer.py
│   ├── test_room_graph.py
│   └── test_zoning.py
└── venv/                           # Python virtual environment