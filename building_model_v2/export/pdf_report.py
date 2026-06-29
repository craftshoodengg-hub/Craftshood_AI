"""PDF report generator for architectural documentation."""
from __future__ import annotations
import os
from typing import Any

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from ..validation.cross_entity_validator import BuildingModel
from .pdf_styles import PAGE_WIDTH, PAGE_HEIGHT, MARGIN
from .pdf_templates import header_footer
from .report_metadata import ReportMetadata
from .cover_page import build_cover_page
from .report_sections import (
    build_project_summary, build_evaluation_summary, build_room_schedule_section,
    build_dimensions_section, build_optimization_section, build_structural_summary,
    build_revision_history,
)
from .room_schedule import generate_room_schedule
from .dimension_engine import generate_all_dimensions
from .annotation_engine import generate_all_annotations


def generate_pdf_report(
    model: BuildingModel,
    output_path: str,
    metadata: ReportMetadata | None = None,
    evaluation_report: Any = None,
    layout_result: Any = None,
) -> str:
    """Generate a professional multi-page PDF report.

    Args:
        model: The building model.
        output_path: File path for the output PDF.
        metadata: Report metadata.
        evaluation_report: Optional evaluation report.
        layout_result: Optional layout evaluation result.

    Returns:
        The output file path.
    """
    if not HAS_REPORTLAB:
        raise ImportError('reportlab is required for PDF generation. Install with: pip install reportlab')

    if metadata is None:
        project_name = model.building.name if model.building else 'Untitled Project'
        metadata = ReportMetadata.create(project_name=project_name)

    # Generate data
    schedule = generate_room_schedule(model)
    dimensions = generate_all_dimensions(model)
    annotations = generate_all_annotations(model)

    # Calculate overall score
    overall_score = 0
    quality = 'N/A'
    if evaluation_report is not None:
        summary = getattr(evaluation_report, 'summary', None)
        if summary:
            overall_score = getattr(summary, 'overall_score', 0)
            design_quality = getattr(evaluation_report, 'design_quality', None)
            if design_quality:
                quality = design_quality

    # Build document
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=metadata.project_name,
        author=metadata.generated_by,
    )

    story = []

    # Page 1: Cover
    story.extend(build_cover_page(metadata, overall_score, quality))
    story.append(PageBreak())

    # Page 2: Project Summary
    story.extend(build_project_summary(model, metadata))
    story.append(PageBreak())

    # Page 3: Evaluation Summary
    story.extend(build_evaluation_summary(evaluation_report))
    story.append(PageBreak())

    # Page 4: Room Schedule
    story.extend(build_room_schedule_section(schedule))
    story.append(PageBreak())

    # Page 5: Dimensions
    story.extend(build_dimensions_section(model, dimensions))
    story.append(PageBreak())

    # Page 6: Optimization
    story.extend(build_optimization_section(evaluation_report))
    story.append(PageBreak())

    # Page 7: Structural Summary
    story.extend(build_structural_summary(model))
    story.append(PageBreak())

    # Page 8: Revision History
    story.extend(build_revision_history(metadata))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return output_path


def generate_pdf_report_to_bytes(
    model: BuildingModel,
    metadata: ReportMetadata | None = None,
    evaluation_report: Any = None,
    layout_result: Any = None,
) -> bytes:
    """Generate PDF report and return as bytes.

    Args:
        model: The building model.
        metadata: Report metadata.
        evaluation_report: Optional evaluation report.
        layout_result: Optional layout evaluation result.

    Returns:
        PDF content as bytes.
    """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        path = f.name
    try:
        generate_pdf_report(model, path, metadata, evaluation_report, layout_result)
        with open(path, 'rb') as f:
            return f.read()
    finally:
        os.unlink(path)
