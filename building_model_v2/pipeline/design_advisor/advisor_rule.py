"""Abstract advisor rule base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .advice_result import AdviceResult


class BaseAdvisorRule(ABC):
    """Abstract base for AI design advisor rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def analyze(
        self,
        design_request: Any,
        building_model: Any,
        pipeline_result: Any,
    ) -> AdviceResult:
        raise NotImplementedError
