"""Dimension and unit normalization."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class Dimension:
    """A scalar dimension normalized into decimal feet."""

    raw: str
    feet: float


class UnitNormalizer:
    """Normalize extracted dimension strings into decimal feet.

    The parser handles common architectural notations such as ``10'-6"``,
    ``10 ft 6 in``, ``126 in``, ``3.048 m``, and bare numeric values. Bare
    numeric values are interpreted using ``default_unit``.
    """

    _FEET_INCH_PATTERN = re.compile(
        r"^\s*(?P<feet>-?\d+(?:\.\d+)?)\s*(?:'|ft|feet)\s*"
        r"(?:-\s*)?(?:(?P<inches>\d+(?:\.\d+)?)\s*(?:\"|in|inch|inches)?)?\s*$",
        re.IGNORECASE,
    )
    _NUMBER_UNIT_PATTERN = re.compile(
        r"^\s*(?P<number>-?\d+(?:\.\d+)?)\s*(?P<unit>mm|millimeter|millimeters|"
        r"cm|centimeter|centimeters|m|meter|meters|in|inch|inches|"
        r"ft|feet|foot|')?\s*$",
        re.IGNORECASE,
    )
    _DIMENSION_SPLIT_PATTERN = re.compile(r"\s*(?:x|by|,|;)\s*", re.IGNORECASE)

    _UNIT_TO_FEET: dict[str, Decimal] = {
        "ft": Decimal("1"),
        "feet": Decimal("1"),
        "foot": Decimal("1"),
        "'": Decimal("1"),
        "in": Decimal("0.08333333333333333333333333333"),
        "inch": Decimal("0.08333333333333333333333333333"),
        "inches": Decimal("0.08333333333333333333333333333"),
        "mm": Decimal("0.003280839895013123359580052493"),
        "millimeter": Decimal("0.003280839895013123359580052493"),
        "millimeters": Decimal("0.003280839895013123359580052493"),
        "cm": Decimal("0.03280839895013123359580052493"),
        "centimeter": Decimal("0.03280839895013123359580052493"),
        "centimeters": Decimal("0.03280839895013123359580052493"),
        "m": Decimal("3.280839895013123359580052493"),
        "meter": Decimal("3.280839895013123359580052493"),
        "meters": Decimal("3.280839895013123359580052493"),
    }

    def __init__(self, *, default_unit: str = "ft", precision: int = 4) -> None:
        if default_unit.lower() not in self._UNIT_TO_FEET:
            raise ValueError(f"Unsupported default unit: {default_unit!r}")
        if precision < 0:
            raise ValueError("precision must be greater than or equal to zero")
        self.default_unit = default_unit.lower()
        self.precision = precision

    def normalize_dimension(self, value: str | int | float | Decimal | None) -> Dimension | None:
        """Parse a single dimension and return decimal feet."""

        if value is None:
            return None

        raw = str(value).strip()
        if not raw:
            return None

        feet = self._parse_feet(raw)
        if feet is None:
            return None
        return Dimension(raw=raw, feet=round(float(feet), self.precision))

    def normalize_dimensions(
        self,
        value: str | int | float | Decimal | None,
    ) -> tuple[Dimension, ...]:
        """Parse one or more extracted dimensions into decimal feet."""

        if value is None:
            return ()
        raw = str(value).strip()
        if not raw:
            return ()

        parts = [part for part in self._DIMENSION_SPLIT_PATTERN.split(raw) if part.strip()]
        return tuple(
            dimension
            for part in parts
            if (dimension := self.normalize_dimension(part)) is not None
        )

    def _parse_feet(self, raw: str) -> Decimal | None:
        if match := self._FEET_INCH_PATTERN.match(raw):
            feet = _to_decimal(match.group("feet"))
            inches = _to_decimal(match.group("inches") or "0")
            if feet is None or inches is None:
                return None
            sign = Decimal("-1") if feet < 0 else Decimal("1")
            return feet + sign * inches * self._UNIT_TO_FEET["in"]

        if match := self._NUMBER_UNIT_PATTERN.match(raw):
            number = _to_decimal(match.group("number"))
            if number is None:
                return None
            unit = (match.group("unit") or self.default_unit).lower()
            return number * self._UNIT_TO_FEET[unit]

        return None


def _to_decimal(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None
