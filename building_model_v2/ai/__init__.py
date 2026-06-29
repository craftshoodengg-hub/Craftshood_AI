"""AI package for Craftshood AI.

Provides deterministic natural language parsing for architectural design requirements.
No LLM. No network. Pure regex-based deterministic parsing.

Modules:
    design_requirements: Immutable dataclasses for structured design specs
    parser_result: Result of parsing with confidence and warnings
    parser_rules: Deterministic extraction helpers (regex-based)
    requirement_parser: Main parser interface
"""

from .design_requirements import (
    BuildingRequirements,
    DesignRequirements,
    PlotRequirements,
)
from .parser_result import ParserResult
from .requirement_parser import RequirementParser
from .room_program import FloorPreference, PrivacyLevel, RoomProgram
from .space_program import SpaceProgram
from .space_generator import SpaceProgramGenerator
from .layout_generator import LayoutGenerator
from .generation_pipeline import GenerationPipeline
from .generation_result import GenerationResult
from .layout_generation_result import LayoutGenerationResult

__all__ = [
    "BuildingRequirements",
    "DesignRequirements",
    "PlotRequirements",
    "ParserResult",
    "RequirementParser",
    "RoomProgram",
    "PrivacyLevel",
    "FloorPreference",
    "SpaceProgram",
    "SpaceProgramGenerator",
    "LayoutGenerator",
    "LayoutGenerationResult",
    "GenerationPipeline",
    "GenerationResult",
]
