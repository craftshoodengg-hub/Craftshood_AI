"""Normalization utilities for extracted CAD information.

The package normalizes labels and scalar values that have already been
extracted from drawings. It does not inspect, infer, or mutate geometry.
"""

from .block_normalizer import BlockNormalizer
from .layer_normalizer import LayerCategory, LayerNormalizer
from .normalizer import Normalizer, NormalizerConfig
from .text_normalizer import RoomName, TextNormalizer
from .unit_normalizer import Dimension, UnitNormalizer

__all__ = [
    "BlockNormalizer",
    "Dimension",
    "LayerCategory",
    "LayerNormalizer",
    "Normalizer",
    "NormalizerConfig",
    "RoomName",
    "TextNormalizer",
    "UnitNormalizer",
]
