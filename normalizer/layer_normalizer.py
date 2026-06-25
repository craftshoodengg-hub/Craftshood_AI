"""Layer-name normalization."""

from __future__ import annotations

import re
from collections.abc import Mapping
from enum import StrEnum


class LayerCategory(StrEnum):
    """Supported standard layer categories."""

    WALL = "WALL"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    TEXT = "TEXT"
    DIMENSION = "DIMENSION"
    FURNITURE = "FURNITURE"
    COLUMN = "COLUMN"
    STAIR = "STAIR"
    UNKNOWN = "UNKNOWN"


DEFAULT_LAYER_MAPPINGS: dict[LayerCategory, tuple[str, ...]] = {
    LayerCategory.WALL: ("wall", "walls", "a-wall", "arch-wall", "masonry", "brick"),
    LayerCategory.DOOR: ("door", "doors", "a-door", "opening-door", "shutter"),
    LayerCategory.WINDOW: ("window", "windows", "a-window", "glazing", "ventilator"),
    LayerCategory.TEXT: ("text", "texts", "a-text", "anno", "annotation", "label", "room"),
    LayerCategory.DIMENSION: (
        "dim",
        "dims",
        "dimension",
        "dimensions",
        "a-dim",
        "measurement",
    ),
    LayerCategory.FURNITURE: ("furniture", "furn", "fixture", "fixtures", "sofa", "table"),
    LayerCategory.COLUMN: ("column", "columns", "col", "pillar", "rcc-column"),
    LayerCategory.STAIR: ("stair", "stairs", "staircase", "steps", "flight"),
}


class LayerNormalizer:
    """Normalize raw CAD layer names into standard categories.

    Args:
        mappings: Optional category-to-alias mapping. The aliases are matched
            after token normalization, so values such as ``A-WALL`` and
            ``a_wall`` are equivalent.
    """

    def __init__(
        self,
        mappings: Mapping[LayerCategory | str, tuple[str, ...] | list[str]] | None = None,
    ) -> None:
        self._patterns = _compile_patterns(mappings or DEFAULT_LAYER_MAPPINGS)

    def normalize(self, layer_name: str | None) -> LayerCategory:
        """Return the standard category for ``layer_name``."""

        normalized = normalize_key(layer_name)
        if not normalized:
            return LayerCategory.UNKNOWN

        for category, aliases in self._patterns.items():
            if normalized in aliases:
                return category
            if any(_contains_token(normalized, alias) for alias in aliases):
                return category
        return LayerCategory.UNKNOWN


def normalize_key(value: str | None) -> str:
    """Normalize a human/CAD label into a comparable lowercase key."""

    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[_./\\-]+", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _compile_patterns(
    mappings: Mapping[LayerCategory | str, tuple[str, ...] | list[str]],
) -> dict[LayerCategory, set[str]]:
    compiled: dict[LayerCategory, set[str]] = {}
    for raw_category, aliases in mappings.items():
        category = _coerce_category(raw_category)
        if category is LayerCategory.UNKNOWN:
            continue
        compiled[category] = {normalize_key(alias) for alias in aliases if normalize_key(alias)}
    return compiled


def _coerce_category(value: LayerCategory | str) -> LayerCategory:
    try:
        return value if isinstance(value, LayerCategory) else LayerCategory[value.upper()]
    except KeyError as exc:
        raise ValueError(f"Unsupported layer category: {value!r}") from exc


def _contains_token(value: str, alias: str) -> bool:
    if not alias:
        return False
    return re.search(rf"(?:^|\s){re.escape(alias)}(?:\s|$)", value) is not None
