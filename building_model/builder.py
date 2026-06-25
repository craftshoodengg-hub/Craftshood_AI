"""Builder for aggregate building models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .models import BuildingModel, BuildingStatistics
from .statistics import BuildingStatisticsCalculator


@dataclass(frozen=True, slots=True)
class ModuleOutputs:
    """Normalized inputs from upstream modules."""

    metadata: Mapping[str, Any] = field(default_factory=dict)
    plot: Mapping[str, Any] | None = None
    walls: Sequence[Any] = field(default_factory=tuple)
    doors: Sequence[Any] = field(default_factory=tuple)
    windows: Sequence[Any] = field(default_factory=tuple)
    rooms: Sequence[Any] = field(default_factory=tuple)
    adjacency_graph: Sequence[Any] = field(default_factory=tuple)
    connectivity_graph: Sequence[Any] = field(default_factory=tuple)
    facing_information: Mapping[str, Any] | None = None
    zoning: Sequence[Any] = field(default_factory=tuple)
    confidence: Sequence[Any] = field(default_factory=tuple)


class BuildingModelBuilder:
    """Construct :class:`BuildingModel` from upstream module outputs."""

    def __init__(self, statistics_calculator: BuildingStatisticsCalculator | None = None) -> None:
        self.statistics_calculator = statistics_calculator or BuildingStatisticsCalculator()

    def build(self, outputs: ModuleOutputs) -> BuildingModel:
        """Build a model and automatically compute statistics."""

        walls = tuple(_json_mapping(item) for item in outputs.walls)
        doors = tuple(_json_mapping(item) for item in outputs.doors)
        windows = tuple(_json_mapping(item) for item in outputs.windows)
        rooms = tuple(_json_mapping(item) for item in outputs.rooms)
        adjacency_graph = tuple(_json_mapping(item) for item in outputs.adjacency_graph)
        connectivity_graph = tuple(_json_mapping(item) for item in outputs.connectivity_graph)
        zoning = tuple(_json_mapping(item) for item in outputs.zoning)
        confidence = tuple(_json_mapping(item) for item in outputs.confidence)
        facing_information = (
            _json_mapping(outputs.facing_information)
            if outputs.facing_information is not None
            else None
        )
        statistics = self.statistics_calculator.calculate(
            rooms=rooms,
            walls=walls,
            doors=doors,
            windows=windows,
            adjacency_graph=adjacency_graph,
            connectivity_graph=connectivity_graph,
            facing_information=facing_information,
            zoning=zoning,
            confidence=confidence,
        )

        return BuildingModel(
            metadata=_json_mapping(outputs.metadata),
            plot=_json_mapping(outputs.plot) if outputs.plot is not None else None,
            walls=walls,
            doors=doors,
            windows=windows,
            rooms=rooms,
            adjacency_graph=adjacency_graph,
            connectivity_graph=connectivity_graph,
            facing_information=facing_information,
            zoning=zoning,
            confidence=confidence,
            statistics=statistics,
        )

    def rebuild_statistics(self, model: BuildingModel) -> BuildingModel:
        """Return a copy of ``model`` with refreshed statistics."""

        return BuildingModel(
            metadata=model.metadata,
            plot=model.plot,
            walls=model.walls,
            doors=model.doors,
            windows=model.windows,
            rooms=model.rooms,
            adjacency_graph=model.adjacency_graph,
            connectivity_graph=model.connectivity_graph,
            facing_information=model.facing_information,
            zoning=model.zoning,
            confidence=model.confidence,
            statistics=self.statistics_calculator.from_model(model),
        )


def build_building_model(outputs: ModuleOutputs) -> BuildingModel:
    """Convenience wrapper around :class:`BuildingModelBuilder`."""

    return BuildingModelBuilder().build(outputs)


def _json_mapping(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        value = value.to_dict()
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError(f"Expected mapping-like value, got {type(value).__name__}")
