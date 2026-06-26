# Craftshood_AI — Product Specification

**Version:** 1.0.0  
**Date:** 2026-06-26  
**Status:** Draft  
**Author:** OWL (AI Assistant)

---

## Table of Contents

1. [Vision](#1-vision)
2. [Target Users](#2-target-users)
3. [User Roles](#3-user-roles)
4. [Features](#4-features)
5. [Core Modules](#5-core-modules)
6. [AI Modules](#6-ai-modules)
7. [Building Analysis Modules](#7-building-analysis-modules)
8. [Vastu Analysis (Basic - Planned Feature)](#8-vastu-analysis-basic---planned-feature)
9. [Future Building Code Compliance](#9-future-building-code-compliance)
10. [Flutter App Features](#10-flutter-app-features)
11. [Backend Features](#11-backend-features)
12. [API Features](#12-api-features)
13. [Reports](#13-reports)
14. [Performance Targets](#14-performance-targets)
15. [Roadmap Summary](#15-roadmap-summary)

---

## 1. Vision

### Product Vision

Craftshood_AI is an **AI-powered architectural floor plan understanding engine** that transforms raw CAD/DXF drawings into rich, structured building intelligence. The system bridges the gap between traditional 2D CAD drawings and modern 3D BIM (Building Information Modeling) workflows.

### Mission

To democratize architectural analysis by making professional-grade floor plan understanding accessible to everyone — from individual homeowners to large architecture firms — through a simple API and intuitive mobile app.

### Long-term Goals

1. **Automate building analysis** — Eliminate manual measurement, annotation, and compliance checking
2. **Enable intelligent design** — Provide AI-driven suggestions for space optimization, code compliance, and cost reduction
3. **Bridge CAD and BIM** — Convert 2D drawings into 3D building information models without manual modeling
4. **Democratize architecture** — Make professional-grade analysis accessible via a simple API and mobile app
5. **Support the full lifecycle** — From initial design to construction documentation and facility management

### Ultimate Goal

A system that can look at any architectural floor plan and understand it like an experienced architect — identifying rooms, relationships, structural elements, MEP systems, and design intent.

---

## 2. Target Users

### Primary Users

| User Type | Description | Use Case |
|-----------|-------------|----------|
| **Architects** | Professional architects and designers | Quick analysis, design validation, client presentations |
| **Interior Designers** | Interior design professionals | Space planning, furniture layout, area calculations |
| **Real Estate Agents** | Property sales and marketing professionals | Property listings, floor plan visualization, area reports |
| **Homeowners** | Individual property owners | Understanding floor plans, renovation planning, Vastu checks |
| **Builders/Contractors** | Construction professionals | Material estimation, construction planning, BOQ generation |
| **Structural Engineers** | Structural engineering firms | Preliminary analysis, load path identification |
| **MEP Engineers** | Mechanical, electrical, plumbing engineers | System layout planning, coordination |
| **Property Managers** | Facility and property management companies | Space management, maintenance planning |

### Secondary Users

| User Type | Description | Use Case |
|-----------|-------------|----------|
| **Students** | Architecture and engineering students | Learning tool, project work |
| **Government Officials** | Building code enforcement | Plan review, compliance checking |
| **Insurance Assessors** | Property insurance companies | Property valuation, risk assessment |
| **Smart Home Providers** | Home automation companies | Planning sensor placement, automation design |

### User Personas

#### Persona 1: Sarah — The Architect
- **Age:** 34
- **Role:** Senior Architect at a mid-size firm
- **Pain Point:** Spends hours manually measuring and annotating floor plans
- **Goal:** Automate routine analysis and focus on design
- **Usage:** Daily, multiple projects

#### Persona 2: Raj — The Homeowner
- **Age:** 42
- **Role:** Software engineer building a new home
- **Pain Point:** Doesn't understand architectural drawings
- **Goal:** Visualize and validate the floor plan before construction
- **Usage:** Weekly during planning phase

#### Persona 3: Priya — The Real Estate Agent
- **Age:** 29
- **Role:** Property sales manager
- **Pain Point:** Needs quick area calculations and property comparisons
- **Goal:** Generate professional property reports quickly
- **Usage:** Per property listing

---

## 3. User Roles

### 3.1 System Roles

| Role | Description | Access Level |
|------|-------------|--------------|
| **Super Admin** | System administrator with full access | All features, user management, system config |
| **Admin** | Organization administrator | Organization settings, team management, billing |
| **Architect** | Professional user with advanced features | Full analysis, AI features, export, collaboration |
| **Analyst** | Standard user with basic analysis | Basic analysis, limited exports |
| **Viewer** | Read-only user | View shared reports, no analysis |
| **Guest** | Unauthenticated user | Limited demo access |

### 3.2 Role Permissions Matrix

| Feature | Super Admin | Admin | Architect | Analyst | Viewer | Guest |
|---------|-------------|-------|-----------|---------|--------|-------|
| Upload DXF | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Basic Analysis | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| AI Analysis | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Export Reports | ✅ | ✅ | ✅ | Limited | ❌ | ❌ |
| Share Reports | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Team Management | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| View Shared Reports | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| API Access | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Vastu Analysis | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Cost Estimation | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| BOQ Generation | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 4. Features

### 4.1 Core Features

| Feature | Description | Priority | Status |
|---------|-------------|----------|--------|
| **DXF Upload** | Upload and parse DXF files | High | ✅ Implemented |
| **Wall Detection** | Detect walls from LINE entities | High | ✅ Implemented |
| **Room Detection** | Detect room boundaries | High | ✅ Implemented |
| **Room Classification** | Classify rooms by type | High | ✅ Implemented |
| **Area Calculation** | Calculate room areas and perimeters | High | ✅ Implemented |
| **Adjacency Analysis** | Detect room-to-room adjacency | High | ✅ Implemented |
| **Connectivity Analysis** | Detect room connectivity via doors | High | ✅ Implemented |
| **Facing Detection** | Detect road-facing rooms | High | ✅ Implemented |
| **Zoning Classification** | Classify rooms into zones | High | ✅ Implemented |
| **Confidence Scoring** | Score analysis confidence | High | ✅ Implemented |
| **JSON Export** | Export analysis results | High | ✅ Implemented |
| **Building Statistics** | Aggregate building metrics | High | ✅ Implemented |

### 4.2 Advanced Features

| Feature | Description | Priority | Status |
|---------|-------------|----------|--------|
| **Door/Window Detection** | Detect openings from blocks/geometry | High | 🔄 Planned |
| **Furniture Detection** | Identify furniture from blocks | Medium | 🔄 Planned |
| **Stair Detection** | Identify staircases | Medium | 🔄 Planned |
| **Column Detection** | Detect structural columns | Medium | 🔄 Planned |
| **Multi-Floor Support** | Handle multiple floors | Medium | 🔄 Planned |
| **3D Model Generation** | Generate 3D from 2D plans | Low | 🔄 Planned |
| **BIM/IFC Export** | Export to IFC format | Low | 🔄 Planned |
| **Point Cloud Integration** | Process 3D scan data | Low | 🔄 Planned |

### 4.3 AI Features

| Feature | Description | Priority | Status |
|---------|-------------|----------|--------|
| **AI Room Detection** | ML-based room detection | High | 🔄 Planned |
| **AI Wall Detection** | ML-based wall detection | High | 🔄 Planned |
| **Design Suggestions** | AI-driven layout improvements | Medium | 🔄 Planned |
| **Code Compliance** | Automated code checking | Medium | 🔄 Planned |
| **Cost Estimation** | ML-based cost prediction | Medium | 🔄 Planned |
| **BOQ Generation** | Auto Bill of Quantities | Medium | 🔄 Planned |
| **Anomaly Detection** | Detect unusual layouts | Low | 🔄 Planned |
| **AI Chatbot** | Natural language queries | Low | 🔄 Planned |

### 4.4 Collaboration Features

| Feature | Description | Priority | Status |
|---------|-------------|----------|--------|
| **Multi-User Support** | Team-based analysis | Medium | 🔄 Planned |
| **Annotation System** | Add comments and markups | Medium | 🔄 Planned |
| **Version History** | Track changes across revisions | Medium | 🔄 Planned |
| **Share Reports** | Share analysis via link | High | 🔄 Planned |
| **Real-time Collaboration** | Simultaneous editing | Low | 🔄 Planned |

### 4.5 Export Features

| Feature | Description | Priority | Status |
|---------|-------------|----------|--------|
| **JSON Export** | Standard JSON output | High | ✅ Implemented |
| **GeoJSON Export** | Geographic JSON format | Medium | 🔄 Planned |
| **PDF Report** | Professional PDF reports | High | 🔄 Planned |
| **PNG/SVG Export** | Image exports | Medium | 🔄 Planned |
| **DWG/DXF Export** | CAD format export | Low | 🔄 Planned |
| **IFC Export** | BIM format export | Low | 🔄 Planned |
| **Excel Export** | Spreadsheet export | Medium | 🔄 Planned |

---

## 5. Core Modules

### 5.1 Pipeline Architecture

```
DXF File
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Normalization (normalizer/)                       │
│  - Layer names → LayerCategory enum                         │
│  - Block names → LayerCategory enum                         │
│  - Room labels → RoomName enum                              │
│  - Dimension strings → decimal feet (Dimension)             │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: Geometry Extraction (geometry_engine/)            │
│  - Read LINE entities from DXF                              │
│  - Detect parallel line pairs                                │
│  - Classify wall-width pairs (brick wall types)              │
│  - Merge connected wall segments into logical walls          │
│  - Export to JSON                                            │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: Room Detection (room_graph/)                      │
│  - Cast radial rays from room center points                 │
│  - Find nearest wall intersections                          │
│  - Build Shapely polygons from boundary points              │
│  - Calculate area, perimeter, centroid                      │
│  - Export room graph JSON                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: Building Model (building_model/)                  │
│  - Aggregate all module outputs                              │
│  - Build unified BuildingModel                              │
│  - Calculate statistics (room counts, areas, etc.)          │
│  - Validate model consistency                                │
│  - Serialize/deserialize JSON                                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 5: Analysis Modules                                  │
│  5a. Adjacency (adjacency.py)                                │
│      - Detect room-to-room adjacency via shared boundaries   │
│  5b. Connectivity (connectivity.py)                          │
│      - Door-based room connectivity                          │
│  5c. Facing (facing.py)                                      │
│      - Road-facing wall and front-room detection             │
│  5d. Zoning (zoning.py + zoning_rules.py)                    │
│      - Room classification (Public/Private/Service zones)    │
│  5e. Confidence (confidence.py)                              │
│      - Weighted confidence scoring (0.0–1.0)                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 6: API (backend/)                                    │
│  - FastAPI application (backend/app.py)                      │
│  - DWG parsing (backend/dwg_parser/)                         │
│  - CAD text intelligence (backend/cad_intelligence/)         │
│  - JSON export and serving                                   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 7: Flutter App (not in this repository)              │
│  - Client consumer of the API                                │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Module Descriptions

#### normalizer/
**Purpose:** Normalize extracted CAD information without mutating geometry.

| Module | Input | Output |
|--------|-------|--------|
| `layer_normalizer.py` | Raw layer names | `LayerCategory` enum |
| `block_normalizer.py` | Block names | `LayerCategory` enum |
| `text_normalizer.py` | Room label text | `RoomName` enum |
| `unit_normalizer.py` | Dimension strings | `Dimension` (decimal feet) |
| `normalizer.py` | All above | High-level facade |

#### geometry_engine/
**Purpose:** LINE-based wall extraction from DXF files.

| Module | Input | Output |
|--------|-------|--------|
| `line_reader.py` | DXF file | `list[LineEntity]` |
| `parallel_detector.py` | `list[LineEntity]` | `list[ParallelPair]` |
| `wall_classifier.py` | `list[ParallelPair]` | `list[WallSegment]` |
| `wall_merger.py` | `list[WallSegment]` | `list[LogicalWall]` |
| `wall_exporter.py` | All above | JSON |

#### room_graph/
**Purpose:** Build room boundary polygons from room centers and logical walls.

| Module | Input | Output |
|--------|-------|--------|
| `graph_builder.py` | Room centers, walls | `list[RoomGraphResult]` |
| `boundary_finder.py` | Room center, walls | `list[BoundaryIntersection]` |
| `polygon_builder.py` | Center, intersections | Shapely `Polygon` |
| `area_calculator.py` | Polygon | Area, perimeter, centroid |
| `room_exporter.py` | Room results | JSON |

#### building_model/
**Purpose:** Aggregate all module outputs into a unified building model.

| Module | Input | Output |
|--------|-------|--------|
| `builder.py` | All module outputs | `BuildingModel` |
| `models.py` | — | Core dataclasses |
| `serializer.py` | `BuildingModel` | JSON |
| `statistics.py` | `BuildingModel` | `BuildingStatistics` |
| `validator.py` | `BuildingModel` | Validation results |

#### analysis modules/
**Purpose:** Compute advanced spatial relationships and classifications.

| Module | Input | Output |
|--------|-------|--------|
| `adjacency.py` | `list[RoomPolygon]` | Adjacency graph |
| `connectivity.py` | Rooms, doors | Connectivity graph |
| `facing.py` | Rooms, walls, road | Facing information |
| `zoning.py` | Room ID, name | Zoning classification |
| `zoning_rules.py` | — | Zoning rules |
| `confidence.py` | Room, graphs, metadata | Confidence score |

#### backend/
**Purpose:** API, DWG parsing, and CAD text intelligence.

| Module | Input | Output |
|--------|-------|--------|
| `app.py` | HTTP requests | HTTP responses |
| `config.py` | Environment | Configuration |
| `cad_intelligence/text_extractor.py` | DXF | `list[TextEntity]` |
| `cad_intelligence/room_detector.py` | Text entities | `list[Detection]` |
| `cad_intelligence/plot_detector.py` | Text entities | Plot dimensions |
| `cad_intelligence/json_exporter.py` | Analysis | JSON |

---

## 6. AI Modules

### 6.1 Current AI Status

**Current State:** No AI/ML modules implemented yet. All analysis is rule-based.

**Planned AI Modules:**

### 6.2 Room Detection AI

**Purpose:** Detect rooms without text labels using machine learning.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | CNN + Transformer hybrid | Planned |
| **Training Data** | 10,000+ labeled floor plans | Planned |
| **Input** | DXF geometry (walls, lines) | Planned |
| **Output** | Room boundary polygons | Planned |
| **Accuracy Target** | >95% | Planned |

### 6.3 Wall Detection AI

**Purpose:** Detect walls from complex drawings with noise.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | U-Net segmentation | Planned |
| **Training Data** | 5,000+ annotated floor plans | Planned |
| **Input** | DXF entities | Planned |
| **Output** | Wall segments with types | Planned |
| **Accuracy Target** | >90% | Planned |

### 6.4 Door/Window Detection AI

**Purpose:** Detect openings from block references and geometry.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | YOLOv8 object detection | Planned |
| **Training Data** | 3,000+ labeled blocks | Planned |
| **Input** | Block references | Planned |
| **Output** | Door/window locations and types | Planned |
| **Accuracy Target** | >90% | Planned |

### 6.5 Furniture Detection AI

**Purpose:** Identify furniture from block references.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | Faster R-CNN | Planned |
| **Training Data** | 5,000+ labeled furniture blocks | Planned |
| **Input** | Block references | Planned |
| **Output** | Furniture type and location | Planned |
| **Accuracy Target** | >85% | Planned |

### 6.6 Stair Detection AI

**Purpose:** Identify staircases from parallel lines and text.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | Pattern matching + CNN | Planned |
| **Training Data** | 2,000+ labeled staircases | Planned |
| **Input** | Lines + text labels | Planned |
| **Output** | Stair location and direction | Planned |
| **Accuracy Target** | >90% | Planned |

### 6.7 Design Suggestion AI

**Purpose:** Recommend layout improvements based on best practices.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | LLM + RAG | Planned |
| **Knowledge Base** | Building codes, standards | Planned |
| **Input** | Building model | Planned |
| **Output** | Suggested improvements | Planned |

### 6.8 Cost Estimation AI

**Purpose:** Predict construction costs from drawings.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | Gradient Boosting + Neural Net | Planned |
| **Training Data** | Historical cost data | Planned |
| **Input** | Building model (areas, materials) | Planned |
| **Output** | Cost estimate with breakdown | Planned |
| **Accuracy Target** | ±15% | Planned |

### 6.9 Anomaly Detection AI

**Purpose:** Detect unusual layouts and potential errors.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | Autoencoder | Planned |
| **Training Data** | Normal floor plans | Planned |
| **Input** | Building model | Planned |
| **Output** | Anomaly score and details | Planned |

### 6.10 AI Chatbot

**Purpose:** Natural language queries about floor plans.

| Component | Description | Status |
|-----------|-------------|--------|
| **Model Architecture** | LLM (GPT/Claude) + RAG | Planned |
| **Context** | Building model + building codes | Planned |
| **Input** | Natural language query | Planned |
| **Output** | Natural language response | Planned |

---

## 7. Building Analysis Modules

### 7.1 Adjacency Analysis

**Purpose:** Detect which rooms share walls.

| Aspect | Details |
|--------|---------|
| **Input** | `list[RoomPolygon]` |
| **Output** | Adjacency graph with shared boundary lengths |
| **Algorithm** | Pairwise polygon intersection |
| **Complexity** | O(n²) |
| **Config** | `minimum_shared_wall_length` |

### 7.2 Connectivity Analysis

**Purpose:** Detect which rooms are connected by doors.

| Aspect | Details |
|--------|---------|
| **Input** | Rooms, adjacency graph, door locations |
| **Output** | Connectivity graph |
| **Algorithm** | Check door on shared boundary |
| **Complexity** | O(r² × d) |
| **Config** | `door_tolerance` |

### 7.3 Facing Analysis

**Purpose:** Detect road-facing rooms and cardinal direction.

| Aspect | Details |
|--------|---------|
| **Input** | Rooms, exterior walls, road location |
| **Output** | Road side, front rooms, cardinal direction |
| **Algorithm** | Nearest wall to room, room-wall intersection |
| **Complexity** | O(r × w) |
| **Config** | `exterior_wall_types` |

### 7.4 Zoning Classification

**Purpose:** Classify rooms into Public/Private/Service zones.

| Aspect | Details |
|--------|---------|
| **Input** | Room ID, room name |
| **Output** | Zone, privacy, preferred/avoid neighbors |
| **Algorithm** | Rule-based lookup |
| **Complexity** | O(r) |
| **Config** | `ZoningRuleBook` |

**Zone Types:**

| Zone | Privacy | Typical Rooms |
|------|---------|---------------|
| Public | Public | Living, Dining, Sitout, Portico |
| Private | Private | Master Bedroom, Bedroom, Toilet |
| Service | Semi-Private | Kitchen, Utility, Bathroom |

### 7.5 Confidence Scoring

**Purpose:** Score analysis confidence from 0.0 to 1.0.

| Aspect | Details |
|--------|---------|
| **Input** | Room polygon, adjacency, connectivity, facing, metadata |
| **Output** | Confidence score, quality label, breakdown |
| **Algorithm** | Weighted scoring |
| **Complexity** | O(r) |

**Scoring Weights:**

| Factor | Weight | Condition |
|--------|--------|-----------|
| Closed polygon | 0.20 | Polygon is closed |
| Valid geometry | 0.25 | Polygon is valid and non-empty |
| Known room name | 0.15 | Name matches known room types |
| Adjacency available | 0.15 | Adjacency data exists |
| Connectivity available | 0.15 | Connectivity data exists |
| Facing available | 0.10 | Facing data exists |

**Quality Labels:**

| Score Range | Label |
|-------------|-------|
| 0.90 - 1.00 | Excellent |
| 0.70 - 0.89 | Good |
| 0.50 - 0.69 | Fair |
| 0.00 - 0.49 | Poor |

### 7.6 Building Statistics

**Purpose:** Aggregate building-level metrics.

| Statistic | Description |
|-----------|-------------|
| `room_count` | Total number of rooms |
| `wall_count` | Total number of logical walls |
| `door_count` | Total number of detected doors |
| `window_count` | Total number of detected windows |
| `total_room_area` | Sum of all room areas |
| `average_room_area` | Mean room area |
| `total_room_perimeter` | Sum of all room perimeters |
| `adjacency_edge_count` | Number of adjacency relationships |
| `connectivity_edge_count` | Number of connectivity relationships |
| `front_room_count` | Number of road-facing rooms |
| `average_confidence` | Mean confidence score |
| `zones` | Room count per zone |

---

## 8. Vastu Analysis (Basic - Planned Feature)

### 8.1 Overview

Vastu Shastra is an ancient Indian science of architecture and spatial arrangement. Craftshood_AI will provide basic Vastu compliance checking for floor plans.

### 8.2 Planned Vastu Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Zone Mapping** | Map rooms to Vastu zones (NE, NW, SE, SW, Center) | High |
| **Zone Compliance** | Check if room placements follow Vastu principles | High |
| **Direction Detection** | Detect cardinal directions from plan | High |
| **Entrance Analysis** | Check main entrance direction | Medium |
| **Staircase Check** | Verify staircase placement | Medium |
| **Toilet Check** | Verify toilet placement | Medium |
| **Kitchen Check** | Verify kitchen placement | Medium |
| **Score Generation** | Generate Vastu compliance score | High |
| **Remedies** | Suggest Vastu remedies for violations | Low |

### 8.3 Vastu Zones

| Zone | Direction | Suitable For | Avoid |
|------|-----------|--------------|-------|
| **Ishanya** | NE | Living, Study, Prayer | Toilet, Kitchen |
| **Vayavya** | NW | Guest Room, Children's Room | Kitchen, Toilet |
| **Agneya** | SE | Kitchen, Dining | Bedroom, Prayer |
| **Nairutya** | SW | Master Bedroom, Storage | Kitchen, Prayer |
| **Madhya** | Center | Living, Prayer | Toilet, Kitchen, Stair |

### 8.4 Vastu Rules (Basic)

| Rule | Description | Check |
|------|-------------|-------|
| **Main Entrance** | Should be in N, NE, or E | Direction check |
| **Kitchen** | Should be in SE (Agni corner) | Zone check |
| **Master Bedroom** | Should be in SW | Zone check |
| **Toilet** | Should be in NW or W | Zone check |
| **Staircase** | Should be in S, SW, or W | Zone check |
| **Pooja Room** | Should be in NE (Ishanya) | Zone check |
| **Brahmasthan** | Center should be open and clear | Zone check |

### 8.5 Vastu Score Calculation

| Factor | Weight | Description |
|--------|--------|-------------|
| Zone Compliance | 0.40 | Room in correct zone |
| Direction Compliance | 0.30 | Entrance, windows direction |
| Avoidance Compliance | 0.20 | No toilet in NE, etc. |
| Brahmasthan | 0.10 | Center is clear |

**Vastu Score Labels:**

| Score Range | Label | Description |
|-------------|-------|-------------|
| 90-100 | Excellent | Highly compliant |
| 70-89 | Good | Mostly compliant |
| 50-69 | Fair | Some violations |
| 0-49 | Poor | Major violations |

### 8.6 Vastu Report

The Vastu report will include:
- Vastu zone map overlay
- Room-by-room compliance
- Overall Vastu score
- List of violations
- Suggested remedies
- Direction compass

---

## 9. Future Building Code Compliance

### 9.1 Overview

Future versions will include automated building code compliance checking for various jurisdictions.

### 9.2 Planned Code Compliance Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **IRC Compliance** | International Residential Code | High |
| **IBC Compliance** | International Building Code | High |
| **NBC Compliance** | National Building Code (India) | High |
| **Local Codes** | State/municipal building codes | Medium |
| **Fire Code** | Fire safety requirements | Medium |
| **Accessibility** | ADA/DDA compliance | Medium |
| **Structural Code** | Basic structural checks | Low |

### 9.3 Compliance Checks

| Category | Check | Description |
|----------|-------|-------------|
| **Room Size** | Minimum area | Rooms meet minimum area requirements |
| **Room Size** | Minimum dimension | Rooms meet minimum width/height |
| **Egress** | Exit distance | Maximum distance to exit |
| **Egress** | Exit width | Minimum door/corridor width |
| **Ventilation** | Natural ventilation | Window area vs floor area |
| **Lighting** | Natural light | Window area vs floor area |
| **Ceiling Height** | Minimum height | Rooms meet minimum ceiling height |
| **Fire Safety** | Smoke detectors | Required locations |
| **Fire Safety** | Fire exits | Number and location |
| **Accessibility** | Door width | Minimum accessible door width |
| **Accessibility** | Ramp slope | Maximum ramp slope |
| **Structural** | Column spacing | Basic span checks |

### 9.4 Compliance Report

The compliance report will include:
- Overall compliance score
- Pass/fail per requirement
- List of violations with references to code sections
- Suggested remediation
- Jurisdiction-specific requirements

### 9.5 Jurisdiction Support (Planned)

| Jurisdiction | Code | Priority |
|--------------|------|----------|
| International | IRC, IBC | High |
| India | NBC, IS Codes | High |
| USA | IBC, NFPA | Medium |
| UK | Building Regulations | Medium |
| UAE | Dubai Building Code | Medium |
| Singapore | SCDF Code | Low |

---

## 10. Flutter App Features

### 10.1 App Overview

The Flutter mobile app provides a mobile-friendly interface for Craftshood_AI, enabling architects, homeowners, and real estate professionals to analyze floor plans on the go.

### 10.2 App Screens

| Screen | Description | Priority |
|--------|-------------|----------|
| **Splash Screen** | App branding and loading | High |
| **Login/Signup** | Authentication | High |
| **Home Dashboard** | Quick actions and recent analyses | High |
| **Upload Screen** | DXF file upload | High |
| **Analysis Progress** | Real-time progress tracking | High |
| **Results Overview** | Summary of analysis | High |
| **Room List** | List of detected rooms | High |
| **Room Details** | Detailed room information | High |
| **Floor Plan Viewer** | Interactive 2D viewer | High |
| **3D Viewer** | 3D model viewer | Medium |
| **Reports** | Generated reports | High |
| **Settings** | App settings | Medium |
| **Profile** | User profile | Medium |

### 10.3 Core App Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **DXF Upload** | Upload from device or cloud | High |
| **Camera Capture** | Capture floor plan photos | Medium |
| **Progress Tracking** | Real-time analysis progress | High |
| **Offline Mode** | View cached results offline | Medium |
| **Push Notifications** | Analysis complete notification | High |
| **Share Reports** | Share via link, email, WhatsApp | High |
| **Export PDF** | Generate and download PDF | High |
| **Multi-language** | Support for multiple languages | Medium |

### 10.4 Floor Plan Viewer Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Pan & Zoom** | Navigate large plans | High |
| **Room Highlighting** | Tap room to highlight | High |
| **Room Labels** | Show room names and areas | High |
| **Layer Toggle** | Show/hide layers | Medium |
| **Measure Tool** | Measure distances | Medium |
| **Annotation** | Add notes and markups | Medium |
| **Compass** | Show cardinal directions | Low |

### 10.5 3D Viewer Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **3D Model** | Extruded 3D view | Medium |
| **Rotation** | Rotate 3D model | Medium |
| **Walkthrough** | Virtual walkthrough | Low |
| **Furniture** | Add furniture placeholders | Low |
| **Lighting** | Simulate natural lighting | Low |

### 10.6 Collaboration Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Share Analysis** | Share with team members | High |
| **Comments** | Add comments to analysis | Medium |
| **Tasks** | Create action items | Medium |
| **Version History** | View analysis history | Low |

---

## 11. Backend Features

### 11.1 Architecture

| Component | Technology | Status |
|-----------|------------|--------|
| Framework | FastAPI | ✅ Implemented |
| Server | Uvicorn | ✅ Implemented |
| Validation | Pydantic | ✅ Implemented |
| JSON | orjson | ✅ Implemented |
| DXF Parsing | ezdxf | ✅ Implemented |
| Geometry | Shapely, NumPy | ✅ Implemented |
| Logging | loguru | ✅ Implemented |
| Database | PostgreSQL | 🔄 Planned |
| Cache | Redis | 🔄 Planned |
| Task Queue | Celery/ARQ | 🔄 Planned |
| Object Storage | S3-compatible | 🔄 Planned |

### 11.2 Backend Features

| Feature | Description | Priority | Status |
|---------|-------------|----------|--------|
| **Pipeline Orchestration** | Coordinate analysis pipeline | High | ✅ Implemented |
| **File Upload** | Handle DXF file uploads | High | 🔄 Planned |
| **Async Processing** | Background task processing | High | 🔄 Planned |
| **Result Caching** | Cache analysis results | Medium | 🔄 Planned |
| **Health Checks** | System health endpoints | Medium | 🔄 Planned |
| **Rate Limiting** | API rate limiting | Medium | 🔄 Planned |
| **Request Validation** | Input validation | High | 🔄 Planned |
| **Error Handling** | Graceful error handling | High | 🔄 Planned |
| **Logging** | Structured logging | High | ✅ Implemented |
| **Configuration** | YAML/JSON config | Medium | 🔄 Planned |

### 11.3 Security Features

| Feature | Description | Priority | Status |
|---------|-------------|----------|--------|
| **Authentication** | API key / JWT | High | 🔄 Planned |
| **Authorization** | Role-based access control | High | 🔄 Planned |
| **CORS** | Cross-origin resource sharing | High | 🔄 Planned |
| **Rate Limiting** | Request throttling | Medium | 🔄 Planned |
| **Input Validation** | File and data validation | High | 🔄 Planned |
| **HTTPS** | TLS encryption | High | 🔄 Planned |
| **Audit Logging** | Access and action logging | Medium | 🔄 Planned |
| **Secret Management** | Environment-based secrets | High | 🔄 Planned |

### 11.4 Database Schema (Planned)

**Users Table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | String | Unique email |
| password_hash | String | Bcrypt hash |
| role | Enum | User role |
| created_at | Timestamp | Account creation |
| updated_at | Timestamp | Last update |

**Projects Table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner |
| name | String | Project name |
| description | String | Project description |
| created_at | Timestamp | Creation time |
| updated_at | Timestamp | Last update |

**Analyses Table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| project_id | UUID | Parent project |
| file_name | String | Original filename |
| file_hash | String | SHA256 hash |
| status | Enum | queued/processing/completed/failed |
| result_json | JSONB | Analysis results |
| created_at | Timestamp | Creation time |
| completed_at | Timestamp | Completion time |

---

## 12. API Features

### 12.1 API Architecture

| Feature | Description | Status |
|---------|-------------|--------|
| **RESTful Design** | Standard REST conventions | ✅ Implemented |
| **Versioning** | API version in URL | ✅ Implemented |
| **JSON Responses** | Standard JSON format | ✅ Implemented |
| **Error Handling** | Consistent error format | 🔄 Planned |
| **Pagination** | Cursor-based pagination | 🔄 Planned |
| **Filtering** | Query-based filtering | 🔄 Planned |
| **Sorting** | Field-based sorting | 🔄 Planned |
| **OpenAPI Docs** | Auto-generated docs | 🔄 Planned |

### 12.2 API Endpoints

#### Authentication Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/auth/register` | POST | Register new user | 🔄 Planned |
| `/api/v1/auth/login` | POST | Login and get JWT | 🔄 Planned |
| `/api/v1/auth/refresh` | POST | Refresh JWT token | 🔄 Planned |
| `/api/v1/auth/logout` | POST | Logout | 🔄 Planned |
| `/api/v1/auth/api-keys` | POST | Generate API key | 🔄 Planned |

#### Analysis Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/analyze` | POST | Full analysis | 🔄 Planned |
| `/api/v1/analyze/geometry` | POST | Geometry only | 🔄 Planned |
| `/api/v1/analyze/rooms` | POST | Rooms only | 🔄 Planned |
| `/api/v1/analyze/text` | POST | Text extraction | 🔄 Planned |
| `/api/v1/analysis/{id}` | GET | Get analysis status | 🔄 Planned |
| `/api/v1/analysis/{id}/results` | GET | Get results | 🔄 Planned |
| `/api/v1/analysis/{id}/export` | GET | Export results | 🔄 Planned |

#### Project Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/projects` | GET | List projects | 🔄 Planned |
| `/api/v1/projects` | POST | Create project | 🔄 Planned |
| `/api/v1/projects/{id}` | GET | Get project | 🔄 Planned |
| `/api/v1/projects/{id}` | PUT | Update project | 🔄 Planned |
| `/api/v1/projects/{id}` | DELETE | Delete project | 🔄 Planned |

#### File Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/files` | GET | List files | 🔄 Planned |
| `/api/v1/files` | POST | Upload file | 🔄 Planned |
| `/api/v1/files/{id}` | GET | Get file metadata | 🔄 Planned |
| `/api/v1/files/{id}` | DELETE | Delete file | 🔄 Planned |

#### AI Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/ai/suggestions` | POST | Get design suggestions | 🔄 Planned |
| `/api/v1/ai/chat` | POST | Chat with AI | 🔄 Planned |
| `/api/v1/ai/compliance` | POST | Check compliance | 🔄 Planned |
| `/api/v1/ai/cost` | POST | Estimate cost | 🔄 Planned |
| `/api/v1/ai/boq` | POST | Generate BOQ | 🔄 Planned |

#### Vastu Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/vastu/analyze` | POST | Analyze Vastu compliance | 🔄 Planned |
| `/api/v1/vastu/report/{id}` | GET | Get Vastu report | 🔄 Planned |

### 12.3 API Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-06-26T12:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid DXF file format",
    "details": [ ... ],
    "timestamp": "2026-06-26T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### 12.4 Rate Limiting (Planned)

| Tier | Requests/min | Concurrent | Price |
|------|-------------|------------|-------|
| Free | 10 | 1 | $0 |
| Starter | 60 | 5 | $29/mo |
| Pro | 300 | 20 | $99/mo |
| Enterprise | 1000+ | Unlimited | Custom |

---

## 13. Reports

### 13.1 Report Types

| Report | Description | Format | Priority |
|--------|-------------|--------|----------|
| **Analysis Summary** | Overview of floor plan analysis | PDF, JSON | High |
| **Room Schedule** | List of rooms with areas, zones | PDF, Excel | High |
| **Adjacency Matrix** | Room adjacency relationships | PDF, Excel | Medium |
| **Connectivity Map** | Room connectivity via doors | PDF, Image | Medium |
| **Facing Analysis** | Road-facing rooms and direction | PDF, JSON | Medium |
| **Zoning Map** | Zone classification visualization | PDF, Image | Medium |
| **Confidence Report** | Confidence scores per room | PDF, JSON | Medium |
| **Vastu Report** | Vastu compliance analysis | PDF | Low |
| **Compliance Report** | Building code compliance | PDF | Low |
| **Cost Estimate** | Construction cost estimate | PDF, Excel | Low |
| **BOQ** | Bill of Quantities | PDF, Excel | Low |

### 13.2 Report Contents

#### Analysis Summary Report

| Section | Content |
|---------|---------|
| **Cover Page** | Project name, date, logo |
| **Executive Summary** | Key metrics, room count, total area |
| **Floor Plan Image** | Rendered floor plan |
| **Room Schedule** | Table of rooms with areas, zones, confidence |
| **Statistics** | Building-level statistics |
| **Adjacency Graph** | Visual representation |
| **Zoning Map** | Color-coded zone map |
| **Confidence Chart** | Confidence distribution chart |
| **Recommendations** | AI-generated suggestions (if available) |

#### Room Schedule Report

| Column | Description |
|--------|-------------|
| Room Name | Name of the room |
| Zone | Public/Private/Service |
| Area (sq ft) | Room area |
| Perimeter (ft) | Room perimeter |
| Confidence | Analysis confidence |
| Adjacent To | List of adjacent rooms |
| Connected To | List of connected rooms |
| Facing | Direction (if applicable) |

#### Vastu Report

| Section | Content |
|---------|---------|
| **Vastu Score** | Overall compliance score |
| **Zone Map** | Vastu zone overlay |
| **Room Compliance** | Per-room Vastu compliance |
| **Violations** | List of violations |
| **Remedies** | Suggested remedies |
| **Compass** | Direction indicator |

### 13.3 Report Generation

| Feature | Description | Status |
|---------|-------------|--------|
| **PDF Generation** | Professional PDF reports | 🔄 Planned |
| **Excel Generation** | Spreadsheet reports | 🔄 Planned |
| **Custom Templates** | Customizable report templates | 🔄 Planned |
| **Branding** | Company logo and colors | 🔄 Planned |
| **Scheduling** | Automated report generation | 🔄 Planned |
| **Email Delivery** | Email reports to stakeholders | 🔄 Planned |

---

## 14. Performance Targets

### 14.1 Processing Speed

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| **Line Reading** | <1s | <1s | ✅ Met |
| **Parallel Detection** | <3s | 1-5s | ⚠️ Close |
| **Wall Classification** | <1s | <1s | ✅ Met |
| **Wall Merging** | <1s | <1s | ✅ Met |
| **Room Detection** | <5s | 2-10s | ⚠️ Close |
| **Adjacency Analysis** | <2s | 1-3s | ⚠️ Close |
| **Connectivity Analysis** | <1s | <1s | ✅ Met |
| **Facing Analysis** | <1s | <1s | ✅ Met |
| **Zoning Classification** | <1s | <1s | ✅ Met |
| **Confidence Scoring** | <1s | <1s | ✅ Met |
| **Total Pipeline** | <30s | 10-30s | ✅ Met |

### 14.2 Scalability Targets

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| **Max File Size** | 50 MB | Unlimited | ⚠️ No limit |
| **Max LINE Entities** | 10,000 | Unlimited | ⚠️ No limit |
| **Max Rooms** | 100 | Unlimited | ⚠️ No limit |
| **Concurrent Users** | 100+ | 1 | ⚠️ Single user |
| **API Uptime** | 99.9% | N/A | ⚠️ No SLA |

### 14.3 Accuracy Targets

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| **Room Detection** | >95% | ~80% | ⚠️ Needs improvement |
| **Wall Detection** | >90% | ~85% | ⚠️ Close |
| **Room Classification** | >90% | ~85% | ⚠️ Close |
| **Adjacency Accuracy** | >90% | ~85% | ⚠️ Close |
| **Area Calculation** | >98% | ~95% | ⚠️ Close |

### 14.4 Quality Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **Test Coverage** | >80% | Currently ~50% |
| **Code Quality** | A grade | Currently B+ |
| **Documentation** | Complete | Currently partial |
| **Bug Density** | <1 per 1000 LOC | Unknown |

### 14.5 Optimization Roadmap

| Priority | Optimization | Expected Impact |
|----------|--------------|-----------------|
| High | Spatial indexing (R-tree) | 10x faster for large files |
| High | Result caching | Eliminate duplicate processing |
| High | Async processing | Non-blocking API |
| Medium | NumPy vectorization | 2-5x faster geometry ops |
| Medium | Streaming file reading | Handle large files |
| Low | Connection pooling | Faster database queries |

---

## 15. Roadmap Summary

### Phase 1: Foundation (Q3 2026)
**Status:** In Progress

| Task | Status | Priority |
|------|--------|----------|
| LINE entity reading | ✅ Complete | High |
| Parallel pair detection | ✅ Complete | High |
| Wall classification | ✅ Complete | High |
| Wall merging | ✅ Complete | High |
| Layer normalization | ✅ Complete | High |
| Block normalization | ✅ Complete | High |
| Text normalization | ✅ Complete | High |
| Unit normalization | ✅ Complete | High |
| Room detection (basic) | ✅ Complete | High |
| Building model | ✅ Complete | High |
| Adjacency analysis | ✅ Complete | High |
| Connectivity analysis | ✅ Complete | High |
| Facing analysis | ✅ Complete | High |
| Zoning classification | ✅ Complete | High |
| Confidence scoring | ✅ Complete | High |
| POLYLINE support | 🔄 In Progress | High |
| ARC/CIRCLE support | 🔄 Planned | High |
| Spatial indexing | 🔄 Planned | High |
| Configurable wall types | 🔄 Planned | Medium |

### Phase 2: Intelligence (Q4 2026)
**Status:** Planned

| Task | Priority |
|------|----------|
| Door/window detection | High |
| Room auto-detection (geometry-only) | High |
| Corridor detection | Medium |
| Balcony/terrace detection | Medium |
| Furniture detection | Medium |
| Stair detection | Medium |
| Column detection | Medium |
| AI room detection (basic) | Medium |

### Phase 3: API & Backend (Q4 2026)
**Status:** Planned

| Task | Priority |
|------|----------|
| File upload API | High |
| Authentication (JWT) | High |
| Async processing (Celery) | High |
| Result caching (Redis) | Medium |
| Database persistence | Medium |
| Rate limiting | Medium |
| Health checks | Medium |
| OpenAPI documentation | Medium |
| Docker containerization | Medium |

### Phase 4: Mobile App (Q1 2027)
**Status:** Planned

| Task | Priority |
|------|----------|
| Flutter app architecture | High |
| DXF upload UI | High |
| Analysis progress UI | High |
| Results display | High |
| Interactive floor plan viewer | High |
| Export to PDF | High |
| Offline mode | Medium |
| Push notifications | Medium |
| 3D viewer | Low |

### Phase 5: AI Features (Q1-Q2 2027)
**Status:** Planned

| Task | Priority |
|------|----------|
| AI room detection (advanced) | High |
| AI wall detection | High |
| Design suggestions | Medium |
| Anomaly detection | Medium |
| Cost estimation | Medium |
| BOQ generation | Medium |
| AI chatbot | Low |

### Phase 6: Compliance & Vastu (Q2 2027)
**Status:** Planned

| Task | Priority |
|------|----------|
| Vastu analysis (basic) | High |
| Vastu scoring | High |
| IRC compliance | High |
| NBC compliance (India) | High |
| Fire code compliance | Medium |
| Accessibility compliance | Medium |

### Phase 7: Advanced Features (Q3-Q4 2027)
**Status:** Planned

| Task | Priority |
|------|----------|
| 3D model generation | Medium |
| BIM/IFC export | Medium |
| Multi-floor support | Medium |
| Point cloud integration | Low |
| Electrical layout detection | Low |
| Plumbing layout detection | Low |
| HVAC layout detection | Low |

### Timeline Summary

| Phase | Duration | Target |
|-------|----------|--------|
| Phase 1: Foundation | 2-3 weeks | Q3 2026 |
| Phase 2: Intelligence | 4-6 weeks | Q4 2026 |
| Phase 3: API & Backend | 3-4 weeks | Q4 2026 |
| Phase 4: Mobile App | 6-8 weeks | Q1 2027 |
| Phase 5: AI Features | 8-12 weeks | Q1-Q2 2027 |
| Phase 6: Compliance | 4-6 weeks | Q2 2027 |
| Phase 7: Advanced | 8-12 weeks | Q3-Q4 2027 |

**Total estimated time to full feature set: 12-18 months**

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **DXF** | Drawing Exchange Format, AutoCAD's file format for 2D CAD data |
| **DWG** | AutoCAD's proprietary binary file format |
| **BIM** | Building Information Modeling, 3D model-based process |
| **IFC** | Industry Foundation Classes, open BIM standard |
| **Vastu** | Ancient Indian science of architecture and spatial arrangement |
| **BOQ** | Bill of Quantities, document listing materials and costs |
| **MEP** | Mechanical, Electrical, Plumbing |
| **RAG** | Retrieval-Augmented Generation, AI technique |
| **LLM** | Large Language Model |

## Appendix B: References

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture documentation |
| [PIPELINE.md](PIPELINE.md) | Processing pipeline documentation |
| [API.md](API.md) | API documentation |
| [ROADMAP.md](ROADMAP.md) | Development roadmap |
| [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md) | Technical audit report |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-06-26  
**Next Review:** TBD