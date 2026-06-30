"""Tests for circulation planner."""
from __future__ import annotations

from typing import Any

import pytest

from building_model_v2.architect.architect_result import ArchitectResult
from building_model_v2.architect.bubble_connection import BubbleConnection
from building_model_v2.architect.bubble_diagram import BubbleDiagram
from building_model_v2.architect.bubble_node import BubbleNode
from building_model_v2.architect.circulation_planner import CirculationPlanner
from building_model_v2.architect.circulation_result import CirculationResult
from building_model_v2.architect.zoning_result import ZoningResult


def _make_zoning_result() -> ZoningResult:
    """Create an empty zoning result for testing."""
    return ZoningResult(zones=(), unassigned_rooms=(), metadata={})


def _make_architect_result(
    nodes: tuple[BubbleNode, ...] = (),
    connections: tuple[BubbleConnection, ...] = (),
) -> ArchitectResult:
    """Create an architect result with given nodes and connections."""
    diagram = BubbleDiagram(nodes=nodes, connections=connections)
    return ArchitectResult(
        bubble_diagram=diagram,
        zoning_result=_make_zoning_result(),
    )


class TestCirculationPlannerConstruction:
    """Tests for CirculationPlanner construction."""

    def test_create_planner(self) -> None:
        """Test creating a circulation planner."""
        planner = CirculationPlanner()
        assert planner is not None

    def test_plan_empty_diagram(self) -> None:
        """Test planning with an empty bubble diagram."""
        planner = CirculationPlanner()
        result = planner.plan(_make_architect_result())
        assert isinstance(result, CirculationResult)
        assert result.circulation_graph.node_count == 0
        assert result.circulation_graph.edge_count == 0
        assert result.total_length == 0.0
        assert result.entry_count == 0
        assert result.exit_count == 0


class TestCirculationPlannerGraphGeneration:
    """Tests for graph generation from bubble diagrams."""

    @pytest.fixture
    def sample_nodes(self) -> tuple[BubbleNode, ...]:
        """Create sample bubble nodes for testing."""
        from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel
        from building_model_v2.types import RoomType
        return (
            BubbleNode(
                id="living",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=400.0,
                privacy_level=PrivacyLevel.PUBLIC,
                preferred_floor=FloorPreference.GROUND,
            ),
            BubbleNode(
                id="kitchen",
                room_type=RoomType.KITCHEN,
                name="Kitchen",
                target_area=150.0,
                privacy_level=PrivacyLevel.SERVICE,
                preferred_floor=FloorPreference.GROUND,
            ),
            BubbleNode(
                id="bedroom",
                room_type=RoomType.BEDROOM,
                name="Master Bedroom",
                target_area=300.0,
                privacy_level=PrivacyLevel.PRIVATE,
                preferred_floor=FloorPreference.UPPER,
            ),
            BubbleNode(
                id="bathroom",
                room_type=RoomType.BATHROOM,
                name="Bathroom",
                target_area=60.0,
                privacy_level=PrivacyLevel.PRIVATE,
                preferred_floor=FloorPreference.UPPER,
            ),
        )

    @pytest.fixture
    def sample_connections(self) -> tuple[BubbleConnection, ...]:
        """Create sample connections for testing."""
        return (
            BubbleConnection(
                source_id="living",
                target_id="kitchen",
                weight=0.9,
                required=True,
                bidirectional=True,
            ),
            BubbleConnection(
                source_id="living",
                target_id="bedroom",
                weight=0.7,
                bidirectional=True,
            ),
            BubbleConnection(
                source_id="bedroom",
                target_id="bathroom",
                weight=0.8,
                bidirectional=True,
            ),
        )

    def test_plan_generates_nodes(
        self,
        sample_nodes: tuple[BubbleNode, ...],
        sample_connections: tuple[BubbleConnection, ...],
    ) -> None:
        """Test that plan produces correct number of nodes."""
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=sample_connections)
        )
        assert result.circulation_graph.node_count == 4
        assert result.circulation_graph.edge_count == 3

    def test_plan_preserves_node_ids(
        self,
        sample_nodes: tuple[BubbleNode, ...],
        sample_connections: tuple[BubbleConnection, ...],
    ) -> None:
        """Test that node IDs are preserved from bubble diagram."""
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=sample_connections)
        )
        node_ids = set(result.circulation_graph.node_ids)
        assert node_ids == {"living", "kitchen", "bedroom", "bathroom"}

    def test_plan_preserves_bidirectional(
        self,
        sample_nodes: tuple[BubbleNode, ...],
        sample_connections: tuple[BubbleConnection, ...],
    ) -> None:
        """Test that bidirectional flag is preserved."""
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=sample_connections)
        )
        for edge in result.circulation_graph.edges:
            assert edge.bidirectional

    def test_plan_creates_entry_exit_nodes(
        self,
        sample_nodes: tuple[BubbleNode, ...],
        sample_connections: tuple[BubbleConnection, ...],
    ) -> None:
        """Test that entry/exit nodes are identified."""
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=sample_connections)
        )
        # Nodes with degree < 2 are entry/exit:
        # living -> 2 (kitchen, bedroom)
        # kitchen -> 1 (living)
        # bedroom -> 2 (living, bathroom)
        # bathroom -> 1 (bedroom)
        entry_exit = result.circulation_graph.entry_exit_nodes()
        entry_exit_ids = {n.id for n in entry_exit}
        assert entry_exit_ids == {"kitchen", "bathroom"}

    def test_plan_computes_total_length(
        self,
        sample_nodes: tuple[BubbleNode, ...],
        sample_connections: tuple[BubbleConnection, ...],
    ) -> None:
        """Test that total path length is computed correctly."""
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=sample_connections)
        )
        assert result.total_length > 0
        assert result.total_length == result.circulation_graph.total_path_length()

    def test_plan_deterministic(
        self,
        sample_nodes: tuple[BubbleNode, ...],
        sample_connections: tuple[BubbleConnection, ...],
    ) -> None:
        """Test that planning is deterministic."""
        planner = CirculationPlanner()
        result1 = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=sample_connections)
        )
        result2 = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=sample_connections)
        )
        assert result1.total_length == result2.total_length
        assert result1.entry_count == result2.entry_count
        assert result1.exit_count == result2.exit_count
        assert result1.circulation_graph.node_ids == result2.circulation_graph.node_ids

    def test_plan_edge_weights_affect_length(
        self,
        sample_nodes: tuple[BubbleNode, ...],
    ) -> None:
        """Test that connection weights affect edge lengths."""
        # Strong connection (weight 1.0) = short edge
        strong_conn = (
            BubbleConnection(
                source_id="living", target_id="kitchen", weight=1.0,
            ),
        )
        # Weak connection (weight 0.0) = long edge
        weak_conn = (
            BubbleConnection(
                source_id="living", target_id="kitchen", weight=0.0,
            ),
        )

        planner = CirculationPlanner()
        strong_result = planner.plan(
            _make_architect_result(nodes=sample_nodes[:2], connections=strong_conn)
        )
        weak_result = planner.plan(
            _make_architect_result(nodes=sample_nodes[:2], connections=weak_conn)
        )
        # Stronger connection = shorter length
        assert strong_result.total_length < weak_result.total_length

    def test_plan_duplicate_connections_deduplicated(
        self,
        sample_nodes: tuple[BubbleNode, ...],
    ) -> None:
        """Test that duplicate connections are deduplicated."""
        connections = (
            BubbleConnection(
                source_id="living", target_id="kitchen", weight=0.9,
            ),
            BubbleConnection(
                source_id="living", target_id="kitchen", weight=0.9,
            ),
        )
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes[:2], connections=connections)
        )
        assert result.circulation_graph.edge_count == 1

    def test_plan_reverse_connections_deduplicated(
        self,
        sample_nodes: tuple[BubbleNode, ...],
    ) -> None:
        """Test that reverse connections are deduplicated."""
        connections = (
            BubbleConnection(
                source_id="living", target_id="kitchen", weight=0.9,
            ),
            BubbleConnection(
                source_id="kitchen", target_id="living", weight=0.9,
            ),
        )
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes[:2], connections=connections)
        )
        assert result.circulation_graph.edge_count == 1

    def test_plan_isolated_node_is_entry_exit(
        self,
        sample_nodes: tuple[BubbleNode, ...],
    ) -> None:
        """Test that an isolated node (no connections) is entry/exit."""
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes[:1])
        )
        assert result.circulation_graph.edge_count == 0
        assert result.entry_count == 1
        entry_exit = result.circulation_graph.entry_exit_nodes()
        assert entry_exit[0].id == "living"

    def test_plan_line_topology(
        self,
        sample_nodes: tuple[BubbleNode, ...],
    ) -> None:
        """Test line topology: A-B-C-D has two ends as entry/exit."""
        connections = (
            BubbleConnection(source_id="living", target_id="kitchen", weight=0.5),
            BubbleConnection(source_id="kitchen", target_id="bedroom", weight=0.5),
            BubbleConnection(source_id="bedroom", target_id="bathroom", weight=0.5),
        )
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes, connections=connections)
        )
        # Living and bathroom are ends (degree 1)
        # Kitchen and bedroom are middle (degree 2)
        entry_exit_ids = {n.id for n in result.circulation_graph.entry_exit_nodes()}
        assert entry_exit_ids == {"living", "bathroom"}

    def test_plan_single_connection(
        self,
        sample_nodes: tuple[BubbleNode, ...],
    ) -> None:
        """Test that a single connection creates exactly one edge."""
        connections = (
            BubbleConnection(source_id="living", target_id="kitchen", weight=0.5),
        )
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=sample_nodes[:2], connections=connections)
        )
        assert result.circulation_graph.edge_count == 1
        edge = result.circulation_graph.edges[0]
        assert edge.source_id == "living"
        assert edge.target_id == "kitchen"


class TestCirculationPlannerSerialization:
    """Tests for serialization of circulation results."""

    @pytest.fixture
    def planner_result(self) -> tuple[CirculationPlanner, ArchitectResult]:
        """Create a planner and a result for serialization tests."""
        from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel
        from building_model_v2.types import RoomType
        nodes = (
            BubbleNode(
                id="living",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=400.0,
                privacy_level=PrivacyLevel.PUBLIC,
                preferred_floor=FloorPreference.GROUND,
            ),
            BubbleNode(
                id="kitchen",
                room_type=RoomType.KITCHEN,
                name="Kitchen",
                target_area=150.0,
                privacy_level=PrivacyLevel.SERVICE,
                preferred_floor=FloorPreference.GROUND,
            ),
        )
        connections = (
            BubbleConnection(
                source_id="living", target_id="kitchen", weight=0.8,
            ),
        )
        architect_result = _make_architect_result(
            nodes=nodes, connections=connections
        )
        planner = CirculationPlanner()
        return planner, architect_result

    def test_serialization_round_trip(
        self, planner_result: tuple[CirculationPlanner, ArchitectResult],
    ) -> None:
        """Test that serialization round-trips correctly."""
        planner, architect_result = planner_result
        original = planner.plan(architect_result)
        data = original.to_dict()
        restored = CirculationResult.from_dict(data)
        assert restored.total_length == original.total_length
        assert restored.entry_count == original.entry_count
        assert restored.exit_count == original.exit_count
        assert restored.circulation_graph.node_count == original.circulation_graph.node_count
        assert restored.circulation_graph.edge_count == original.circulation_graph.edge_count
        assert restored.circulation_graph.node_ids == original.circulation_graph.node_ids

    def test_serialization_empty(self) -> None:
        """Test serialization of empty result."""
        planner = CirculationPlanner()
        result = planner.plan(_make_architect_result())
        data = result.to_dict()
        restored = CirculationResult.from_dict(data)
        assert restored.total_length == 0.0
        assert restored.entry_count == 0
        assert restored.exit_count == 0
        assert restored.circulation_graph.node_count == 0
        assert restored.circulation_graph.edge_count == 0

    def test_serialization_preserves_graph(
        self, planner_result: tuple[CirculationPlanner, ArchitectResult],
    ) -> None:
        """Test that graph is preserved through serialization."""
        planner, architect_result = planner_result
        original = planner.plan(architect_result)
        data = original.to_dict()
        restored = CirculationResult.from_dict(data)
        assert restored.circulation_graph.total_path_length() == original.circulation_graph.total_path_length()
        assert len(restored.circulation_graph.entry_exit_nodes()) == len(original.circulation_graph.entry_exit_nodes())


class TestCirculationResultValidation:
    """Tests for CirculationResult validation."""

    def test_negative_total_length_raises_error(self) -> None:
        """Test that negative total_length raises ValueError."""
        from building_model_v2.architect.circulation_graph import CirculationGraph
        with pytest.raises(ValueError, match="total_length must be non-negative"):
            CirculationResult(
                circulation_graph=CirculationGraph(),
                total_length=-1.0,
            )

    def test_negative_entry_count_raises_error(self) -> None:
        """Test that negative entry_count raises ValueError."""
        from building_model_v2.architect.circulation_graph import CirculationGraph
        with pytest.raises(ValueError, match="entry_count must be non-negative"):
            CirculationResult(
                circulation_graph=CirculationGraph(),
                total_length=0.0,
                entry_count=-1,
            )

    def test_negative_exit_count_raises_error(self) -> None:
        """Test that negative exit_count raises ValueError."""
        from building_model_v2.architect.circulation_graph import CirculationGraph
        with pytest.raises(ValueError, match="exit_count must be non-negative"):
            CirculationResult(
                circulation_graph=CirculationGraph(),
                total_length=0.0,
                exit_count=-1,
            )


class TestCirculationResultProperties:
    """Tests for CirculationResult properties."""

    def test_result_metadata(self) -> None:
        """Test that result contains metadata."""
        from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel
        from building_model_v2.types import RoomType
        nodes = (
            BubbleNode(
                id="room1",
                room_type=RoomType.LIVING,
                name="Room 1",
                target_area=200.0,
                privacy_level=PrivacyLevel.PUBLIC,
                preferred_floor=FloorPreference.GROUND,
            ),
        )
        planner = CirculationPlanner()
        result = planner.plan(
            _make_architect_result(nodes=nodes)
        )
        assert result.metadata["source"] == "circulation_planner"
        assert result.metadata["bubble_room_count"] == 1