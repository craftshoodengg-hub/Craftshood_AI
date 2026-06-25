from __future__ import annotations

from normalizer import (
    LayerCategory,
    LayerNormalizer,
    Normalizer,
    NormalizerConfig,
    RoomName,
    TextNormalizer,
    UnitNormalizer,
)


def test_layer_names_are_normalized_to_standard_categories() -> None:
    normalizer = LayerNormalizer()

    assert normalizer.normalize("A-WALL-EXT") == LayerCategory.WALL
    assert normalizer.normalize("door_opening") == LayerCategory.DOOR
    assert normalizer.normalize("DIMENSIONS") == LayerCategory.DIMENSION
    assert normalizer.normalize("not-a-known-layer") == LayerCategory.UNKNOWN


def test_layer_mappings_are_configurable() -> None:
    normalizer = LayerNormalizer({LayerCategory.COLUMN: ("struct pier",)})

    assert normalizer.normalize("STRUCT-PIER") == LayerCategory.COLUMN
    assert normalizer.normalize("A-WALL") == LayerCategory.UNKNOWN


def test_room_names_are_normalized() -> None:
    normalizer = TextNormalizer()

    assert normalizer.normalize_room_name("MASTER BEDROOM") == RoomName.MASTER_BED_ROOM
    assert normalizer.normalize_room_name("bed-room") == RoomName.BED_ROOM
    assert normalizer.normalize_room_name("SIT OUT") == RoomName.SITOUT
    assert normalizer.normalize_room_name("garage") is None


def test_room_mappings_are_configurable() -> None:
    normalizer = TextNormalizer({"Living": ("family lounge",)})

    assert normalizer.normalize_room_name("Family Lounge") == RoomName.LIVING
    assert normalizer.normalize_room_name("living") is None


def test_dimension_strings_are_normalized_to_decimal_feet() -> None:
    normalizer = UnitNormalizer(precision=3)

    assert normalizer.normalize_dimension("10'-6\"").feet == 10.5
    assert normalizer.normalize_dimension("126 in").feet == 10.5
    assert normalizer.normalize_dimension("3.048 m").feet == 10.0
    assert normalizer.normalize_dimension("3000 mm").feet == 9.843


def test_dimension_lists_are_normalized() -> None:
    normalizer = UnitNormalizer(precision=2)

    dimensions = normalizer.normalize_dimensions("12 x 10'-6\"")

    assert [dimension.feet for dimension in dimensions] == [12.0, 10.5]


def test_facade_adds_normalized_fields_without_mutating_source_record() -> None:
    normalizer = Normalizer()
    source = {
        "layer": "A-WALL",
        "text": "Kitchen",
        "dimension": "10 ft",
        "x": 25.0,
        "y": 15.0,
    }

    result = normalizer.normalize_record(source)

    assert result == {
        "layer": "A-WALL",
        "text": "Kitchen",
        "dimension": "10 ft",
        "x": 25.0,
        "y": 15.0,
        "layer_category": "WALL",
        "room_name_normalized": "Kitchen",
        "dimension_feet": 10.0,
    }
    assert source == {
        "layer": "A-WALL",
        "text": "Kitchen",
        "dimension": "10 ft",
        "x": 25.0,
        "y": 15.0,
    }


def test_facade_uses_configurable_mappings() -> None:
    normalizer = Normalizer(
        NormalizerConfig(
            layer_mappings={LayerCategory.STAIR: ("vertical circulation",)},
            room_mappings={RoomName.PORTICO: ("entry porch",)},
        )
    )

    result = normalizer.normalize_record(
        {"layer": "vertical-circulation", "text": "Entry Porch"}
    )

    assert result["layer_category"] == "STAIR"
    assert result["room_name_normalized"] == "Portico"
