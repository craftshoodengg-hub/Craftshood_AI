"""Base constraint abstraction for the pipeline constraint framework."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..design_request import DesignRequest
from .constraint_result import ConstraintResult


class BaseConstraint(ABC):
    """Abstract base class for architecture constraint checks."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate(self, design_request: DesignRequest) -> ConstraintResult:
        raise NotImplementedError
