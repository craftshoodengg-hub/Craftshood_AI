"""Tests for DrawingModel, DrawingBuilder, and drawing entities - Part 1."""
from __future__ import annotations
import pytest
from building_model_v2.base import Point2D
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_wall import Wall
from building_model_v2.entities_column import Column
from building_model_v2.entities_stair import Stair
from building_model_v2.entities_opening import Door, Window
from building_model_v2.types import RoomType, WallType, ColumnType, StairType, DoorType
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.export.drawing_entities import (
    LineEntity, PolylineEntity, PolygonEntity, CircleEntity,
    ArcEntity, TextEntity, DimensionEntity, HatchEntity, GroupEntity,
    _entity_to_dict, _entity_from_dict,
)
from building_model_v2.export.drawing_model import DrawingModel, DrawingLayer, DrawingBounds
from building_model_v2.export.drawing_builder import build_drawing_model


@pytest.fixture
def sample_building():
    building = Building.create(name="Test Building", project_number="PRJ-001", floor_ids=("f1",))
    floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1", "r2"}))
    r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
    r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], room_type=RoomType.BEDROOM)
    w1 = Wall.create(start=(0,0), end=(10,0), wall_type=WallType.EXTERIOR)
    col = Column.create(location=Point2D(x=5, y=5), size=1.0, column_type=ColumnType.SQUARE)
    stair = Stair.create(start=(0,0), end=(5,0), width=3.0, stair_type=StairType.STRAIGHT)
    door = Door.create(location=Point2D(x=5, y=0), width=3.0, door_type=DoorType.SINGLE_LEAF)
    window = Window.create(location=Point2D(x=15, y=0), width=4.0)
    return BuildingModel(
        building=building, floors={"f1": floor},
        rooms={"r1": r1, "r2": r2}, walls={"w1": w1},
        columns={"c1": col}, stairs={"s1": stair},
        doors={"d1": door}, windows={"w1": window}, relationships=[],
    )


@pytest.fixture
def empty_building():
    return BuildingModel()


class TestDrawingBounds:
    def test_default(self):
        b = DrawingBounds()
        assert b.min_x == 0.0
        assert b.width == 0.0
        assert b.height == 0.0

    def test_width_height(self):
        b = DrawingBounds(min_x=0, min_y=0, max_x=20, max_y=10)
        assert b.width == 20.0
        assert b.height == 10.0

    def test_to_dict(self):
        b = DrawingBounds(1.0, 2.0, 3.0, 4.0)
        d = b.to_dict()
        assert d["min_x"] == 1.0
        assert d["max_y"] == 4.0

    def test_from_dict(self):
        b = DrawingBounds.from_dict({"min_x": 1, "min_y": 2, "max_x": 3, "max_y": 4})
        assert b.min_x == 1.0
        assert b.max_y == 4.0

    def test_round_trip(self):
        b = DrawingBounds(1.5, 2.5, 3.5, 4.5)
        b2 = DrawingBounds.from_dict(b.to_dict())
        assert b == b2


class TestDrawingLayer:
    def test_default(self):
        layer = DrawingLayer(name="A-WALL")
        assert layer.name == "A-WALL"
        assert layer.color == "#000000"
        assert layer.visible is True
        assert layer.locked is False

    def test_custom(self):
        layer = DrawingLayer(name="TEST", color="#FF0000", visible=False, locked=True)
        assert layer.color == "#FF0000"
        assert layer.visible is False
        assert layer.locked is True

    def test_round_trip(self):
        layer = DrawingLayer(name="A-WALL", color="#FF0000")
        layer2 = DrawingLayer.from_dict(layer.to_dict())
        assert layer == layer2

    def test_frozen(self):
        layer = DrawingLayer(name="TEST")
        with pytest.raises(AttributeError):
            layer.name = "OTHER"


class TestDrawingModel:
    def test_empty(self):
        dm = DrawingModel.empty()
        assert dm.layers == ()
        assert dm.entities == ()
        assert dm.metadata == {}

    def test_to_dict(self):
        dm = DrawingModel(
            layers=(DrawingLayer(name="A-WALL"),),
            entities=(LineEntity(0, 0, 10, 10),),
            bounds=DrawingBounds(0, 0, 10, 10),
            metadata={"title": "Test"},
        )
        d = dm.to_dict()
        assert len(d["layers"]) == 1
        assert len(d["entities"]) == 1
        assert d["metadata"]["title"] == "Test"

    def test_from_dict(self):
        dm = DrawingModel(
            layers=(DrawingLayer(name="A-WALL"),),
            entities=(LineEntity(0, 0, 10, 10),),
            bounds=DrawingBounds(0, 0, 10, 10),
        )
        dm2 = DrawingModel.from_dict(dm.to_dict())
        assert len(dm2.layers) == 1
        assert len(dm2.entities) == 1
        assert dm2.bounds.max_x == 10.0

    def test_frozen(self):
        dm = DrawingModel()
        with pytest.raises(AttributeError):
            dm.metadata = {"x": 1}


class TestLineEntity:
    def test_frozen(self):
        e = LineEntity(0, 0, 10, 10)
        with pytest.raises(AttributeError):
            e.x1 = 5

    def test_round_trip(self):
        e = LineEntity(1, 2, 3, 4, layer="A-WALL", color="#FF0000", stroke_width=0.5)
        e2 = LineEntity.from_dict(e.to_dict())
        assert e == e2

    def test_default_layer(self):
        e = LineEntity(0, 0, 1, 1)
        assert e.layer == "0"


class TestPolylineEntity:
    def test_round_trip(self):
        e = PolylineEntity(points=((0,0),(1,1),(2,0)), closed=True)
        e2 = PolylineEntity.from_dict(e.to_dict())
        assert e == e2
        assert e2.closed is True

    def test_empty(self):
        e = PolylineEntity()
        assert e.points == ()
        assert e.closed is False


class TestPolygonEntity:
    def test_round_trip(self):
        e = PolygonEntity(points=((0,0),(1,0),(1,1),(0,1)), fill_color="#FF0000")
        e2 = PolygonEntity.from_dict(e.to_dict())
        assert e == e2

    def test_default_opacity(self):
        e = PolygonEntity()
        assert e.fill_opacity == 1.0


class TestCircleEntity:
    def test_round_trip(self):
        e = CircleEntity(cx=5, cy=5, radius=2, layer="A-COLUMN")
        e2 = CircleEntity.from_dict(e.to_dict())
        assert e == e2


class TestArcEntity:
    def test_round_trip(self):
        e = ArcEntity(cx=0, cy=0, radius=5, start_angle=0, end_angle=90)
        e2 = ArcEntity.from_dict(e.to_dict())
        assert e == e2


class TestTextEntity:
    def test_round_trip(self):
        e = TextEntity(x=5, y=5, text="Hello", font_size=0.7, rotation=45)
        e2 = TextEntity.from_dict(e.to_dict())
        assert e == e2

    def test_default_anchor(self):
        e = TextEntity()
        assert e.anchor == "middle"


class TestDimensionEntity:
    def test_round_trip(self):
        e = DimensionEntity(x1=0, y1=0, x2=10, y2=0, label="10 ft")
        e2 = DimensionEntity.from_dict(e.to_dict())
        assert e == e2

    def test_default_layer(self):
        e = DimensionEntity()
        assert e.layer == "A-DIMS"


class TestHatchEntity:
    def test_round_trip(self):
        e = HatchEntity(points=((0,0),(1,0),(1,1),(0,1)), pattern="ANSI31")
        e2 = HatchEntity.from_dict(e.to_dict())
        assert e == e2


class TestGroupEntity:
    def test_round_trip(self):
        child = LineEntity(0, 0, 10, 10)
        e = GroupEntity(name="mygroup", entities=(child,))
        e2 = GroupEntity.from_dict(e.to_dict())
        assert e2.name == "mygroup"
        assert len(e2.entities) == 1
        assert isinstance(e2.entities[0], LineEntity)

    def test_nested_groups(self):
        inner = GroupEntity(name="inner", entities=(LineEntity(0, 0, 1, 1),))
        outer = GroupEntity(name="outer", entities=(inner, TextEntity(text="hi")))
        restored = GroupEntity.from_dict(outer.to_dict())
        assert restored.name == "outer"
        assert len(restored.entities) == 2
        assert isinstance(restored.entities[0], GroupEntity)


class TestSerialization:
    def test_all_entity_types_round_trip(self):
        entities = [
            LineEntity(0, 0, 1, 1),
            PolylineEntity(points=((0,0),(1,1))),
            PolygonEntity(points=((0,0),(1,0),(1,1),(0,1))),
            CircleEntity(cx=0, cy=0, radius=1),
            ArcEntity(cx=0, cy=0, radius=1, start_angle=0, end_angle=90),
            TextEntity(x=0, y=0, text="test"),
            DimensionEntity(x1=0, y1=0, x2=1, y2=1, label="1 ft"),
            HatchEntity(points=((0,0),(1,0),(1,1),(0,1))),
            GroupEntity(name="g", entities=(LineEntity(0,0,1,1),)),
        ]
        for entity in entities:
            d = _entity_to_dict(entity)
            restored = _entity_from_dict(d)
            assert type(restored) == type(entity)

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown entity type"):
            _entity_from_dict({"type": "unknown"})

    def test_non_entity_raises(self):
        with pytest.raises(TypeError):
            _entity_to_dict("not an entity")


class TestDrawingBuilder:
    def test_build_from_sample(self, sample_building):
        dm = build_drawing_model(sample_building)
        assert len(dm.layers) == 9
        assert len(dm.entities) > 0
        assert dm.bounds.min_x == 0.0
        assert dm.bounds.max_x == 20.0
        assert dm.metadata["room_count"] == 2
        assert dm.metadata["building_name"] == "Test Building"

    def test_build_empty_model(self, empty_building):
        dm = build_drawing_model(empty_building)
        assert len(dm.layers) == 9
        assert dm.bounds.min_x == -10.0

    def test_deterministic(self, sample_building):
        dm1 = build_drawing_model(sample_building)
        dm2 = build_drawing_model(sample_building)
        assert dm1.to_dict() == dm2.to_dict()

    def test_no_grid_by_default(self, sample_building):
        dm = build_drawing_model(sample_building)
        grid = [e for e in dm.entities if getattr(e, "layer", "") == "A-GRID"]
        assert len(grid) == 0

    def test_with_grid(self, sample_building):
        dm = build_drawing_model(sample_building, include_grid=True)
        grid = [e for e in dm.entities if getattr(e, "layer", "") == "A-GRID"]
        assert len(grid) > 0

    def test_without_dimensions(self, sample_building):
        dm = build_drawing_model(sample_building, include_dimensions=False)
        dims = [e for e in dm.entities if isinstance(e, DimensionEntity)]
        assert len(dims) == 0

    def test_without_north_arrow(self, sample_building):
        dm = build_drawing_model(sample_building, include_north_arrow=False)
        n_texts = [e for e in dm.entities if isinstance(e, TextEntity) and e.text == "N"]
        assert len(n_texts) == 0

    def test_without_title_block(self, sample_building):
        dm = build_drawing_model(sample_building, include_title_block=False)
        title_texts = [e for e in dm.entities if isinstance(e, TextEntity) and "Project:" in e.text]
        assert len(title_texts) == 0

    def test_room_entities_present(self, sample_building):
        dm = build_drawing_model(sample_building)
        polygons = [e for e in dm.entities if isinstance(e, PolygonEntity)]
        assert len(polygons) >= 2

    def test_wall_entities_present(self, sample_building):
        dm = build_drawing_model(sample_building)
        lines = [e for e in dm.entities if isinstance(e, LineEntity) and e.layer == "A-WALL"]
        assert len(lines) > 0

    def test_column_entities_present(self, sample_building):
        dm = build_drawing_model(sample_building)
        circles = [e for e in dm.entities if isinstance(e, CircleEntity) and e.layer == "A-COLUMN"]
        assert len(circles) >= 1

    def test_door_entities_present(self, sample_building):
        dm = build_drawing_model(sample_building)
        door_circles = [e for e in dm.entities if isinstance(e, CircleEntity) and e.layer == "A-DOOR"]
        assert len(door_circles) >= 1

    def test_window_entities_present(self, sample_building):
        dm = build_drawing_model(sample_building)
        win_circles = [e for e in dm.entities if isinstance(e, CircleEntity) and e.layer == "A-WINDOW"]
        assert len(win_circles) >= 1

    def test_stair_entities_present(self, sample_building):
        dm = build_drawing_model(sample_building)
        stairs = [e for e in dm.entities if isinstance(e, PolylineEntity) and e.layer == "A-STAIR"]
        assert len(stairs) >= 1

    def test_label_entities_present(self, sample_building):
        dm = build_drawing_model(sample_building)
        labels = [e for e in dm.entities if isinstance(e, TextEntity) and e.layer == "A-TEXT"]
        assert len(labels) >= 2

    def test_metadata_populated(self, sample_building):
        dm = build_drawing_model(sample_building)
        assert dm.metadata["source"] == "BuildingModel"
        assert dm.metadata["room_count"] == 2
        assert dm.metadata["wall_count"] == 1
        assert dm.metadata["door_count"] == 1
        assert dm.metadata["window_count"] == 1
        assert dm.metadata["column_count"] == 1
        assert dm.metadata["stair_count"] == 1
        assert dm.metadata["building_name"] == "Test Building"
        assert dm.metadata["project_number"] == "PRJ-001"

    def test_multi_floor_building(self):
        building = Building.create(name="Multi", floor_ids=("f1", "f2"))
        f1 = Floor.create(name="F1", level=0, room_ids=frozenset({"r1"}))
        f2 = Floor.create(name="F2", level=1, room_ids=frozenset({"r2"}))
        r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
        r2 = Room.create(vertices=[(0,0),(15,0),(15,12),(0,12)], room_type=RoomType.KITCHEN)
        model = BuildingModel(
            building=building, floors={"f1": f1, "f2": f2},
            rooms={"r1": r1, "r2": r2}, walls={}, columns={}, stairs={},
            doors={}, windows={}, relationships=[],
        )
        dm = build_drawing_model(model)
        assert dm.metadata["room_count"] == 2
        assert dm.bounds.max_x == 15.0
        assert dm.bounds.max_y == 12.0

    def test_large_building(self):
        building = Building.create(name="Large", floor_ids=("f1",))
        rooms = {}
        floor_room_ids = set()
        for i in range(20):
            rid = f"r{i}"
            x = (i % 5) * 12
            y = (i // 5) * 12
            rooms[rid] = Room.create(
                vertices=[(x,y),(x+10,y),(x+10,y+10),(x,y+10)],
                room_type=RoomType.LIVING,
            )
            floor_room_ids.add(rid)
        f1 = Floor.create(name="F1", level=0, room_ids=frozenset(floor_room_ids))
        model = BuildingModel(
            building=building, floors={"f1": f1}, rooms=rooms,
            walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[],
        )
        dm = build_drawing_model(model)
        assert dm.metadata["room_count"] == 20
        assert len(dm.entities) > 50

    def test_serialization_round_trip(self, sample_building):
        dm = build_drawing_model(sample_building)
        dm2 = DrawingModel.from_dict(dm.to_dict())
        assert dm2.metadata["room_count"] == 2
        assert len(dm2.layers) == 9
