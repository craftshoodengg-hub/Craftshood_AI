# Building Model v2 - Pipeline Documentation

## Overview

The Building Model v2 pipeline processes architectural floor plans through
multiple deterministic analysis stages. Each stage produces immutable results
that feed into the next stage.

---

## Complete Pipeline

```
  DXF Input
      |
      v
  Normalizer -> Geometry Engine -> Wall Detection -> Room Detection
      |
      v
  RoomGraph (built once, shared by all layout engines)
      |
      v
  BuildingModel
      |
      v
  ValidationPipeline
      |
      v
  ConstraintEngine -> ConstraintScoreEngine -> EvaluationReport
      |
      +---> VastuAnalyzer -> Vastu Constraints
      |
      +---> Layout Evaluation
      |           |
      |           +---> AdjacencyEngine.evaluate()
      |           +---> CirculationEngine.analyze() + evaluate()
      |           +---> PrivacyEngine.analyze(graph)
      |           +---> EgressEngine.analyze(graph) + evaluate(graph)
      |           |
      |           v
      |       Layout EvaluationResult
      |
      +---> RecommendationEngine -> Optimizer -> IterationEngine
```

---

## Stages

### 1. Normalization
- Scale correction, rotation alignment
- Entity cleanup (duplicate removal, vertex snapping)

### 2. Geometry Engine
- Pure functions for distance, polygon, transform
- No mutation, no AI, deterministic

### 3. Wall Detection
- LINE entity processing from DXF
- Wall type classification (exterior, interior, bearing)

### 4. Room Detection
- Polygon-based room boundary detection
- Room type classification (Living, Bedroom, Kitchen, etc.)

### 5. RoomGraph
- Built once via AdjacencyEngine
- Shared by Circulation, Privacy, Egress engines
- BFS shortest path for connectivity queries

### 6. Validation
- Cross-entity reference integrity
- Geometry consistency checks

### 7. Constraints
- Functional, Building Code, Accessibility, Environmental, Structural, Vastu

### 8. Layout Evaluation
- Adjacency, Circulation, Privacy, Egress analysis
- Aggregated score with quality classification

### 9. Optimization
- RecommendationEngine -> Optimizer -> IterationEngine
- Repeats until convergence

