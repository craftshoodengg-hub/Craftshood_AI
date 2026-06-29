# Building Model v2 - Version 1.0 Baseline

## Overview

Building Model v2 is a deterministic architectural floor plan understanding engine.
It converts structured building data into actionable intelligence through
validation, constraint evaluation, layout analysis, and optimization.

**No AI. No randomness. Pure deterministic computation.**

### Capabilities

- **Validation**: Structural integrity, entity references, geometry consistency
- **Constraints**: Functional, building code, accessibility, environmental, structural, Vastu
- **Evaluation**: Weighted scoring, quality classification, comprehensive reporting
- **Layout Analysis**: Adjacency, circulation, privacy, egress (4 independent engines)
- **Vastu Analysis**: Direction-based zone placement, 7 deterministic rules
- **Optimization**: Recommendation engine, iterative improvement, multi-objective scoring
- **Geometry**: Distance, polygon, transform, intersection, snap (pure functions)

---

## Modules

### Validation
- ValidationPipeline, ValidationResult, Validator, ValidationError

### Evaluation
- EvaluationPipeline, EvaluationReport, EvaluationSummary

### Optimization
- RecommendationEngine, Optimizer, IterationEngine, MultiObjectiveOptimizer

### Layout
- AdjacencyEngine, CirculationEngine, PrivacyEngine, EgressEngine
- LayoutEvaluationEngine, LayoutEvaluationResult, RoomGraph, AdjacencyRule

### Vastu
- VastuAnalyzer, VastuMetadata, VastuDirection, VastuZone, VastuGrid
- 7 Vastu Constraints

### Geometry
- Distance, Polygon, Transform, Intersection, Snap

---

## Pipelines

### Main Evaluation Pipeline
```
DXF -> Normalizer -> Geometry -> Walls -> Rooms -> RoomGraph -> BuildingModel
    -> Validation -> Constraints -> Scoring -> Evaluation Report
```

### Layout Pipeline
```
BuildingModel -> AdjacencyEngine -> RoomGraph (shared)
    -> CirculationEngine (analyze + evaluate)
    -> PrivacyEngine (analyze)
    -> EgressEngine (analyze + evaluate)
    -> LayoutEvaluationEngine -> LayoutEvaluationResult
```

### Optimization Pipeline
```
EvaluationReport -> RecommendationEngine -> ImprovementPlan
    -> Optimizer -> OptimizationResult
    -> IterationEngine -> IterationHistory (until convergence)
```

### Vastu Pipeline
```
BuildingModel -> VastuAnalyzer -> VastuMetadata
    -> 7 Vastu Constraints -> ConstraintResult
```

---

## Public API

```
building_model_v2/
  base.py                    BaseEntity, Point2D, BoundingBox
  types.py                   RoomType, WallType, FloorType, etc.
  entities_*.py              Building, Floor, Room, Wall, Column, Stair
  relationships.py           Relationship, RelationshipType
  geometry/                  distance, polygon, transform, intersection, snap
  validation/                ValidationPipeline, ValidationResult
  constraints/               ConstraintEngine, Constraint, ConstraintResult
  evaluation/                EvaluationPipeline, EvaluationReport
  optimization/              IterationEngine, Optimizer, RecommendationEngine
  rules/                     RulePacks (configuration only)
  vastu/                     VastuAnalyzer, VastuMetadata, VastuConstraints
  layout/                    AdjacencyEngine, CirculationEngine, PrivacyEngine,
                             EgressEngine, LayoutEvaluationEngine, RoomGraph
```

---

## Current Test Status

| Module | Tests | Status |
|--------|-------|--------|
| Vastu Models | 52 | PASS |
| Vastu Constraints | 54 | PASS |
| Vastu Geometry | 42 | PASS |
| Structural Constraints | 47 | PASS |
| Room Graph | 15 | PASS |
| Adjacency Rules | 22 | PASS |
| Adjacency Engine | 16 | PASS |
| Circulation | 19 | PASS |
| Privacy | 20 | PASS |
| Egress | 24 | PASS |
| Layout Evaluation | 26 | PASS |
| Rule Packs | 62 | PASS |
| Iteration Engine | ~30 | PASS |
| Optimization | ~50 | PASS |
| Building Model | ~40 | PASS |
| Entities | ~60 | PASS |
| Validation | ~40 | PASS |
| Geometry | ~50 | PASS |
| Constraints | ~100 | PASS |
| Evaluation | ~30 | PASS |
| **TOTAL** | **~2080** | **PASS** |

---

## Known Limitations

1. **Environment**: 3 test errors on Windows due to temp directory permission
   (pytest-of-CARFTSHOOD). Not a code issue.

2. **Legacy Modules**: 4 test files have pre-existing circular imports and null
   byte issues from earlier development phases. Not part of v2 engine.

3. **Rule Pack Serialization**: rule_pack_from_dict() requires all config sections.
   Partial deserialization is not yet supported.

4. **Multi-floor Analysis**: Layout engines primarily analyze single-floor
   buildings. Vertical circulation simulation is not implemented.

5. **Vastu Grid**: Uses simple bounding-box subdivision. Non-rectangular
   buildings may have imprecise zone assignments.

---

*Version: 1.0.0*
*Last Updated: 2026-06-28*
*Branch: feature/building-model-v2*

