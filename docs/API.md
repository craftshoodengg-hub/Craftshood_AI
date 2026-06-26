# Craftshood_AI — API Documentation

## Overview

The Craftshood_AI API is built with **FastAPI** and provides endpoints for uploading, analyzing, and retrieving insights from architectural DXF floor plans. The API follows RESTful conventions and returns JSON responses.

## Base URL

```
http://localhost:8000
```

## Authentication

> **Note:** Authentication is not yet implemented. Planned for v0.2.0.

Future authentication will use API keys passed via the `X-API-Key` header.

---

## Current Endpoints

> **Note:** The API is currently in development. The following endpoints are planned or partially implemented.

---

### Health Check

#### `GET /health`

Returns the health status of the API.

**Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-06-26T12:00:00Z"
}
```

---

### DXF Analysis

#### `POST /api/v1/analyze`

Upload and analyze a DXF file.

**Request:**

- Content-Type: `multipart/form-data`
- Body: DXF file

**Response:**

```json
{
  "id": "analysis_abc123",
  "status": "completed",
  "source_file": "floor_plan.dxf",
  "generated_at": "2026-06-26T12:00:00Z",
  "summary": {
    "room_count": 5,
    "wall_count": 12,
    "door_count": 4,
    "window_count": 6,
    "total_area": 1250.5
  },
  "rooms": [
    {
      "room_id": "room_1",
      "room_name": "Living",
      "area": 250.0,
      "perimeter": 60.0,
      "centroid": {"x": 100.0, "y": 150.0},
      "zone": "Public",
      "confidence": 0.95
    }
  ],
  "walls": [...],
  "adjacency_graph": [...],
  "connectivity_graph": [...],
  "facing_information": {...},
  "zoning": [...],
  "confidence": [...]
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Invalid file format (not a DXF) |
| 422 | Validation error |
| 500 | Internal processing error |

---

### Text Extraction

#### `POST /api/v1/extract/text`

Extract text entities from a DXF file.

**Request:**

- Content-Type: `multipart/form-data`
- Body: DXF file

**Response:**

```json
{
  "text_entities": [
    {
      "text": "Living Room",
      "entity_type": "TEXT",
      "layer": "A-TEXT",
      "position": {"x": 100.0, "y": 200.0},
      "height": 2.5,
      "rotation": 0.0,
      "space": "layout:Model",
      "handle": "ABC123"
    }
  ],
  "room_labels": [
    {
      "label": "Living",
      "text": "Living Room",
      "category": "room",
      "x": 100.0,
      "y": 200.0,
      "layer": "A-TEXT"
    }
  ],
  "floor_titles": [...],
  "road_labels": [...],
  "built_up_areas": [...],
  "plot_dimensions": [...]
}
```

---

### Geometry Analysis

#### `POST /api/v1/analyze/geometry`

Extract wall geometry from a DXF file.

**Request:**

- Content-Type: `multipart/form-data`
- Body: DXF file

**Response:**

```json
{
  "lines": [
    {
      "id": "layout:ABC123",
      "start": {"x": 0.0, "y": 0.0},
      "end": {"x": 100.0, "y": 0.0},
      "length": 100.0,
      "angle": 0.0,
      "layer": "A-WALL",
      "space": "layout:Model"
    }
  ],
  "parallel_pairs": [
    {
      "id": "layout:ABC123|layout:DEF456",
      "line_a": {...},
      "line_b": {...},
      "angle_difference": 0.5,
      "perpendicular_distance": 0.75
    }
  ],
  "wall_segments": [
    {
      "id": "wall-segment-1",
      "wall_type": "9 inch brick wall",
      "width": 0.75,
      "measured_width": 0.76,
      "line_ids": ["layout:ABC123", "layout:DEF456"]
    }
  ],
  "logical_walls": [
    {
      "id": "logical-wall-1",
      "wall_type": "9 inch brick wall",
      "width": 0.75,
      "segment_ids": ["wall-segment-1", "wall-segment-2"],
      "line_ids": ["layout:ABC123", "layout:DEF456", "layout:GHI789"],
      "source_lines": [...]
    }
  ]
}
```

---

### Room Detection

#### `POST /api/v1/analyze/rooms`

Detect room boundaries from a DXF file.

**Request:**

- Content-Type: `multipart/form-data`
- Body: DXF file
- Query Parameters:
  - `include_blocks` (bool, optional): Include block entities (default: true)

**Response:**

```json
{
  "rooms": [
    {
      "room_name": "Living",
      "polygon": [[0, 0], [100, 0], [100, 100], [0, 100], [0, 0]],
      "area": 10000.0,
      "perimeter": 400.0,
      "centroid": {"x": 50.0, "y": 50.0},
      "boundary_wall_ids": ["logical-wall-1", "logical-wall-2"]
    }
  ]
}
```

---

### Building Model

#### `POST /api/v1/analyze/full`

Run the complete analysis pipeline.

**Request:**

- Content-Type: `multipart/form-data`
- Body: DXF file

**Response:**

```json
{
  "metadata": {...},
  "plot": {...},
  "walls": [...],
  "doors": [...],
  "windows": [...],
  "rooms": [...],
  "adjacency_graph": [...],
  "connectivity_graph": [...],
  "facing_information": {...},
  "zoning": [...],
  "confidence": [...],
  "statistics": {
    "room_count": 5,
    "wall_count": 12,
    "door_count": 4,
    "window_count": 6,
    "total_room_area": 1250.5,
    "average_room_area": 250.1,
    "total_room_perimeter": 250.0,
    "adjacency_edge_count": 8,
    "connectivity_edge_count": 4,
    "front_room_count": 2,
    "average_confidence": 0.87,
    "zones": {"Public": 2, "Private": 2, "Service": 1}
  }
}
```

---

### Analysis Status

#### `GET /api/v1/analysis/{analysis_id}`)

Check the status of a long-running analysis.

**Response:**

```json
{
  "id": "analysis_abc123",
  "status": "processing",
  "progress": 65,
  "stage": "room_detection",
  "started_at": "2026-06-26T12:00:00Z",
  "estimated_completion": "2026-06-26T12:00:30Z"
}
```

**Status Values:**

| Status | Description |
|--------|-------------|
| `queued` | Waiting to be processed |
| `processing` | Currently being analyzed |
| `completed` | Analysis finished successfully |
| `failed` | Analysis encountered an error |

---

### Analysis Results

#### `GET /api/v1/analysis/{analysis_id}/results`

Retrieve the results of a completed analysis.

**Response:** Same as `POST /api/v1/analyze/full` response.

---

### Export

#### `GET /api/v1/analysis/{analysis_id}/export`

Export analysis results in various formats.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Export format: `json`, `geojson`, `ifc` (planned) |

**Response:** File download in the requested format.

---

## Backend Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Server | Uvicorn |
| Validation | Pydantic |
| JSON | orjson (fast serialization) |
| DXF Parsing | ezdxf |
| Geometry | Shapely, NumPy |
| Logging | loguru |
| Database | PostgreSQL (planned) |
| Cache | Redis (planned) |
| Task Queue | Celery/ARQ (planned) |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flutter App                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Routers   │  │  Middleware │  │  Background Tasks       │ │
│  │  /api/v1/*  │  │  CORS/Log   │  │  (Celery/ARQ)           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Pipeline Orchestrator                      │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ Normalizer    │   │ Geometry Engine │   │ CAD Intelligence│
└───────────────┘   └─────────────────┘   └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │   Room Graph    │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Building Model  │
                    └─────────────────┘
                              │
        ┌─────────┬───────────┼───────────┬─────────┐
        ▼         ▼           ▼           ▼         ▼
   ┌─────────┐┌────────┐┌────────┐┌────────┐┌─────────┐
   │Adjacency││Connect ││Facing  ││Zoning  ││Confid.  │
   └─────────┘└────────┘└────────┘└────────┘└─────────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `backend/app.py` | FastAPI application, routing, middleware |
| `backend/config.py` | Configuration management |
| `backend/cad_intelligence/` | Text extraction and rule-based detection |
| `backend/dwg_parser/` | DWG file parsing utilities |
| `geometry_engine/` | Wall detection and geometry extraction |
| `normalizer/` | Label and dimension normalization |
| `room_graph/` | Room boundary polygon construction |
| `building_model/` | Result aggregation and statistics |
| `adjacency.py` | Room adjacency analysis |
| `connectivity.py` | Door-based connectivity |
| `facing.py` | Road-facing detection |
| `zoning.py` | Room zoning classification |
| `confidence.py` | Confidence scoring |

---

## Future API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login and get JWT token |
| `/api/v1/auth/refresh` | POST | Refresh JWT token |
| `/api/v1/auth/api-keys` | POST | Generate API key |

### Project Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/projects` | GET | List user projects |
| `/api/v1/projects` | POST | Create new project |
| `/api/v1/projects/{id}` | GET | Get project details |
| `/api/v1/projects/{id}` | PUT | Update project |
| `/api/v1/projects/{id}` | DELETE | Delete project |

### File Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/files` | GET | List project files |
| `/api/v1/files` | POST | Upload DXF file |
| `/api/v1/files/{id}` | GET | Get file metadata |
| `/api/v1/files/{id}` | DELETE | Delete file |

### Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analysis` | GET | List analyses |
| `/api/v1/analysis/{id}` | GET | Get analysis status/results |
| `/api/v1/analysis/{id}/export` | GET | Export results |
| `/api/v1/analysis/{id}/compare` | POST | Compare two analyses |

### 3D and BIM

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analysis/{id}/3d` | GET | Get 3D model data |
| `/api/v1/analysis/{id}/ifc` | GET | Export to IFC format |
| `/api/v1/analysis/{id}/bim` | GET | Get BIM metadata |

### AI Features

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ai/suggestions` | POST | Get design suggestions |
| `/api/v1/ai/chat` | POST | Chat with AI about plan |
| `/api/v1/ai/compliance` | POST | Check code compliance |
| `/api/v1/ai/cost` | POST | Estimate construction cost |
| `/api/v1/ai/boq` | POST | Generate Bill of Quantities |

### Webhooks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/webhooks` | POST | Register webhook |
| `/api/v1/webhooks` | GET | List webhooks |
| `/api/v1/webhooks/{id}` | DELETE | Delete webhook |

---

## Rate Limiting

> **Note:** Not yet implemented. Planned for v0.2.0.

| Tier | Requests/min | Concurrent |
|------|-------------|------------|
| Free | 10 | 1 |
| Pro | 100 | 10 |
| Enterprise | 1000 | Unlimited |

---

## Error Format

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid DXF file format",
    "details": [
      {
        "field": "file",
        "message": "File must be a valid DXF file"
      }
    ],
    "timestamp": "2026-06-26T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## SDK Examples

### Python

```python
import requests

# Upload and analyze a DXF file
with open("floor_plan.dxf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        files={"file": ("floor_plan.dxf", f, "application/dxf")}
    )

results = response.json()
print(f"Found {results['statistics']['room_count']} rooms")
```

### JavaScript/TypeScript

```typescript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("http://localhost:8000/api/v1/analyze", {
  method: "POST",
  body: formData,
});

const results = await response.json();
console.log(`Found ${results.statistics.room_count} rooms`);
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@floor_plan.dxf" \
  -H "Accept: application/json"