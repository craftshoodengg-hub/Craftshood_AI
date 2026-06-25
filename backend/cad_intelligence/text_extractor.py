"""DXF text extraction utilities for CAD intelligence.

The module intentionally reads only textual CAD entities. Geometry detection
such as walls, doors, or windows belongs in future detector modules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import ezdxf
from ezdxf.entities import DXFEntity
from loguru import logger


TEXT_ENTITY_TYPES = {"TEXT", "MTEXT"}


@dataclass(frozen=True, slots=True)
class Point2D:
    """A 2D insertion point extracted from a DXF entity."""

    x: float
    y: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TextEntity:
    """Normalized representation of TEXT and MTEXT entities."""

    text: str
    entity_type: str
    layer: str
    position: Point2D
    height: float | None
    rotation: float | None
    space: str
    handle: str | None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["position"] = self.position.to_dict()
        return payload


def extract_text_entities(dxf_path: str | Path, *, include_blocks: bool = True) -> list[TextEntity]:
    """Read all TEXT and MTEXT entities from a DXF file.

    Args:
        dxf_path: Path to the source DXF file.
        include_blocks: When true, also scans block definitions. Layout entities
            are always scanned.

    Returns:
        A list of normalized text entities in drawing order where possible.

    Raises:
        FileNotFoundError: If the DXF file does not exist.
        ezdxf.DXFError: If ezdxf cannot parse the file.
    """

    source = Path(dxf_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"DXF file not found: {source}")

    logger.info("Reading DXF text entities from {}", source)
    document = ezdxf.readfile(source)

    records: list[TextEntity] = []
    for layout in document.layouts:
        records.extend(_extract_from_space(layout, space_name=f"layout:{layout.name}"))

    if include_blocks:
        for block in document.blocks:
            records.extend(_extract_from_space(block, space_name=f"block:{block.name}"))

    logger.info("Extracted {} text entities from {}", len(records), source.name)
    return records


def _extract_from_space(space: Any, *, space_name: str) -> list[TextEntity]:
    records: list[TextEntity] = []
    for entity in space:
        if entity.dxftype() not in TEXT_ENTITY_TYPES:
            continue

        text = _read_entity_text(entity)
        if not text:
            continue

        records.append(
            TextEntity(
                text=text,
                entity_type=entity.dxftype(),
                layer=_safe_dxf_value(entity, "layer", default="0"),
                position=_read_insert_point(entity),
                height=_read_height(entity),
                rotation=_safe_float(_safe_dxf_value(entity, "rotation")),
                space=space_name,
                handle=getattr(entity.dxf, "handle", None),
            )
        )
    return records


def _read_entity_text(entity: DXFEntity) -> str:
    if entity.dxftype() == "TEXT":
        return _clean_text(_safe_dxf_value(entity, "text", default=""))

    if entity.dxftype() == "MTEXT":
        plain_text = getattr(entity, "plain_text", None)
        if callable(plain_text):
            try:
                return _clean_text(plain_text())
            except TypeError:
                return _clean_text(plain_text(split=False))
        return _clean_text(_safe_dxf_value(entity, "text", default=""))

    return ""


def _read_insert_point(entity: DXFEntity) -> Point2D:
    insert = _safe_dxf_value(entity, "insert")
    if insert is None:
        return Point2D(x=0.0, y=0.0)
    return Point2D(x=float(insert[0]), y=float(insert[1]))


def _read_height(entity: DXFEntity) -> float | None:
    height = _safe_dxf_value(entity, "height")
    if height is None and entity.dxftype() == "MTEXT":
        height = _safe_dxf_value(entity, "char_height")
    return _safe_float(height)


def _safe_dxf_value(entity: DXFEntity, name: str, default: Any = None) -> Any:
    try:
        return getattr(entity.dxf, name)
    except AttributeError:
        return default


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_text(value: Any) -> str:
    text = str(value or "")
    return " ".join(text.replace("\\P", " ").split()).strip()
