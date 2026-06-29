# Building Model v2 - Architecture Overview

## Package Overview

Building Model v2 is a deterministic architectural floor plan understanding engine.
It converts structured building data into actionable intelligence through a
pipeline of evaluation, constraint checking, and optimization.

**No AI. No randomness. Pure deterministic computation.**

### Core Principles

- **Immutable data**: All entities and results use frozen dataclasses
- **Deterministic outputs**: Same input always produces same output
- **Modular engines**: Each analysis domain is an independent subsystem
- **Graph-based spatial analysis**: Room connectivity drives layout intelligence

---

## Package Structure

```
building_model_v2/
  base.py                    # BaseEntity, Point2D, BoundingBox
  types.py                   # RoomType, WallType, FloorType, etc.
  entities_*.py              # Building, Floor, Room, Wall, Column, Stair, Door, Window
  relationships.py           # Relationship, RelationshipType
  geometry/                  # Distance, polygon, transform, intersection, snap
  validation/                # ValidationPipeline, ValidationResult
  constraints/               # Constraint framework + implementations
  evaluation/                # EvaluationPipeline, EvaluationReport
  optimization/              # IterationEngine, Optimizer, RecommendationEngine
  rules/                     # RulePacks (configuration only)
  vastu/                     # Vastu data models, geometry, analyzer, constraints
  layout/                    # Room graph, adjacency, circulation, privacy, egress
```

---

## Evaluation Pipeline

```
BuildingModel
    |
    v
ValidationPipeline -> ValidationResult
    |
    v
ConstraintEngine -> ConstraintResult
    |
    v
ConstraintScoreEngine -> ConstraintScore
    |
    v
EvaluationSummary
    |
    v
EvaluationReport
```

### Key Components

- **ValidationPipeline**: Structural integrity checks (entity references, geometry)
- **ConstraintEngine**: Aggregates all constraint categories
- **ConstraintScoreEngine**: Weighted scoring of constraint results
- **EvaluationPipeline**: Orchestrates the full evaluation into a single report

---

## Optimization Pipeline

```
EvaluationReport
    |
    v
RecommendationEngine -> ImprovementPlan
    |
    v
Optimizer -> OptimizationResult
    |
    v
IterationEngine -> IterationHistory
```

### Key Components

- **RecommendationEngine**: Converts evaluation issues into prioritized actions
- **Optimizer**: Applies improvement actions to a copy of the BuildingModel
- **IterationEngine**: Repeatedly evaluates and improves until convergence
- **MultiObjectiveOptimizer**: Weighted multi-objective scoring for trade-off analysis

---

## Layout Pipeline

```
BuildingModel
    |
    v
AdjacencyEngine.build_graph() -> RoomGraph
    |
    v
AdjacencyEngine.evaluate()
CirculationEngine.analyze() + evaluate()
PrivacyEngine.analyze(graph)
EgressEngine.analyze(graph) + evaluate(graph)
    |
    v
LayoutEvaluationEngine -> LayoutEvaluationResult
```

### Key Components

- **RoomGraph**: Undirected graph of room connectivity (BFS pathfinding)
- **AdjacencyEngine**: Evaluates preferred/discouraged room adjacencies
- **CirculationEngine**: Analyzes movement patterns and dead ends
- **PrivacyEngine**: Checks bedroom/toilet/pooja privacy violations
- **EgressEngine**: Verifies all rooms can reach an exit
- **LayoutEvaluationEngine**: Aggregates all layout results with scoring

### Layout Scoring

```
Start: 100
- Adjacency issues x 2
- Privacy conflicts x 3
- Egress issues x 4
- Circulation issues x 2
Clamp: 0-100
```

| Score | Quality |
|-------|---------|
| 95-100 | Excellent |
| 85-94 | Good |
| 70-84 | Fair |
| <70 | Poor |

---

## Vastu Pipeline

```
BuildingModel
    |
    v
VastuAnalyzer.analyze() -> VastuMetadata
    |
    v
EntranceDirectionConstraint
KitchenPlacementConstraint
MasterBedroomConstraint
PoojaRoomConstraint
StaircaseConstraint
ToiletPlacementConstraint
BrahmasthanConstraint
```

### Key Components

- **VastuAnalyzer**: Computes Vastu directions from room geometry centroids
- **VastuMetadata**: Stores entrance, kitchen, bedroom, pooja, staircase, toilet directions
- **Vastu Constraints**: 7 deterministic rules checking zone placements
- **VastuGrid**: 3x3 grid overlay for zone-based analysis

---

## Extension Points

1. **New Constraint Categories**: Extend `Constraint` base class
2. **New Room Types**: Add to `RoomType` enum
3. **Custom Rule Packs**: Use `create_custom_rule_pack()`
4. **New Analysis Engines**: Follow pattern in `layout/`
5. **IFC/BIM Export**: Entities designed for future IfcMapping
6. **Flutter Rendering**: Polygon geometry supports canvas rendering

---

## Data Flow

```
DXF -> Normalizer -> Geometry -> Walls -> Rooms -> RoomGraph -> BuildingModel
    -> Validation -> Constraints -> Evaluation -> Layout -> Recommendations
```

*Document Version: 1.0.0*

