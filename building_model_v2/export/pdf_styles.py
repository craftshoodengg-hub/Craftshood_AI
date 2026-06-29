"""PDF styling constants and stylesheets."""
from __future__ import annotations

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


# Colors
COLOR_PRIMARY = colors.HexColor('#1a5276')
COLOR_SECONDARY = colors.HexColor('#2e86c1')
COLOR_ACCENT = colors.HexColor('#f39c12')
COLOR_SUCCESS = colors.HexColor('#27ae60')
COLOR_WARNING = colors.HexColor('#e67e22')
COLOR_DANGER = colors.HexColor('#e74c3c')
COLOR_GRAY = colors.HexColor('#7f8c8d')
COLOR_LIGHT_GRAY = colors.HexColor('#ecf0f1')
COLOR_DARK = colors.HexColor('#2c3e50')
COLOR_WHITE = colors.white
COLOR_BLACK = colors.black


def get_styles():
    base = getSampleStyleSheet()
    styles = {}
    styles['title'] = ParagraphStyle('Title', parent=base['Title'], fontSize=24, textColor=COLOR_PRIMARY, spaceAfter=12, alignment=TA_CENTER)
    styles['subtitle'] = ParagraphStyle('Subtitle', parent=base['Normal'], fontSize=14, textColor=COLOR_GRAY, spaceAfter=6, alignment=TA_CENTER)
    styles['heading1'] = ParagraphStyle('Heading1', parent=base['Heading1'], fontSize=18, textColor=COLOR_PRIMARY, spaceBefore=16, spaceAfter=8)
    styles['heading2'] = ParagraphStyle('Heading2', parent=base['Heading2'], fontSize=14, textColor=COLOR_SECONDARY, spaceBefore=12, spaceAfter=6)
    styles['body'] = ParagraphStyle('Body', parent=base['Normal'], fontSize=10, textColor=COLOR_DARK, spaceAfter=4)
    styles['small'] = ParagraphStyle('Small', parent=base['Normal'], fontSize=8, textColor=COLOR_GRAY)
    styles['score_excellent'] = ParagraphStyle('ScoreExcellent', parent=base['Normal'], fontSize=12, textColor=COLOR_SUCCESS, alignment=TA_CENTER)
    styles['score_good'] = ParagraphStyle('ScoreGood', parent=base['Normal'], fontSize=12, textColor=COLOR_SECONDARY, alignment=TA_CENTER)
    styles['score_fair'] = ParagraphStyle('ScoreFair', parent=base['Normal'], fontSize=12, textColor=COLOR_WARNING, alignment=TA_CENTER)
    styles['score_poor'] = ParagraphStyle('ScorePoor', parent=base['Normal'], fontSize=12, textColor=COLOR_DANGER, alignment=TA_CENTER)
    return styles
