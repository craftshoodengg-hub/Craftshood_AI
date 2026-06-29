"""Shared DXF utility functions for Craftshood_AI.

This module provides common DXF entity operations used across the
geometry_engine and backend packages.
"""

from __future__ import annotations

from typing import Any

from ezdxf.entities import DXFEntity


def safe_dxf_value(entity: DXFEntity, name: str, default: Any = None) -> Any:
    """Safely read a DXF attribute value from an entity.

    Attempts to read the named attribute from the entity's DXF namespace.
    If the attribute does not exist, returns the default value instead
    of raising an AttributeError.

    Args:
        entity: A DXF entity object.
        name: The attribute name to read from the entity's DXF namespace.
        default: The value to return if the attribute is not found.

    Returns:
        The attribute value, or the default if the attribute is missing.
    """
    try:
        return getattr(entity.dxf, name)
    except AttributeError:
        return default
