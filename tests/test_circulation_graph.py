"""Tests for circulation graph types."""
from __future__ import annotations

import pytest

from building_model_v2.architect.circulation_edge import CirculationEdge
from building_model_v2.architect.circulation_graph import CirculationGraph
from building_model_v2.architect.circulation_node import CirculationNode


class TestCirculationNode:
    """Tests for CirculationNode dataclass."""

    def test_create_valid_node(self) -> None:
        """Test creating a valid circulation node."""
        node = CirculationNode(
            id="corridor_1",
            name="Main Corridor",
            space_id="room_1",
            width=1.5,
            is_entry_exit=False,
        )
        assert node.id == "corridor_1"
        assert node.name == "Main Corridor"
        assert node.space_id == "room_1"
        assert node.width == 1.5
        assert not node.is_entry_exit

    def test_create_entry_exit_node(self) -> None:
        """Test creating an entry/exit node."""
        node = CirculationNode(
            id="entrance_1",
            name="Main Entrance",
            is_entry_exit=True,
        )
        assert node.is_entry_exit

    def test_default_width(self) -> None:
        """Test default width value."""
        node = CirculationNode(id="n1", name="Node 1")
        assert node.width == 1.2

    def test_empty_id_raises_error(self) -> None:
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            CirculationNode(id="", name="Node 1")

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            CirculationNode(id="n1", name="")

    def test_non_positive_width_raises_error(self) -> None:
        """Test that non-positive width raises ValueError."""
        with pytest.raises(ValueError, match="width must be positive"):
            CirculationNode(id="n1", name="Node 1", width=0)

    def test_negative_width_raises_error(self) -> None:
        """Test that negative width raises ValueError."""
        with pytest.raises(ValueError, match="width must be positive"):
            CirculationNode(id="n1", name="Node 1", width=-1.0)

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        node = CirculationNode(
            id="corridor_1",
            name="Main Corridor",
            space_id="room_1",
            width=1.5,
            is_entry_exit=True,
            metadata={"floor": "ground"},
        )
        data = node.to_dict()
        assert data["id"] == "corridor_1"
        assert data["name"] == "Main Corridor"
        assert data["space_id"] == "room_1"
        assert data["width"] == 1.5
        assert data["is_entry_exit"] is True
        assert data["metadata"] == {"floor": "ground"}

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "id": "corridor_1",
            "name": "Main Corridor",
            "space_id": "room_1",
            "width": 1.5,
            "is_entry_exit": True,
            "metadata": {"floor": "ground"},
        }
        node = CirculationNode.from_dict(data)
        assert node.id == "corridor_1"
        assert node.name == "Main Corridor"
        assert node.space_id == "room_1"
        assert node.width == 1.5
        assert node.is_entry_exit
        assert node.metadata == {"floor": "ground"}

    def test_from_dict_with_defaults(self) -> None:
        """Test deserialization with default values."""
        data = {"id": "n1", "name": "Node 1"}
        node = CirculationNode.from_dict(data)
        assert node.id == "n1"
        assert node.name == "Node 1"
        assert node.space_id is None
        assert node.width == 1.2
        assert not node.is_entry_exit
        assert node.metadata == {}

    def test_from_dict_missing_required_raises_error(self) -> None:
        """Test that missing required fields raise KeyError."""
        with pytest.raises(KeyError):
            CirculationNode.from_dict({"name": "Node 1"})

    def test_immutable(self) -> None:
        """Test that the dataclass is frozen."""
        node = CirculationNode(id="n1", name="Node 1")
        with pytest.raises(AttributeError):
            node.name = "Changed"  # type: ignore[misc]

    def test_slots(self) -> None:
        """Test that slots is enabled."""
        node = CirculationNode(id="n1", name="Node 1")
        with pytest.raises((AttributeError, TypeError)):
            node.new_attr = "test"  # type: ignore[attr-defined]

    def test_equality(self) -> None:
        """Test equality comparison."""
        node1 = CirculationNode(id="n1", name="Node 1")
        node2 = CirculationNode(id="n1", name="Node 1")
        node3 = CirculationNode(id="n2", name="Node 2")
        assert node1 == node2
        assert node1 != node3

    def test_hashable(self) -> None:
        """Test that node is hashable (frozen dataclass)."""
        node = CirculationNode(id="n1", name="Node 1")
        s = {node}
        assert node in s

    def test_repr(self) -> None:
        """Test string representation."""
        node = CirculationNode(id="n1", name="Node 1")
        assert "CirculationNode" in repr(node)
        assert "n1" in repr(node)


class TestCirculationEdge:
    """Tests for CirculationEdge dataclass."""

    def test_create_valid_edge(self) -> None:
        """Test creating a valid circulation edge."""
        edge = CirculationEdge(
            source_id="n1",
            target_id="n2",
            length=5.0,
            width=1.5,
            bidirectional=True,
            is_accessible=True,
        )
        assert edge.source_id == "n1"
        assert edge.target_id == "n2"
        assert edge.length == 5.0
        assert edge.width == 1.5
        assert edge.bidirectional
        assert edge.is_accessible

    def test_default_values(self) -> None:
        """Test default values."""
        edge = CirculationEdge(source_id="n1", target_id="n2", length=3.0)
        assert edge.width == 1.2
        assert edge.bidirectional
        assert edge.is_accessible

    def test_empty_source_id_raises_error(self) -> None:
        """Test that empty source_id raises ValueError."""
        with pytest.raises(ValueError, match="source_id cannot be empty"):
            CirculationEdge(source_id="", target_id="n2", length=3.0)

    def test_empty_target_id_raises_error(self) -> None:
        """Test that empty target_id raises ValueError."""
        with pytest.raises(ValueError, match="target_id cannot be empty"):
            CirculationEdge(source_id="n1", target_id="", length=3.0)

    def test_self_loop_raises_error(self) -> None:
        """Test that self-loop raises ValueError."""
        with pytest.raises(ValueError, match="source_id and target_id must be different"):
            CirculationEdge(source_id="n1", target_id="n1", length=3.0)

    def test_non_positive_length_raises_error(self) -> None:
        """Test that non-positive length raises ValueError."""
        with pytest.raises(ValueError, match="length must be positive"):
            CirculationEdge(source_id="n1", target_id="n2", length=0)

    def test_negative_length_raises_error(self) -> None:
        """Test that negative length raises ValueError."""
        with pytest.raises(ValueError, match="length must be positive"):
            CirculationEdge(source_id="n1", target_id="n2", length=-1.0)

    def test_non_positive_width_raises_error(self) -> None:
        """Test that non-positive width raises ValueError."""
        with pytest.raises(ValueError, match="width must be positive"):
            CirculationEdge(source_id="n1", target_id="n2", length=3.0, width=0)

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        edge = CirculationEdge(
            source_id="n1",
            target_id="n2",
            length=5.0,
            width=1.5,
            bidirectional=False,
            is_accessible=True,
            metadata={"type": "corridor"},
        )
        data = edge.to_dict()
        assert data["source_id"] == "n1"
        assert data["target_id"] == "n2"
        assert data["length"] == 5.0
        assert data["width"] == 1.5
        assert data["bidirectional"] is False
        assert data["is_accessible"] is True
        assert data["metadata"] == {"type": "corridor"}

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "source_id": "n1",
            "target_id": "n2",
            "length": 5.0,
            "width": 1.5,
            "bidirectional": False,
            "is_accessible": True,
            "metadata": {"type": "corridor"},
        }
        edge = CirculationEdge.from_dict(data)
        assert edge.source_id == "n1"
        assert edge.target_id == "n2"
        assert edge.length == 5.0
        assert edge.width == 1.5
        assert not edge.bidirectional
        assert edge.is_accessible
        assert edge.metadata == {"type": "corridor"}

    def test_from_dict_with_defaults(self) -> None:
        """Test deserialization with default values."""
        data = {"source_id": "n1", "target_id": "n2", "length": 3.0}
        edge = CirculationEdge.from_dict(data)
        assert edge.width == 1.2
        assert edge.bidirectional
        assert edge.is_accessible
        assert edge.metadata == {}

    def test_from_dict_missing_required_raises_error(self) -> None:
        """Test that missing required fields raise KeyError."""
        with pytest.raises(KeyError):
            CirculationEdge.from_dict({"source_id": "n1"})

    def test_immutable(self) -> None:
        """Test that the dataclass is frozen."""
        edge = CirculationEdge(source_id="n1", target_id="n2", length=3.0)
        with pytest.raises(AttributeError):
            edge.length = 5.0  # type: ignore[misc]

    def test_equality(self) -> None:
        """Test equality comparison."""
        e1 = CirculationEdge(source_id="n1", target_id="n2", length=3.0)
        e2 = CirculationEdge(source_id="n1", target_id="n2", length=3.0)
        e3 = CirculationEdge(source_id="n1", target_id="n3", length=3.0)
        assert e1 == e2
        assert e1 != e3

    def test_hashable(self) -> None:
        """Test that edge is hashable (frozen dataclass)."""
        edge = CirculationEdge(source_id="n1", target_id="n2", length=3.0)
        s = {edge}
        assert edge in s


class TestCirculationGraph:
    """Tests for CirculationGraph dataclass."""

    @pytest.fixture
    def sample_nodes(self) -> tuple[CirculationNode, ...]:
        """Create sample nodes for testing."""
        return (
            CirculationNode(id="n1", name="Entrance", is_entry_exit=True),
            CirculationNode(id="n2", name="Corridor A", width=1.5),
            CirculationNode(id="n3", name="Corridor B", width=1.5),
            CirculationNode(id="n4", name="Exit", is_entry_exit=True),
        )

    @pytest.fixture
    def sample_edges(self) -> tuple[CirculationEdge, ...]:
        """Create sample edges for testing."""
        return (
            CirculationEdge(source_id="n1", target_id="n2", length=3.0),
            CirculationEdge(source_id="n2", target_id="n3", length=5.0),
            CirculationEdge(source_id="n3", target_id="n4", length=3.0),
        )

    def test_create_empty_graph(self) -> None:
        """Test creating an empty graph."""
        graph = CirculationGraph()
        assert graph.node_count == 0
        assert graph.edge_count == 0
        assert graph.node_ids == ()

    def test_create_valid_graph(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test creating a valid graph."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        assert graph.node_count == 4
        assert graph.edge_count == 3
        assert graph.node_ids == ("n1", "n2", "n3", "n4")

    def test_duplicate_node_ids_raises_error(self) -> None:
        """Test that duplicate node ids raise ValueError."""
        nodes = (
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n1", name="Node 1 Duplicate"),
        )
        with pytest.raises(ValueError, match="node ids must be unique"):
            CirculationGraph(nodes=nodes)

    def test_edge_source_not_found_raises_error(
        self, sample_nodes: tuple[CirculationNode, ...],
    ) -> None:
        """Test that edge referencing non-existent source raises ValueError."""
        edges = (
            CirculationEdge(source_id="n5", target_id="n1", length=3.0),
        )
        with pytest.raises(ValueError, match="edge source 'n5' does not exist"):
            CirculationGraph(nodes=sample_nodes, edges=edges)

    def test_edge_target_not_found_raises_error(
        self, sample_nodes: tuple[CirculationNode, ...],
    ) -> None:
        """Test that edge referencing non-existent target raises ValueError."""
        edges = (
            CirculationEdge(source_id="n1", target_id="n5", length=3.0),
        )
        with pytest.raises(ValueError, match="edge target 'n5' does not exist"):
            CirculationGraph(nodes=sample_nodes, edges=edges)

    def test_get_node(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test getting a node by ID."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        node = graph.get_node("n1")
        assert node is not None
        assert node.id == "n1"
        assert node.name == "Entrance"

    def test_get_node_not_found(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test getting a non-existent node returns None."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        assert graph.get_node("nonexistent") is None

    def test_neighbors(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test getting neighbors of a node."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        neighbors = graph.neighbors("n2")
        assert len(neighbors) == 2
        neighbor_ids = {n.id for n in neighbors}
        assert neighbor_ids == {"n1", "n3"}

    def test_neighbors_no_bidirectional(self) -> None:
        """Test neighbors with non-bidirectional edges."""
        nodes = (
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n2", name="Node 2"),
        )
        edges = (
            CirculationEdge(source_id="n1", target_id="n2", length=3.0, bidirectional=False),
        )
        graph = CirculationGraph(nodes=nodes, edges=edges)
        # n1 should see n2 as neighbor
        assert len(graph.neighbors("n1")) == 1
        # n2 should NOT see n1 as neighbor (non-bidirectional)
        assert len(graph.neighbors("n2")) == 0

    def test_neighbors_not_found(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test getting neighbors of a non-existent node."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        assert graph.neighbors("nonexistent") == ()

    def test_total_path_length(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test total path length calculation."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        assert graph.total_path_length() == 11.0  # 3.0 + 5.0 + 3.0

    def test_total_path_length_empty(self) -> None:
        """Test total path length of empty graph."""
        graph = CirculationGraph()
        assert graph.total_path_length() == 0.0

    def test_entry_exit_nodes(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test getting entry/exit nodes."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        entries = graph.entry_exit_nodes()
        assert len(entries) == 2
        entry_ids = {n.id for n in entries}
        assert entry_ids == {"n1", "n4"}

    def test_entry_exit_nodes_none(self) -> None:
        """Test entry/exit nodes when none exist."""
        nodes = (
            CirculationNode(id="n1", name="Node 1"),
            CirculationNode(id="n2", name="Node 2"),
        )
        graph = CirculationGraph(nodes=nodes)
        assert graph.entry_exit_nodes() == ()

    def test_to_dict(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test serialization to dictionary."""
        graph = CirculationGraph(
            nodes=sample_nodes,
            edges=sample_edges,
            metadata={"building": "test"},
        )
        data = graph.to_dict()
        assert len(data["nodes"]) == 4
        assert len(data["edges"]) == 3
        assert data["metadata"] == {"building": "test"}
        assert data["nodes"][0]["id"] == "n1"
        assert data["edges"][0]["source_id"] == "n1"

    def test_from_dict(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test deserialization from dictionary."""
        original = CirculationGraph(
            nodes=sample_nodes,
            edges=sample_edges,
            metadata={"building": "test"},
        )
        data = original.to_dict()
        restored = CirculationGraph.from_dict(data)
        assert restored.node_count == original.node_count
        assert restored.edge_count == original.edge_count
        assert restored.metadata == original.metadata
        assert restored.node_ids == original.node_ids
        assert restored.total_path_length() == original.total_path_length()

    def test_from_dict_empty(self) -> None:
        """Test deserialization of empty graph."""
        graph = CirculationGraph.from_dict({})
        assert graph.node_count == 0
        assert graph.edge_count == 0

    def test_immutable(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test that the dataclass is frozen."""
        graph = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        with pytest.raises(AttributeError):
            graph.nodes = ()  # type: ignore[misc]

    def test_equality(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test equality comparison."""
        g1 = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        g2 = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        g3 = CirculationGraph()
        assert g1 == g2
        assert g1 != g3

    def test_deterministic_order(
        self, sample_nodes: tuple[CirculationNode, ...],
        sample_edges: tuple[CirculationEdge, ...],
    ) -> None:
        """Test that node order is deterministic."""
        reversed_nodes = tuple(reversed(sample_nodes))
        graph1 = CirculationGraph(nodes=sample_nodes, edges=sample_edges)
        graph2 = CirculationGraph(nodes=reversed_nodes, edges=sample_edges)
        # Different node order should produce different graphs
        assert graph1 != graph2
        # But each should be deterministic
        assert graph1.node_ids == ("n1", "n2", "n3", "n4")
        assert graph2.node_ids == ("n4", "n3", "n2", "n1")