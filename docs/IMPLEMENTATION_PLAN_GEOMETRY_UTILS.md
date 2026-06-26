# Implementation Plan: Create `geometry_utils.py`

**Date:** 2026-06-26  
**Status:** Pending Approval  
**Estimated Effort:** 2 hours

---

## Overview

Create a new shared utility module `geometry_utils.py` containing the `linear_length()` function that is currently duplicated across three files: `adjacency.py`, `connectivity.py`, and `facing.py`.

---

## Current State Analysis

### Duplicated Function

The following identical function exists in three files:

**File 1: `adjacency.py` (lines 147-154)**
```python
def _linear_length(geometry: Any) -> float:
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(_linear_length(part) for part in geometry.geoms)
    return 0.0
```

**File 2: `connectivity.py` (lines 202-209)**
```python
def _linear_length(geometry: Any) -> float:
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(_linear_length(part) for part in geometry.geoms)
    return 0.0
```

**File 3: `facing.py` (lines 211-218)**
```python
def _linear_length(geometry: Any) -> float:
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(_linear_length(part) for part in geometry.geoms)
    return 0.0
```

### Usage Count

| File | Call Sites | Context |
|------|------------|---------|
| `adjacency.py` | 1 | `shared_boundary_length()` function |
| `connectivity.py` | 1 | `_door_on_shared_boundary()` method |
| `facing.py` | 2 | `_room_touches_front_wall()` method |

---

## Implementation Plan

### Step 1: Create `geometry_utils.py`

**Location:** `d:\craftshood_ai\geometry_utils.py`

```python
"""Shared geometry utility functions for Craftshood_AI.

This module provides common geometry operations used across the
geometry_engine and analysis packages.
"""

from __future__ import annotations

from typing import Any

from shapely.geometry import GeometryCollection, LineString, MultiLineString


def linear_length(geometry: Any) -> float:
    """Return the total linear length of a Shapely geometry.
    
    Handles the following geometry types:
    - LineString: returns the line length
    - MultiLineString: returns the sum of all line lengths
    - GeometryCollection: returns the sum of all component lengths
    - Empty geometries: returns 0.0
    
    Args:
        geometry: A Shapely geometry object.
        
    Returns:
        The total linear length as a float. Returns 0.0 for empty
        or unsupported geometry types.
        
    Examples:
        >>> from shapely.geometry import LineString, MultiLineString
        >>> line = LineString([(0, 0), (3, 4)])
        >>> linear_length(line)
        5.0
        >>> multi = MultiLineString([[(0, 0), (1, 0)], [(2, 0), (2, 1)]])
        >>> linear_length(multi)
        2.0
        >>> linear_length(line)
        0.0
    """
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(linear_length(part) for part in geometry.geoms)
    return 0.0
```

**Design Decisions:**
- Public function name (no underscore prefix) for use across packages
- Comprehensive docstring with examples
- Type hint `Any` for geometry parameter (Shapely uses dynamic types)
- Recursive handling of nested GeometryCollection

### Step 2: Update `adjacency.py`

**Changes:**
1. Add import: `from geometry_utils import linear_length`
2. Remove local `_linear_length()` function (lines 147-154)
3. Update call site in `shared_boundary_length()` (line 144)

**Before:**
```python
from shapely.geometry import GeometryCollection, LineString, MultiLineString, Polygon

# ... (at line 140)
def shared_boundary_length(first: Polygon, second: Polygon) -> float:
    intersection = first.boundary.intersection(second.boundary)
    return _linear_length(intersection)

# ... (at line 147)
def _linear_length(geometry: Any) -> float:
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(_linear_length(part) for part in geometry.geoms)
    return 0.0
```

**After:**
```python
from shapely.geometry import LineString, Polygon
from geometry_utils import linear_length

# ... (at line 140)
def shared_boundary_length(first: Polygon, second: Polygon) -> float:
    intersection = first.boundary.intersection(second.boundary)
    return linear_length(intersection)
```

**Note:** Remove unused imports (`GeometryCollection`, `MultiLineString`, `Any`)

### Step 3: Update `connectivity.py`

**Changes:**
1. Add import: `from geometry_utils import linear_length`
2. Remove local `_linear_length()` function (lines 202-209)
3. Update call site in `_door_on_shared_boundary()` (line 139)

**Before:**
```python
from shapely.geometry import GeometryCollection, LineString, MultiLineString, Point, Polygon

# ... (at line 132)
def _door_on_shared_boundary(self, first, second, doors):
    shared_boundary = first.boundary.intersection(second.boundary)
    if _linear_length(shared_boundary) <= 0:
        return None

# ... (at line 202)
def _linear_length(geometry: Any) -> float:
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(_linear_length(part) for part in geometry.geoms)
    return 0.0
```

**After:**
```python
from shapely.geometry import LineString, Point, Polygon
from geometry_utils import linear_length

# ... (at line 132)
def _door_on_shared_boundary(self, first, second, doors):
    shared_boundary = first.boundary.intersection(second.boundary)
    if linear_length(shared_boundary) <= 0:
        return None
```

**Note:** Remove unused imports (`GeometryCollection`, `MultiLineString`, `Any`)

### Step 4: Update `facing.py`

**Changes:**
1. Add import: `from geometry_utils import linear_length`
2. Remove local `_linear_length()` function (lines 211-218)
3. Update call sites in `_room_touches_front_wall()` (lines 115, 126)

**Before:**
```python
from shapely.geometry import GeometryCollection, LineString, MultiLineString, Point, Polygon

# ... (at line 114)
def _room_touches_front_wall(self, room, wall):
    shared_length = _linear_length(room.boundary.intersection(wall))
    # ...
    touch_length = _linear_length(room.boundary.intersection(buffered_wall))

# ... (at line 211)
def _linear_length(geometry: Any) -> float:
    if geometry.is_empty:
        return 0.0
    if isinstance(geometry, (LineString, MultiLineString)):
        return float(geometry.length)
    if isinstance(geometry, GeometryCollection):
        return sum(_linear_length(part) for part in geometry.geoms)
    return 0.0
```

**After:**
```python
from shapely.geometry import LineString, Point, Polygon
from geometry_utils import linear_length

# ... (at line 114)
def _room_touches_front_wall(self, room, wall):
    shared_length = linear_length(room.boundary.intersection(wall))
    # ...
    touch_length = linear_length(room.boundary.intersection(buffered_wall))
```

**Note:** Remove unused imports (`GeometryCollection`, `MultiLineString`, `Any`)

### Step 5: Create Tests

**Location:** `tests/test_geometry_utils.py`

```python
"""Tests for geometry_utils module."""

from __future__ import annotations

from shapely.geometry import GeometryCollection, LineString, MultiLineString

from geometry_utils import linear_length


class TestLinearLength:
    """Tests for the linear_length function."""

    def test_linestring_returns_length(self) -> None:
        """LineString returns its length."""
        line = LineString([(0, 0), (3, 4)])
        assert linear_length(line) == 5.0

    def test_multilinestring_returns_sum(self) -> None:
        """MultiLineString returns sum of all line lengths."""
        multi = MultiLineString([
            [(0, 0), (1, 0)],
            [(2, 0), (2, 1)],
            [(5, 5), (8, 9)],  # length = 5
        ])
        assert linear_length(multi) == 3.0

    def test_empty_linestring_returns_zero(self) -> None:
        """Empty LineString returns 0.0."""
        line = LineString()
        assert linear_length(line) == 0.0

    def test_empty_multilinestring_returns_zero(self) -> None:
        """Empty MultiLineString returns 0.0."""
        multi = MultiLineString([])
        assert linear_length(multi) == 0.0

    def test_geometry_collection_returns_sum(self) -> None:
        """GeometryCollection returns sum of component lengths."""
        line1 = LineString([(0, 0), (1, 0)])
        line2 = LineString([(2, 0), (2, 1)])
        collection = GeometryCollection([line1, line2])
        assert linear_length(collection) == 2.0

    def test_nested_geometry_collection(self) -> None:
        """Nested GeometryCollection is handled recursively."""
        inner = GeometryCollection([
            LineString([(0, 0), (1, 0)]),
            LineString([(2, 0), (3, 0)]),
        ])
        outer = GeometryCollection([
            inner,
            LineString([(5, 0), (5, 2)]),
        ])
        assert linear_length(outer) == 4.0

    def test_empty_geometry_collection_returns_zero(self) -> None:
        """Empty GeometryCollection returns 0.0."""
        collection = GeometryCollection([])
        assert linear_length(collection) == 0.0

    def test_returns_float_type(self) -> None:
        """Return type is always float."""
        line = LineString([(0, 0), (3, 4)])
        result = linear_length(line)
        assert isinstance(result, float)

    def test_zero_length_linestring(self) -> None:
        """Zero-length LineString returns 0.0."""
        line = LineString([(1, 1), (1, 1)])
        assert linear_length(line) == 0.0
```

### Step 6: Run Tests

```bash
# Run new tests
pytest tests/test_geometry_utils.py -v

# Run existing tests to verify no regressions
pytest tests/test_adjacency.py tests/test_connectivity.py tests/test_facing.py -v

# Run full test suite
pytest tests/ -v
```

---

## Files Changed

| File | Action | Lines Changed |
|------|--------|---------------|
| `geometry_utils.py` | **CREATE** | +45 lines |
| `adjacency.py` | **MODIFY** | -8 lines (remove function), +1 import |
| `connectivity.py` | **MODIFY** | -8 lines (remove function), +1 import |
| `facing.py` | **MODIFY** | -8 lines (remove function), +1 import |
| `tests/test_geometry_utils.py` | **CREATE** | +75 lines |

**Net Change:** +105 lines (45 new utility + 60 new tests - 24 removed duplicates)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Import path issues | Very Low | Low | Use absolute imports from project root |
| Breaking existing tests | Very Low | Medium | Function signature and behavior identical |
| Shapely version compatibility | Very Low | Low | Uses basic Shapely types available in all versions |
| Circular imports | None | — | Utility module has no project dependencies |

---

## Verification Checklist

- [ ] `geometry_utils.py` created with proper docstring
- [ ] `adjacency.py` imports and uses `linear_length` from `geometry_utils`
- [ ] `connectivity.py` imports and uses `linear_length` from `geometry_utils`
- [ ] `facing.py` imports and uses `linear_length` from `geometry_utils`
- [ ] No remaining `_linear_length` definitions in codebase
- [ ] All new tests pass
- [ ] All existing tests pass
- [ ] No reduction in code coverage

---

## Expected Outcome

1. **Code Deduplication:** 3 identical function definitions replaced with 1 shared function
2. **Maintainability:** Single source of truth for linear length calculation
3. **Test Coverage:** New utility module has 100% test coverage
4. **Zero Breaking Changes:** All existing tests continue to pass
5. **Foundation for Future:** Pattern established for extracting other shared utilities

---

**Awaiting approval before implementation.**