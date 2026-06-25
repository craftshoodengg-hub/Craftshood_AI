"""Block-name normalization.

Blocks are normalized only from already extracted block names. This module does
not inspect block geometry or infer entities from geometry.
"""

from __future__ import annotations

from collections.abc import Mapping

from .layer_normalizer import DEFAULT_LAYER_MAPPINGS, LayerCategory, LayerNormalizer


DEFAULT_BLOCK_MAPPINGS: dict[LayerCategory, tuple[str, ...]] = {
    **DEFAULT_LAYER_MAPPINGS,
    LayerCategory.DOOR: (*DEFAULT_LAYER_MAPPINGS[LayerCategory.DOOR], "d", "dr"),
    LayerCategory.WINDOW: (*DEFAULT_LAYER_MAPPINGS[LayerCategory.WINDOW], "w", "win"),
    LayerCategory.FURNITURE: (
        *DEFAULT_LAYER_MAPPINGS[LayerCategory.FURNITURE],
        "bed",
        "chair",
        "wardrobe",
        "wc",
    ),
}


class BlockNormalizer:
    """Normalize raw CAD block names into standard categories."""

    def __init__(
        self,
        mappings: Mapping[LayerCategory | str, tuple[str, ...] | list[str]] | None = None,
    ) -> None:
        self._layer_normalizer = LayerNormalizer(mappings or DEFAULT_BLOCK_MAPPINGS)

    def normalize(self, block_name: str | None) -> LayerCategory:
        """Return a standard category for ``block_name``."""

        return self._layer_normalizer.normalize(block_name)
