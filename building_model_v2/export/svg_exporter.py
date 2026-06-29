"""SVG Exporter for the unified drawing model.

Converts a DrawingModel into a responsive SVG document.
Deterministic. No AI. No randomness.
"""
from __future__ import annotations

import math
from typing import TextIO

from .drawing_entities import (
    ArcEntity,
    CircleEntity,
    DimensionEntity,
    GroupEntity,
    HatchEntity,
    LineEntity,
    PolygonEntity,
    PolylineEntity,
    TextEntity,
)
from .drawing_model import DrawingModel
from .svg_styles import SVG_BACKGROUND, SVG_FONT_FAMILY, SVG_NAMESPACE, SVG_VERSION


def _escape_xml(text: str) -> str:
    """Escape special XML characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _fmt(value: float) -> str:
    """Format a float for SVG output (deterministic)."""
    return "{:.2f}".format(value)


def _write_line(f: TextIO, e: LineEntity) -> None:
    f.write(
        f'  <line x1="{_fmt(e.x1)}" y1="{_fmt(e.y1)}" '
        f'x2="{_fmt(e.x2)}" y2="{_fmt(e.y2)}" '
        f'stroke="{e.color}" stroke-width="{_fmt(e.stroke_width)}" '
        f'stroke-linecap="round"/>\n'
    )


def _write_polyline(f: TextIO, e: PolylineEntity) -> None:
    if not e.points:
        return
    pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in e.points)
    if e.closed:
        f.write(
            f'  <polygon points="{pts}" '
            f'stroke="{e.color}" stroke-width="{_fmt(e.stroke_width)}" '
            f'fill="none" stroke-linejoin="round"/>\n'
        )
    else:
        f.write(
            f'  <polyline points="{pts}" '
            f'stroke="{e.color}" stroke-width="{_fmt(e.stroke_width)}" '
            f'fill="none" stroke-linejoin="round" stroke-linecap="round"/>\n'
        )


def _write_polygon(f: TextIO, e: PolygonEntity) -> None:
    if not e.points:
        return
    pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in e.points)
    f.write(
        f'  <polygon points="{pts}" '
        f'fill="{e.fill_color}" fill-opacity="{_fmt(e.fill_opacity)}" '
        f'stroke="{e.stroke_color}" stroke-width="{_fmt(e.stroke_width)}" '
        f'stroke-linejoin="round"/>\n'
    )


def _write_circle(f: TextIO, e: CircleEntity) -> None:
    f.write(
        f'  <circle cx="{_fmt(e.cx)}" cy="{_fmt(e.cy)}" '
        f'r="{_fmt(e.radius)}" '
        f'fill="{e.fill_color}" fill-opacity="{_fmt(e.fill_opacity)}" '
        f'stroke="{e.stroke_color}" stroke-width="{_fmt(e.stroke_width)}"/>\n'
    )


def _write_arc(f: TextIO, e: ArcEntity) -> None:
    sr = math.radians(e.start_angle)
    er = math.radians(e.end_angle)
    x1 = e.cx + e.radius * math.cos(sr)
    y1 = e.cy + e.radius * math.sin(sr)
    x2 = e.cx + e.radius * math.cos(er)
    y2 = e.cy + e.radius * math.sin(er)
    large = 1 if (e.end_angle - e.start_angle) > 180 else 0
    f.write(
        f'  <path d="M {_fmt(x1)} {_fmt(y1)} '
        f'A {_fmt(e.radius)} {_fmt(e.radius)} 0 '
        f'{large} 1 {_fmt(x2)} {_fmt(y2)}" '
        f'stroke="{e.color}" stroke-width="{_fmt(e.stroke_width)}" '
        f'fill="none" stroke-linecap="round"/>\n'
    )


def _write_text(f: TextIO, e: TextEntity) -> None:
    safe = _escape_xml(e.text)
    transform = ""
    if e.rotation != 0.0:
        transform = f' transform="rotate({_fmt(e.rotation)} {_fmt(e.x)} {_fmt(e.y)})"'
    f.write(
        f'  <text x="{_fmt(e.x)}" y="{_fmt(e.y)}" '
        f'font-family="{SVG_FONT_FAMILY}" font-size="{_fmt(e.font_size)}" '
        f'fill="{e.color}" text-anchor="{e.anchor}"{transform}>{safe}</text>\n'
    )


def _write_dimension(f: TextIO, e: DimensionEntity) -> None:
    f.write(
        f'  <line x1="{_fmt(e.x1)}" y1="{_fmt(e.offset_y)}" '
        f'x2="{_fmt(e.x2)}" y2="{_fmt(e.offset_y)}" '
        f'stroke="{e.color}" stroke-width="{_fmt(e.font_size * 0.3)}"/>\n'
    )
    f.write(
        f'  <line x1="{_fmt(e.x1)}" y1="{_fmt(e.y1)}" '
        f'x2="{_fmt(e.x1)}" y2="{_fmt(e.offset_y)}" '
        f'stroke="{e.color}" stroke-width="{_fmt(e.font_size * 0.2)}" '
        f'stroke-dasharray="0.5,0.3"/>\n'
    )
    f.write(
        f'  <line x1="{_fmt(e.x2)}" y1="{_fmt(e.y2)}" '
        f'x2="{_fmt(e.x2)}" y2="{_fmt(e.offset_y)}" '
        f'stroke="{e.color}" stroke-width="{_fmt(e.font_size * 0.2)}" '
        f'stroke-dasharray="0.5,0.3"/>\n'
    )
    mid_x = (e.x1 + e.x2) / 2
    mid_y = e.offset_y - 0.5
    safe = _escape_xml(e.label)
    f.write(
        f'  <text x="{_fmt(mid_x)}" y="{_fmt(mid_y)}" '
        f'font-family="{SVG_FONT_FAMILY}" font-size="{_fmt(e.font_size)}" '
        f'fill="{e.color}" text-anchor="middle">{safe}</text>\n'
    )


def _write_hatch(f: TextIO, e: HatchEntity) -> None:
    if not e.points:
        return
    pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in e.points)
    f.write(
        f'  <polygon points="{pts}" '
        f'fill="{e.color}" fill-opacity="0.5" '
        f'stroke="none"/>\n'
    )


def _write_group(f: TextIO, e: GroupEntity) -> None:
    f.write(f'  <g id="{_escape_xml(e.name)}">\n')
    for child in e.entities:
        _write_entity(f, child)
    f.write('  </g>\n')


def _write_entity(f: TextIO, entity: object) -> None:
    """Write a single entity to the SVG output."""
    if isinstance(entity, LineEntity):
        _write_line(f, entity)
    elif isinstance(entity, PolylineEntity):
        _write_polyline(f, entity)
    elif isinstance(entity, PolygonEntity):
        _write_polygon(f, entity)
    elif isinstance(entity, CircleEntity):
        _write_circle(f, entity)
    elif isinstance(entity, ArcEntity):
        _write_arc(f, entity)
    elif isinstance(entity, TextEntity):
        _write_text(f, entity)
    elif isinstance(entity, DimensionEntity):
        _write_dimension(f, entity)
    elif isinstance(entity, HatchEntity):
        _write_hatch(f, entity)
    elif isinstance(entity, GroupEntity):
        _write_group(f, entity)


def _compute_viewbox(model: DrawingModel, padding: float = 30.0) -> tuple[float, float, float, float]:
    """Compute the SVG viewBox with padding."""
    b = model.bounds
    return (b.min_x - padding, b.min_y - padding, b.width + 2 * padding, b.height + 2 * padding)


def export_svg(model: DrawingModel, output_path: str) -> str:
    """Export a DrawingModel to an SVG file."""
    svg_content = export_svg_to_string(model)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    return output_path


def _entity_to_svg_string(entity: object) -> str:
    """Convert a single entity to its SVG string representation."""
    if isinstance(entity, LineEntity):
        return (
            f'  <line x1="{_fmt(entity.x1)}" y1="{_fmt(entity.y1)}" '
            f'x2="{_fmt(entity.x2)}" y2="{_fmt(entity.y2)}" '
            f'stroke="{entity.color}" stroke-width="{_fmt(entity.stroke_width)}" '
            f'stroke-linecap="round"/>'
        )
    elif isinstance(entity, PolylineEntity):
        if not entity.points:
            return ""
        pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in entity.points)
        if entity.closed:
            return (f'  <polygon points="{pts}" '
                    f'stroke="{entity.color}" stroke-width="{_fmt(entity.stroke_width)}" '
                    f'fill="none" stroke-linejoin="round"/>')
        else:
            return (f'  <polyline points="{pts}" '
                    f'stroke="{entity.color}" stroke-width="{_fmt(entity.stroke_width)}" '
                    f'fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    elif isinstance(entity, PolygonEntity):
        if not entity.points:
            return ""
        pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in entity.points)
        return (f'  <polygon points="{pts}" '
                f'fill="{entity.fill_color}" fill-opacity="{_fmt(entity.fill_opacity)}" '
                f'stroke="{entity.stroke_color}" stroke-width="{_fmt(entity.stroke_width)}" '
                f'stroke-linejoin="round"/>')
    elif isinstance(entity, CircleEntity):
        return (f'  <circle cx="{_fmt(entity.cx)}" cy="{_fmt(entity.cy)}" '
                f'r="{_fmt(entity.radius)}" '
                f'fill="{entity.fill_color}" fill-opacity="{_fmt(entity.fill_opacity)}" '
                f'stroke="{entity.stroke_color}" stroke-width="{_fmt(entity.stroke_width)}"/>')
    elif isinstance(entity, ArcEntity):
        sr = math.radians(entity.start_angle)
        er = math.radians(entity.end_angle)
        x1 = entity.cx + entity.radius * math.cos(sr)
        y1 = entity.cy + entity.radius * math.sin(sr)
        x2 = entity.cx + entity.radius * math.cos(er)
        y2 = entity.cy + entity.radius * math.sin(er)
        large = 1 if (entity.end_angle - entity.start_angle) > 180 else 0
        return (f'  <path d="M {_fmt(x1)} {_fmt(y1)} '
                f'A {_fmt(entity.radius)} {_fmt(entity.radius)} 0 '
                f'{large} 1 {_fmt(x2)} {_fmt(y2)}" '
                f'stroke="{entity.color}" stroke-width="{_fmt(entity.stroke_width)}" '
                f'fill="none" stroke-linecap="round"/>')
    elif isinstance(entity, TextEntity):
        safe = _escape_xml(entity.text)
        transform = ""
        if entity.rotation != 0.0:
            transform = f' transform="rotate({_fmt(entity.rotation)} {_fmt(entity.x)} {_fmt(entity.y)})"'
        return (f'  <text x="{_fmt(entity.x)}" y="{_fmt(entity.y)}" '
                f'font-family="{SVG_FONT_FAMILY}" font-size="{_fmt(entity.font_size)}" '
                f'fill="{entity.color}" text-anchor="{entity.anchor}"{transform}>{safe}</text>')
    elif isinstance(entity, DimensionEntity):
        mid_x = (entity.x1 + entity.x2) / 2
        mid_y = entity.offset_y - 0.5
        safe = _escape_xml(entity.label)
        return (f'  <line x1="{_fmt(entity.x1)}" y1="{_fmt(entity.offset_y)}" '
                f'x2="{_fmt(entity.x2)}" y2="{_fmt(entity.offset_y)}" '
                f'stroke="{entity.color}" stroke-width="{_fmt(entity.font_size * 0.3)}"/>\n'
                f'  <text x="{_fmt(mid_x)}" y="{_fmt(mid_y)}" '
                f'font-family="{SVG_FONT_FAMILY}" font-size="{_fmt(entity.font_size)}" '
                f'fill="{entity.color}" text-anchor="middle">{safe}</text>')
    elif isinstance(entity, HatchEntity):
        if not entity.points:
            return ""
        pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in entity.points)
        return (f'  <polygon points="{pts}" '
                f'fill="{entity.color}" fill-opacity="0.5" '
                f'stroke="none"/>')
    elif isinstance(entity, GroupEntity):
        parts = [f'  <g id="{_escape_xml(entity.name)}">']
        for child in entity.entities:
            child_svg = _entity_to_svg_string(child)
            if child_svg:
                parts.append(child_svg)
        parts.append('  </g>')
        return "\n".join(parts)
    return ""


def export_svg_to_string(model: DrawingModel) -> str:
    """Export a DrawingModel to an SVG string."""
    vx, vy, vw, vh = _compute_viewbox(model)

    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(
        f'<svg xmlns="{SVG_NAMESPACE}" version="{SVG_VERSION}" '
        f'viewBox="{_fmt(vx)} {_fmt(vy)} {_fmt(vw)} {_fmt(vh)}" '
        f'width="100%" height="100%" '
        f'style="background-color:{SVG_BACKGROUND}">'
    )

    # Group entities by layer
    layer_groups: dict[str, list[object]] = {}
    for entity in model.entities:
        layer = getattr(entity, "layer", "0")
        if layer not in layer_groups:
            layer_groups[layer] = []
        layer_groups[layer].append(entity)

    # Write each layer as a <g> element (sorted for determinism)
    for layer_name in sorted(layer_groups.keys()):
        entities = layer_groups[layer_name]
        lines.append(f'  <g id="layer-{_escape_xml(layer_name)}">')
        for entity in entities:
            entity_svg = _entity_to_svg_string(entity)
            if entity_svg:
                lines.append(entity_svg)
        lines.append('  </g>')

    lines.append('</svg>')
    return "\n".join(lines) + "\n"
