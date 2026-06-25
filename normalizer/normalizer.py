"""Facade for normalizing extracted CAD information."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .block_normalizer import BlockNormalizer, DEFAULT_BLOCK_MAPPINGS
from .layer_normalizer import DEFAULT_LAYER_MAPPINGS, LayerCategory, LayerNormalizer
from .text_normalizer import DEFAULT_ROOM_MAPPINGS, RoomName, TextNormalizer
from .unit_normalizer import UnitNormalizer


@dataclass(frozen=True, slots=True)
class NormalizerConfig:
    """Configuration for all normalizers."""

    layer_mappings: Mapping[LayerCategory | str, tuple[str, ...] | list[str]] = field(
        default_factory=lambda: DEFAULT_LAYER_MAPPINGS.copy()
    )
    block_mappings: Mapping[LayerCategory | str, tuple[str, ...] | list[str]] = field(
        default_factory=lambda: DEFAULT_BLOCK_MAPPINGS.copy()
    )
    room_mappings: Mapping[RoomName | str, tuple[str, ...] | list[str]] = field(
        default_factory=lambda: DEFAULT_ROOM_MAPPINGS.copy()
    )
    default_dimension_unit: str = "ft"
    dimension_precision: int = 4


class Normalizer:
    """High-level normalizer for already extracted drawing information.

    The facade never mutates the input mapping and never edits geometry fields.
    It only derives normalized values from extracted text-like information.
    """

    def __init__(self, config: NormalizerConfig | None = None) -> None:
        self.config = config or NormalizerConfig()
        self.layers = LayerNormalizer(self.config.layer_mappings)
        self.blocks = BlockNormalizer(self.config.block_mappings)
        self.text = TextNormalizer(self.config.room_mappings)
        self.units = UnitNormalizer(
            default_unit=self.config.default_dimension_unit,
            precision=self.config.dimension_precision,
        )

    def normalize_layer(self, layer_name: str | None) -> LayerCategory:
        return self.layers.normalize(layer_name)

    def normalize_block(self, block_name: str | None) -> LayerCategory:
        return self.blocks.normalize(block_name)

    def normalize_room_name(self, value: str | None) -> RoomName | None:
        return self.text.normalize_room_name(value)

    def normalize_dimension(self, value: Any) -> float | None:
        dimension = self.units.normalize_dimension(value)
        return None if dimension is None else dimension.feet

    def normalize_record(self, record: Mapping[str, Any]) -> dict[str, Any]:
        """Return a copy of ``record`` with derived normalized fields.

        Recognized source keys:
            ``layer`` -> ``layer_category``
            ``block`` or ``block_name`` -> ``block_category``
            ``text`` or ``room`` or ``room_name`` -> ``room_name_normalized``
            ``dimension`` or ``measurement`` -> ``dimension_feet``
        """

        normalized = dict(record)

        if "layer" in record:
            normalized["layer_category"] = self.normalize_layer(record.get("layer")).value

        block_name = record.get("block_name", record.get("block"))
        if block_name is not None:
            normalized["block_category"] = self.normalize_block(block_name).value

        text_value = record.get("room_name", record.get("room", record.get("text")))
        room_name = self.normalize_room_name(text_value)
        if room_name is not None:
            normalized["room_name_normalized"] = room_name.value

        dimension_value = record.get("dimension", record.get("measurement"))
        if dimension_value is not None:
            dimension = self.normalize_dimension(dimension_value)
            if dimension is not None:
                normalized["dimension_feet"] = dimension

        return normalized
