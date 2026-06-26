# Craftshood_AI — Development Roadmap

---

## Vision

Craftshood_AI aims to become a **comprehensive AI-powered architectural floor plan understanding engine** that transforms raw CAD/DXF drawings into rich, structured building intelligence. The long-term vision is to:

1. **Automate building analysis** — Eliminate manual measurement, annotation, and compliance checking
2. **Enable intelligent design** — Provide AI-driven suggestions for space optimization, code compliance, and cost reduction
3. **Bridge CAD and BIM** — Convert 2D drawings into 3D building information models without manual modeling
4. **Democratize architecture** — Make professional-grade analysis accessible via a simple API and mobile app
5. **Support the full lifecycle** — From initial design to construction documentation and facility management

The ultimate goal is a system that can look at any architectural floor plan and understand it like an experienced architect — identifying rooms, relationships, structural elements, MEP systems, and design intent.

---

## Current Status

Based on repository analysis, the project is approximately **35-40% complete** toward a production-ready AI floor plan engine.

| Category | Completion | Notes |
|----------|------------|-------|
| Core Pipeline Structure | 80% | Architecture is solid, modular, and extensible |
| Geometry Extraction | 60% | LINE-only; needs POLYLINE, ARC, CIRCLE support |
| Normalization | 70% | Layer, block, text, and unit normalization working |
| Room Detection | 50% | Radial ray casting works but requires known centers |
| Building Model | 75% | Aggregation, serialization, validation complete |
| Analysis Modules | 60% | Adjacency, connectivity, facing, zoning, confidence done |
| Backend API | 30% | FastAPI app exists but lacks key features |
| AI/ML Components | 0% | No machine learning or deep learning yet |
| Mobile App | 0% | Flutter app not in this repository |
| Testing | 50% | Core modules tested; edge cases and integration tests missing |
| Documentation | 40% | ARCHITECTURE.md created; API docs, user guides missing |

**Overall estimate: ~35-40% of a production-ready system.**

---

## Completed

### Core Infrastructure
- [x] Project structure with modular package architecture
- [x] Frozen dataclass models with `slots=True` for all data types
- [x] JSON serialization/deserialization for all data types
- [x] Configuration objects with validation for all modules
- [x] Convenience wrapper functions for simple API usage
- [x] Logging with `loguru` throughout the codebase

### Geometry Engine
- [x] DXF LINE entity reading (layouts and blocks)
- [x] Parallel line pair detection with angle/distance/overlap tolerances
- [x] Wall-width classification (9" and 4.5" brick walls)
- [x] Logical wall merging via connected components (DFS)
- [x] JSON export pipeline

### Normalizer
- [x] Layer name normalization to `LayerCategory` enum
- [x] Block name normalization to `LayerCategory` enum
- [x] Room label normalization to `RoomName` enum
- [x] Dimension string parsing to decimal feet (supports ft/in, mm, cm, m)
- [x] High-level `Normalizer` facade

### Room Graph
- [x] Radial ray casting for boundary detection
- [x] Clockwise polygon construction from boundary points
- [x] Shapely polygon validation and repair
- [x] Area, perimeter, and centroid calculation
- [x] Room graph JSON export

### Building Model
- [x] `BuildingModel` aggregate with all analysis results
- [x] `BuildingStatistics` calculation (counts, areas, averages, zones)
- [x] `BuildingModelValidator` with referential integrity checks
- [x] `BuildingModelSerializer` with JSON import/export
- [x] `BuildingModelBuilder` with automatic statistics computation

### Analysis Modules
- [x] **Adjacency** — Room-to-room adjacency via shared boundary length
- [x] **Connectivity** — Door-based connectivity (requires provided door points)
- [x] **Facing** — Road-facing wall and front-room detection
- [x] **Zoning** — Room classification (Public/Private/Service) with configurable rules
- [x] **Confidence** — Weighted confidence scoring (0.0–1.0) with quality labels

### Backend
- [x] FastAPI application structure
- [x] CAD text intelligence (room, floor, road, built-up area detection)
- [x] Text entity extraction (TEXT and MTEXT)
- [x] Plot dimension detection
- [x] DXF analysis JSON export

### Tests
- [x] Unit tests for adjacency, building model, confidence, connectivity
- [x] Unit tests for facing, geometry engine, normalizer, room graph, zoning

---

## In Progress

### Geometry Engine (Partial)
- [x] LINE entity support
- [ ] POLYLINE and LWPOLYLINE support
- [ ] ARC and CIRCLE support
- [ ] Spatial indexing for O(n log n) parallel detection
- [ ] Configurable wall type definitions (JSON/YAML)

### Room Detection (Partial)
- [x] Radial ray casting from known centers
- [ ] Automatic room center detection from text labels
- [ ] Room detection without text labels (geometry-only)
- [ ] Door/window-aware boundary detection

### Backend API (Partial)
- [x] FastAPI app structure
- [x] DXF text analysis endpoints (planned)
- [ ] Authentication and authorization
- [ ] Async background task processing
- [ ] WebSocket support for real-time progress
- [ ] Rate limiting and request validation

### Testing (Partial)
- [x] Core unit tests for all existing modules
- [ ] Integration tests for full pipeline
- [ ] Performance benchmarks
- [ ] Edge case coverage (empty drawings, malformed files, large files)

---

## Missing Modules

### Critical (Required for MVP)
| Module | Description | Priority |
|--------|-------------|----------|
| **DXF File Upload API** | Endpoint to upload and process DXF files | High |
| **Room Auto-Detection** | Detect rooms without text labels using geometry | High |
| **Door/Window Detection** | Identify openings from block references or geometry | High |
| **Wall Thickness Detection** | Measure actual wall thickness from drawings | High |
| **Result Caching** | Cache analysis results by file hash | Medium |
| **Error Handling** | Graceful handling of malformed DXF files | High |
| **Configuration Management** | YAML/JSON config file support | Medium |

### Important (Required for Production)
| Module | Description | Priority |
|--------|-------------|----------|
| **Authentication** | API key or JWT-based auth | High |
| **Async Processing** | Background tasks for long-running analyses | High |
| **Database Persistence** | Store results in PostgreSQL/SQLite | Medium |
| **Health Checks** | System health and readiness endpoints | Medium |
| **API Documentation** | OpenAPI/Swagger docs | Medium |
| **Logging Aggregation** | Structured logging with correlation IDs | Medium |
| **Docker Support** | Containerization for deployment | Medium |

### Advanced (Differentiating Features)
| Module | Description | Priority |
|--------|-------------|----------|
| **Furniture Detection** | Identify beds, sofas, tables from blocks | Medium |
| **Stair Detection** | Identify staircases and vertical circulation | Medium |
| **Column Detection** | Identify structural columns | Medium |
| **Multi-Floor Support** | Handle multiple floors and stair connections | Medium |
| **Electrical Layouts** | Detect switches, outlets, lighting | Low |
| **Plumbing Layouts** | Detect fixtures, pipes, drains | Low |
| **HVAC Layouts** | Detect ducts, vents, units | Low |
| **3D Model Generation** | Generate 3D building from 2D plan | Low |
| **BIM/IFC Export** | Export to Industry Foundation Classes | Low |
| **AI Design Suggestions** | ML-based space optimization | Low |
| **Cost Estimation** | Material and labor cost calculation | Low |
| **BOQ Generation** | Bill of Quantities generation | Low |

---

## Development Phases

### Phase 1: Geometry Engine
**Status:** In Progress
**Goal:** Robust geometric entity extraction and wall detection

- [x] LINE entity reading
- [x] Parallel pair detection
- [x] Wall classification
- [x] Wall merging
- [ ] Add POLYLINE/LWPOLYLINE support
- [ ] Add ARC/CIRCLE support
- [ ] Implement spatial indexing (R-tree)
- [ ] Configurable wall type definitions
- [ ] Improve perpendicular distance calculation
- [ ] Handle nested blocks and xrefs

**Estimated effort:** 2-3 weeks

---

### Phase 2: Normalization
**Status:** Complete (core)
**Goal:** Comprehensive CAD data normalization

- [x] Layer normalization
- [x] Block normalization
- [x] Room label normalization
- [x] Dimension normalization
- [ ] Add hatch pattern normalization
- [ ] Add linetype normalization
- [ ] Add elevation/height normalization
- [ ] Multi-language room label support
- [ ] Custom mapping import/export (YAML/JSON)

**Estimated effort:** 1 week

---

### Phase 3: Room Detection
**Status:** In Progress
**Goal:** Automatic room boundary detection

- [x] Radial ray casting from known centers
- [x] Polygon construction
- [x] Area/perimeter calculation
- [ ] Automatic room center detection from text
- [ ] Room detection without text labels
- [ ] Door/window-aware boundaries
- [ ] Handle non-convex rooms
- [ ] Handle rooms with holes (courtyards)
- [ ] Room merging/splitting logic

**Estimated effort:** 3-4 weeks

---

### Phase 4: Building Intelligence
**Status:** Complete (core)
**Goal:** Comprehensive building analysis and scoring

- [x] Adjacency graph
- [x] Connectivity graph
- [x] Facing detection
- [x] Zoning classification
- [x] Confidence scoring
- [x] Building model aggregation
- [x] Statistics calculation
- [x] Model validation
- [ ] Door/window detection (enables full connectivity)
- [ ] Corridor detection
- [ ] Utility room detection
- [ ] Balcony/terrace detection

**Estimated effort:** 2-3 weeks

---

### Phase 5: AI Reasoning
**Status:** Not Started
**Goal:** ML-based detection and intelligent analysis

- [ ] Train room detection model (CNN/Transformer)
- [ ] Train wall detection model
- [ ] Train door/window detection model
- [ ] Train furniture detection model
- [ ] Train stair detection model
- [ ] Train column detection model
- [ ] OCR for handwritten text recognition
- [ ] Anomaly detection (unusual layouts)
- [ ] Design suggestion engine
- [ ] Code compliance checker
- [ ] Space optimization recommendations
- [ ] RAG knowledge base for building codes

**Estimated effort:** 8-12 weeks

---

### Phase 6: Backend API
**Status:** In Progress
**Goal:** Production-ready API with full feature set

- [x] FastAPI app structure
- [x] DXF text analysis
- [ ] DXF file upload endpoint
- [ ] Full pipeline orchestration endpoint
- [ ] Authentication (API key / JWT)
- [ ] Async background tasks (Celery/ARQ)
- [ ] WebSocket progress updates
- [ ] Result caching (Redis)
- [ ] Database persistence (PostgreSQL)
- [ ] Rate limiting
- [ ] Health check endpoints
- [ ] OpenAPI documentation
- [ ] Docker containerization
- [ ] CI/CD pipeline

**Estimated effort:** 3-4 weeks

---

### Phase 7: Flutter Integration
**Status:** Not Started
**Goal:** Mobile app for field use

- [ ] Flutter app architecture
- [ ] DXF file upload UI
- [ ] Analysis progress UI
- [ ] Interactive floor plan viewer
- [ ] Room list and details
- [ ] 3D model viewer
- [ ] Export to PDF/PNG
- [ ] Offline mode
- [ ] Push notifications
- [ ] Collaboration features

**Estimated effort:** 6-8 weeks

---

## Future Features

### Detection Capabilities
- **Furniture Detection** — Identify beds, sofas, tables, wardrobes from block references or geometry
- **Door/Window Detection** — Detect openings from block references, line patterns, or gap analysis
- **Stair Detection** — Identify staircases from parallel lines and text labels
- **Column Detection** — Detect structural columns from filled circles or rectangles
- **Fixture Detection** — Identify plumbing fixtures, electrical outlets, switches

### Building Systems
- **Electrical Layouts** — Map circuits, panels, switches, and lighting
- **Plumbing Layouts** — Trace water supply, drainage, and gas lines
- **HVAC Layouts** — Detect ducts, vents, and equipment
- **Fire Safety** — Identify exits, extinguishers, sprinklers

### Multi-Floor Support
- **Multi-Floor Buildings** — Handle multiple levels with vertical connections
- **Stair/Ramp Analysis** — Analyze vertical circulation
- **Elevation Analysis** — Process elevation sections

### 3D and BIM
- **3D Model Generation** — Extrude 2D plans into 3D building models
- **BIM Export** — Export to IFC format for BIM software
- **IFC Import** — Read and analyze existing BIM models
- **Point Cloud Integration** — Process 3D scan data

### AI-Powered Features
- **AI Design Suggestions** — Recommend layout improvements
- **Cost Estimation** — Predict construction costs from drawings
- **BOQ Generation** — Auto-generate Bill of Quantities
- **Structural Analysis** — Basic structural feasibility checks
- **Energy Analysis** — Estimate energy efficiency
- **AI Chatbot** — Natural language queries about floor plans
- **RAG Knowledge Base** — Building codes, standards, best practices

### Collaboration
- **Multi-User Support** — Team-based analysis and review
- **Annotation System** — Add comments and markups
- **Version History** — Track changes across revisions
- **Export Formats** — PDF, DWG, DXF, PNG, SVG output

---

## Timeline Estimate

| Phase | Status | Est. Duration | Target |
|-------|--------|---------------|--------|
| Phase 1: Geometry Engine | In Progress | 2-3 weeks | Q3 2026 |
| Phase 2: Normalization | Complete | 1 week | Q3 2026 |
| Phase 3: Room Detection | In Progress | 3-4 weeks | Q3 2026 |
| Phase 4: Building Intelligence | Complete | 2-3 weeks | Q4 2026 |
| Phase 5: AI Reasoning | Not Started | 8-12 weeks | Q1 2027 |
| Phase 6: Backend API | In Progress | 3-4 weeks | Q4 2026 |
| Phase 7: Flutter Integration | Not Started | 6-8 weeks | Q1 2027 |

**Total estimated time to production MVP: ~6-8 months**
**Total estimated time to full feature set: ~12-18 months**

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Room detection accuracy | >95% |
| Wall detection accuracy | >90% |
| Processing time per floor plan | <30 seconds |
| API uptime | 99.9% |
| Supported DXF versions | AutoCAD 2000+ |
| Concurrent users | 100+ |
| Mobile app rating | 4.5+ stars |

---

## Contributing

When contributing to any phase:

1. Read existing code before making changes
2. Follow the established patterns (frozen dataclasses, config objects, convenience wrappers)
3. Add type hints to all functions
4. Update tests when changing behavior
5. Maintain backward compatibility
6. Document new features in this roadmap