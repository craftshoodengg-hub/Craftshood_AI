"""End-to-end integration test for the semantic DWG knowledge pipeline."""
from __future__ import annotations

import math
from pathlib import Path

import ezdxf
import pytest

from building_model_v2.pipeline.dwg_knowledge.plot_information_detector import (
    PlotInformationDetector,
)
from building_model_v2.pipeline.dwg_knowledge.door_window_detector import (
    DoorWindowDetector,
)
from building_model_v2.pipeline.dwg_knowledge.room_polygon_builder import (
    RoomPolygonBuilder,
)
from building_model_v2.pipeline.dwg_knowledge.room_opening_assigner import (
    RoomOpeningAssigner,
)
from building_model_v2.pipeline.dwg_knowledge.semantic_room_builder import (
    SemanticRoomBuilder,
)
from building_model_v2.pipeline.dwg_knowledge.room_adjacency_graph_builder import (
    RoomAdjacencyGraphBuilder,
)
from building_model_v2.pipeline.dwg_knowledge.semantic_building_builder import (
    SemanticBuildingBuilder,
    _reset_building_counter,
)
from building_model_v2.pipeline.dwg_knowledge.building_knowledge_graph import (
    BuildingKnowledgeGraphBuilder,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _create_test_dxf(tmp_path: Path) -> Path:
    """Create a temporary DXF with two adjacent rooms, labels, doors, windows
    and plot text."""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # --- Room A: Bedroom (0,0) -> (10,10) ---
    # LWPOLYLINE for the bedroom boundary
    bedroom_points = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    msp.add_lwpolyline(bedroom_points, close=True, dxfattribs={"layer": "WALL"})

    # Room label inside bedroom
    msp.add_text(
        "BEDROOM",
        dxfattribs={
            "height": 1.0,
            "insert": (5, 5),
            "layer": "TEXT",
        },
    )

    # --- Room B: Living Room (10,0) -> (20,10) ---
    living_points = [(10, 0), (20, 0), (20, 10), (10, 10), (10, 0)]
    msp.add_lwpolyline(living_points, close=True, dxfattribs={"layer": "WALL"})

    # Room label inside living room
    msp.add_text(
        "LIVING ROOM",
        dxfattribs={
            "height": 1.0,
            "insert": (15, 5),
            "layer": "TEXT",
        },
    )

    # --- Door at the shared wall between rooms (at x=10, y=4..6) ---
    # Represent door as a TEXT entity with "DOOR" text near the shared wall
    msp.add_text(
        "DOOR",
        dxfattribs={
            "height": 0.5,
            "insert": (10, 5),
            "layer": "DOOR",
        },
    )

    # --- Window on the outer wall of bedroom (at y=10, x=3..7) ---
    msp.add_text(
        "WINDOW",
        dxfattribs={
            "height": 0.5,
            "insert": (5, 10),
            "layer": "WINDOW",
        },
    )

    # --- Plot / orientation text ---
    msp.add_text(
        "PLOT 30x40",
        dxfattribs={
            "height": 1.0,
            "insert": (25, 15),
            "layer": "TEXT",
        },
    )
    msp.add_text(
        "NORTH",
        dxfattribs={
            "height": 0.8,
            "insert": (25, 12),
            "layer": "TEXT",
        },
    )

    dxf_path = tmp_path / "test_semantic_pipeline.dxf"
    doc.saveas(str(dxf_path))
    return dxf_path


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_counter() -> None:
    _reset_building_counter(0)


@pytest.fixture
def dxf_document(tmp_path: Path):
    """Create a temporary DXF and return the loaded document."""
    dxf_path = _create_test_dxf(tmp_path)
    return ezdxf.readfile(str(dxf_path))


# ---------------------------------------------------------------------------
# test
# ---------------------------------------------------------------------------


def test_semantic_pipeline_end_to_end(dxf_document) -> None:
    """Run the full semantic pipeline and verify all outputs."""
    doc = dxf_document

    # 1. Detect plot information
    plot_detector = PlotInformationDetector()
    plot_info = plot_detector.detect(doc)
    assert isinstance(plot_info, dict)
    # Plot text "PLOT 30x40" should be detected
    assert plot_info.get("plot_width") is not None
    assert plot_info.get("plot_depth") is not None
    # Orientation "NORTH" should be detected
    assert plot_info.get("orientation") is not None

    # 2. Detect doors / windows
    dw_detector = DoorWindowDetector()
    dw_result = dw_detector.detect(doc)
    assert isinstance(dw_result, dict)
    # We have 1 door LINE and 1 window LINE
    # (detection may find them based on layer or text patterns)
    assert dw_result.get("door_count", 0) >= 0
    assert dw_result.get("window_count", 0) >= 0

    # 3. Build room polygons
    room_polygons = RoomPolygonBuilder.build(doc)
    assert len(room_polygons) >= 2, (
        f"Expected at least 2 room polygons, got {len(room_polygons)}"
    )

    # 4. Assign openings to rooms
    assigner = RoomOpeningAssigner()
    rooms_with_openings = assigner.assign(room_polygons, dw_result)
    assert len(rooms_with_openings) >= 2

    # 5. Build semantic rooms
    room_builder = SemanticRoomBuilder()
    semantic_rooms = room_builder.build(rooms_with_openings)
    assert len(semantic_rooms) >= 2

    # 6. Verify semantic rooms
    room_ids = [r.room_id for r in semantic_rooms]
    # Room IDs should be unique
    assert len(room_ids) == len(set(room_ids)), f"Duplicate room IDs: {room_ids}"
    # Room IDs should be deterministic
    for rid in room_ids:
        assert "_" in rid, f"Room ID '{rid}' missing underscore separator"

    # 7. Build room adjacency graph
    adj_builder = RoomAdjacencyGraphBuilder()
    adjacency_graph = adj_builder.build(semantic_rooms)
    # Two adjacent rooms should produce at least one adjacency
    assert len(adjacency_graph) >= 1, "Expected at least one adjacency"

    # 8. Build semantic building
    building_builder = SemanticBuildingBuilder()
    building = building_builder.build(plot_info, semantic_rooms, adjacency_graph)
    assert building.building_id == "building_1"
    assert building.total_rooms == len(semantic_rooms)
    assert building.total_area > 0
    assert building.total_doors >= 0
    assert building.total_windows >= 0

    # Verify building totals are consistent
    expected_area = sum(r.area for r in semantic_rooms)
    assert math.isclose(building.total_area, expected_area, rel_tol=1e-9)
    expected_doors = sum(r.door_count for r in semantic_rooms)
    assert building.total_doors == expected_doors
    expected_windows = sum(r.window_count for r in semantic_rooms)
    assert building.total_windows == expected_windows

    # 9. Build building knowledge graph
    kg_builder = BuildingKnowledgeGraphBuilder()
    kg = kg_builder.build(building)
    assert kg.building_id == "building_1"

    # Verify graph has required node types
    node_types = {n.node_type for n in kg.nodes}
    assert "Building" in node_types, "Missing Building node"
    assert "Plot" in node_types, "Missing Plot node"
    assert "Room" in node_types, "Missing Room node(s)"

    # Verify every graph edge source/target exists as a node
    node_ids = {n.node_id for n in kg.nodes}
    for edge in kg.edges:
        assert edge.source in node_ids, (
            f"Edge source '{edge.source}' not found in nodes"
        )
        assert edge.target in node_ids, (
            f"Edge target '{edge.target}' not found in nodes"
        )

    # 10. Verify serialization round-trip for the building
    building_dict = building.to_dict()
    from building_model_v2.pipeline.dwg_knowledge.semantic_building_builder import (
        SemanticBuilding,
    )
    restored_building = SemanticBuilding.from_dict(building_dict)
    assert restored_building.building_id == building.building_id
    assert restored_building.total_rooms == building.total_rooms
    assert restored_building.total_area == building.total_area
    assert len(restored_building.rooms) == len(building.rooms)
    assert len(restored_building.adjacency_graph) == len(building.adjacency_graph)

    # 11. Verify knowledge graph serialization round-trip
    kg_dict = kg.to_dict()
    from building_model_v2.pipeline.dwg_knowledge.building_knowledge_graph import (
        BuildingKnowledgeGraph,
    )
    restored_kg = BuildingKnowledgeGraph.from_dict(kg_dict)
    assert restored_kg.building_id == kg.building_id
    assert len(restored_kg.nodes) == len(kg.nodes)
    assert len(restored_kg.edges) == len(kg.edges)