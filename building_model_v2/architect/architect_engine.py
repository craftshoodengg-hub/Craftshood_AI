"""Architect engine orchestration layer.

Coordinates the Architect Brain pipeline:
SpaceProgram -> BubbleGenerator -> ZoningEngine -> ArchitectResult
"""
from __future__ import annotations

from typing import Any, Dict

from ..ai.space_program import SpaceProgram
from .architect_result import ArchitectResult
from .bubble_generator import BubbleGenerator
from .zoning_engine import ZoningEngine


class ArchitectEngine:
    """Orchestration engine for architectural analysis.

    Coordinates the pipeline from space program to bubble diagram
    to zoning analysis.
    """

    def __init__(
        self,
        bubble_generator: BubbleGenerator | None = None,
        zoning_engine: ZoningEngine | None = None,
    ) -> None:
        """Initialize the architect engine.

        Args:
            bubble_generator: Optional bubble generator instance.
            zoning_engine: Optional zoning engine instance.
        """
        self._bubble_generator = bubble_generator or BubbleGenerator()
        self._zoning_engine = zoning_engine or ZoningEngine()

    def analyze(self, program: SpaceProgram) -> ArchitectResult:
        """Analyze a space program and produce architect results.

        Pipeline:
        1. Generate bubble diagram from space program
        2. Analyze zoning from bubble diagram
        3. Return combined result

        Args:
            program: The space program to analyze.

        Returns:
            An ArchitectResult containing bubble diagram and zoning.
        """
        # Step 1: Generate bubble diagram
        bubble_diagram = self._bubble_generator.generate(program)

        # Step 2: Analyze zoning
        zoning_result = self._zoning_engine.analyze(bubble_diagram)

        # Step 3: Build result
        metadata = {
            "source": "architect_engine",
            "program_room_count": len(program.rooms),
            "floor_count": program.floor_count,
        }

        return ArchitectResult(
            bubble_diagram=bubble_diagram,
            zoning_result=zoning_result,
            metadata=metadata,
        )