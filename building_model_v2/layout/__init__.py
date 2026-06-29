"""Layout package for Building Model v2.

Provides room graph, adjacency rules, and adjacency evaluation engine.
No AI. No randomness. Pure deterministic spatial analysis.
"""

from .adjacency_engine import AdjacencyEngine
from ..vastu.vastu_analyzer import VastuAnalyzer
from .circulation_engine import CirculationEngine
from .privacy_engine import PrivacyEngine
from .egress_engine import EgressEngine
from .layout_evaluation import LayoutEvaluationEngine
from .layout_evaluation_result import LayoutEvaluationResult
from .egress_metrics import EgressMetrics, ExitPath
from .privacy_metrics import PrivacyConflict, PrivacyMetrics
from .circulation_metrics import CirculationMetrics, CirculationPath
from .adjacency_rules import (
    AdjacencyRule,
    AdjacencyRuleSet,
    create_default_rules,
)
from .room_graph import (
    RoomConnection,
    RoomGraph,
)

__all__ = [
    "AdjacencyEngine",
    "VastuAnalyzer",
    "AdjacencyRule",
    "AdjacencyRuleSet",
    "RoomConnection",
    "RoomGraph",
    "create_default_rules",
    "CirculationEngine",
    "CirculationMetrics",
    "CirculationPath",
    "PrivacyEngine",
    "PrivacyConflict",
    "PrivacyMetrics",
    "EgressEngine",
    "EgressMetrics",
    "ExitPath",
    "LayoutEvaluationEngine",
    "LayoutEvaluationResult",
]
