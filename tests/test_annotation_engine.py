"""Tests for annotation engine - Part 1."""
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
from building_model_v2.export.annotation_entities import (
    LinearDimension, AlignedDimension, LeaderNote,
    RoomTag, DoorTag, WindowTag, GridBubble, NorthArrow, ScaleBar,
    TitleNote, RevisionCloud, annotation_to_dict, annotation_from_dict,
)
from building_model_v2.export.annotation_settings import AnnotationSettings
from building_model_v2.export.annotation_engine import (
    generate_all_annotations, generate_room_tags, generate_door_tags,
    generate_window_tags, generate_grid_bubbles, generate_north_arrow,
    generate_scale_bar, generate_title_note,
)


@pytest.fixture
def sample_building():
    building = Building.create(name="Test Building", floor_ids=("f1",))
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


@pytest.fixture
def default_settings():
    return AnnotationSettings.default()


class TestLinearDimension:
    def test_frozen(self):
        d = LinearDimension(x1=0, y1=0, x2=10, y2=0)
        with pytest.raises(AttributeError):
            d.x1 = 5
    def test_round_trip(self):
        d = LinearDimension(x1=0, y1=0, x2=10, y2=0, label="10 ft", precision=1)
        d2 = LinearDimension.from_dict(d.to_dict())
        assert d == d2
    def test_default_layer(self):
        d = LinearDimension(x1=0, y1=0, x2=10, y2=0)
        assert d.layer == "A-DIMS"


class TestAlignedDimension:
    def test_round_trip(self):
        d = AlignedDimension(x1=0, y1=0, x2=10, y2=0, label="10 ft")
        d2 = AlignedDimension.from_dict(d.to_dict())
        assert d == d2


class TestRoomTag:
    def test_round_trip(self):
        d = RoomTag(x=5, y=5, room_name="Living", room_number="R01", area=100)
        d2 = RoomTag.from_dict(d.to_dict())
        assert d == d2


class TestDoorTag:
    def test_round_trip(self):
        d = DoorTag(x=5, y=0, door_number="D01", width=3)
        d2 = DoorTag.from_dict(d.to_dict())
        assert d == d2


class TestWindowTag:
    def test_round_trip(self):
        d = WindowTag(x=5, y=0, window_number="W01", width=4)
        d2 = WindowTag.from_dict(d.to_dict())
        assert d == d2


class TestGridBubble:
    def test_round_trip(self):
        d = GridBubble(x=0, y=0, label="A", direction="horizontal")
        d2 = GridBubble.from_dict(d.to_dict())
        assert d == d2


class TestNorthArrow:
    def test_round_trip(self):
        d = NorthArrow(x=50, y=50, size=10)
        d2 = NorthArrow.from_dict(d.to_dict())
        assert d == d2


class TestScaleBar:
    def test_round_trip(self):
        d = ScaleBar(x=0, y=0, length=10, label="10 ft")
        d2 = ScaleBar.from_dict(d.to_dict())
        assert d == d2


class TestTitleNote:
    def test_round_trip(self):
        d = TitleNote(x=50, y=50, text="Title", font_size=0.7)
        d2 = TitleNote.from_dict(d.to_dict())
        assert d == d2


class TestRevisionCloud:
    def test_round_trip(self):
        d = RevisionCloud(x=50, y=50, revision="A", date="2024-01-01")
        d2 = RevisionCloud.from_dict(d.to_dict())
        assert d == d2


class TestAnnotationSerialization:
    def test_all_types_round_trip(self):
        entities = [
            LinearDimension(x1=0, y1=0, x2=10, y2=0),
            AlignedDimension(x1=0, y1=0, x2=10, y2=0),
            LeaderNote(x=5, y=5, text="Note"),
            RoomTag(x=5, y=5, room_name="Living"),
            DoorTag(x=5, y=0, door_number="D01"),
            WindowTag(x=5, y=0, window_number="W01"),
            GridBubble(x=0, y=0, label="A"),
            NorthArrow(x=50, y=50),
            ScaleBar(x=0, y=0),
            TitleNote(x=50, y=50, text="Title"),
            RevisionCloud(x=50, y=50),
        ]
        for entity in entities:
            d = annotation_to_dict(entity)
            restored = annotation_from_dict(d)
            assert type(restored) == type(entity)
    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown annotation type"):
            annotation_from_dict({"type": "unknown"})


class TestAnnotationSettings:
    def test_default(self):
        s = AnnotationSettings.default()
        assert s.text_height == 0.5
        assert s.show_room_labels is True
        assert s.units == "feet"
    def test_round_trip(self):
        s = AnnotationSettings(text_height=0.7, show_room_labels=False)
        s2 = AnnotationSettings.from_dict(s.to_dict())
        assert s == s2
    def test_frozen(self):
        s = AnnotationSettings()
        with pytest.raises(AttributeError):
            s.text_height = 1.0


class TestAnnotationEngine:
    def test_generate_all_annotations(self, sample_building, default_settings):
        annotations = generate_all_annotations(sample_building, default_settings)
        assert len(annotations) > 0
    def test_room_tags_generated(self, sample_building, default_settings):
        tags = generate_room_tags(sample_building, default_settings)
        assert len(tags) >= 2
    def test_door_tags_generated(self, sample_building, default_settings):
        tags = generate_door_tags(sample_building, default_settings)
        assert len(tags) >= 1
    def test_window_tags_generated(self, sample_building, default_settings):
        tags = generate_window_tags(sample_building, default_settings)
        assert len(tags) >= 1
    def test_grid_bubbles_generated(self, sample_building, default_settings):
        bubbles = generate_grid_bubbles(sample_building, default_settings)
        assert len(bubbles) > 0
    def test_north_arrow_generated(self, sample_building, default_settings):
        arrows = generate_north_arrow(sample_building, default_settings)
        assert len(arrows) == 1
    def test_scale_bar_generated(self, sample_building, default_settings):
        bars = generate_scale_bar(sample_building, default_settings)
        assert len(bars) == 1
    def test_title_note_generated(self, sample_building, default_settings):
        titles = generate_title_note(sample_building, default_settings)
        assert len(titles) == 1
        assert titles[0].text == "Test Building"
    def test_empty_model(self, empty_building, default_settings):
        annotations = generate_all_annotations(empty_building, default_settings)
        assert isinstance(annotations, list)
    def test_deterministic(self, sample_building, default_settings):
        a1 = generate_all_annotations(sample_building, default_settings)
        a2 = generate_all_annotations(sample_building, default_settings)
        assert [annotation_to_dict(a) for a in a1] == [annotation_to_dict(a) for a in a2]
    def test_no_room_labels_when_disabled(self, sample_building):
        settings = AnnotationSettings(show_room_labels=False)
        annotations = generate_all_annotations(sample_building, settings)
        room_tags = [a for a in annotations if isinstance(a, RoomTag) and a.room_number]
        assert len(room_tags) == 0
    def test_no_dimensions_when_disabled(self, sample_building):
        settings = AnnotationSettings(show_dimensions=False)
        annotations = generate_all_annotations(sample_building, settings)
        dims = [a for a in annotations if isinstance(a, (LinearDimension, AlignedDimension))]
        assert len(dims) == 0
    def test_no_north_arrow_when_disabled(self, sample_building):
        settings = AnnotationSettings(show_north_arrow=False)
        annotations = generate_all_annotations(sample_building, settings)
        arrows = [a for a in annotations if isinstance(a, NorthArrow)]
        assert len(arrows) == 0
    def test_no_scale_bar_when_disabled(self, sample_building):
        settings = AnnotationSettings(show_scale_bar=False)
        annotations = generate_all_annotations(sample_building, settings)
        bars = [a for a in annotations if isinstance(a, ScaleBar)]
        assert len(bars) == 0
    def test_no_title_when_disabled(self, sample_building):
        settings = AnnotationSettings(show_title=False)
        annotations = generate_all_annotations(sample_building, settings)
        titles = [a for a in annotations if isinstance(a, TitleNote)]
        assert len(titles) == 0
    def test_no_grid_when_disabled(self, sample_building):
        settings = AnnotationSettings(show_grid_labels=False)
        annotations = generate_all_annotations(sample_building, settings)
        grids = [a for a in annotations if isinstance(a, GridBubble)]
        assert len(grids) == 0
    def test_room_numbering(self, sample_building, default_settings):
        tags = generate_room_tags(sample_building, default_settings)
        numbers = [t.room_number for t in tags if t.room_number]
        assert "R01" in numbers
        assert "R02" in numbers
    def test_door_numbering(self, sample_building, default_settings):
        tags = generate_door_tags(sample_building, default_settings)
        numbers = [t.door_number for t in tags]
        assert "D01" in numbers
    def test_window_numbering(self, sample_building, default_settings):
        tags = generate_window_tags(sample_building, default_settings)
        numbers = [t.window_number for t in tags]
        assert "W01" in numbers
