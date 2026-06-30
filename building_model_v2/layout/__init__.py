"""Layout module for grid-based room placement."""

from .building_model_converter import BuildingModelConverter
from .layout_cell import LayoutCell
from .layout_grid import LayoutGrid
from .placed_room import PlacedRoom
from .layout_refinement_result import LayoutRefinementResult
from .layout_refiner import LayoutRefiner
from .placement_issue import PlacementIssue
from .placement_result import PlacementResult
from .placement_validation_result import PlacementValidationResult
from .placement_validator import PlacementValidator
from .room_placement_engine import RoomPlacementEngine


class AdjacencyEngine:
    """Placeholder for compatibility with package-level imports."""


class AdjacencyRule:
    """Placeholder for compatibility with package-level imports."""


class AdjacencyRuleSet:
    """Placeholder for compatibility with package-level imports."""


class RoomConnection:
    """Placeholder for compatibility with package-level imports."""


class RoomGraph:
    """Placeholder for compatibility with package-level imports."""


def create_default_rules() -> None:
    """Placeholder for compatibility with package-level imports."""


class CirculationEngine:
    """Placeholder for compatibility with package-level imports."""


class CirculationMetrics:
    """Placeholder for compatibility with package-level imports."""


class CirculationPath:
    """Placeholder for compatibility with package-level imports."""


class PrivacyEngine:
    """Placeholder for compatibility with package-level imports."""


class PrivacyConflict:
    """Placeholder for compatibility with package-level imports."""


class PrivacyMetrics:
    """Placeholder for compatibility with package-level imports."""


class EgressEngine:
    """Placeholder for compatibility with package-level imports."""


class EgressMetrics:
    """Placeholder for compatibility with package-level imports."""


class ExitPath:
    """Placeholder for compatibility with package-level imports."""


class LayoutEvaluationEngine:
    """Placeholder for compatibility with package-level imports."""


class LayoutEvaluationResult:
    """Placeholder for compatibility with package-level imports."""


__all__ = [
    "AdjacencyEngine",
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
    "BuildingModelConverter",
    "LayoutCell",
    "LayoutGrid",
    "LayoutRefinementResult",
    "LayoutRefiner",
    "PlacedRoom",
    "PlacementIssue",
    "PlacementResult",
    "PlacementValidationResult",
    "PlacementValidator",
    "RoomPlacementEngine",
]
