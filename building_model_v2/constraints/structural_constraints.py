"""Structural Constraints for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Final
from ..entities_column import Column
from ..entities_stair import Stair
from ..entities_wall import Wall
from ..validation.cross_entity_validator import BuildingModel
from .constraint import Constraint
from .constraint_category import ConstraintCategory
from .constraint_issue import ConstraintIssue
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity

STRUCTURAL_WALL_SPAN: Final[str] = "STRUCTURAL_WALL_SPAN"
STRUCTURAL_COLUMN_SPACING: Final[str] = "STRUCTURAL_COLUMN_SPACING"
STRUCTURAL_UNSUPPORTED_ROOM: Final[str] = "STRUCTURAL_UNSUPPORTED_ROOM"
STRUCTURAL_WALL_CONTINUITY: Final[str] = "STRUCTURAL_WALL_CONTINUITY"
STRUCTURAL_COLUMN_ALIGNMENT: Final[str] = "STRUCTURAL_COLUMN_ALIGNMENT"
STRUCTURAL_STAIR_SUPPORT: Final[str] = "STRUCTURAL_STAIR_SUPPORT"
STRUCTURAL_SYMMETRY: Final[str] = "STRUCTURAL_SYMMETRY"

@dataclass(slots=True)
class StructuralConstraintConfig:
    severity: ConstraintSeverity = ConstraintSeverity.WARNING

class StructuralConstraint(Constraint):
    def __init__(self, name: str, description: str = "", config: StructuralConstraintConfig | None = None) -> None:
        super().__init__(name=name, description=description)
        self._config = config or StructuralConstraintConfig()
    @property
    def category(self) -> ConstraintCategory:
        return ConstraintCategory.STRUCTURAL
    @property
    def default_severity(self) -> ConstraintSeverity:
        return self._config.severity
    def _create_issue(self, code: str, message: str, entity_id: str | None = None, score: float = 0.5) -> ConstraintIssue:
        return ConstraintIssue(code=code, message=message, severity=self.default_severity, entity_id=entity_id, score=score)

@dataclass(slots=True)
class MaximumWallSpanConfig(StructuralConstraintConfig):
    max_span_ft: float = 20.0

class MaximumWallSpanConstraint(StructuralConstraint):
    def __init__(self, config: MaximumWallSpanConfig | None = None) -> None:
        super().__init__(name="Maximum Wall Span", description="Ensures walls do not exceed maximum unsupported span", config=config)
        self._config = config or MaximumWallSpanConfig()
    @property
    def max_span_ft(self) -> float:
        return self._config.max_span_ft
    def evaluate(self, m: BuildingModel) -> ConstraintResult:
        issues = []
        for wid, wall in m.walls.items():
            if wall.geometry.is_empty: continue
            wl = wall.length
            if wl > self._config.max_span_ft:
                issues.append(self._create_issue(STRUCTURAL_WALL_SPAN, f"Wall span of {wl:.1f} ft exceeds maximum of {self._config.max_span_ft:.1f} ft", wid, min(1.0, (wl - self._config.max_span_ft) / self._config.max_span_ft)))
        return ConstraintResult(issues=issues)

@dataclass(slots=True)
class ColumnSpacingConfig(StructuralConstraintConfig):
    max_spacing_ft: float = 18.0
    min_columns: int = 2

class ColumnSpacingConstraint(StructuralConstraint):
    def __init__(self, config: ColumnSpacingConfig | None = None) -> None:
        super().__init__(name="Column Spacing", description="Ensures structural columns are adequately spaced", config=config)
        self._config = config or ColumnSpacingConfig()
    @property
    def max_spacing_ft(self) -> float:
        return self._config.max_spacing_ft
    def evaluate(self, m: BuildingModel) -> ConstraintResult:
        issues = []
        cols = list(m.columns.values())
        if len(cols) < self._config.min_columns: return ConstraintResult(issues=issues)
        for i, c1 in enumerate(cols):
            for c2 in cols[i+1:]:
                d = c1.geometry.distance_to(c2.geometry)
                if d > self._config.max_spacing_ft:
                    issues.append(self._create_issue(STRUCTURAL_COLUMN_SPACING, f"Column spacing of {d:.1f} ft exceeds maximum of {self._config.max_spacing_ft:.1f} ft", f"{c1.id},{c2.id}", min(1.0, (d - self._config.max_spacing_ft) / self._config.max_spacing_ft)))
        return ConstraintResult(issues=issues)

@dataclass(slots=True)
class LargeUnsupportedRoomConfig(StructuralConstraintConfig):
    max_area_sqft: float = 400.0

class LargeUnsupportedRoomConstraint(StructuralConstraint):
    def __init__(self, config: LargeUnsupportedRoomConfig | None = None) -> None:
        super().__init__(name="Large Unsupported Room", description="Detects rooms exceeding maximum unsupported area", config=config)
        self._config = config or LargeUnsupportedRoomConfig()
    @property
    def max_area_sqft(self) -> float:
        return self._config.max_area_sqft
    def evaluate(self, m: BuildingModel) -> ConstraintResult:
        issues = []
        for rid, room in m.rooms.items():
            if room.polygon.is_empty: continue
            area = float(room.polygon.area)
            if area > self._config.max_area_sqft:
                issues.append(self._create_issue(STRUCTURAL_UNSUPPORTED_ROOM, f"Room area of {area:.0f} sq ft exceeds maximum of {self._config.max_area_sqft:.0f} sq ft", rid, min(1.0, (area - self._config.max_area_sqft) / self._config.max_area_sqft)))
        return ConstraintResult(issues=issues)


@dataclass(slots=True)
class WallContinuityConfig(StructuralConstraintConfig):
    require_continuity: bool = True

class WallContinuityConstraint(StructuralConstraint):
    def __init__(self, config: WallContinuityConfig | None = None) -> None:
        super().__init__(name="Wall Continuity", description="Recommends continuous structural walls", config=config)
        self._config = config or WallContinuityConfig()
    def evaluate(self, m: BuildingModel) -> ConstraintResult:
        issues = []
        if not self._config.require_continuity: return ConstraintResult(issues=issues)
        for wall in m.walls.values():
            if not wall.is_load_bearing: continue
            if wall.floor_id is None:
                issues.append(self._create_issue(STRUCTURAL_WALL_CONTINUITY, "Load-bearing wall has no floor connection", wall.id, 0.6))
                continue
            if not wall.metadata.get("has_support", False) and wall.metadata.get("supported_by") is None:
                issues.append(self._create_issue(STRUCTURAL_WALL_CONTINUITY, "Load-bearing wall may lack proper vertical support", wall.id, 0.5))
        return ConstraintResult(issues=issues)

@dataclass(slots=True)
class ColumnAlignmentConfig(StructuralConstraintConfig):
    tolerance_ft: float = 2.0
    min_floors: int = 2

class ColumnAlignmentConstraint(StructuralConstraint):
    def __init__(self, config: ColumnAlignmentConfig | None = None) -> None:
        super().__init__(name="Column Alignment", description="Recommends vertically aligned columns across floors", config=config)
        self._config = config or ColumnAlignmentConfig()
    def evaluate(self, m: BuildingModel) -> ConstraintResult:
        issues = []
        floor_columns: dict[str, list] = {}
        for col in m.columns.values():
            fid = col.floor_id
            if fid is None: continue
            floor_columns.setdefault(fid, []).append(col)
        if len(floor_columns) < self._config.min_floors: return ConstraintResult(issues=issues)
        floor_ids = sorted(floor_columns.keys())
        for i in range(len(floor_ids) - 1):
            cols_lower = floor_columns[floor_ids[i]]
            cols_upper = floor_columns[floor_ids[i + 1]]
            for cu in cols_upper:
                if cu.geometry.is_empty: continue
                has_match = False
                for cl in cols_lower:
                    if cl.geometry.is_empty: continue
                    if cu.geometry.distance_to(cl.geometry) <= self._config.tolerance_ft:
                        has_match = True; break
                if not has_match:
                    issues.append(self._create_issue(STRUCTURAL_COLUMN_ALIGNMENT, f"Column not aligned with any column on floor below", cu.id, 0.4))
        return ConstraintResult(issues=issues)


@dataclass(slots=True)
class StairSupportConfig(StructuralConstraintConfig):
    require_floor_connection: bool = True

class StairSupportConstraint(StructuralConstraint):
    def __init__(self, config: StairSupportConfig | None = None) -> None:
        super().__init__(name="Stair Support", description="Ensures stairs have proper supporting floor connections", config=config)
        self._config = config or StairSupportConfig()
    def evaluate(self, m: BuildingModel) -> ConstraintResult:
        issues = []
        for sid, stair in m.stairs.items():
            if not self._config.require_floor_connection: continue
            if stair.floor_id is None:
                issues.append(self._create_issue(STRUCTURAL_STAIR_SUPPORT, "Stair has no floor connection - may lack proper support", sid, 0.5))
                continue
            if not stair.metadata.get("has_landing", False) and stair.metadata.get("supported_by") is None:
                issues.append(self._create_issue(STRUCTURAL_STAIR_SUPPORT, "Stair landing support metadata incomplete", sid, 0.3))
        return ConstraintResult(issues=issues)

@dataclass(slots=True)
class StructuralSymmetryConfig(StructuralConstraintConfig):
    tolerance: float = 0.20

class StructuralSymmetryConstraint(StructuralConstraint):
    def __init__(self, config: StructuralSymmetryConfig | None = None) -> None:
        super().__init__(name="Structural Symmetry", description="Evaluates approximate balance of structural elements", config=config)
        self._config = config or StructuralSymmetryConfig()
    @property
    def tolerance(self) -> float:
        return self._config.tolerance
    def evaluate(self, m: BuildingModel) -> ConstraintResult:
        issues = []
        walls = [w for w in m.walls.values() if not w.geometry.is_empty]
        cols = [c for c in m.columns.values() if not c.geometry.is_empty]
        if not walls and not cols: return ConstraintResult(issues=issues)
        all_geoms = [w.geometry for w in walls] + [c.geometry for c in cols]
        from shapely.ops import unary_union
        combined = unary_union(all_geoms)
        centroid = combined.centroid
        min_x, min_y, max_x, max_y = combined.bounds
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        offset_x = abs(centroid.x - center_x)
        offset_y = abs(centroid.y - center_y)
        bbox_w = max_x - min_x
        bbox_h = max_y - min_y
        if bbox_w == 0 and bbox_h == 0: return ConstraintResult(issues=issues)
        asym_x = offset_x / bbox_w if bbox_w > 0 else 0
        asym_y = offset_y / bbox_h if bbox_h > 0 else 0
        max_asym = max(asym_x, asym_y)
        if max_asym > self._config.tolerance:
            issues.append(self._create_issue(STRUCTURAL_SYMMETRY, f"Structural asymmetry detected (max deviation: {max_asym:.0%}, tolerance: {self._config.tolerance:.0%})", score=min(1.0, max_asym / (self._config.tolerance * 2))))
        return ConstraintResult(issues=issues)
