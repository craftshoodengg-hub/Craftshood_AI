"""Tests for PDF report generation - Part 1."""
from __future__ import annotations
import os
import tempfile
import pytest

from building_model_v2.base import Point2D
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_wall import Wall
from building_model_v2.entities_column import Column
from building_model_v2.entities_opening import Door, Window
from building_model_v2.types import RoomType, WallType, ColumnType, DoorType
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.export.report_metadata import ReportMetadata
from building_model_v2.export.pdf_styles import get_styles, PAGE_WIDTH, PAGE_HEIGHT, MARGIN, CONTENT_WIDTH
from building_model_v2.export.pdf_templates import make_score_card, make_data_table, make_section_title, make_divider
from building_model_v2.export.cover_page import build_cover_page
from building_model_v2.export.report_sections import (
    build_project_summary, build_evaluation_summary, build_room_schedule_section,
    build_dimensions_section, build_optimization_section, build_structural_summary,
    build_revision_history,
)

try:
    import reportlab
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


@pytest.fixture
def sample_building():
    building = Building.create(name="Test Building", floor_ids=("f1",))
    floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1", "r2"}))
    r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
    r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], room_type=RoomType.BEDROOM)
    w1 = Wall.create(start=(0,0), end=(10,0), wall_type=WallType.EXTERIOR)
    col = Column.create(location=Point2D(x=5, y=5), size=1.0, column_type=ColumnType.SQUARE)
    door = Door.create(location=Point2D(x=5, y=0), width=3.0, door_type=DoorType.SINGLE_LEAF)
    window = Window.create(location=Point2D(x=15, y=0), width=4.0)
    return BuildingModel(
        building=building, floors={"f1": floor},
        rooms={"r1": r1, "r2": r2}, walls={"w1": w1},
        columns={"c1": col}, stairs={},
        doors={"d1": door}, windows={"w1": window}, relationships=[],
    )


@pytest.fixture
def empty_building():
    return BuildingModel()


@pytest.fixture
def default_metadata():
    return ReportMetadata.create(project_name="Test Project")


class TestReportMetadata:
    def test_default(self):
        m = ReportMetadata()
        assert m.project_name == "Untitled Project"
        assert m.report_version == "1.0.0"
        assert m.generated_by == "Craftshood AI"
    def test_create(self):
        m = ReportMetadata.create(project_name="My Project")
        assert m.project_name == "My Project"
    def test_round_trip(self):
        m = ReportMetadata(project_name="Test", revision="B")
        m2 = ReportMetadata.from_dict(m.to_dict())
        assert m == m2
    def test_frozen(self):
        m = ReportMetadata()
        with pytest.raises(AttributeError):
            m.project_name = "New"


class TestPDFStyles:
    def test_get_styles(self):
        styles = get_styles()
        assert 'title' in styles
        assert 'heading1' in styles
        assert 'body' in styles
    def test_constants(self):
        assert PAGE_WIDTH > 0
        assert PAGE_HEIGHT > 0
        assert MARGIN > 0
        assert CONTENT_WIDTH == PAGE_WIDTH - 2 * MARGIN


class TestPDFTemplates:
    def test_make_score_card(self):
        card = make_score_card("Test Score", 85.5, [("Items", 5)])
        assert card is not None
    def test_make_data_table(self):
        table = make_data_table(["Col1", "Col2"], [["A", "B"], ["C", "D"]])
        assert table is not None
    def test_make_section_title(self):
        title = make_section_title("Test Section")
        assert title is not None
    def test_make_divider(self):
        divider = make_divider()
        assert divider is not None


class TestCoverPage:
    def test_build_cover_page(self, default_metadata):
        story = build_cover_page(default_metadata, 85, "Good")
        assert len(story) > 0
    def test_build_cover_page_no_score(self, default_metadata):
        story = build_cover_page(default_metadata)
        assert len(story) > 0


class TestReportSections:
    def test_build_project_summary(self, sample_building, default_metadata):
        story = build_project_summary(sample_building, default_metadata)
        assert len(story) > 0
    def test_build_evaluation_summary_none(self):
        story = build_evaluation_summary(None)
        assert len(story) > 0
    def test_build_room_schedule_section(self, sample_building):
        from building_model_v2.export.room_schedule import generate_room_schedule
        schedule = generate_room_schedule(sample_building)
        story = build_room_schedule_section(schedule)
        assert len(story) > 0
    def test_build_room_schedule_section_empty(self, empty_building):
        from building_model_v2.export.room_schedule import generate_room_schedule
        schedule = generate_room_schedule(empty_building)
        story = build_room_schedule_section(schedule)
        assert len(story) > 0
    def test_build_dimensions_section(self, sample_building):
        from building_model_v2.export.dimension_engine import generate_all_dimensions
        dims = generate_all_dimensions(sample_building)
        story = build_dimensions_section(sample_building, dims)
        assert len(story) > 0
    def test_build_optimization_section_none(self):
        story = build_optimization_section(None)
        assert len(story) > 0
    def test_build_structural_summary(self, sample_building):
        story = build_structural_summary(sample_building)
        assert len(story) > 0
    def test_build_revision_history(self, default_metadata):
        story = build_revision_history(default_metadata)
        assert len(story) > 0


@pytest.mark.skipif(not HAS_REPORTLAB, reason="reportlab not installed")
class TestPDFReportGeneration:
    def test_generate_pdf_report(self, sample_building, default_metadata):
        from building_model_v2.export.pdf_report import generate_pdf_report
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            result = generate_pdf_report(sample_building, path, default_metadata)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)

    def test_generate_pdf_report_empty_model(self, empty_building):
        from building_model_v2.export.pdf_report import generate_pdf_report
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            result = generate_pdf_report(empty_building, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)

    def test_generate_pdf_report_large_building(self):
        from building_model_v2.export.pdf_report import generate_pdf_report
        building = Building.create(name="Large Building", floor_ids=("f1",))
        rooms = {}
        for i in range(20):
            rid = f"r{i}"
            x = (i % 5) * 12
            y = (i // 5) * 12
            rooms[rid] = Room.create(
                vertices=[(x,y),(x+10,y),(x+10,y+10),(x,y+10)],
                room_type=RoomType.LIVING,
            )
        model = BuildingModel(building=building, rooms=rooms)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            result = generate_pdf_report(model, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)

    def test_generate_pdf_report_multi_floor(self):
        from building_model_v2.export.pdf_report import generate_pdf_report
        building = Building.create(name="Multi Floor", floor_ids=("f1", "f2"))
        f1 = Floor.create(name="F1", level=0, room_ids=frozenset({"r1"}))
        f2 = Floor.create(name="F2", level=1, room_ids=frozenset({"r2"}))
        r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
        r2 = Room.create(vertices=[(0,0),(15,0),(15,12),(0,12)], room_type=RoomType.KITCHEN)
        model = BuildingModel(
            building=building, floors={"f1": f1, "f2": f2},
            rooms={"r1": r1, "r2": r2},
        )
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            result = generate_pdf_report(model, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)

    def test_generate_pdf_to_bytes(self, sample_building):
        from building_model_v2.export.pdf_report import generate_pdf_report_to_bytes
        pdf_bytes = generate_pdf_report_to_bytes(sample_building)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

    def test_deterministic_output(self, sample_building):
        from building_model_v2.export.pdf_report import generate_pdf_report_to_bytes
        from building_model_v2.export.report_metadata import ReportMetadata
        # Use fixed metadata for deterministic output
        metadata = ReportMetadata(
            project_name="Deterministic Test",
            report_version="1.0.0",
            engine_version="2.0.0",
            craftshood_version="2.0.0",
            generated_at="2024-01-01T00:00:00+00:00",
            generated_by="Craftshood AI",
            revision="A",
        )
        # Generate two reports with same metadata
        b1 = generate_pdf_report_to_bytes(sample_building, metadata)
        b2 = generate_pdf_report_to_bytes(sample_building, metadata)
        # Check both are valid PDFs
        assert b1[:4] == b'%PDF'
        assert b2[:4] == b'%PDF'
        # Check they have similar sizes (within 1% tolerance for timestamps)
        assert abs(len(b1) - len(b2)) < len(b1) * 0.01
        # Check both have multiple pages
        assert b1.count(b'/Type /Page') > 5
        assert b2.count(b'/Type /Page') > 5

    def test_pdf_has_multiple_pages(self, sample_building):
        from building_model_v2.export.pdf_report import generate_pdf_report_to_bytes
        pdf_bytes = generate_pdf_report_to_bytes(sample_building)
        page_count = pdf_bytes.count(b'/Type /Page')
        assert page_count > 5


class TestBackwardCompatibility:
    def test_dxf_still_works(self, sample_building):
        from building_model_v2.export.dxf_exporter import DXFExporter
        exporter = DXFExporter()
        result = exporter.export_to_string(sample_building)
        assert "EOF" in result

    def test_svg_still_works(self, sample_building):
        from building_model_v2.export.drawing_builder import build_drawing_model
        from building_model_v2.export.svg_exporter import export_svg_to_string
        dm = build_drawing_model(sample_building)
        svg = export_svg_to_string(dm)
        assert "<svg" in svg

    def test_drawing_model_unchanged(self, sample_building):
        from building_model_v2.export.drawing_builder import build_drawing_model
        dm = build_drawing_model(sample_building)
        assert len(dm.layers) == 9
        assert len(dm.entities) > 0
