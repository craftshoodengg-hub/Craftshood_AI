# Changelog - Building Model v2

## Version 1.0.0 - 2026-06-28

### Phase 1: Code Quality & Consolidation
- Created geometry_utils.py with linear_length()
- Created validation.py with validate_room_polygons()
- Created dxf_utils.py with safe_dxf_value()
- Unified normalization patterns
- Removed empty files and dead code
- Updated imports in all affected modules

### Phase 9A-2: Vastu Constraint Engine
- VastuConstraint base class (category=VASTU, severity=RECOMMENDATION)
- EntranceDirectionConstraint (prefers North/East/North-East)
- KitchenPlacementConstraint (prefers South-East, acceptable North-West)
- MasterBedroomConstraint (prefers South-West)
- PoojaRoomConstraint (prefers North-East)
- StaircaseConstraint (prefers South/West/South-West, disallows center)
- ToiletPlacementConstraint (disallows North-East/Center)
- BrahmasthanConstraint (ensures center stays clear)
- 52 deterministic unit tests

### Phase 9B-1: Spatial Vastu Geometry Engine
- VastuCell and VastuGrid (3x3 grid with zone mapping)
- 7 geometry helper functions (centroid, direction, rotation, zone)
- VastuAnalyzer (auto-detects directions from room geometry)
- 42 deterministic unit tests

### Phase 9C: Structural Constraint Engine
- StructuralConstraint base class (category=STRUCTURAL, severity=WARNING)
- MaximumWallSpanConstraint (default 20ft)
- ColumnSpacingConstraint (default 18ft)
- LargeUnsupportedRoomConstraint (default 400 sqft)
- WallContinuityConstraint (load-bearing wall support)
- ColumnAlignmentConstraint (vertical alignment across floors)
- StairSupportConstraint (floor connection verification)
- StructuralSymmetryConstraint (approximate balance)
- 47 deterministic unit tests

### Phase 10A: Room Adjacency Intelligence Engine
- RoomConnection and RoomGraph (undirected graph with BFS pathfinding)
- AdjacencyRule/AdjacencyRuleSet (14 built-in rules)
- AdjacencyEngine (evaluate preferred/discouraged/required adjacencies)
- 57 deterministic unit tests

### Phase 10B: Circulation Intelligence Engine
- CirculationPath and CirculationMetrics
- CirculationEngine (BFS shortest paths, dead ends, efficiency)
- 35 deterministic unit tests

### Phase 10C: Privacy Intelligence Engine
- PrivacyConflict and PrivacyMetrics
- PrivacyEngine (master bedroom access, toilet visibility, pooja placement)
- 31 deterministic unit tests

### Phase 10D: Fire & Egress Intelligence Engine
- ExitPath and EgressMetrics
- EgressEngine (exit reachability, travel distance, dead ends)
- 38 deterministic unit tests

### Phase 10E: Layout Evaluation Aggregator
- LayoutEvaluationResult (aggregates all 4 layout engines)
- LayoutEvaluationEngine (orchestrates with shared RoomGraph)
- Deterministic scoring: 100 - adjacency*2 - privacy*3 - egress*4 - circulation*2
- Quality classification: Excellent/Good/Fair/Poor
- 26 deterministic unit tests

### Phase 10F: Architecture Cleanup & Public API Stabilization
- Added missing vastu and layout exports to main __init__.py
- Added VastuAnalyzer export to vastu and layout packages
- Fixed duplicate imports
- Created architecture documentation (2 docs)
- Created pipeline documentation
- Audited: serialization, type hints, immutability, exports

### Phase 10G: Test Suite Stabilization & Version 1.0 Baseline
- Fixed 12 rule pack test failures (structural constraint config mismatch)
- Fixed import errors in custom_rule_pack.py
- Fixed _parse_config call signatures
- Created Version 1.0 baseline documentation
- Created CHANGELOG
- **2080 tests passing**

---

*All phases implement deterministic, non-mutating, frozen dataclass-based analysis.*
*No AI. No randomness. Pure deterministic computation.*

