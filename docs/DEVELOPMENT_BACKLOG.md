# Craftshood_AI — Development Backlog

**Version:** 1.0.0  
**Date:** 2026-06-26  
**Status:** Active  
**Target:** Version 1.0.0 Production Release

---

## Table of Contents

1. [Sprint 1: Code Quality & Consolidation](#sprint-1-code-quality--consolidation)
2. [Sprint 2: Performance Optimization](#sprint-2-performance-optimization)
3. [Sprint 3: Extended Geometry Support](#sprint-3-extended-geometry-support)
4. [Sprint 4: Room Detection Improvements](#sprint-4-room-detection-improvements)
5. [Sprint 5: Door/Window Detection](#sprint-5-doorwindow-detection)
6. [Sprint 6: Backend API — Core](#sprint-6-backend-api--core)
7. [Sprint 7: Backend API — Security](#sprint-7-backend-api--security)
8. [Sprint 8: Async Processing & Caching](#sprint-8-async-processing--caching)
9. [Sprint 9: Database & File Management](#sprint-9-database--file-management)
10. [Sprint 10: Testing & Quality Assurance](#sprint-10-testing--quality-assurance)
11. [Sprint 11: Documentation & Developer Experience](#sprint-11-documentation--developer-experience)
12. [Sprint 12: Production Readiness](#sprint-12-production-readiness)
13. [Sprint 13: Flutter App — Core](#sprint-13-flutter-app--core)
14. [Sprint 14: Flutter App — Viewer & Reports](#sprint-14-flutter-app--viewer--reports)
15. [Sprint 15: AI Features — Phase 1](#sprint-15-ai-features--phase-1)
16. [Sprint 16: Vastu Analysis](#sprint-16-vastu-analysis)
17. [Sprint 17: Building Code Compliance](#sprint-17-building-code-compliance)
18. [Sprint 18: AI Features — Phase 2](#sprint-18-ai-features--phase-2)
19. [Sprint 19: Advanced Features](#sprint-19-advanced-features)
20. [Sprint 20: Production Release](#sprint-20-production-release)

---

## Sprint 1: Code Quality & Consolidation

### Goal
Eliminate code duplication, remove dead code, and establish shared utility modules to reduce maintenance burden and improve code quality.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 1.1 | Create `geometry_utils.py` with shared `linear_length()` function | High | 2 |
| 1.2 | Create `validation.py` with shared `validate_room_polygons()` function | High | 2 |
| 1.3 | Create `dxf_utils.py` with shared `safe_dxf_value()` function | Medium | 2 |
| 1.4 | Unify normalization patterns (`normalize_key` vs `_room_key`) | Medium | 3 |
| 1.5 | Remove empty files in `backend/dwg_parser/` | Low | 1 |
| 1.6 | Remove empty `backend/Craftshood_AI/` directory | Low | 0.5 |
| 1.7 | Add README to `data/` directory | Low | 0.5 |
| 1.8 | Add `backend/outputs/` to `.gitignore` | Low | 0.5 |
| 1.9 | Update imports in all affected modules | Medium | 2 |
| 1.10 | Run full test suite and verify no regressions | High | 2 |

### Estimated Duration
**1 week** (16 hours)

### Dependencies
None — this sprint can start immediately.

### Deliverables
- New shared utility modules: `geometry_utils.py`, `validation.py`, `dxf_utils.py`
- Removed dead code and empty directories
- All existing tests passing
- Reduced code duplication by ~60%

### Tests to Write
- `test_geometry_utils.py` — Tests for `linear_length()` with various geometry types
- `test_validation.py` — Tests for `validate_room_polygons()` with valid/invalid inputs
- `test_dxf_utils.py` — Tests for `safe_dxf_value()` with mock DXF entities
- Update existing tests to use shared utilities

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Import errors after refactoring | High | Run tests after each module change |
| Breaking existing API | Medium | Maintain backward compatibility |
| Missed duplicate code | Low | Use search_files to find all instances |

### Definition of Done
- [ ] All duplicate functions consolidated into shared modules
- [ ] All empty files/directories removed
- [ ] All imports updated
- [ ] All existing tests passing
- [ ] New utility tests written and passing
- [ ] No reduction in code coverage

---

## Sprint 2: Performance Optimization

### Goal
Replace O(n²) algorithms with optimized alternatives and add caching to improve processing speed for large floor plans.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 2.1 | Implement R-tree spatial indexing in `parallel_detector.py` | High | 8 |
| 2.2 | Optimize `adjacency.py` with spatial indexing | High | 6 |
| 2.3 | Add NumPy vectorization to geometry operations | Medium | 6 |
| 2.4 | Implement result caching by file hash | Medium | 4 |
| 2.5 | Add streaming file reading for large DXF files | Medium | 4 |
| 2.6 | Cache `BuildingModelStatistics` on model | Low | 2 |
| 2.7 | Benchmark performance before/after changes | High | 3 |

### Estimated Duration
**2 weeks** (33 hours)

### Dependencies
- Sprint 1 complete (shared utilities needed for optimization)

### Deliverables
- R-tree spatial indexing for parallel detection
- Spatial indexing for adjacency analysis
- Result caching layer
- Performance benchmarks showing 5-10x improvement

### Tests to Write
- `test_spatial_index.py` — Tests for R-tree operations
- `test_cache.py` — Tests for caching layer
- `test_performance.py` — Performance regression tests
- Update existing tests for optimized modules

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Spatial index bugs | High | Extensive testing with real DXF files |
| Cache invalidation issues | Medium | Use content-based hashing |
| Memory usage increase | Medium | Set cache size limits |

### Definition of Done
- [ ] Parallel detection uses R-tree (O(n log n))
- [ ] Adjacency analysis uses spatial indexing
- [ ] Result caching implemented
- [ ] 5x performance improvement on large files (>1000 lines)
- [ ] All tests passing
- [ ] Performance benchmarks documented

---

## Sprint 3: Extended Geometry Support

### Goal
Add support for POLYLINE, LWPOLYLINE, ARC, and CIRCLE entities to handle complex floor plans.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 3.1 | Add POLYLINE entity reading to `line_reader.py` | High | 6 |
| 3.2 | Add LWPOLYLINE entity reading | High | 4 |
| 3.3 | Add ARC entity reading and conversion | High | 6 |
| 3.4 | Add CIRCLE entity reading | Medium | 3 |
| 3.5 | Update `ParallelDetector` to handle curved entities | High | 6 |
| 3.6 | Add configurable wall type definitions (JSON/YAML) | Medium | 4 |
| 3.7 | Improve perpendicular distance calculation | Medium | 3 |

### Estimated Duration
**2 weeks** (32 hours)

### Dependencies
- Sprint 2 complete (performance optimization needed for complex geometries)

### Deliverables
- POLYLINE, LWPOLYLINE, ARC, CIRCLE support
- Configurable wall type definitions
- Improved distance calculations
- Support for complex floor plans

### Tests to Write
- `test_polyline_reader.py` — Tests for POLYLINE/LWPOLYLINE reading
- `test_arc_reader.py` — Tests for ARC entity handling
- `test_circle_reader.py` — Tests for CIRCLE entity handling
- `test_wall_types.py` — Tests for configurable wall types
- `test_parallel_detector_extended.py` — Tests with new entity types

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Curved entity handling complexity | High | Start with approximation, refine later |
| Breaking existing LINE-only logic | Medium | Keep LINE path separate initially |
| Performance regression | Medium | Benchmark after each entity type |

### Definition of Done
- [ ] All four entity types supported
- [ ] Configurable wall types working
- [ ] Existing tests still passing
- [ ] New tests written with >80% coverage
- [ ] Performance no worse than Sprint 2

---

## Sprint 4: Room Detection Improvements

### Goal
Improve room detection to work without text labels and handle non-convex rooms.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 4.1 | Implement automatic room center detection from text labels | High | 6 |
| 4.2 | Add room detection without text labels (geometry-only) | High | 10 |
| 4.3 | Handle non-convex rooms in `polygon_builder.py` | High | 6 |
| 4.4 | Handle rooms with holes (courtyards) | Medium | 4 |
| 4.5 | Add room merging/splitting logic | Medium | 4 |
| 4.6 | Improve radial ray casting (adaptive sampling) | Medium | 4 |

### Estimated Duration
**2 weeks** (34 hours)

### Dependencies
- Sprint 3 complete (extended geometry support needed)

### Deliverables
- Automatic room center detection
- Geometry-only room detection
- Non-convex room support
- Improved boundary detection

### Tests to Write
- `test_room_center_detection.py` — Tests for automatic center detection
- `test_geometry_only_detection.py` — Tests for geometry-only room detection
- `test_non_convex_rooms.py` — Tests for non-convex polygon handling
- `test_room_merging.py` — Tests for room merging/splitting
- `test_adaptive_sampling.py` — Tests for improved ray casting

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| False room detection | High | Add confidence threshold |
| Non-convex polygon errors | Medium | Use Shapely validation |
| Performance impact | Medium | Profile and optimize hotspots |

### Definition of Done
- [ ] Room detection works without text labels
- [ ] Non-convex rooms handled correctly
- [ ] Room merging/splitting working
- [ ] >90% room detection accuracy
- [ ] All tests passing

---

## Sprint 5: Door/Window Detection

### Goal
Detect doors and windows from block references and geometry to enable full connectivity analysis.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 5.1 | Detect door block references from DXF | High | 6 |
| 5.2 | Detect window block references from DXF | High | 4 |
| 5.3 | Detect doors from geometry (gap analysis) | High | 8 |
| 5.4 | Update `connectivity.py` to use detected doors | Medium | 4 |
| 5.5 | Add door/window types and properties | Medium | 3 |
| 5.6 | Export door/window data in building model | Medium | 2 |

### Estimated Duration
**2 weeks** (27 hours)

### Dependencies
- Sprint 4 complete (room detection needed for door placement)

### Deliverables
- Door detection from blocks and geometry
- Window detection from blocks
- Updated connectivity analysis
- Door/window data in building model

### Tests to Write
- `test_door_detection.py` — Tests for door detection
- `test_window_detection.py` — Tests for window detection
- `test_gap_analysis.py` — Tests for geometry-based detection
- `test_connectivity_updated.py` — Tests for updated connectivity

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| False door detection | High | Use multiple detection methods |
| Block naming inconsistency | Medium | Maintain comprehensive block maps |
| Performance impact | Medium | Cache detection results |

### Definition of Done
- [ ] Doors detected from blocks and geometry
- [ ] Windows detected from blocks
- [ ] Connectivity analysis uses detected doors
- [ ] >85% door detection accuracy
- [ ] All tests passing

---

## Sprint 6: Backend API — Core

### Goal
Implement core API endpoints for file upload, analysis, and result retrieval.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 6.1 | Implement DXF file upload endpoint | High | 4 |
| 6.2 | Implement full pipeline orchestration endpoint | High | 8 |
| 6.3 | Implement geometry-only analysis endpoint | Medium | 3 |
| 6.4 | Implement room-only analysis endpoint | Medium | 3 |
| 6.5 | Implement text extraction endpoint | Medium | 3 |
| 6.6 | Implement analysis status endpoint | High | 4 |
| 6.7 | Implement analysis results endpoint | High | 3 |
| 6.8 | Implement results export endpoint (JSON, GeoJSON) | Medium | 4 |
| 6.9 | Add request validation and error handling | High | 4 |

### Estimated Duration
**2 weeks** (36 hours)

### Dependencies
- Sprint 1 complete (code quality)
- Sprint 5 complete (door/window detection for full analysis)

### Deliverables
- File upload endpoint
- Full analysis pipeline endpoint
- Status and results endpoints
- Export endpoints
- Comprehensive error handling

### Tests to Write
- `test_api_upload.py` — Tests for file upload
- `test_api_analysis.py` — Tests for analysis endpoints
- `test_api_status.py` — Tests for status endpoint
- `test_api_export.py` — Tests for export endpoint
- `test_api_errors.py` — Tests for error handling

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Large file handling | High | Implement size limits and streaming |
| Pipeline failure handling | Medium | Add comprehensive error handling |
| API backward compatibility | Medium | Version API endpoints |

### Definition of Done
- [ ] All core endpoints implemented
- [ ] File upload working with validation
- [ ] Full pipeline orchestration working
- [ ] Error handling comprehensive
- [ ] All API tests passing
- >90% test coverage

---

## Sprint 7: Backend API — Security

### Goal
Add authentication, authorization, and security hardening to the API.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 7.1 | Implement JWT authentication | High | 6 |
| 7.2 | Implement API key authentication | High | 4 |
| 7.3 | Add role-based access control (RBAC) | High | 6 |
| 7.4 | Add CORS middleware | Medium | 2 |
| 7.5 | Add request size limits | Medium | 2 |
| 7.6 | Add rate limiting | Medium | 4 |
| 7.7 | Add HTTPS enforcement | Low | 1 |
| 7.8 | Add audit logging | Medium | 3 |
| 7.9 | Add input validation middleware | High | 3 |

### Estimated Duration
**1.5 weeks** (31 hours)

### Dependencies
- Sprint 6 complete (core API needed)

### Deliverables
- JWT and API key authentication
- Role-based access control
- CORS, rate limiting, request limits
- Audit logging
- Security middleware

### Tests to Write
- `test_auth_jwt.py` — Tests for JWT authentication
- `test_auth_api_key.py` — Tests for API key authentication
- `test_rbac.py` — Tests for role-based access
- `test_rate_limiting.py` — Tests for rate limiting
- `test_security.py` — Security integration tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Authentication bypass | High | Use established libraries |
| Token management | Medium | Implement refresh tokens |
| Performance impact | Medium | Cache authentication results |

### Definition of Done
- [ ] JWT authentication working
- [ ] API key authentication working
- [ ] RBAC implemented for all roles
- [ ] Rate limiting active
- [ ] All security tests passing
- [ ] Security audit passed

---

## Sprint 8: Async Processing & Caching

### Goal
Add background task processing and caching for long-running analyses.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 8.1 | Set up Celery/ARQ task queue | High | 6 |
| 8.2 | Convert analysis pipeline to async tasks | High | 8 |
| 8.3 | Implement WebSocket progress updates | High | 6 |
| 8.4 | Set up Redis for result caching | Medium | 4 |
| 8.5 | Implement file-hash based caching | Medium | 3 |
| 8.6 | Add task status tracking | Medium | 3 |
| 8.7 | Add task retry logic | Medium | 2 |

### Estimated Duration
**1.5 weeks** (32 hours)

### Dependencies
- Sprint 6 complete (core API)
- Sprint 7 complete (security)

### Deliverables
- Async task processing with Celery/ARQ
- WebSocket progress updates
- Redis caching layer
- Task status and retry logic

### Tests to Write
- `test_async_tasks.py` — Tests for async processing
- `test_websocket.py` — Tests for WebSocket updates
- `test_caching.py` — Tests for Redis caching
- `test_task_status.py` — Tests for status tracking

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Task queue failures | High | Implement retry logic |
| WebSocket connection issues | Medium | Add reconnection logic |
| Cache invalidation | Medium | Use TTL and explicit invalidation |

### Definition of Done
- [ ] Async processing working for all analyses
- [ ] WebSocket progress updates working
- [ ] Redis caching active
- [ ] Task retry logic implemented
- [ ] All tests passing

---

## Sprint 9: Database & File Management

### Goal
Add database persistence for analysis results and file management.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 9.1 | Set up PostgreSQL database | High | 4 |
| 9.2 | Create database models (Users, Projects, Analyses) | High | 6 |
| 9.3 | Implement user registration and management | High | 6 |
| 9.4 | Implement project CRUD operations | Medium | 4 |
| 9.5 | Implement file upload and storage (S3-compatible) | Medium | 6 |
| 9.6 | Migrate results to database storage | Medium | 4 |
| 9.7 | Add database migrations (Alembic) | Medium | 3 |

### Estimated Duration
**2 weeks** (33 hours)

### Dependencies
- Sprint 7 complete (authentication needed for user management)
- Sprint 8 complete (async processing for background jobs)

### Deliverables
- PostgreSQL database with migrations
- User and project management
- File storage system
- Database-backed result storage

### Tests to Write
- `test_database.py` — Tests for database operations
- `test_user_management.py` — Tests for user CRUD
- `test_project_management.py` — Tests for project CRUD
- `test_file_storage.py` — Tests for file upload/storage
- `test_migrations.py` — Tests for database migrations

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Database performance | Medium | Add indexes, use connection pooling |
| Migration failures | High | Test migrations thoroughly |
| File storage costs | Low | Implement lifecycle policies |

### Definition of Done
- [ ] PostgreSQL database running with migrations
- [ ] User management working
- [ ] Project CRUD working
- [ ] File storage working
- [ ] All tests passing

---

## Sprint 10: Testing & Quality Assurance

### Goal
Achieve >80% test coverage and establish quality gates.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 10.1 | Write integration tests for full pipeline | High | 10 |
| 10.2 | Write edge case tests (empty files, malformed DXF) | High | 6 |
| 10.3 | Write performance regression tests | Medium | 4 |
| 10.4 | Write API integration tests | High | 8 |
| 10.5 | Set up code coverage reporting | Medium | 2 |
| 10.6 | Set up linting (flake8, mypy, black) | Medium | 3 |
| 10.7 | Fix all linting issues | Medium | 6 |
| 10.8 | Achieve >80% test coverage | High | 8 |

### Estimated Duration
**2 weeks** (47 hours)

### Dependencies
- Sprint 9 complete (all features implemented)

### Deliverables
- Integration tests for full pipeline
- Edge case tests
- Performance regression tests
- >80% test coverage
- Linting and code quality tools

### Tests to Write
- `test_pipeline_integration.py` — Full pipeline integration tests
- `test_edge_cases.py` — Edge case tests
- `test_performance_regression.py` — Performance tests
- `test_api_integration.py` — API integration tests
- `test_linting.py` — Code quality checks

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Flaky integration tests | Medium | Use deterministic test data |
| Coverage gaps | High | Prioritize critical paths |
| Linting false positives | Low | Configure linting rules |

### Definition of Done
- [ ] >80% test coverage
- [ ] All integration tests passing
- [ ] All edge cases covered
- [ ] Linting clean
- [ ] Performance tests passing

---

## Sprint 11: Documentation & Developer Experience

### Goal
Create comprehensive documentation and improve developer experience.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 11.1 | Generate OpenAPI/Swagger documentation | High | 4 |
| 11.2 | Write deployment guide (DEPLOYMENT.md) | High | 4 |
| 11.3 | Write configuration guide (CONFIGURATION.md) | Medium | 3 |
| 11.4 | Write developer guide (DEVELOPER_GUIDE.md) | Medium | 6 |
| 11.5 | Write user guide (USER_GUIDE.md) | Medium | 6 |
| 11.6 | Add API examples | Medium | 3 |
| 11.7 | Create Docker Compose for local development | Medium | 4 |
| 11.8 | Set up development environment scripts | Low | 2 |

### Estimated Duration
**1.5 weeks** (32 hours)

### Dependencies
- Sprint 10 complete (all features stable)

### Deliverables
- OpenAPI documentation
- Deployment guide
- Configuration guide
- Developer and user guides
- Docker Compose setup

### Tests to Write
- `test_documentation.py` — Verify documentation links
- `test_docker_compose.py` — Verify Docker setup

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Documentation staleness | Low | Automate where possible |
| Docker environment issues | Medium | Test on multiple platforms |

### Definition of Done
- [ ] OpenAPI docs auto-generated
- [ ] All guides written
- [ ] Docker Compose working
- [ ] New developer can setup in <30 minutes

---

## Sprint 12: Production Readiness

### Goal
Prepare the backend for production deployment with monitoring, CI/CD, and hardening.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 12.1 | Set up Docker containerization | High | 4 |
| 12.2 | Set up CI/CD pipeline (GitHub Actions) | High | 8 |
| 12.3 | Add health check endpoints | Medium | 2 |
| 12.4 | Add Prometheus metrics | Medium | 4 |
| 12.5 | Set up structured logging with correlation IDs | Medium | 3 |
| 12.6 | Add graceful shutdown handling | Medium | 2 |
| 12.7 | Set up staging environment | Medium | 4 |
| 12.8 | Performance testing and tuning | High | 6 |
| 12.9 | Security audit and penetration testing | High | 4 |

### Estimated Duration
**2 weeks** (37 hours)

### Dependencies
- Sprint 11 complete (documentation)

### Deliverables
- Docker containerization
- CI/CD pipeline
- Health checks and metrics
- Staging environment
- Security audit report

### Tests to Write
- `test_docker.py` — Verify Docker build
- `test_health_checks.py` — Verify health endpoints
- `test_metrics.py` — Verify Prometheus metrics
- `test_security_audit.py` — Security checks

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| CI/CD pipeline failures | Medium | Test locally first |
| Security vulnerabilities | High | Address critical issues immediately |
| Performance regression | Medium | Benchmark before deployment |

### Definition of Done
- [ ] Docker build successful
- [ ] CI/CD pipeline working
- [ ] Health checks responding
- [ ] Metrics being collected
- [ ] Security audit passed
- [ ] Staging environment running

---

## Sprint 13: Flutter App — Core

### Goal
Build the core Flutter app with authentication, file upload, and results display.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 13.1 | Set up Flutter project structure | High | 4 |
| 13.2 | Implement authentication (login/signup) | High | 8 |
| 13.3 | Implement home dashboard | High | 6 |
| 13.4 | Implement DXF file upload screen | High | 6 |
| 13.5 | Implement analysis progress screen | High | 6 |
| 13.6 | Implement results overview screen | High | 8 |
| 13.7 | Implement room list screen | Medium | 4 |
| 13.8 | Implement room details screen | Medium | 4 |
| 13.9 | Set up API client and state management | High | 6 |

### Estimated Duration
**3 weeks** (52 hours)

### Dependencies
- Sprint 12 complete (production-ready API)

### Deliverables
- Flutter app with authentication
- File upload functionality
- Analysis progress tracking
- Results display

### Tests to Write
- `test_auth_ui.py` — Authentication UI tests
- `test_upload_ui.py` — Upload UI tests
- `test_results_ui.py` — Results display tests
- `test_api_client.py` — API client tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| API integration issues | High | Use API client library |
| UI performance on low-end devices | Medium | Optimize rendering |
| State management complexity | Medium | Use established patterns |

### Definition of Done
- [ ] Authentication working
- [ ] File upload working
- [ ] Progress tracking working
- [ ] Results display working
- [ ] App runs on iOS and Android

---

## Sprint 14: Flutter App — Viewer & Reports

### Goal
Add interactive floor plan viewer and report generation to the Flutter app.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 14.1 | Implement interactive 2D floor plan viewer | High | 12 |
| 14.2 | Add room highlighting and labels | High | 6 |
| 14.3 | Add pan and zoom functionality | Medium | 4 |
| 14.4 | Implement measure tool | Medium | 4 |
| 14.5 | Implement annotation system | Medium | 6 |
| 14.6 | Implement PDF report generation | High | 8 |
| 14.7 | Implement share functionality | Medium | 4 |
| 14.8 | Add offline mode for cached results | Medium | 6 |

### Estimated Duration
**2.5 weeks** (50 hours)

### Dependencies
- Sprint 13 complete (core app)

### Deliverables
- Interactive floor plan viewer
- Measurement tool
- Annotation system
- PDF report generation
- Offline mode

### Tests to Write
- `test_viewer.py` — Viewer functionality tests
- `test_measure_tool.py` — Measurement tool tests
- `test_annotations.py` — Annotation system tests
- `test_pdf_generation.py` — PDF generation tests
- `test_offline_mode.py` — Offline mode tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Viewer performance with large plans | High | Use level-of-detail rendering |
| PDF generation complexity | Medium | Use established libraries |
| Offline sync issues | Medium | Implement conflict resolution |

### Definition of Done
- [ ] Floor plan viewer working smoothly
- [ ] Measurement tool accurate
- [ ] Annotations working
- [ ] PDF reports generated
- [ ] Offline mode functional

---

## Sprint 15: AI Features — Phase 1

### Goal
Implement ML-based room and wall detection to improve accuracy.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 15.1 | Collect and label training data | High | 10 |
| 15.2 | Train room detection model (CNN) | High | 12 |
| 15.3 | Train wall detection model (U-Net) | High | 12 |
| 15.4 | Create model serving infrastructure | High | 8 |
| 15.5 | Integrate models with pipeline | High | 8 |
| 15.6 | Add model versioning and A/B testing | Medium | 4 |
| 15.7 | Implement fallback to rule-based detection | Medium | 4 |

### Estimated Duration
**3 weeks** (58 hours)

### Dependencies
- Sprint 12 complete (production infrastructure)
- Sprint 14 complete (app ready for AI features)

### Deliverables
- Trained room detection model
- Trained wall detection model
- Model serving infrastructure
- AI-enhanced pipeline

### Tests to Write
- `test_ml_room_detection.py` — ML model tests
- `test_ml_wall_detection.py` — ML model tests
- `test_model_serving.py` — Model serving tests
- `test_ai_pipeline.py` — AI pipeline integration tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Model accuracy below target | High | Iterate on training data |
| Model serving latency | Medium | Use GPU inference |
| Training data quality | High | Manual review process |

### Definition of Done
- [ ] Room detection model >90% accuracy
- [ ] Wall detection model >85% accuracy
- [ ] Model serving infrastructure working
- [ ] AI pipeline integrated
- [ ] Fallback to rule-based working

---

## Sprint 16: Vastu Analysis

### Goal
Implement basic Vastu compliance checking for floor plans.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 16.1 | Implement Vastu zone mapping | High | 6 |
| 16.2 | Implement zone compliance checking | High | 6 |
| 16.3 | Implement direction detection | High | 4 |
| 16.4 | Implement Vastu score calculation | High | 4 |
| 16.5 | Implement Vastu report generation | Medium | 4 |
| 16.6 | Add Vastu API endpoints | Medium | 3 |
| 16.7 | Add Vastu visualization to Flutter app | Medium | 6 |

### Estimated Duration
**2 weeks** (33 hours)

### Dependencies
- Sprint 15 complete (AI features for better room detection)

### Deliverables
- Vastu zone mapping
- Compliance checking
- Score calculation
- Vastu report
- API endpoints
- App visualization

### Tests to Write
- `test_vastu_zones.py` — Vastu zone tests
- `test_vastu_compliance.py` — Compliance checking tests
- `test_vastu_score.py` — Score calculation tests
- `test_vastu_api.py` — Vastu API tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Cultural sensitivity | High | Consult Vastu experts |
| Complex rule interpretation | Medium | Start with basic rules |
| Accuracy of direction detection | Medium | Use multiple methods |

### Definition of Done
- [ ] Vastu zones mapped correctly
- [ ] Compliance checking working
- [ ] Score calculation accurate
- [ ] Report generation working
- [ ] API endpoints functional
- [ ] App visualization working

---

## Sprint 17: Building Code Compliance

### Goal
Implement basic building code compliance checking.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 17.1 | Implement room size validation | High | 4 |
| 17.2 | Implement egress distance checking | High | 6 |
| 17.3 | Implement ventilation requirement checking | Medium | 4 |
| 17.4 | Implement ceiling height validation | Medium | 3 |
| 17.5 | Create building code database | High | 8 |
| 17.6 | Implement compliance report generation | Medium | 4 |
| 17.7 | Add compliance API endpoints | Medium | 3 |
| 17.8 | Add jurisdiction support (IRC, NBC) | Medium | 6 |

### Estimated Duration
**2 weeks** (38 hours)

### Dependencies
- Sprint 15 complete (AI features for accurate measurements)

### Deliverables
- Room size validation
- Egress checking
- Ventilation checking
- Compliance report
- API endpoints
- Jurisdiction support

### Tests to Write
- `test_room_size_validation.py` — Room size tests
- `test_egress_checking.py` — Egress distance tests
- `test_ventilation_checking.py` — Ventilation tests
- `test_compliance_api.py` — Compliance API tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Code interpretation errors | High | Consult building officials |
| Jurisdiction variations | Medium | Start with common codes |
| Complex geometry handling | Medium | Use approximations |

### Definition of Done
- [ ] Room size validation working
- [ ] Egress checking working
- [ ] Ventilation checking working
- [ ] Compliance report generated
- [ ] API endpoints functional
- [ ] IRC and NBC supported

---

## Sprint 18: AI Features — Phase 2

### Goal
Implement advanced AI features including design suggestions and cost estimation.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 18.1 | Implement design suggestion engine | High | 10 |
| 18.2 | Implement anomaly detection | High | 8 |
| 18.3 | Implement cost estimation model | High | 10 |
| 18.4 | Implement BOQ generation | Medium | 8 |
| 18.5 | Add AI chatbot interface | Medium | 8 |
| 18.6 | Create RAG knowledge base | Medium | 6 |
| 18.7 | Add AI API endpoints | Medium | 4 |

### Estimated Duration
**3 weeks** (54 hours)

### Dependencies
- Sprint 15 complete (Phase 1 AI infrastructure)
- Sprint 17 complete (compliance data for suggestions)

### Deliverables
- Design suggestion engine
- Anomaly detection
- Cost estimation
- BOQ generation
- AI chatbot
- RAG knowledge base

### Tests to Write
- `test_design_suggestions.py` — Suggestion engine tests
- `test_anomaly_detection.py` — Anomaly detection tests
- `test_cost_estimation.py` — Cost estimation tests
- `test_boq_generation.py` — BOQ generation tests
- `test_chatbot.py` — Chatbot tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| AI hallucination | High | Implement guardrails |
| Cost estimation accuracy | Medium | Use historical data |
| Chatbot context limitations | Medium | Clear scope definition |

### Definition of Done
- [ ] Design suggestions working
- [ ] Anomaly detection working
- [ ] Cost estimation within ±20%
- [ ] BOQ generation working
- [ ] Chatbot functional
- [ ] All tests passing

---

## Sprint 19: Advanced Features

### Goal
Implement advanced features including 3D model generation and multi-floor support.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 19.1 | Implement 3D model generation from 2D plans | High | 12 |
| 19.2 | Implement multi-floor support | High | 10 |
| 19.3 | Implement furniture detection | Medium | 8 |
| 19.4 | Implement stair detection | Medium | 6 |
| 19.5 | Implement column detection | Medium | 6 |
| 19.6 | Add 3D viewer to Flutter app | Medium | 10 |
| 19.7 | Implement BIM/IFC export | Low | 8 |

### Estimated Duration
**3 weeks** (60 hours)

### Dependencies
- Sprint 18 complete (AI features)

### Deliverables
- 3D model generation
- Multi-floor support
- Furniture/stair/column detection
- 3D viewer in app
- BIM export (optional)

### Tests to Write
- `test_3d_generation.py` — 3D model tests
- `test_multi_floor.py` — Multi-floor tests
- `test_furniture_detection.py` — Furniture detection tests
- `test_3d_viewer.py` — 3D viewer tests

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| 3D generation complexity | High | Use extrusion approach |
| Multi-floor logic complexity | Medium | Start with 2 floors |
| Performance impact | Medium | Use level-of-detail |

### Definition of Done
- [ ] 3D model generation working
- [ ] Multi-floor support working
- [ ] Furniture/stair/column detection working
- [ ] 3D viewer functional
- [ ] All tests passing

---

## Sprint 20: Production Release

### Goal
Final polish, performance optimization, and production release of version 1.0.0.

### Tasks

| ID | Task | Priority | Est. Hours |
|----|------|----------|------------|
| 20.1 | Final performance optimization | High | 8 |
| 20.2 | Security hardening | High | 6 |
| 20.3 | Documentation finalization | High | 4 |
| 20.4 | CI/CD pipeline finalization | Medium | 4 |
| 20.5 | Monitoring and alerting setup | Medium | 4 |
| 20.6 | Production environment setup | High | 6 |
| 20.7 | Load testing | Medium | 4 |
| 20.8 | User acceptance testing | High | 6 |
| 20.9 | Release notes and changelog | Medium | 2 |
| 20.10 | Version 1.0.0 release | High | 2 |

### Estimated Duration
**2 weeks** (46 hours)

### Dependencies
- Sprint 19 complete (all features)

### Deliverables
- Production-ready release
- Final documentation
- Monitoring and alerting
- Load test results
- Version 1.0.0 released

### Tests to Write
- `test_load.py` — Load testing
- `test_uat.py` — User acceptance tests
- `test_security_final.py` — Final security audit

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Last-minute bugs | High | Feature freeze before release |
| Performance issues | Medium | Load test early |
| Documentation gaps | Medium | Review all docs |

### Definition of Done
- [ ] All tests passing
- [ ] >85% test coverage
- [ ] Performance targets met
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Production environment running
- [ ] Version 1.0.0 released

---

## Summary

### Total Timeline

| Sprint | Duration | Cumulative |
|--------|----------|------------|
| Sprint 1: Code Quality | 1 week | 1 week |
| Sprint 2: Performance | 2 weeks | 3 weeks |
| Sprint 3: Extended Geometry | 2 weeks | 5 weeks |
| Sprint 4: Room Detection | 2 weeks | 7 weeks |
| Sprint 5: Door/Window Detection | 2 weeks | 9 weeks |
| Sprint 6: Backend API Core | 2 weeks | 11 weeks |
| Sprint 7: Backend API Security | 1.5 weeks | 12.5 weeks |
| Sprint 8: Async Processing | 1.5 weeks | 14 weeks |
| Sprint 9: Database | 2 weeks | 16 weeks |
| Sprint 10: Testing | 2 weeks | 18 weeks |
| Sprint 11: Documentation | 1.5 weeks | 19.5 weeks |
| Sprint 12: Production Readiness | 2 weeks | 21.5 weeks |
| Sprint 13: Flutter Core | 3 weeks | 24.5 weeks |
| Sprint 14: Flutter Viewer | 2.5 weeks | 27 weeks |
| Sprint 15: AI Phase 1 | 3 weeks | 30 weeks |
| Sprint 16: Vastu Analysis | 2 weeks | 32 weeks |
| Sprint 17: Code Compliance | 2 weeks | 34 weeks |
| Sprint 18: AI Phase 2 | 3 weeks | 37 weeks |
| Sprint 19: Advanced Features | 3 weeks | 40 weeks |
| Sprint 20: Production Release | 2 weeks | 42 weeks |

**Total estimated time: ~42 weeks (10.5 months)**

### Effort Distribution

| Category | Sprints | Hours | Percentage |
|----------|---------|-------|------------|
| Core Engine | 1-5 | 132 | 25% |
| Backend API | 6-9 | 138 | 26% |
| Quality & Docs | 10-11 | 79 | 15% |
| Production | 12 | 37 | 7% |
| Mobile App | 13-14 | 102 | 19% |
| AI & Advanced | 15-19 | 213 | 40% |
| Release | 20 | 46 | 9% |

*Note: Some sprints run in parallel, so total calendar time is less than sum of sprint durations.*

### Key Milestones

| Milestone | Sprint | Deliverable |
|-----------|--------|-------------|
| Code Quality Baseline | 1 | Refactored codebase |
| Performance Target | 2 | 5x speed improvement |
| Full Geometry Support | 3 | POLYLINE, ARC, CIRCLE |
| Room Detection v2 | 4 | Geometry-only detection |
| Door/Window Detection | 5 | Full connectivity |
| API v1 | 6 | Core endpoints |
| Secure API | 7 | Authentication, RBAC |
| Async Processing | 8 | Background tasks |
| Database | 9 | Persistence layer |
| Quality Gate | 10 | >80% coverage |
| Documentation | 11 | Complete docs |
| Production Backend | 12 | Deployed backend |
| Mobile App v1 | 13 | Core app |
| Mobile App v2 | 14 | Viewer and reports |
| AI v1 | 15 | ML detection |
| Vastu Analysis | 16 | Compliance checking |
| Code Compliance | 17 | Building code checks |
| AI v2 | 18 | Advanced AI |
| Advanced Features | 19 | 3D, multi-floor |
| **Version 1.0.0** | **20** | **Production release** |

---

## Appendix A: Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ML model accuracy below target | Medium | High | Iterative training, fallback to rule-based |
| Performance regression | Low | High | Continuous benchmarking |
| Security vulnerability | Low | Critical | Regular audits, bug bounty |
| Scope creep | High | Medium | Strict sprint planning |
| Technical debt | Medium | Medium | Regular refactoring sprints |
| Team availability | Medium | High | Cross-training, documentation |
| Third-party dependency issues | Low | Medium | Pin versions, vendor critical libs |

## Appendix B: Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Room detection accuracy | >95% | Test dataset |
| Wall detection accuracy | >90% | Test dataset |
| Processing time (avg floor plan) | <30s | Benchmark |
| API uptime | 99.9% | Monitoring |
| Test coverage | >80% | Coverage tool |
| Code quality | A grade | Linting |
| Documentation completeness | 100% | Checklist |
| User satisfaction | >4.5/5 | Surveys |

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Next Review:** End of Sprint 1