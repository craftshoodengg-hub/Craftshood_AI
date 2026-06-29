"""Space Program Generator for Craftshood AI.

Deterministic conversion of DesignRequirements into a complete SpaceProgram.
No AI. No mutation. Pure deterministic architectural programming.
"""
from __future__ import annotations
from typing import Any, Dict, FrozenSet, Optional, Tuple

from ..ai.design_requirements import BuildingRequirements, DesignRequirements
from ..ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from ..ai.space_program import SpaceProgram

DEFAULT_ROOM_AREAS: Dict[str, float] = {
    "living": 180.0, "dining": 120.0, "kitchen": 140.0,
    "bedroom": 140.0, "master_bedroom": 180.0, "bathroom": 45.0,
    "common_bathroom": 45.0, "pooja": 40.0, "office": 100.0,
    "parking": 220.0, "utility": 50.0, "stair": 90.0,
    "balcony": 60.0, "entrance": 40.0, "corridor": 60.0, "store": 30.0,
}

MINIMUM_AREA_FACTOR = 0.7
MAXIMUM_AREA_FACTOR = 1.5
CIRCULATION_FACTOR = 0.15

ROOM_PRIVACY: Dict[str, PrivacyLevel] = {
    "living": PrivacyLevel.PUBLIC, "dining": PrivacyLevel.PUBLIC,
    "kitchen": PrivacyLevel.SEMI_PRIVATE, "bedroom": PrivacyLevel.PRIVATE,
    "master_bedroom": PrivacyLevel.PRIVATE, "bathroom": PrivacyLevel.PRIVATE,
    "common_bathroom": PrivacyLevel.PRIVATE, "pooja": PrivacyLevel.SEMI_PRIVATE,
    "office": PrivacyLevel.SEMI_PRIVATE, "parking": PrivacyLevel.SERVICE,
    "utility": PrivacyLevel.SERVICE, "stair": PrivacyLevel.SERVICE,
    "balcony": PrivacyLevel.SEMI_PRIVATE, "entrance": PrivacyLevel.PUBLIC,
    "corridor": PrivacyLevel.SERVICE, "store": PrivacyLevel.SERVICE,
}

ROOM_NATURAL_LIGHT: Dict[str, bool] = {
    "living": True, "dining": True, "kitchen": True,
    "bedroom": True, "master_bedroom": True, "bathroom": False,
    "common_bathroom": False, "pooja": True, "office": True,
    "parking": False, "utility": False, "stair": False,
    "balcony": True, "entrance": True, "corridor": False, "store": False,
}

ROOM_VENTILATION: Dict[str, bool] = {
    "living": True, "dining": True, "kitchen": True,
    "bedroom": True, "master_bedroom": True, "bathroom": True,
    "common_bathroom": True, "pooja": False, "office": True,
    "parking": False, "utility": True, "stair": False,
    "balcony": True, "entrance": False, "corridor": False, "store": False,
}

ROOM_VASTU: Dict[str, str] = {
    "kitchen": "south-east", "pooja": "north-east",
    "master_bedroom": "south-west", "living": "north",
    "dining": "east", "bedroom": "west", "bathroom": "north-west",
    "common_bathroom": "north-west", "office": "north-east",
    "parking": "north-west", "stair": "south",
}

ROOM_ADJACENCY_PREFERENCES: Dict[str, FrozenSet[str]] = {
    "kitchen": frozenset({"dining", "utility"}),
    "dining": frozenset({"living", "kitchen"}),
    "living": frozenset({"dining", "entrance"}),
    "master_bedroom": frozenset({"bathroom"}),
    "bedroom": frozenset({"common_bathroom"}),
    "pooja": frozenset({"entrance", "living"}),
    "utility": frozenset({"kitchen"}),
    "office": frozenset({"entrance"}),
}

ROOM_ADJACENCY_REQUIREMENTS: Dict[str, FrozenSet[str]] = {
    "master_bedroom": frozenset({"bathroom"}),
}

ROOM_FLOOR_PREFERENCE: Dict[str, FloorPreference] = {
    "living": FloorPreference.GROUND, "dining": FloorPreference.GROUND,
    "kitchen": FloorPreference.GROUND, "master_bedroom": FloorPreference.GROUND,
    "bedroom": FloorPreference.UPPER, "pooja": FloorPreference.GROUND,
    "parking": FloorPreference.GROUND, "entrance": FloorPreference.GROUND,
    "utility": FloorPreference.GROUND, "stair": FloorPreference.ANY,
    "balcony": FloorPreference.UPPER, "office": FloorPreference.ANY,
}

ROOM_CIRCULATION: Dict[str, float] = {
    "living": 0.9, "dining": 0.7, "kitchen": 0.6, "bedroom": 0.4,
    "master_bedroom": 0.3, "bathroom": 0.3, "common_bathroom": 0.5,
    "pooja": 0.3, "office": 0.4, "parking": 0.8, "utility": 0.3,
    "stair": 1.0, "balcony": 0.2, "entrance": 1.0, "corridor": 1.0, "store": 0.2,
}


class SpaceProgramGenerator:
    """Deterministic generator that converts DesignRequirements to SpaceProgram."""

    def generate(self, requirements: DesignRequirements) -> SpaceProgram:
        rooms: list[RoomProgram] = []
        building = requirements.building
        floors = building.floors or 1
        bedrooms = building.bedrooms or 1

        rooms.append(self._make_room("living", "Living Room", "living", floors, requirements, floor_preference="ground"))
        rooms.append(self._make_room("dining", "Dining Room", "dining", floors, requirements, floor_preference="ground"))
        rooms.append(self._make_room("kitchen", "Kitchen", "kitchen", floors, requirements, floor_preference="ground"))

        for i in range(bedrooms):
            if i == 0:
                rooms.append(self._make_room("master_bedroom", "Master Bedroom", "master_bedroom", floors, requirements, floor_preference="ground"))
                rooms.append(self._make_room("bathroom_master", "Master Bathroom", "bathroom", floors, requirements, floor_preference="ground", adjacency_req=frozenset({"master_bedroom"})))
            else:
                rooms.append(self._make_room(f"bedroom_{i+1}", f"Bedroom {i+1}", "bedroom", floors, requirements, floor_preference="upper"))

        common_bath_count = max(1, bedrooms - 1)
        for i in range(common_bath_count):
            fp = "upper" if floors > 1 else "ground"
            rooms.append(self._make_room(f"bathroom_common_{i+1}", f"Common Bathroom {i+1}", "common_bathroom", floors, requirements, floor_preference=fp))

        if building.utility:
            rooms.append(self._make_room("utility", "Utility Room", "utility", floors, requirements, floor_preference="ground"))
        if building.pooja:
            rooms.append(self._make_room("pooja", "Pooja Room", "pooja", floors, requirements, floor_preference="ground"))
        if building.office:
            rooms.append(self._make_room("office", "Office Room", "office", floors, requirements))
        if building.parking:
            rooms.append(self._make_room("parking", "Parking", "parking", floors, requirements, floor_preference="ground"))
        if floors > 1:
            rooms.append(self._make_room("stair", "Staircase", "stair", floors, requirements, floor_preference="any"))
        if building.balcony:
            rooms.append(self._make_room("balcony", "Balcony", "balcony", floors, requirements, required=False, floor_preference="upper"))
        rooms.append(self._make_room("entrance", "Entrance", "entrance", floors, requirements, required=False, floor_preference="ground"))

        total_target = sum(r.target_area for r in rooms if r.target_area)
        circulation = total_target * CIRCULATION_FACTOR

        return SpaceProgram(
            rooms=tuple(rooms),
            total_target_area=total_target,
            circulation_area=circulation,
            usable_area=total_target,
            floor_count=floors,
            metadata={"bedrooms": bedrooms, "bathrooms": building.bathrooms, "building_type": building.building_type},
        )

    def _make_room(self, room_id: str, name: str, room_type: str, floors: int, requirements: DesignRequirements, required: bool = True, floor_preference: str | None = None, adjacency_req: FrozenSet[str] | None = None) -> RoomProgram:
        area = DEFAULT_ROOM_AREAS.get(room_type, 100.0)
        privacy = ROOM_PRIVACY.get(room_type, PrivacyLevel.PRIVATE)
        natural_light = ROOM_NATURAL_LIGHT.get(room_type, False)
        ventilation = ROOM_VENTILATION.get(room_type, False)
        vastu = ROOM_VASTU.get(room_type)
        circulation = ROOM_CIRCULATION.get(room_type, 0.5)
        fp = FloorPreference.ANY
        if floor_preference == "ground":
            fp = FloorPreference.GROUND
        elif floor_preference == "upper":
            fp = FloorPreference.UPPER
        adj_pref = ROOM_ADJACENCY_PREFERENCES.get(room_type, frozenset())
        adj_req = adjacency_req if adjacency_req else ROOM_ADJACENCY_REQUIREMENTS.get(room_type, frozenset())
        return RoomProgram(
            id=room_id, room_type=room_type, name=name,
            target_area=area, minimum_area=area * MINIMUM_AREA_FACTOR,
            maximum_area=area * MAXIMUM_AREA_FACTOR, privacy_level=privacy,
            required=required, floor_preference=fp,
            adjacency_preferences=adj_pref, adjacency_requirements=adj_req,
            circulation_importance=circulation, natural_light_required=natural_light,
            ventilation_required=ventilation, vastu_preference=vastu,
        )
