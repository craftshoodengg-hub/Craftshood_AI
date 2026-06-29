# Craftshood AI - Developer Guide

Version 1.0.0

## Table of Contents

1. [Project Structure](#project-structure)
2. [Architecture Overview](#architecture-overview)
3. [Core Pipelines](#core-pipelines)
4. [Building Model](#building-model)
5. [Export System](#export-system)
6. [Evaluation Engine](#evaluation-engine)
7. [Optimization Engine](#optimization-engine)
8. [Flutter Integration](#flutter-integration)
9. [Testing](#testing)
10. [Contributing](#contributing)

---

## Project Structure

```
craftshood_ai/
├── building_model_v2/          # Core library
│   ├── base.py                 # BaseEntity, Point2D, BoundingBox
│   ├── types.py                # Enums (RoomType, WallType, etc.)
│   ├── entities_*.py           # Building components
│   ├── relationships.py        # Entity relationships
│   ├── geometry/               # Geometric operations
│   ├── validation/             # Validation framework
│   ├── constraints/            # Constraint checking
│   ├── evaluation/             # Evaluation pipeline
│   ├── optimization/           # Optimization engine
│   ├── rules/                  # Rule packs
│   ├── ai/                     # Natural language parsing
│   ├── layout/                 # Layout analysis
│   ├── export/                 # Export system
│   └── vastu/                  # Vastu analysis
├── api/                        # FastAPI application
├── backend/                    # Backend services
├── tests/                      # Test suite
├── docs/                       # Documentation
├── examples/                   # Example projects
└── benchmarks/                 # Performance benchmarks
```

---

## Architecture Overview

### Design Principles

1. **Immutable Data**: All entities are frozen dataclasses
2. **Deterministic**: No randomness, no AI/ML
3. **Modular**: Each package has a single responsibility
4. **Type-Safe**: Full type hints throughout
5. **Testable**: Comprehensive test coverage

### Data Flow

```
User Prompt
    │
    ▼
RequirementParser
    │
    ▼
DesignRequirements
    │
    ▼
GenerationPipeline
    │
    ├── SpaceProgramGenerator
    ├── LayoutGenerator
    └── BuildingModelBuilder
    │
    ▼
BuildingModel
    │
    ├── EvaluationPipeline
    ├── OptimizationEngine
    └── ExportSystem
```

---

## Core Pipelines

### Generation Pipeline

```python
from building_model_v2.ai import GenerationPipeline

pipeline = GenerationPipeline()
result = pipeline.generate(design_requirements)

# Access results
building_model = result.building_model
space_program = result.space_program
initial_layout = result.initial_layout
```

### Evaluation Pipeline

```python
from building_model_v2.evaluation import EvaluationPipeline

pipeline = EvaluationPipeline()
report = pipeline.evaluate(building_model)

# Access results
summary = report.summary
issues = report.constraint_issues
errors = report.validation_errors
```

### Optimization Pipeline

```python
from building_model_v2.optimization import IterationEngine

engine = IterationEngine()
history = engine.run(building_model)

# Access results
best = history.best_iteration
iterations = history.iterations
```

---

## Building Model

### Entity Hierarchy

```
BaseEntity (abstract)
├── Building
├── Floor
├── Room
├── Wall
├── Opening
│   ├── Door
│   └── Window
├── Column
└── Stair
```

### Creating Entities

All entities use factory methods:

```python
from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType

room = Room.create(
    vertices=[(0,0), (10,0), (10,10), (0,10)],
    room_type=RoomType.LIVING,
    ceiling_height=9.0
)
```

### BuildingModel Container

```python
from building_model_v2.validation.cross_entity_validator import BuildingModel

model = BuildingModel(
    building=building,
    floors={"floor_1": floor},
    rooms={"room_1": room},
    walls={"wall_1": wall},
    columns={},
    stairs={},
    doors={"door_1": door},
    windows={"window_1": window},
    relationships=[],
)
```

---

## Export System

### DrawingModel

The `DrawingModel` is the intermediate representation for all exports:

```python
from building_model_v2.export import build_drawing_model

drawing = build_drawing_model(building_model)
# Contains: layers, entities, bounds, annotations
```

### DXF Export

```python
from building_model_v2.export import DXFExporter

exporter = DXFExporter()
exporter.export(building_model, "output.dxf")
```

### SVG Export

```python
from building_model_v2.export import export_svg_to_string

svg = export_svg_to_string(drawing_model)
```

### PDF Export

```python
from building_model_v2.export import generate_pdf_report

generate_pdf_report(building_model, "report.pdf")
```

---

## Evaluation Engine

### Constraint System

Constraints check specific rules:

```python
from building_model_v2.constraints import MinimumRoomAreaConstraint

constraint = MinimumRoomAreaConstraint()
result = constraint.check(building_model)
```

### Constraint Categories

- **Functional**: Room connectivity, isolation
- **Building Code**: Area, width, height minimums
- **Accessibility**: Door widths, turning radius
- **Environmental**: Natural light, ventilation
- **Structural**: Wall spans, column spacing
- **Vastu**: Direction-based compliance

### Scoring

Each constraint produces a score (0-100):

```python
score = result.score  # 0-100
issues = result.issues  # List of ConstraintIssue
```

---

## Optimization Engine

### Recommendation Engine

Generates improvement plans:

```python
from building_model_v2.optimization import RecommendationEngine

engine = RecommendationEngine()
plan = engine.generate(evaluation_report)
```

### Action Registry

Maps constraint codes to optimization functions:

```python
from building_model_v2.optimization import ActionRegistry

registry = ActionRegistry()
func = registry.get("ROOM_TOO_SMALL")  # Returns expand_room function
```

### Optimizer

Applies actions to building model:

```python
from building_model_v2.optimization import Optimizer

optimizer = Optimizer()
result = optimizer.optimize(building_model, plan)
optimized_model = result.optimized_model
```

### Iteration Engine

Automatically iterates until convergence:

```python
from building_model_v2.optimization import IterationEngine, IterationEngineConfig

config = IterationEngineConfig(max_iterations=10)
engine = IterationEngine(config=config)
history = engine.run(building_model)
```

---

## Flutter Integration

### API Endpoints

The Flutter app communicates via REST API:

```
POST /api/v1/generate    - Generate design
POST /api/v1/evaluate    - Evaluate design
POST /api/v1/optimize    - Optimize design
GET  /api/v1/export/dxf  - Export DXF
GET  /api/v1/export/svg  - Export SVG
GET  /api/v1/export/pdf  - Export PDF
```

### Data Exchange

JSON serialization for all models:

```python
# Serialize
data = building_model.to_dict()

# Deserialize
model = BuildingModel.from_dict(data)
```

---

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# Specific module
pytest tests/test_building_model_v2.py

# With coverage
pytest --cov=building_model_v2 tests/
```

### Test Organization

- `test_entities_*.py` - Entity tests
- `test_geometry_*.py` - Geometry tests
- `test_validation_*.py` - Validation tests
- `test_constraint_*.py` - Constraint tests
- `test_optimization_*.py` - Optimization tests
- `test_pdf_report.py` - PDF export tests

---

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Update documentation
5. Submit pull request

### Versioning

Semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

---

## Next Steps

- Read `docs/API.md` for complete API reference
- Check `docs/PERFORMANCE.md` for benchmarks
- See `docs/ARCHITECTURE_OVERVIEW.md` for diagrams
- Review `examples/` for usage patterns