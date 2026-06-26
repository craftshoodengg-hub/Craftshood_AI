# Changelog

All notable changes to Craftshood_AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Architecture documentation (`docs/ARCHITECTURE.md`)
- API documentation (`docs/API.md`)
- Pipeline documentation (`docs/PIPELINE.md`)
- Development roadmap (`docs/ROADMAP.md`)

### Changed
- No code changes yet

### Deprecated
- No deprecations

### Removed
- No removals

### Security
- No security changes

---

## [0.1.0] - 2026-06-26

### Added

#### Core Infrastructure
- Modular package architecture with frozen dataclasses and `slots=True`
- JSON serialization/deserialization for all data types
- Configuration objects with validation for all modules
- Convenience wrapper functions for simple API usage
- Logging with `loguru` throughout the codebase

#### Geometry Engine (`geometry_engine/`)
- DXF LINE entity reading from layouts and blocks
- Parallel line pair detection with configurable angle, distance, and overlap tolerances
- Wall-width classification supporting 9" and 4.5" brick walls
- Logical wall merging via DFS-based connected components
- Complete JSON export pipeline

#### Normalizer (`normalizer/`)
- Layer name normalization to `LayerCategory` enum (WALL, DOOR, WINDOW, TEXT, DIMENSION, FURNITURE, COLUMN, STAIR)
- Block name normalization extending layer mappings
- Room label normalization to `RoomName` enum (Living, Bed room, Kitchen, Dining, Toilet, Sitout, Portico)
- Dimension string parsing to decimal feet (supports ft/in, mm, cm, m)
- High-level `Normalizer` facade for unified access

#### Room Graph (`room_graph/`)
- Radial ray casting for boundary detection (360 rays configurable)
- Clockwise polygon construction from boundary points
- Shapely polygon validation and repair (buffer(0))
- Area, perimeter, and centroid calculation
- Room graph JSON export

#### Building Model (`building_model/`)
- `BuildingModel` aggregate containing all analysis results
- `BuildingStatistics` calculation (room counts, areas, averages, zones, confidence)
- `BuildingModelValidator` with referential integrity checks
- `BuildingModelSerializer` with JSON import/export and Shapely geometry support
- `BuildingModelBuilder` with automatic statistics computation

#### Analysis Modules
- **Adjacency** (`adjacency.py`) — Room-to-room adjacency via shared boundary length with configurable minimum
- **Connectivity** (`connectivity.py`) — Door-based room connectivity using provided door points
- **Facing** (`facing.py`) — Road-facing wall and front-room detection with cardinal direction inference
- **Zoning** (`zoning.py`) — Room classification into Public/Private/Service zones with configurable rules
- **Confidence** (`confidence.py`) — Weighted confidence scoring (0.0–1.0) with quality labels (Excellent/Good/Fair/Poor)

#### Backend (`backend/`)
- FastAPI application structure
- CAD text intelligence package (`cad_intelligence/`)
  - TEXT and MTEXT entity extraction
  - Rule-based room label detection
  - Floor title detection
  - Built-up area detection
  - Road label detection
  - Plot dimension detection
  - Complete DXF analysis JSON export
- DWG parser package (`dwg_parser/`)
  - Entity counting
  - Layer analysis
  - Export utilities

#### Tests
- Unit tests for adjacency graph construction
- Unit tests for building model, serializer, validator, and statistics
- Unit tests for confidence scoring
- Unit tests for connectivity graph construction
- Unit tests for facing detection
- Unit tests for geometry engine (line reader, parallel detector, wall classifier, merger)
- Unit tests for normalizer (layer, block, text, unit)
- Unit tests for room graph (boundary finder, polygon builder, area calculator)
- Unit tests for zoning classification

### Changed
- Initial release — no previous version to compare

### Deprecated
- No deprecations in initial release

### Removed
- No removals in initial release

### Security
- No security changes in initial release

---

## [0.2.0] - Planned

### Planned
- FastAPI endpoint implementation for DXF file upload and analysis
- Authentication system (API key / JWT)
- Async background task processing
- Result caching with Redis
- Database persistence (PostgreSQL)
- WebSocket support for real-time progress updates
- Rate limiting
- Health check endpoints
- OpenAPI documentation
- Docker containerization

---

## [0.3.0] - Planned

### Planned
- POLYLINE and LWPOLYLINE support in geometry engine
- ARC and CIRCLE entity support
- Spatial indexing (R-tree) for O(n log n) parallel detection
- Configurable wall type definitions (JSON/YAML)
- Automatic room center detection from text labels
- Room detection without text labels (geometry-only)
- Door/window detection from block references
- Corridor and utility room detection

---

## [0.4.0] - Planned

### Planned
- Furniture detection from block references
- Stair detection from parallel lines and text labels
- Column detection from filled circles/rectangles
- Multi-floor building support
- Electrical layout detection
- Plumbing layout detection
- HVAC layout detection

---

## [0.5.0] - Planned

### Planned
- ML-based room detection (CNN/Transformer models)
- ML-based wall detection
- ML-based door/window detection
- OCR for handwritten text recognition
- Anomaly detection for unusual layouts
- Design suggestion engine
- Code compliance checker
- RAG knowledge base for building codes

---

## [0.6.0] - Planned

### Planned
- 3D model generation from 2D plans
- BIM export to IFC format
- IFC import and analysis
- Point cloud integration
- Cost estimation engine
- Bill of Quantities (BOQ) generation
- Structural analysis basics
- Energy efficiency estimation

---

## [0.7.0] - Planned

### Planned
- Flutter mobile app
- Interactive floor plan viewer
- Real-time collaboration
- Annotation system
- Export to PDF/PNG/SVG
- AI chatbot for plan queries
- Multi-user support with roles

---

## [1.0.0] - Planned

### Planned
- Production-ready release
- Full documentation
- Performance optimization
- Comprehensive test coverage
- CI/CD pipeline
- Monitoring and alerting
- Enterprise features