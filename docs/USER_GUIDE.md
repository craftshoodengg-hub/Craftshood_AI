# Craftshood AI - User Guide

Version 1.0.0

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Generating Your First Design](#generating-your-first-design)
5. [Understanding the Output](#understanding-the-output)
6. [Editing Designs](#editing-designs)
7. [Live Evaluation](#live-evaluation)
8. [Applying Optimizations](#applying-optimizations)
9. [Exporting Your Design](#exporting-your-design)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

Craftshood AI is a deterministic architectural floor plan analysis and generation engine. It transforms natural language descriptions into structured building models with professional documentation.

### Key Features

- **Natural Language Input**: Describe your design in plain English
- **Instant Evaluation**: Get immediate feedback on code compliance, accessibility, and more
- **Automatic Optimization**: Receive prioritized improvement suggestions
- **Professional Exports**: Generate DXF, SVG, and PDF reports
- **Deterministic**: Same input always produces same output
- **No AI/ML**: Pure rule-based system with transparent logic

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
git clone https://github.com/your-org/craftshood-ai.git
cd craftshood-ai
pip install -e .
```

### Install with Optional Features

```bash
# For PDF export support
pip install -e ".[pdf]"

# For all features
pip install -e ".[all]"
```

### Verify Installation

```bash
python -c "import building_model_v2; print(building_model_v2.__version__)"
```

---

## Quick Start

### 1. Generate a Design

```python
from building_model_v2.ai import RequirementParser, GenerationPipeline

# Parse requirements
parser = RequirementParser()
result = parser.parse("3BHK modern apartment with balcony")

# Generate design
pipeline = GenerationPipeline()
generation_result = pipeline.generate(result.design_requirements)

# Access the building model
building_model = generation_result.building_model
```

### 2. Evaluate the Design

```python
from building_model_v2.evaluation import EvaluationPipeline

eval_pipeline = EvaluationPipeline()
eval_report = eval_pipeline.evaluate(building_model)

print(f"Overall Score: {eval_report.summary.overall_score}")
```

### 3. Export to PDF

```python
from building_model_v2.export import generate_pdf_report

generate_pdf_report(building_model, "my_design.pdf", evaluation_report=eval_report)
```

---

## Generating Your First Design

### Supported Room Types

- Living Room
- Bedroom (Master, Guest)
- Kitchen
- Dining Room
- Bathroom
- Balcony
- Staircase
- Corridor
- Store Room
- Pooja Room
- Study Room

### Example Prompts

```
"2BHK apartment with kitchen and balcony"
"3BHK modern villa with garden"
"4BHK duplex with parking"
"Small office with 4 workstations"
"Clinic with 2 consultation rooms"
```

### Understanding the Parser

The requirement parser extracts:
- Number of bedrooms
- Building type (apartment, villa, duplex, commercial)
- Special features (balcony, garden, parking)
- Style preferences (modern, traditional)

---

## Understanding the Output

### Building Model Structure

```
Building
├── Floors[]
│   ├── Rooms[]
│   ├── Walls[]
│   ├── Doors[]
│   ├── Windows[]
│   ├── Columns[]
│   └── Stairs[]
└── Relationships[]
```

### Room Properties

Each room includes:
- **Type**: Living, Bedroom, Kitchen, etc.
- **Area**: Square footage
- **Perimeter**: Linear feet
- **Vertices**: Polygon coordinates
- **Privacy Level**: Public, Private, Service
- **Natural Light**: Rating
- **Ventilation**: Rating

### Evaluation Scores

- **Overall Score**: 0-100 composite score
- **Category Scores**:
  - Functional
  - Building Code Compliance
  - Accessibility
  - Environmental
  - Structural
  - Vastu (optional)

---

## Editing Designs

### Modifying Rooms

```python
from building_model_v2.entities_room import Room

# Create a modified room
new_room = Room.create(
    vertices=[(0,0), (12,0), (12,10), (0,10)],
    room_type=RoomType.LIVING,
    ceiling_height=9.0
)

# Update the building model
building_model.rooms["living_1"] = new_room
```

### Adding Elements

```python
from building_model_v2.entities_wall import Wall

new_wall = Wall.create(
    start=(0, 0),
    end=(10, 0),
    wall_type=WallType.EXTERIOR
)

building_model.walls["wall_new"] = new_wall
```

---

## Live Evaluation

### Running Evaluation

```python
from building_model_v2.evaluation import EvaluationPipeline

pipeline = EvaluationPipeline()
report = pipeline.evaluate(building_model)

# Check specific categories
print(f"Building Code: {report.summary.category_scores['building_code']}")
print(f"Accessibility: {report.summary.category_scores['accessibility']}")
```

### Understanding Issues

Each issue includes:
- **Code**: Unique identifier (e.g., "ROOM_AREA_BELOW_MINIMUM")
- **Severity**: INFO, SUGGESTION, WARNING, RECOMMENDATION
- **Message**: Human-readable description
- **Entity ID**: Which room/element is affected
- **Score**: Impact on overall score

### Filtering Issues

```python
# Get only warnings
warnings = [i for i in report.constraint_issues if i.severity == ConstraintSeverity.WARNING]

# Get issues for specific room
room_issues = [i for i in report.constraint_issues if i.entity_id == "room_1"]
```

---

## Applying Optimizations

### Generating Improvement Plans

```python
from building_model_v2.optimization import RecommendationEngine

engine = RecommendationEngine()
plan = engine.generate(eval_report)

print(f"Actions: {plan.action_count}")
print(f"Estimated Improvement: {plan.total_estimated_gain}")
```

### Understanding Actions

Each action includes:
- **Title**: Short description
- **Description**: Detailed explanation
- **Priority**: 1 (highest) to 4 (lowest)
- **Target Entity**: What to modify
- **Estimated Gain**: Expected score improvement
- **Confidence**: Reliability of the suggestion

### Applying Actions

```python
from building_model_v2.optimization import Optimizer

optimizer = Optimizer()
result = optimizer.optimize(building_model, plan)

# Access optimized model
optimized_model = result.optimized_model
```

### Iteration Engine

For automatic convergence:

```python
from building_model_v2.optimization import IterationEngine, IterationEngineConfig

config = IterationEngineConfig(max_iterations=10, minimum_score_gain=0.25)
engine = IterationEngine(config=config)
history = engine.run(building_model)

print(f"Iterations: {history.iteration_count}")
print(f"Best Score: {history.best_score}")
print(f"Converged: {history.converged}")
```

---

## Exporting Your Design

### PDF Report

```python
from building_model_v2.export import generate_pdf_report, ReportMetadata

metadata = ReportMetadata.create(
    project_name="My Apartment",
    author="John Doe"
)

generate_pdf_report(
    building_model,
    "report.pdf",
    metadata=metadata,
    evaluation_report=eval_report
)
```

### DXF Export

```python
from building_model_v2.export import DXFExporter

exporter = DXFExporter()
exporter.export(building_model, "drawing.dxf")
```

### SVG Export

```python
from building_model_v2.export import build_drawing_model, export_svg_to_string

drawing = build_drawing_model(building_model)
svg_string = export_svg_to_string(drawing)

with open("drawing.svg", "w") as f:
    f.write(svg_string)
```

---

## Examples

See the `examples/` directory for complete working examples:

- `2bhk_apartment/` - Simple 2-bedroom apartment
- `3bhk_villa/` - 3-bedroom villa with garden
- `4bhk_duplex/` - 4-bedroom duplex
- `commercial_office/` - Small office space
- `small_clinic/` - Medical clinic

Each example includes:
- `prompt.txt` - Input description
- `building_model.json` - Generated model
- `evaluation_report.json` - Evaluation results
- `improvement_plan.json` - Optimization suggestions
- `drawing.svg` - Vector drawing
- `drawing.dxf` - CAD file
- `report.pdf` - Professional report
- `README.md` - Description

---

## Troubleshooting

### Common Issues

**Issue**: "reportlab is required for PDF generation"
```bash
pip install reportlab
```

**Issue**: "Invalid polygon for room"
- Ensure vertices form a closed polygon
- Check for self-intersections
- Verify minimum 3 vertices

**Issue**: Low evaluation score
- Check room areas meet minimums
- Verify door widths for accessibility
- Ensure window-to-floor ratios

### Getting Help

- Check `docs/DEVELOPER_GUIDE.md` for technical details
- Review `docs/API.md` for API reference
- See `docs/PERFORMANCE.md` for optimization tips

---

## Next Steps

1. Try the examples in `examples/`
2. Read `docs/DEVELOPER_GUIDE.md` for advanced usage
3. Explore `docs/API.md` for complete API reference
4. Check `docs/PERFORMANCE.md` for benchmarking data