"""Parser Rules for Craftshood AI.

Deterministic regex-based extraction helpers for architectural requirements.
No AI. No LLM. Pure pattern matching.
"""
from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple


def extract_plot_size(text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Extract plot dimensions from text."""
    text_lower = text.lower()
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:x|X|by|BY)\s*(\d+(?:\.\d+)?)(?:\s*(feet|ft|metres|meters|m|sqft|sqm))?",
        text_lower,
    )
    if match:
        return float(match.group(1)), float(match.group(2)), match.group(3)
    match = re.search(r"(\d+(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqm|sq\.?\s*m)", text_lower)
    if match:
        return None, None, float(match.group(1))
    return None, None, None


def extract_facing(text: str) -> Optional[str]:
    """Extract plot facing direction."""
    text_lower = text.lower()
    directions = [
        ("north-east", r"north[\s-]?east"),
        ("north-west", r"north[\s-]?west"),
        ("south-east", r"south[\s-]?east"),
        ("south-west", r"south[\s-]?west"),
        ("east", r"east"),
        ("west", r"west"),
        ("north", r"north"),
        ("south", r"south"),
    ]
    for direction, pattern in directions:
        if re.search(pattern, text_lower):
            return direction
    return None


def extract_bhk(text: str) -> Optional[int]:
    """Extract BHK count."""
    text_lower = text.lower()
    match = re.search(r"(\d+)\s*bhk", text_lower)
    if match:
        return int(match.group(1))
    return None


def extract_bedrooms(text: str) -> Optional[int]:
    """Extract bedroom count."""
    text_lower = text.lower()
    match = re.search(r"(\d+)\s*bed(?:room)?s?", text_lower)
    if match:
        return int(match.group(1))
    word_numbers = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    }
    for word, num in word_numbers.items():
        if re.search(rf"{word}\s*bed(?:room)?s?", text_lower):
            return num
    return None


def extract_bathrooms(text: str) -> Optional[int]:
    """Extract bathroom count."""
    text_lower = text.lower()
    match = re.search(r"(\d+)\s*bath(?:room)?s?", text_lower)
    if match:
        return int(match.group(1))
    return None


def extract_floors(text: str) -> Optional[int]:
    """Extract floor count."""
    text_lower = text.lower()
    match = re.search(r"g\+(\d+)", text_lower)
    if match:
        return int(match.group(1)) + 1
    match = re.search(r"(\d+)\s*(?:floor|storey|storeys|story|stories)", text_lower)
    if match:
        return int(match.group(1))
    word_numbers = {"single": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    for word, num in word_numbers.items():
        if re.search(rf"{word}\s*(?:floor|storey|story)", text_lower):
            return num
    if "duplex" in text_lower:
        return 2
    return None


def extract_building_type(text: str) -> Optional[str]:
    """Extract building type."""
    text_lower = text.lower()
    if "duplex" in text_lower:
        return "duplex"
    if "villa" in text_lower:
        return "villa"
    if "apartment" in text_lower or "flat" in text_lower:
        return "apartment"
    if "office" in text_lower or "commercial" in text_lower:
        return "commercial"
    if "residential" in text_lower or "house" in text_lower or "home" in text_lower:
        return "residential"
    return None


def extract_style(text: str) -> Optional[str]:
    """Extract architectural style."""
    text_lower = text.lower()
    styles = [
        "modern", "contemporary", "traditional", "minimalist",
        "luxury", "classic", "industrial", "mediterranean",
        "colonial", "vernacular",
    ]
    for style in styles:
        if style in text_lower:
            return style
    return None


def extract_boolean_features(text: str) -> Dict[str, bool]:
    """Extract boolean features from text."""
    text_lower = text.lower()
    features: Dict[str, bool] = {}
    if re.search(r"parking|car\s*port|garage|vehicle", text_lower):
        features["parking"] = True
    if re.search(r"pooja|puja|prayer|temple|worship", text_lower):
        features["pooja"] = True
    if re.search(r"office|work\s*from\s*home|study\s*room", text_lower):
        features["office"] = True
    if re.search(r"balcony|terrace|verandah|patio", text_lower):
        features["balcony"] = True
    if re.search(r"utility|laundry|washroom|servant\s*quarter", text_lower):
        features["utility"] = True
    if re.search(r"vastu|vaastu|vastu\s*shastra", text_lower):
        features["vastu"] = True
    if re.search(r"accessible|accessibility|wheelchair|ramp|elderly|senior", text_lower):
        features["accessibility"] = True
    return features


def extract_parking_count(text: str) -> Optional[int]:
    """Extract number of parking spaces."""
    text_lower = text.lower()
    match = re.search(r"(\d+)\s*(?:car|vehicle|parking)", text_lower)
    if match:
        return int(match.group(1))
    return None


def extract_budget(text: str) -> Tuple[Optional[float], Optional[str]]:
    """Extract budget information."""
    text_lower = text.lower()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|lacs)", text_lower)
    if match:
        return float(match.group(1)) * 100000, "INR"
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:crore|cr)", text_lower)
    if match:
        return float(match.group(1)) * 10000000, "INR"
    match = re.search(r"[\$\xe2\x82\xac\xc2\xa3]\s*(\d+(?:[,\d]*(?:\.\d+)?)?)", text)
    if match:
        amount = float(match.group(1).replace(",", ""))
        currency = "USD" if text[match.start():match.start()+1] == "$" else "EUR" if char == "\u20ac" else "GBP"
        return amount, currency
    match = re.search(r"(?:budget|cost|price|rs\.?)\s*:?\s*(\d+(?:[,\d]+)*(?:\.\d+)?)", text_lower)
    if match:
        return float(match.group(1).replace(",", "")), "INR"
    return None, None


def extract_priorities(text: str) -> List[str]:
    """Extract design priorities."""
    text_lower = text.lower()
    priority_keywords = [
        "spacious", "ventilated", "natural light", "vastu compliant",
        "eco-friendly", "energy efficient", "open concept", "privacy",
        "storage", "low maintenance", "budget-friendly",
    ]
    return [kw for kw in priority_keywords if kw in text_lower]
