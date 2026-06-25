"""DXF LINE entity reader."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import ezdxf
import numpy as np
from ezdxf.entities import DXFEntity
from loguru import logger


@dataclass(frozen=True, slots=True)
class Point2D:
    """A two-dimensional DXF point."""

    x: float
    y: float

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LineEntity:
    """A normalized representation of a DXF LINE entity."""

    id: str
    start: Point2D
    end: Point2D
    length: float
    angle: float
    layer: str
    space: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["start"] = self.start.to_dict()
        payload["end"] = self.end.to_dict()
        return payload


class LineReader:
    """Read every LINE entity from DXF layouts and, optionally, block definitions."""

    def __init__(self, *, include_blocks: bool = True) -> None:
        self.include_blocks = include_blocks

    def read(self, dxf_path: str | Path) -> list[LineEntity]:
        """Read LINE entities from ``dxf_path``.

        Raises:
            FileNotFoundError: If the DXF path does not exist.
            ezdxf.DXFError: If the DXF file cannot be parsed.
        """

        source = Path(dxf_path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"DXF file not found: {source}")

        logger.info("Reading DXF LINE entities from {}", source)
        document = ezdxf.readfile(source)

        lines: list[LineEntity] = []
        for layout in document.layouts:
            lines.extend(_read_lines_from_space(layout, space_name=f"layout:{layout.name}"))

        if self.include_blocks:
            for block in document.blocks:
                lines.extend(_read_lines_from_space(block, space_name=f"block:{block.name}"))

        logger.info("Read {} LINE entities from {}", len(lines), source.name)
        return lines


def read_line_entities(
    dxf_path: str | Path,
    *,
    include_blocks: bool = True,
) -> list[LineEntity]:
    """Convenience wrapper around :class:`LineReader`."""

    return LineReader(include_blocks=include_blocks).read(dxf_path)


def _read_lines_from_space(space: Any, *, space_name: str) -> list[LineEntity]:
    lines: list[LineEntity] = []
    for index, entity in enumerate(space):
        if entity.dxftype() != "LINE":
            continue

        start = _read_point(entity, "start")
        end = _read_point(entity, "end")
        length = _length(start, end)
        if length == 0:
            logger.debug("Skipping zero-length LINE in {}", space_name)
            continue

        lines.append(
            LineEntity(
                id=_line_id(entity, space_name=space_name, index=index),
                start=start,
                end=end,
                length=length,
                angle=_angle_degrees(start, end),
                layer=_safe_dxf_value(entity, "layer", default="0"),
                space=space_name,
            )
        )
    return lines


def _read_point(entity: DXFEntity, attr_name: str) -> Point2D:
    value = _safe_dxf_value(entity, attr_name)
    return Point2D(x=float(value[0]), y=float(value[1]))


def _line_id(entity: DXFEntity, *, space_name: str, index: int) -> str:
    handle = getattr(entity.dxf, "handle", None)
    return f"{space_name}:{handle or index}"


def _length(start: Point2D, end: Point2D) -> float:
    return float(np.linalg.norm(end.to_array() - start.to_array()))


def _angle_degrees(start: Point2D, end: Point2D) -> float:
    vector = end.to_array() - start.to_array()
    return math.degrees(math.atan2(float(vector[1]), float(vector[0]))) % 180.0


def _safe_dxf_value(entity: DXFEntity, name: str, default: Any = None) -> Any:
    try:
        return getattr(entity.dxf, name)
    except AttributeError:
        return default
