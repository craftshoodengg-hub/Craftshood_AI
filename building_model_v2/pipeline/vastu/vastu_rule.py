"""Base class for Vastu analysis rules."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..design_request import DesignRequest
from .vastu_result import VastuResult


class BaseVastuRule(ABC):
    """Abstract base for Vastu rule implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def analyze(self, design_request: DesignRequest) -> VastuResult:
        raise NotImplementedError
