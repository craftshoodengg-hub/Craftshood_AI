"""Report section builders for PDF reports."""
from __future__ import annotations
from typing import Any

try:
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from .pdf_styles import *
from .pdf_templates import make_score_card, make_data_table, make_section_title, make_divider


def build_project_summary(model, metadata):
    story = []
    story.append(make_section_title('Project Summary'))
    story.append(make_divider())
    building_name = model.building.name if model.building else 'Untitled'
    floor_count = len(model.floors)
    total_rooms = len(model.rooms)
    total_area = sum(r.area for r in model.rooms.values() if not r.polygon.is_empty)
    info = [
        ['Project Name', building_name],
        ['Floor Count', str(floor_count)],
        ['Total Rooms', str(total_rooms)],
        ['Total Area', '{:.0f} sqft'.format(total_area)],
        ['Wall Count', str(len(model.walls))],
        ['Column Count', str(len(model.columns))],
        ['Stair Count', str(len(model.stairs))],
        ['Door Count', str(len(model.doors))],
        ['Window Count', str(len(model.windows))],
    ]
    t = Table(info, colWidths=[CONTENT_WIDTH*0.4, CONTENT_WIDTH*0.4])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), COLOR_GRAY),
        ('TEXTCOLOR', (1, 0), (1, -1), COLOR_DARK),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_LIGHT_GRAY),
    ]))
    story.append(t)
    return story


def build_evaluation_summary(evaluation_report=None):
    story = []
    story.append(make_section_title('Evaluation Summary'))
    story.append(make_divider())
    if evaluation_report is None:
        story.append(Paragraph('No evaluation data available.', ParagraphStyle('body', fontSize=10, textColor=COLOR_GRAY)))
        return story
    summary = getattr(evaluation_report, 'summary', None)
    if summary:
        score = getattr(summary, 'overall_score', 0)
        story.append(make_score_card('Overall Design Score', score))
        story.append(Spacer(1, 10*mm))
        cat_scores = getattr(summary, 'category_scores', {})
        if cat_scores:
            story.append(Paragraph('<b>Category Scores</b>', ParagraphStyle('h2', fontSize=12, textColor=COLOR_PRIMARY, spaceBefore=6)))
            score_data = []
            for cat, val in sorted(cat_scores.items()):
                score_data.append([cat.replace('_', ' ').title(), '{:.0f}/100'.format(val)])
            if score_data:
                story.append(make_data_table(['Category', 'Score'], score_data))
    else:
        story.append(Paragraph('Summary data not available.', ParagraphStyle('body', fontSize=10, textColor=COLOR_GRAY)))
    return story


def build_room_schedule_section(schedule):
    story = []
    story.append(make_section_title('Room Schedule'))
    story.append(make_divider())
    if not schedule or not schedule.entries:
        story.append(Paragraph('No rooms in schedule.', ParagraphStyle('body', fontSize=10, textColor=COLOR_GRAY)))
        return story
    headers = ['Room No', 'Name', 'Floor', 'Area (sqft)', 'Perimeter (ft)', 'Privacy', 'Light', 'Ventilation']
    col_widths = [CONTENT_WIDTH*0.08, CONTENT_WIDTH*0.15, CONTENT_WIDTH*0.12, CONTENT_WIDTH*0.12, CONTENT_WIDTH*0.12, CONTENT_WIDTH*0.12, CONTENT_WIDTH*0.12, CONTENT_WIDTH*0.12]
    data = []
    for entry in schedule.entries:
        data.append([entry.room_number, entry.room_name, entry.floor, '{:.0f}'.format(entry.area), '{:.1f}'.format(entry.perimeter), entry.privacy, entry.natural_light, entry.ventilation])
    story.append(make_data_table(headers, data, col_widths))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph('<b>Total Area: {:.0f} sqft</b>'.format(schedule.total_area), ParagraphStyle('total', fontSize=11, textColor=COLOR_PRIMARY)))
    return story


def build_dimensions_section(model, dimensions):
    story = []
    story.append(make_section_title('Dimensions'))
    story.append(make_divider())
    if not dimensions:
        story.append(Paragraph('No dimensions generated.', ParagraphStyle('body', fontSize=10, textColor=COLOR_GRAY)))
        return story
    headers = ['Type', 'From', 'To', 'Measurement']
    data = []
    for dim in dimensions:
        label = getattr(dim, 'label', '')
        x1 = getattr(dim, 'x1', 0)
        y1 = getattr(dim, 'y1', 0)
        x2 = getattr(dim, 'x2', 0)
        y2 = getattr(dim, 'y2', 0)
        dim_type = type(dim).__name__.replace('Dimension', '')
        data.append([dim_type, '({:.1f}, {:.1f})'.format(x1, y1), '({:.1f}, {:.1f})'.format(x2, y2), label])
    story.append(make_data_table(headers, data))
    return story


def build_optimization_section(evaluation_report=None):
    story = []
    story.append(make_section_title('Optimization Report'))
    story.append(make_divider())
    if evaluation_report is None:
        story.append(Paragraph('No optimization data available.', ParagraphStyle('body', fontSize=10, textColor=COLOR_GRAY)))
        return story
    opportunities = getattr(evaluation_report, 'improvement_opportunities', [])
    if opportunities:
        story.append(Paragraph('<b>Improvement Opportunities:</b>', ParagraphStyle('h2', fontSize=12, textColor=COLOR_PRIMARY)))
        for i, opp in enumerate(opportunities, 1):
            story.append(Paragraph(f'{i}. {opp}', ParagraphStyle('body', fontSize=10, textColor=COLOR_DARK)))
    else:
        story.append(Paragraph('No improvements identified. Design is optimal.', ParagraphStyle('body', fontSize=10, textColor=COLOR_SUCCESS)))
    return story


def build_structural_summary(model):
    story = []
    story.append(make_section_title('Structural Summary'))
    story.append(make_divider())
    wall_count = len(model.walls)
    column_count = len(model.columns)
    stair_count = len(model.stairs)
    load_bearing_walls = sum(1 for w in model.walls.values() if w.is_load_bearing)
    total_wall_length = sum(w.length for w in model.walls.values())
    info = [
        ['Total Walls', str(wall_count)],
        ['Load-bearing Walls', str(load_bearing_walls)],
        ['Total Wall Length', '{:.1f} ft'.format(total_wall_length)],
        ['Total Columns', str(column_count)],
        ['Total Stairs', str(stair_count)],
    ]
    t = Table(info, colWidths=[CONTENT_WIDTH*0.5, CONTENT_WIDTH*0.3])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), COLOR_GRAY),
        ('TEXTCOLOR', (1, 0), (1, -1), COLOR_DARK),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_LIGHT_GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    return story


def build_revision_history(metadata):
    story = []
    story.append(make_section_title('Revision History'))
    story.append(make_divider())
    info = [
        ['Report Version', metadata.report_version],
        ['Generation Timestamp', metadata.generated_at],
        ['Engine Version', metadata.engine_version],
        ['Craftshood AI Version', metadata.craftshood_version],
        ['Revision', metadata.revision],
    ]
    t = Table(info, colWidths=[CONTENT_WIDTH*0.5, CONTENT_WIDTH*0.4])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), COLOR_GRAY),
        ('TEXTCOLOR', (1, 0), (1, -1), COLOR_DARK),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_LIGHT_GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    return story
