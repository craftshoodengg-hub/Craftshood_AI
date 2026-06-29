"""Shared normalization utilities for Craftshood_AI.

This module provides common string normalization functions used across
the normalizer and zoning packages.
"""

from __future__ import annotations

import re


def normalize_key(value: str | None) -> str:
    """Normalize a human/CAD label into a comparable lowercase key.

    Converts the input to lowercase, replaces common separators with spaces,
    removes non-alphanumeric characters, and collapses whitespace.

    Args:
        value: The string to normalize. None is treated as empty string.

    Returns:
        A normalized lowercase key suitable for comparison.

    Examples:
        >>> normalize_key("A-WALL")
        'a wall'
        >>> normalize_key("Living_Room")
        'living room'
        >>> normalize_key(None)
        ''
    """
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[_./\\-]+", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())
