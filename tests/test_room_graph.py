"""Unit tests for Room Graph."""
from __future__ import annotations
import pytest
from building_model_v2.layout.room_graph import RoomConnection, RoomGraph
from building_model_v2.layout.adjacency_rules import ConnectionType


class TestRoomConnection:
    def test_create(self):
        c = RoomConnection("a", "b", ConnectionType.DIRECT)
        assert c.source_room_id == "a" and c.target_room_id == "b" and c.connection_type == ConnectionType.DIRECT

    def test_to_dict(self):
        c = RoomConnection("a", "b", ConnectionType.VIA_DOOR, "d1")
        d = c.to_dict()
        assert d["source_room_id"] == "a" and d["door_id"] == "d1"

    def test_from_dict(self):
        c = RoomConnection.from_dict({"source_room_id": "a", "target_room_id": "b", "connection_type": "direct"})
        assert c.source_room_id == "a" and c.connection_type == ConnectionType.DIRECT

    def test_equality(self):
        c1 = RoomConnection("a", "b", ConnectionType.DIRECT)
        c2 = RoomConnection("a", "b", ConnectionType.DIRECT)
        assert c1 == c2

    def test_hash(self):
        c1 = RoomConnection("a", "b", ConnectionType.DIRECT)
        c2 = RoomConnection("a", "b", ConnectionType.DIRECT)
        assert hash(c1) == hash(c2)


class TestRoomGraph:
    def test_add_connection(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        assert g.edge_count == 1 and g.room_count == 2

    def test_neighbors(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        g.add_connection(RoomConnection("a", "c", ConnectionType.DIRECT))
        assert g.neighbors("a") == {"b", "c"}

    def test_connected(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        assert g.connected("a", "b") and g.connected("b", "a")
        assert not g.connected("a", "c")

    def test_shortest_path_direct(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        path = g.shortest_path("a", "b")
        assert path == ["a", "b"]

    def test_shortest_path_multi(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        g.add_connection(RoomConnection("b", "c", ConnectionType.DIRECT))
        path = g.shortest_path("a", "c")
        assert path == ["a", "b", "c"]

    def test_shortest_path_same(self):
        g = RoomGraph()
        assert g.shortest_path("a", "a") == ["a"]

    def test_shortest_path_disconnected(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        g.add_connection(RoomConnection("c", "d", ConnectionType.DIRECT))
        assert g.shortest_path("a", "c") is None

    def test_degree(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        g.add_connection(RoomConnection("a", "c", ConnectionType.DIRECT))
        assert g.degree("a") == 2

    def test_empty_graph(self):
        g = RoomGraph()
        assert g.room_count == 0 and g.edge_count == 0

    def test_rooms(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        assert g.rooms == {"a", "b"}

    def test_serialization(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        d = g.to_dict()
        assert d["room_count"] == 2 and d["edge_count"] == 1
        g2 = RoomGraph.from_dict(d)
        assert g.edge_count == g2.edge_count

    def test_deterministic(self):
        g = RoomGraph()
        g.add_connection(RoomConnection("a", "b", ConnectionType.DIRECT))
        g.add_connection(RoomConnection("b", "c", ConnectionType.DIRECT))
        assert g.shortest_path("a", "c") == g.shortest_path("a", "c")

    def test_no_mutation(self):
        g = RoomGraph()
        c = RoomConnection("a", "b", ConnectionType.DIRECT)
        g.add_connection(c)
        original_rooms = g.rooms
        _ = g.neighbors("a")
        assert g.rooms == original_rooms
