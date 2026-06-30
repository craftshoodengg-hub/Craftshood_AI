"""Basic Vastu analysis domain models."""
from __future__ import annotations

from .vastu_result import VastuResult
from .vastu_rule import BaseVastuRule

__all__ = [
    "VastuResult",
    "BaseVastuRule",
]
