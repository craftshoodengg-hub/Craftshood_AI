"""Layout Evaluation Engine for Building Model v2."""
from __future__ import annotations
from ..validation.cross_entity_validator import BuildingModel
from .adjacency_engine import AdjacencyEngine
from .circulation_engine import CirculationEngine
from .privacy_engine import PrivacyEngine
from .egress_engine import EgressEngine
from .layout_evaluation_result import LayoutEvaluationResult
from .room_graph import RoomGraph


class LayoutEvaluationEngine:
    def __init__(self) -> None:
        self._adjacency_engine = AdjacencyEngine()
        self._circulation_engine = CirculationEngine()
        self._privacy_engine = PrivacyEngine()
        self._egress_engine = EgressEngine()

    def evaluate(self, building_model: BuildingModel) -> LayoutEvaluationResult:
        graph = self._adjacency_engine.build_graph(building_model)
        adjacency_result = self._adjacency_engine.evaluate(building_model)
        circulation_metrics = self._circulation_engine.analyze(building_model)
        circulation_result = self._circulation_engine.evaluate(building_model)
        privacy_metrics = self._privacy_engine.analyze(building_model, room_graph=graph)
        egress_metrics = self._egress_engine.analyze(building_model, room_graph=graph)
        egress_result = self._egress_engine.evaluate(building_model, room_graph=graph)
        return LayoutEvaluationResult(
            adjacency_result=adjacency_result,
            circulation_metrics=circulation_metrics,
            circulation_result=circulation_result,
            privacy_metrics=privacy_metrics,
            egress_metrics=egress_metrics,
            egress_result=egress_result,
        )
