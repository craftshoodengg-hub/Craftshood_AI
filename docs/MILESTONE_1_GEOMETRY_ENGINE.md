# Milestone 1 — Stable Geometry Engine

**Target Date:** Q3 2026  
**Estimated Effort:** 6-8 weeks  
**Priority:** Critical Path

---

## 1. Current Maturity Assessment

### Overall Maturity: 6/10 — Functional but Not Production-Ready

The Geometry Engine is well-architected with clean module separation and immutable data structures. The core pipeline (LINE reading → parallel detection → wall classification → wall merging → JSON export) works correctly for simple floor plans. However, several gaps prevent it from being production-ready.

### Strengths

| Area | Assessment |
|------|------------|
| **Architecture** | Excellent modular design with clear separation of concerns |
| **Data Model** | Consistent use of frozen dataclasses with `slots=True` |
| **Type Hints** | Comprehensive type annotations throughout |
| **Configuration** | Config objects with validation for all modules |
| **API Design** | Both class-based and convenience wrapper functions |
| **Test Coverage** | Core modules tested with ~70% coverage |
| **Documentation** | Clear docstrings and module-level documentation |

### Weaknesses

| Area | Assessment |
|------|------------|
| **Entity Support** | LINE-only; POLYLINE, LWPOLYLINE, ARC, CIRCLE not supported |
| **Performance** | O(n²) parallel detection; no spatial indexing |
| **Wall Types** | Only 2 hardcoded types (9" and 4.5" brick) |
| **Error Handling** | Minimal; no graceful handling of malformed input |
| **Edge Cases** | No handling for degenerate geometries |
| **Scalability** | Loads all entities into memory; no streaming |

---

## 2. Missing Functionality

### 2.1 Extended Entity Support

| Entity Type | Current Status | Priority | Complexity |
|-------------|---------------|----------|------------|
| LINE | ✅ Supported | — | — |
| POLYLINE | ❌ Not supported | High | Medium |
| LWPOLYLINE | ❌ Not supported | High | Low |
| ARC | ❌ Not supported | Medium | High |
| CIRCLE | ❌ Not supported | Medium | Low |

**Impact:** Many real-world DXF files use POLYLINE for walls. Without this support, the engine cannot process a significant portion of production drawings.

### 2.2 Configurable Wall Types

| Feature | Current Status | Priority |
|---------|---------------|----------|
| 9" brick wall | ✅ Hardcoded | — |
| 4.5" brick wall | ✅ Hardcoded | — |
| Custom wall types | ❌ Not supported | High |
| JSON/YAML config | ❌ Not supported | Medium |

**Impact:** Different projects use different wall types (concrete, drywall, etc.). Hardcoded limits prevent broader adoption.

### 2.3 Spatial Indexing

| Feature | Current Status | Priority |
|---------|---------------|----------|
| R-tree spatial index | ❌ Not implemented | High |
| O(n log n) detection | ❌ Not implemented | High |

**Impact:** O(n²) parallel detection is slow for large drawings (>1000 LINE entities). A drawing with 5000 lines requires 12.5 million comparisons.

### 2.4 Streaming File Reading

| Feature | Current Status | Priority |
|---------|---------------|----------|
| Streaming/chunked reading | ❌ Not implemented | Medium |
| Memory-efficient processing | ❌ Not implemented | Medium |

**Impact:** Large DXF files (>50MB) may cause memory issues when loaded entirely into memory.

---

## 3. Performance Improvements

### 3.1 Parallel Detection Optimization

**Current:** O(n²) brute-force pairwise comparison  
**Target:** O(n log n) using R-tree spatial indexing

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| 100 lines | 4,950 comparisons | ~500 operations | 10x |
| 1,000 lines | 499,500 comparisons | ~5,000 operations | 100x |
| 10,000 lines | 49,995,000 comparisons | ~50,000 operations | 1000x |

**Implementation:** Use `rtree` library or Shapely's STRtree for spatial indexing.

### 3.2 NumPy Vectorization

**Current:** Python loops for distance calculations  
**Target:** Vectorized NumPy operations

| Operation | Current | Vectorized | Improvement |
|-----------|---------|------------|-------------|
| Distance calculation | Python loop | NumPy broadcast | 5-10x |
| Angle calculation | Python loop | NumPy vectorized | 5-10x |

### 3.3 Result Caching

**Current:** No caching  
**Target:** File-hash based caching

| Scenario | Current | With Caching |
|----------|---------|--------------|
| Repeated analysis | Full reprocessing | Instant return |
| Same file, different run | O(n²) | O(1) |

---

## 4. Accuracy Improvements

### 4.1 Perpendicular Distance Calculation

**Current:** Uses midpoint of one line only  
**Target:** Use full carrier line distance

**Issue:** Current implementation calculates distance from midpoint of `line_b` to carrier line of `line_a`. This can be inaccurate for lines of different lengths.

**Fix:** Calculate minimum distance between all endpoints and carrier lines, or use average of endpoint distances.

### 4.2 Angle Calculation

**Current:** Simple modulo 180  
**Target:** Handle edge cases near 0°/180° boundary

**Issue:** Lines at 0.1° and 179.9° should be considered parallel, but current implementation may miss this.

**Fix:** Use circular angle difference calculation.

### 4.3 Overlap Detection

**Current:** Simple interval overlap  
**Target:** Handle floating-point precision issues

**Issue:** Floating-point arithmetic may cause precision errors in overlap calculations.

**Fix:** Add epsilon tolerance for floating-point comparisons.

---

## 5. Error Handling Improvements

### 5.1 Input Validation

| Scenario | Current Behavior | Expected Behavior |
|----------|------------------|-------------------|
| Empty DXF file | Returns empty list | Returns empty list with warning |
| Corrupted DXF | Raises `ezdxf.DXFError` | Raises with clear error message |
| Zero-length LINE | Skipped with debug log | Skipped with debug log (OK) |
| Negative coordinates | Processed normally | Processed normally (OK) |
| Invalid layer name | Defaults to "0" | Defaults to "0" (OK) |

### 5.2 Graceful Degradation

| Scenario | Current Behavior | Expected Behavior |
|----------|------------------|-------------------|
| No LINE entities | Returns empty list | Returns empty list with warning |
| No parallel pairs | Returns empty list | Returns empty list with warning |
| No wall matches | Returns empty list | Returns empty list with warning |

### 5.3 Error Messages

**Current:** Generic Python exceptions  
**Target:** Descriptive error messages with context

**Example:**
```
GeometryEngineError: Failed to process DXF file "plan.dxf"
  - Cause: File contains 0 LINE entities on layer "A-WALL"
  - Suggestion: Verify layer name or include blocks
```

---

## 6. Missing Unit Tests

### 6.1 Current Test Coverage

| Module | Coverage | Target |
|--------|----------|--------|
| `line_reader.py` | ~75% | 90% |
| `parallel_detector.py` | ~65% | 85% |
| `wall_classifier.py` | ~70% | 90% |
| `wall_merger.py` | ~60% | 85% |
| `wall_exporter.py` | ~80% | 95% |

### 6.2 Missing Test Cases

| Category | Missing Tests |
|----------|---------------|
| **Edge Cases** | Empty file, single line, collinear lines, perpendicular lines |
| **Boundary Conditions** | Zero-length lines, very long lines, negative coordinates |
| **Error Handling** | Invalid file path, corrupted file, missing attributes |
| **Configuration** | Invalid config values, extreme tolerance values |
| **Integration** | Full pipeline with complex drawings |
| **Performance** | Large file handling, memory usage |

### 6.3 Required New Tests

| Test File | Test Count | Priority |
|-----------|-----------|----------|
| `test_line_reader_edge_cases.py` | 8 | High |
| `test_parallel_detector_edge_cases.py` | 6 | High |
| `test_wall_classifier_edge_cases.py` | 5 | Medium |
| `test_wall_merger_edge_cases.py` | 6 | Medium |
| `test_wall_exporter_edge_cases.py` | 4 | Low |
| `test_geometry_engine_integration.py` | 5 | High |
| `test_geometry_engine_performance.py` | 3 | Medium |

---

## 7. Required Refactoring

### 7.1 Code Deduplication

| Item | Files | Action |
|------|-------|--------|
| `_linear_length()` | `adjacency.py`, `connectivity.py`, `facing.py` | Extract to `geometry_utils.py` |
| `_validate_rooms()` | `adjacency.py`, `facing.py` | Extract to `validation.py` |
| `_safe_dxf_value()` | `line_reader.py`, `text_extractor.py` | Extract to `dxf_utils.py` |

### 7.2 Module Organization

| Current | Proposed | Reason |
|---------|----------|--------|
| No `geometry_utils.py` | Create `geometry_utils.py` | Shared geometry utilities |
| No `validation.py` | Create `validation.py` | Shared validation logic |
| No `dxf_utils.py` | Create `dxf_utils.py` | Shared DXF utilities |

### 7.3 Configuration Standardization

| Module | Current | Proposed |
|--------|---------|----------|
| `ParallelDetector` | Config dataclass | Standardize config pattern |
| `WallClassifier` | Config dataclass | Standardize config pattern |
| `WallMerger` | Config dataclass | Standardize config pattern |

---

## 8. Acceptance Criteria

### 8.1 Functional Criteria

- [ ] All LINE entities are correctly read from DXF files
- [ ] Parallel line pairs are detected within configured tolerances
- [ ] Wall segments are classified with correct wall type and width
- [ ] Connected wall segments are merged into logical walls
- [ ] JSON export produces valid, well-structured output
- [ ] POLYLINE and LWPOLYLINE entities are supported
- [ ] Custom wall types can be configured via JSON/YAML

### 8.2 Performance Criteria

- [ ] 1000 LINE entities processed in <3 seconds
- [ ] 5000 LINE entities processed in <10 seconds
- [ ] 10000 LINE entities processed in <30 seconds
- [ ] Memory usage <500MB for 10000 LINE entities

### 8.3 Quality Criteria

- [ ] Test coverage >85% for all modules
- [ ] All edge cases handled gracefully
- [ ] Clear error messages for invalid input
- [ ] No unhandled exceptions
- [ ] Documentation complete for all public APIs

### 8.4 Integration Criteria

- [ ] Pipeline works end-to-end with real DXF files
- [ ] Output is compatible with `room_graph` module
- [ ] Output is compatible with `building_model` module
- [ ] Configuration is consistent across all modules

---

## 9. Estimated Effort

### 9.1 Task Breakdown

| Task | Priority | Effort | Sprint |
|------|----------|--------|--------|
| Create `geometry_utils.py` | High | 2h | 1 |
| Create `validation.py` | High | 2h | 1 |
| Create `dxf_utils.py` | Medium | 2h | 1 |
| Remove dead code | Low | 2h | 1 |
| Implement R-tree spatial indexing | High | 8h | 2 |
| Optimize with NumPy vectorization | Medium | 6h | 2 |
| Add result caching | Medium | 4h | 2 |
| Add POLYLINE support | High | 6h | 3 |
| Add LWPOLYLINE support | High | 4h | 3 |
| Add configurable wall types | Medium | 4h | 3 |
| Improve distance calculation | Medium | 3h | 3 |
| Add ARC entity support | Medium | 6h | 3 |
| Add CIRCLE entity support | Medium | 3h | 3 |
| Add streaming file reading | Medium | 4h | 3 |
| Write edge case tests | High | 10h | 4 |
| Write integration tests | High | 8h | 4 |
| Performance testing | Medium | 4h | 4 |
| Documentation updates | Medium | 4h | 4 |

### 9.2 Total Estimate

| Category | Hours |
|----------|-------|
| Code Quality & Consolidation | 8h |
| Performance Optimization | 18h |
| Extended Geometry Support | 23h |
| Testing & Quality Assurance | 22h |
| Documentation | 4h |
| **Total** | **75h** |

**Estimated Duration:** 6-8 weeks (accounting for code review, bug fixes, and integration testing)

---

## 10. Recommended First Coding Task

### Task: Create `geometry_utils.py` with `linear_length()` function

**Why This Task First:**

1. **Foundation for Performance Work**: The `linear_length()` function is used by `adjacency.py`, which is the primary target for Sprint 2's spatial indexing optimization. Having this utility in place first makes the performance work cleaner.

2. **Low Risk**: This is a pure utility function with no side effects. Extracting it has zero risk of breaking existing functionality.

3. **Establishes Pattern**: This sets the pattern for creating shared utility modules. The same pattern will be used for `validation.py` and `dxf_utils.py`.

4. **Immediate Testability**: The function is easy to unit test in isolation, providing quick wins for test coverage.

5. **Removes Duplication**: Eliminates 3 identical function definitions across the codebase.

### Implementation Details

**File:** `geometry_utils.py` (new file at project root)

```python
"""Shared geometry utility functions."""

from __future__ import annotations

from typing import Any

from shapely.geometry import GeometryCollection, LineString, MultiLineString


def linear_length(geometry: Any) -> float:
    """Return the total linear length of a Shapely geometry.
    
    Handles LineString, MultiLineString, and GeometryCollection.
    Returns 0.0 for empty or unsupported geometry types.
    """
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(linear_length(part) for part in geometry.geoms)
    return 0.0
```

**Files to Modify:**

| File | Change |
|------|--------|
| `adjacency.py` | Remove local `_linear_length()`, import from `geometry_utils.py` |
| `connectivity.py` | Remove local `_linear_length()`, import from `geometry_utils.py` |
| `facing.py` | Remove local `_linear_length()`, import from `geometry_utils.py` |

**Tests to Create:**

| Test | Description |
|------|-------------|
| `test_linear_length_linestring` | Returns correct length for LineString |
| `test_linear_length_multilinestring` | Returns sum for MultiLineString |
| `test_linear_length_geometry_collection` | Returns sum for GeometryCollection |
| `test_linear_length_empty` | Returns 0.0 for empty geometry |
| `test_linear_length_nested` | Handles nested GeometryCollection |

### Expected Outcome

- 3 duplicate function definitions removed
- 1 shared utility module created
- 0 breaking changes
- Foundation laid for Sprint 2 performance work
- Test coverage for new module: 100%

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Import path issues | Low | Low | Use absolute imports |
| Breaking existing tests | Very Low | Medium | Function signature identical |
| Shapely version compatibility | Very Low | Low | Test with current version |

---

## Appendix A: Dependency Map

```
geometry_utils.py (NEW)
    ↓
adjacency.py ← geometry_utils.py
connectivity.py ← geometry_utils.py
facing.py ← geometry_utils.py
    ↓
parallel_detector.py ← (future: spatial indexing)
    ↓
adjacency.py ← parallel_detector.py
```

## Appendix B: Test DXF Files Needed

| File | Content | Purpose |
|------|---------|---------|
| `simple_walls.dxf` | Basic parallel lines | Basic functionality |
| `complex_walls.dxf` | Multiple wall types | Classification testing |
| `no_lines.dxf` | Empty drawing | Edge case testing |
| `polyline_walls.dxf` | POLYLINE entities | Extended entity testing |
| `large_drawing.dxf` | 5000+ LINE entities | Performance testing |

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Next Review:** After Sprint 1 completion