"""Unit tests for Vastu models, enums, rules, and metadata.

Covers VastuDirection, VastuZone, VastuRule, VastuMetadata, documentation examples,
and various edge cases with deterministic checks.
"""
from __future__ import annotations

import pytest
from typing import Any, Dict
from dataclasses import FrozenInstanceError

from building_model_v2.vastu.vastu_direction import VastuDirection
from building_model_v2.vastu.vastu_zone import VastuZone
from building_model_v2.vastu.vastu_rule import VastuRule
from building_model_v2.vastu.vastu_metadata import VastuMetadata
from building_model_v2.constraints.constraint_severity import ConstraintSeverity


# ==============================================================================
# VASTU DIRECTION TESTS (1-12)
# ==============================================================================


def test_direction_enum_values() -> None:
    """1. Verify all expected VastuDirection enum members exist."""
    expected_members = {
        "NORTH", "NORTH_EAST", "EAST", "SOUTH_EAST",
        "SOUTH", "SOUTH_WEST", "WEST", "NORTH_WEST", "CENTER"
    }
    actual_members = {d.name for d in VastuDirection}
    assert actual_members == expected_members


def test_direction_display_names() -> None:
    """2. Verify display name for all VastuDirection members."""
    assert VastuDirection.NORTH.display_name == "North"
    assert VastuDirection.NORTH_EAST.display_name == "North-East"
    assert VastuDirection.EAST.display_name == "East"
    assert VastuDirection.SOUTH_EAST.display_name == "South-East"
    assert VastuDirection.SOUTH.display_name == "South"
    assert VastuDirection.SOUTH_WEST.display_name == "South-West"
    assert VastuDirection.WEST.display_name == "West"
    assert VastuDirection.NORTH_WEST.display_name == "North-West"
    assert VastuDirection.CENTER.display_name == "Center"


def test_direction_angles() -> None:
    """3. Verify angle values in degrees clockwise from true north."""
    assert VastuDirection.NORTH.angle == 0.0
    assert VastuDirection.NORTH_EAST.angle == 45.0
    assert VastuDirection.EAST.angle == 90.0
    assert VastuDirection.SOUTH_EAST.angle == 135.0
    assert VastuDirection.SOUTH.angle == 180.0
    assert VastuDirection.SOUTH_WEST.angle == 225.0
    assert VastuDirection.WEST.angle == 270.0
    assert VastuDirection.NORTH_WEST.angle == 315.0
    assert VastuDirection.CENTER.angle == 0.0


def test_direction_from_angle_exact() -> None:
    """4. Verify from_angle with exact cardinal and intercardinal angles."""
    assert VastuDirection.from_angle(0.0) == VastuDirection.NORTH
    assert VastuDirection.from_angle(45.0) == VastuDirection.NORTH_EAST
    assert VastuDirection.from_angle(90.0) == VastuDirection.EAST
    assert VastuDirection.from_angle(135.0) == VastuDirection.SOUTH_EAST
    assert VastuDirection.from_angle(180.0) == VastuDirection.SOUTH
    assert VastuDirection.from_angle(225.0) == VastuDirection.SOUTH_WEST
    assert VastuDirection.from_angle(270.0) == VastuDirection.WEST
    assert VastuDirection.from_angle(315.0) == VastuDirection.NORTH_WEST


def test_direction_from_angle_boundaries() -> None:
    """5. Verify boundary thresholds (+/- 22.5 degrees) for from_angle."""
    # North covers [337.5, 360) and [0, 22.5)
    assert VastuDirection.from_angle(22.4) == VastuDirection.NORTH
    assert VastuDirection.from_angle(22.5) == VastuDirection.NORTH_EAST
    assert VastuDirection.from_angle(67.4) == VastuDirection.NORTH_EAST
    assert VastuDirection.from_angle(67.5) == VastuDirection.EAST
    assert VastuDirection.from_angle(112.4) == VastuDirection.EAST
    assert VastuDirection.from_angle(112.5) == VastuDirection.SOUTH_EAST
    assert VastuDirection.from_angle(157.4) == VastuDirection.SOUTH_EAST
    assert VastuDirection.from_angle(157.5) == VastuDirection.SOUTH
    assert VastuDirection.from_angle(202.4) == VastuDirection.SOUTH
    assert VastuDirection.from_angle(202.5) == VastuDirection.SOUTH_WEST
    assert VastuDirection.from_angle(247.4) == VastuDirection.SOUTH_WEST
    assert VastuDirection.from_angle(247.5) == VastuDirection.WEST
    assert VastuDirection.from_angle(292.4) == VastuDirection.WEST
    assert VastuDirection.from_angle(292.5) == VastuDirection.NORTH_WEST
    assert VastuDirection.from_angle(337.4) == VastuDirection.NORTH_WEST
    assert VastuDirection.from_angle(337.5) == VastuDirection.NORTH


def test_direction_from_angle_wraparound() -> None:
    """6. Verify wraparound (angle >= 360) in from_angle."""
    assert VastuDirection.from_angle(360.0) == VastuDirection.NORTH
    assert VastuDirection.from_angle(405.0) == VastuDirection.NORTH_EAST
    assert VastuDirection.from_angle(450.0) == VastuDirection.EAST
    assert VastuDirection.from_angle(720.0) == VastuDirection.NORTH
    assert VastuDirection.from_angle(765.0) == VastuDirection.NORTH_EAST


def test_direction_from_angle_negative() -> None:
    """7. Verify negative angle handling in from_angle."""
    assert VastuDirection.from_angle(-0.0) == VastuDirection.NORTH
    assert VastuDirection.from_angle(-22.4) == VastuDirection.NORTH
    assert VastuDirection.from_angle(-22.5) == VastuDirection.NORTH
    assert VastuDirection.from_angle(-45.0) == VastuDirection.NORTH_WEST
    assert VastuDirection.from_angle(-90.0) == VastuDirection.WEST
    assert VastuDirection.from_angle(-180.0) == VastuDirection.SOUTH
    assert VastuDirection.from_angle(-360.0) == VastuDirection.NORTH


def test_direction_to_dict() -> None:
    """8. Verify to_dict for all VastuDirection members."""
    d = VastuDirection.NORTH.to_dict()
    assert d == {"name": "NORTH", "display_name": "North", "angle": 0.0}
    d = VastuDirection.SOUTH_EAST.to_dict()
    assert d == {"name": "SOUTH_EAST", "display_name": "South-East", "angle": 135.0}


def test_direction_from_dict() -> None:
    """9. Verify from_dict round-trip for VastuDirection."""
    for direction in VastuDirection:
        data = direction.to_dict()
        result = VastuDirection.from_dict(data)
        assert result == direction


def test_direction_string_representations() -> None:
    """10. Verify string and repr for VastuDirection."""
    assert str(VastuDirection.NORTH) == "North"
    assert repr(VastuDirection.NORTH) == "VastuDirection.NORTH"
    assert str(VastuDirection.SOUTH_WEST) == "South-West"
    assert repr(VastuDirection.SOUTH_WEST) == "VastuDirection.SOUTH_WEST"


def test_direction_members_are_distinct() -> None:
    """11. Verify all VastuDirection members have distinct names and angles."""
    names = [d.name for d in VastuDirection]
    display_names = [d.display_name for d in VastuDirection]
    angles = [d.angle for d in VastuDirection]
    assert len(names) == len(set(names))
    assert len(display_names) == len(set(display_names))
    non_center_angles = [a for d, a in zip(VastuDirection, angles) if d != VastuDirection.CENTER]
    assert len(non_center_angles) == len(set(non_center_angles))


def test_direction_from_angle_center_not_returned() -> None:
    """12. Verify from_angle never returns CENTER."""
    for angle in range(0, 360, 5):
        result = VastuDirection.from_angle(float(angle))
        assert result != VastuDirection.CENTER


# ==============================================================================
# VASTU ZONE TESTS (13-24)
# ==============================================================================


def test_zone_enum_values() -> None:
    """13. Verify all expected VastuZone enum members exist."""
    expected_members = {
        "BRAHMASTHAN", "ISHANYA", "AGNEYA", "NAIRUTYA",
        "VAYAVYA", "NORTH", "SOUTH", "EAST", "WEST"
    }
    actual_members = {z.name for z in VastuZone}
    assert actual_members == expected_members


def test_zone_display_names() -> None:
    """14. Verify display names for all VastuZone members."""
    assert VastuZone.BRAHMASTHAN.display_name == "Brahmasthan (Center)"
    assert VastuZone.ISHANYA.display_name == "Ishanya (North-East)"
    assert VastuZone.AGNEYA.display_name == "Agneya (South-East)"
    assert VastuZone.NAIRUTYA.display_name == "Nairutya (South-West)"
    assert VastuZone.VAYAVYA.display_name == "Vayavya (North-West)"
    assert VastuZone.NORTH.display_name == "North (Kuber)"
    assert VastuZone.SOUTH.display_name == "South (Yamya)"
    assert VastuZone.EAST.display_name == "East (Indra)"
    assert VastuZone.WEST.display_name == "West (Varun)"


def test_zone_elements() -> None:
    """15. Verify element associations for all VastuZone members."""
    assert VastuZone.BRAHMASTHAN.element == "Space (Akasha)"
    assert VastuZone.ISHANYA.element == "Water (Jal)"
    assert VastuZone.AGNEYA.element == "Fire (Agni)"
    assert VastuZone.NAIRUTYA.element == "Earth (Prithvi)"
    assert VastuZone.VAYAVYA.element == "Air (Vayu)"
    assert VastuZone.NORTH.element == "Water (Jal)"
    assert VastuZone.SOUTH.element == "Earth (Prithvi)"
    assert VastuZone.EAST.element == "Fire (Agni)"
    assert VastuZone.WEST.element == "Air (Vayu)"


def test_zone_primary_directions() -> None:
    """16. Verify primary direction mapping for all VastuZone members."""
    assert VastuZone.BRAHMASTHAN.primary_direction is None
    assert VastuZone.ISHANYA.primary_direction == VastuDirection.NORTH_EAST
    assert VastuZone.AGNEYA.primary_direction == VastuDirection.SOUTH_EAST
    assert VastuZone.NAIRUTYA.primary_direction == VastuDirection.SOUTH_WEST
    assert VastuZone.VAYAVYA.primary_direction == VastuDirection.NORTH_WEST
    assert VastuZone.NORTH.primary_direction == VastuDirection.NORTH
    assert VastuZone.SOUTH.primary_direction == VastuDirection.SOUTH
    assert VastuZone.EAST.primary_direction == VastuDirection.EAST
    assert VastuZone.WEST.primary_direction == VastuDirection.WEST


def test_zone_is_corner() -> None:
    """17. Verify is_corner property for all VastuZone members."""
    assert VastuZone.ISHANYA.is_corner is True
    assert VastuZone.AGNEYA.is_corner is True
    assert VastuZone.NAIRUTYA.is_corner is True
    assert VastuZone.VAYAVYA.is_corner is True
    assert VastuZone.BRAHMASTHAN.is_corner is False
    assert VastuZone.NORTH.is_corner is False
    assert VastuZone.SOUTH.is_corner is False
    assert VastuZone.EAST.is_corner is False
    assert VastuZone.WEST.is_corner is False


def test_zone_is_cardinal() -> None:
    """18. Verify is_cardinal property for all VastuZone members."""
    assert VastuZone.NORTH.is_cardinal is True
    assert VastuZone.SOUTH.is_cardinal is True
    assert VastuZone.EAST.is_cardinal is True
    assert VastuZone.WEST.is_cardinal is True
    assert VastuZone.BRAHMASTHAN.is_cardinal is False
    assert VastuZone.ISHANYA.is_cardinal is False
    assert VastuZone.AGNEYA.is_cardinal is False
    assert VastuZone.NAIRUTYA.is_cardinal is False
    assert VastuZone.VAYAVYA.is_cardinal is False


def test_zone_is_center() -> None:
    """19. Verify is_center property for all VastuZone members."""
    assert VastuZone.BRAHMASTHAN.is_center is True
    assert VastuZone.ISHANYA.is_center is False
    assert VastuZone.AGNEYA.is_center is False
    assert VastuZone.NAIRUTYA.is_center is False
    assert VastuZone.VAYAVYA.is_center is False
    assert VastuZone.NORTH.is_center is False
    assert VastuZone.SOUTH.is_center is False
    assert VastuZone.EAST.is_center is False
    assert VastuZone.WEST.is_center is False


def test_zone_get_adjacent_zones() -> None:
    """20. Verify get_adjacent_zones returns correct neighbors."""
    ishanya_adj = VastuZone.ISHANYA.get_adjacent_zones()
    assert VastuZone.BRAHMASTHAN in ishanya_adj
    assert VastuZone.NORTH in ishanya_adj
    assert VastuZone.EAST in ishanya_adj
    assert VastuZone.ISHANYA not in ishanya_adj

    brahmasthan_adj = VastuZone.BRAHMASTHAN.get_adjacent_zones()
    assert VastuZone.BRAHMASTHAN not in brahmasthan_adj
    assert len(brahmasthan_adj) == 8


def test_zone_get_adjacent_unique() -> None:
    """21. Verify no duplicate zones in adjacency lists."""
    for zone in VastuZone:
        adj = zone.get_adjacent_zones()
        assert len(adj) == len(set(adj))


def test_zone_get_corners() -> None:
    """22. Verify get_corners returns only corner zones."""
    corners = VastuZone.get_corners()
    assert VastuZone.ISHANYA in corners
    assert VastuZone.AGNEYA in corners
    assert VastuZone.NAIRUTYA in corners
    assert VastuZone.VAYAVYA in corners
    assert VastuZone.BRAHMASTHAN not in corners
    assert VastuZone.NORTH not in corners
    assert len(corners) == 4


def test_zone_get_cardinals() -> None:
    """23. Verify get_cardinals returns only cardinal zones."""
    cardinals = VastuZone.get_cardinals()
    assert VastuZone.NORTH in cardinals
    assert VastuZone.SOUTH in cardinals
    assert VastuZone.EAST in cardinals
    assert VastuZone.WEST in cardinals
    assert VastuZone.BRAHMASTHAN not in cardinals
    assert VastuZone.ISHANYA not in cardinals
    assert len(cardinals) == 4


def test_zone_to_dict() -> None:
    """24. Verify to_dict round-trip for all VastuZone members."""
    for zone in VastuZone:
        data = zone.to_dict()
        result = VastuZone.from_dict(data)
        assert result == zone


# ==============================================================================
# VASTU RULE TESTS (25-36)
# ==============================================================================


def test_rule_create_minimal() -> None:
    """25. Verify creation of VastuRule with minimal attributes."""
    rule = VastuRule(id="test_01", name="Test Rule")
    assert rule.id == "test_01"
    assert rule.name == "Test Rule"
    assert rule.description == ""
    assert rule.preferred_zone is None
    assert rule.allowed_zones == ()
    assert rule.enabled is True
    assert rule.metadata == {}


def test_rule_create_full() -> None:
    """26. Verify creation of VastuRule with full attributes."""
    rule = VastuRule(
        id="kitchen_01",
        name="Kitchen in South-East",
        description="Kitchen should be in the South-East zone (Agneya).",
        preferred_zone=VastuZone.AGNEYA,
        allowed_zones=(VastuZone.EAST, VastuZone.NORTH),
        severity=ConstraintSeverity.WARNING,
        enabled=True,
        metadata={"source": "Vastu Shastra"},
    )
    assert rule.id == "kitchen_01"
    assert rule.preferred_zone == VastuZone.AGNEYA
    assert VastuZone.EAST in rule.allowed_zones
    assert rule.severity == ConstraintSeverity.WARNING


def test_rule_is_zone_allowed_preferred() -> None:
    """27. Verify is_zone_allowed returns True for preferred zone."""
    rule = VastuRule(
        id="test_01",
        name="Test Rule",
        preferred_zone=VastuZone.ISHANYA,
        allowed_zones=(VastuZone.NORTH, VastuZone.EAST),
    )
    assert rule.is_zone_allowed(VastuZone.ISHANYA) is True


def test_rule_is_zone_allowed_allowed_list() -> None:
    """28. Verify is_zone_allowed returns True for zones in allowed list."""
    rule = VastuRule(
        id="test_01",
        name="Test Rule",
        preferred_zone=VastuZone.ISHANYA,
        allowed_zones=(VastuZone.NORTH, VastuZone.EAST),
    )
    assert rule.is_zone_allowed(VastuZone.NORTH) is True
    assert rule.is_zone_allowed(VastuZone.EAST) is True


def test_rule_is_zone_allowed_false() -> None:
    """29. Verify is_zone_allowed returns False for disallowed zones."""
    rule = VastuRule(
        id="test_01",
        name="Test Rule",
        preferred_zone=VastuZone.ISHANYA,
        allowed_zones=(VastuZone.NORTH, VastuZone.EAST),
    )
    assert rule.is_zone_allowed(VastuZone.SOUTH) is False
    assert rule.is_zone_allowed(VastuZone.WEST) is False
    assert rule.is_zone_allowed(VastuZone.BRAHMASTHAN) is False


def test_rule_is_zone_preferred() -> None:
    """30. Verify is_zone_preferred returns True only for preferred zone."""
    rule = VastuRule(
        id="test_01",
        name="Test Rule",
        preferred_zone=VastuZone.ISHANYA,
        allowed_zones=(VastuZone.NORTH, VastuZone.EAST),
    )
    assert rule.is_zone_preferred(VastuZone.ISHANYA) is True
    assert rule.is_zone_preferred(VastuZone.NORTH) is False
    assert rule.is_zone_preferred(VastuZone.EAST) is False
    assert rule.is_zone_preferred(VastuZone.SOUTH) is False


def test_rule_is_zone_preferred_none() -> None:
    """31. Verify is_zone_preferred returns False when preferred_zone is None."""
    rule = VastuRule(id="test_01", name="Test Rule")
    assert rule.is_zone_preferred(VastuZone.NORTH) is False


def test_rule_immutability() -> None:
    """32. Verify VastuRule is immutable (frozen dataclass)."""
    rule = VastuRule(id="test_01", name="Test Rule")
    with pytest.raises(FrozenInstanceError):
        rule.name = "Modified"  # type: ignore[misc]


def test_rule_equality() -> None:
    """33. Verify VastuRule equality."""
    rule1 = VastuRule(
        id="equal_01",
        name="Equal Rule",
        preferred_zone=VastuZone.AGNEYA,
        allowed_zones=(VastuZone.EAST, VastuZone.SOUTH),
        description="Same description",
    )
    rule2 = VastuRule(
        id="equal_01",
        name="Equal Rule",
        preferred_zone=VastuZone.AGNEYA,
        allowed_zones=(VastuZone.EAST, VastuZone.SOUTH),
        description="Different description",
    )
    assert rule1 == rule2
    assert hash(rule1) == hash(rule2)


def test_rule_inequality() -> None:
    """34. Verify VastuRule inequality when fields differ."""
    rule1 = VastuRule(id="a", name="A")
    rule2 = VastuRule(id="b", name="B")
    assert rule1 != rule2
    assert hash(rule1) != hash(rule2)


def test_rule_to_dict() -> None:
    """35. Verify to_dict for VastuRule with full fields."""
    rule = VastuRule(
        id="kitchen_01",
        name="Kitchen in South-East",
        description="Kitchen should be in the South-East zone (Agneya).",
        preferred_zone=VastuZone.AGNEYA,
        allowed_zones=(VastuZone.EAST, VastuZone.NORTH),
        severity=ConstraintSeverity.WARNING,
        enabled=True,
        metadata={"source": "Vastu Shastra"},
    )
    data = rule.to_dict()
    assert data["id"] == "kitchen_01"
    assert data["preferred_zone"] == "AGNEYA"
    assert "EAST" in data["allowed_zones"]
    assert "NORTH" in data["allowed_zones"]
    assert data["enabled"] is True
    assert data["metadata"]["source"] == "Vastu Shastra"


def test_rule_from_dict() -> None:
    """36. Verify from_dict round-trip for VastuRule."""
    original = VastuRule(
        id="kitchen_01",
        name="Kitchen in South-East",
        description="Kitchen should be in the South-East zone.",
        preferred_zone=VastuZone.AGNEYA,
        allowed_zones=(VastuZone.EAST, VastuZone.NORTH),
        severity=ConstraintSeverity.WARNING,
        enabled=True,
        metadata={"source": "Vastu Shastra"},
    )
    data = original.to_dict()
    reconstructed = VastuRule.from_dict(data)
    assert reconstructed == original
    assert reconstructed.description == original.description
    assert reconstructed.severity == original.severity


# ==============================================================================
# VASTU METADATA TESTS (37-52)
# ==============================================================================


def test_metadata_defaults() -> None:
    """37. Verify VastuMetadata default values."""
    meta = VastuMetadata()
    assert meta.entrance_direction is None
    assert meta.kitchen_direction is None
    assert meta.master_bedroom_direction is None
    assert meta.north_rotation == 0.0
    assert meta.custom_directions == {}


def test_metadata_create_all_fields() -> None:
    """38. Verify creation of VastuMetadata with all standard fields."""
    meta = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
        pooja_direction=VastuDirection.NORTH_EAST,
        staircase_direction=VastuDirection.WEST,
        toilet_direction=VastuDirection.NORTH_WEST,
        water_tank_direction=VastuDirection.NORTH_EAST,
        septic_direction=VastuDirection.SOUTH,
        plot_facing=VastuDirection.NORTH,
        north_rotation=15.0,
        custom_directions={"backyard": VastuDirection.WEST},
    )
    assert meta.entrance_direction == VastuDirection.NORTH
    assert meta.kitchen_direction == VastuDirection.SOUTH_EAST
    assert meta.master_bedroom_direction == VastuDirection.SOUTH_WEST
    assert meta.pooja_direction == VastuDirection.NORTH_EAST
    assert meta.staircase_direction == VastuDirection.WEST
    assert meta.toilet_direction == VastuDirection.NORTH_WEST
    assert meta.water_tank_direction == VastuDirection.NORTH_EAST
    assert meta.septic_direction == VastuDirection.SOUTH
    assert meta.plot_facing == VastuDirection.NORTH
    assert meta.north_rotation == 15.0
    assert meta.custom_directions["backyard"] == VastuDirection.WEST


def test_metadata_get_direction_standard() -> None:
    """39. Verify get_direction with standard keys."""
    meta = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
    )
    assert meta.get_direction("entrance") == VastuDirection.NORTH
    assert meta.get_direction("kitchen") == VastuDirection.SOUTH_EAST
    assert meta.get_direction("master_bedroom") == VastuDirection.SOUTH_WEST


def test_metadata_get_direction_custom() -> None:
    """40. Verify get_direction with custom keys."""
    meta = VastuMetadata(
        custom_directions={"backyard": VastuDirection.WEST, "garage": VastuDirection.NORTH},
    )
    assert meta.get_direction("backyard") == VastuDirection.WEST
    assert meta.get_direction("garage") == VastuDirection.NORTH


def test_metadata_get_direction_none() -> None:
    """41. Verify get_direction returns None for missing keys."""
    meta = VastuMetadata(entrance_direction=VastuDirection.NORTH)
    assert meta.get_direction("kitchen") is None
    assert meta.get_direction("nonexistent") is None


def test_metadata_get_direction_overrides_custom() -> None:
    """42. Verify standard keys override custom keys."""
    meta = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        custom_directions={"entrance": VastuDirection.SOUTH},
    )
    assert meta.get_direction("entrance") == VastuDirection.NORTH


def test_metadata_partial_fields() -> None:
    """43. Verify VastuMetadata with partially filled fields."""
    meta = VastuMetadata(
        entrance_direction=VastuDirection.EAST,
        north_rotation=30.0,
    )
    assert meta.entrance_direction == VastuDirection.EAST
    assert meta.north_rotation == 30.0
    assert meta.kitchen_direction is None
    assert meta.master_bedroom_direction is None
    assert meta.custom_directions == {}


def test_metadata_with_plot_facing() -> None:
    """44. Verify VastuMetadata with plot_facing set."""
    meta = VastuMetadata(plot_facing=VastuDirection.NORTH)
    assert meta.plot_facing == VastuDirection.NORTH
    assert meta.get_direction("plot_facing") == VastuDirection.NORTH


def test_metadata_empty_custom_directions() -> None:
    """45. Verify empty custom_directions defaults to empty dict."""
    meta = VastuMetadata()
    assert meta.custom_directions == {}


def test_metadata_north_rotation_default() -> None:
    """46. Verify north_rotation defaults to 0.0."""
    meta = VastuMetadata()
    assert meta.north_rotation == 0.0


def test_metadata_north_rotation_negative() -> None:
    """47. Verify north_rotation accepts negative values."""
    meta = VastuMetadata(north_rotation=-45.0)
    assert meta.north_rotation == -45.0


def test_metadata_to_dict() -> None:
    """48. Verify to_dict serialization for VastuMetadata."""
    meta = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        north_rotation=15.0,
        custom_directions={"backyard": VastuDirection.WEST},
    )
    expected = {
        "entrance_direction": "NORTH",
        "kitchen_direction": "SOUTH_EAST",
        "master_bedroom_direction": None,
        "pooja_direction": None,
        "staircase_direction": None,
        "toilet_direction": None,
        "water_tank_direction": None,
        "septic_direction": None,
        "plot_facing": None,
        "north_rotation": 15.0,
        "custom_directions": {"backyard": "WEST"},
    }
    assert meta.to_dict() == expected


def test_metadata_from_dict() -> None:
    """49. Verify deserialization from dictionary of VastuMetadata."""
    data = {
        "entrance_direction": "NORTH",
        "kitchen_direction": "SOUTH_EAST",
        "master_bedroom_direction": None,
        "pooja_direction": "NORTH_EAST",
        "staircase_direction": None,
        "toilet_direction": None,
        "water_tank_direction": None,
        "septic_direction": None,
        "plot_facing": None,
        "north_rotation": 15.0,
        "custom_directions": {"backyard": "WEST"},
    }
    meta = VastuMetadata.from_dict(data)
    assert meta.entrance_direction == VastuDirection.NORTH
    assert meta.kitchen_direction == VastuDirection.SOUTH_EAST
    assert meta.pooja_direction == VastuDirection.NORTH_EAST
    assert meta.master_bedroom_direction is None
    assert meta.north_rotation == 15.0
    assert meta.custom_directions == {"backyard": VastuDirection.WEST}


def test_metadata_round_trip() -> None:
    """50. Verify serialization round-trip for VastuMetadata."""
    original = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
        north_rotation=45.0,
    )
    serialized = original.to_dict()
    reconstructed = VastuMetadata.from_dict(serialized)
    assert reconstructed == original


def test_metadata_equality_and_hashing() -> None:
    """51. Verify equality and hash for VastuMetadata."""
    meta1 = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
        north_rotation=10.0,
    )
    meta2 = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
        north_rotation=10.0,
    )
    assert meta1 == meta2
    assert hash(meta1) == hash(meta2)

    meta_diff_rot = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
        north_rotation=15.0,
    )
    assert meta1 != meta_diff_rot
    assert hash(meta1) != hash(meta_diff_rot)

    meta_diff_nonkey = VastuMetadata(
        entrance_direction=VastuDirection.NORTH,
        kitchen_direction=VastuDirection.SOUTH_EAST,
        master_bedroom_direction=VastuDirection.SOUTH_WEST,
        north_rotation=10.0,
        pooja_direction=VastuDirection.NORTH_EAST,
        custom_directions={"extra": VastuDirection.EAST},
    )
    assert meta1 == meta_diff_nonkey
    assert hash(meta1) == hash(meta_diff_nonkey)


def test_metadata_immutability() -> None:
    """52. Verify VastuMetadata is immutable (frozen dataclass)."""
    meta = VastuMetadata()
    with pytest.raises(FrozenInstanceError):
        meta.north_rotation = 90.0  # type: ignore[misc]
