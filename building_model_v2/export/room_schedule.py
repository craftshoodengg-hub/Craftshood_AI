"""Room schedule generator."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Self
from ..validation.cross_entity_validator import BuildingModel


@dataclass(frozen=True, slots=True)
class RoomScheduleEntry:
    """A single room schedule entry."""
    room_number: str
    room_name: str
    floor: str
    area: float
    perimeter: float
    privacy: str = 'Medium'
    natural_light: str = 'Good'
    ventilation: str = 'Good'
    vastu_zone: str = ''
    def to_dict(self):
        return {'room_number': self.room_number, 'room_name': self.room_name,
                'floor': self.floor, 'area': self.area, 'perimeter': self.perimeter,
                'privacy': self.privacy, 'natural_light': self.natural_light,
                'ventilation': self.ventilation, 'vastu_zone': self.vastu_zone}
    @classmethod
    def from_dict(cls, payload):
        return cls(room_number=str(payload.get('room_number', '')),
                   room_name=str(payload.get('room_name', '')),
                   floor=str(payload.get('floor', '')),
                   area=float(payload.get('area', 0)),
                   perimeter=float(payload.get('perimeter', 0)),
                   privacy=str(payload.get('privacy', 'Medium')),
                   natural_light=str(payload.get('natural_light', 'Good')),
                   ventilation=str(payload.get('ventilation', 'Good')),
                   vastu_zone=str(payload.get('vastu_zone', '')))


@dataclass(frozen=True, slots=True)
class RoomSchedule:
    """Complete room schedule."""
    entries: tuple[RoomScheduleEntry, ...] = ()
    building_name: str = ''
    date: str = ''
    total_area: float = 0.0
    def to_dict(self):
        return {'entries': [e.to_dict() for e in self.entries],
                'building_name': self.building_name, 'date': self.date,
                'total_area': self.total_area}
    @classmethod
    def from_dict(cls, payload):
        entries = tuple(RoomScheduleEntry.from_dict(e) for e in payload.get('entries', []))
        return cls(entries=entries, building_name=str(payload.get('building_name', '')),
                   date=str(payload.get('date', '')), total_area=float(payload.get('total_area', 0)))


def _classify_privacy(room_type: str) -> str:
    private = {'Bedroom', 'Toilet', 'Bathroom'}
    if room_type in private:
        return 'High'
    semi = {'Kitchen', 'Storage', 'Utility'}
    if room_type in semi:
        return 'Medium'
    return 'Low'


def _classify_light(room_type: str) -> str:
    good = {'Living', 'Bedroom', 'Kitchen', 'Dining'}
    if room_type in good:
        return 'Good'
    moderate = {'Corridor', 'Utility', 'Balcony'}
    if room_type in moderate:
        return 'Moderate'
    return 'Low'


def _classify_ventilation(room_type: str) -> str:
    good = {'Living', 'Bedroom', 'Kitchen', 'Balcony'}
    if room_type in good:
        return 'Good'
    moderate = {'Dining', 'Corridor', 'Utility'}
    if room_type in moderate:
        return 'Moderate'
    return 'Low'


def generate_room_schedule(model: BuildingModel) -> RoomSchedule:
    """Generate a deterministic room schedule from a building model."""
    entries = []
    total_area = 0.0
    room_idx = 1
    for room_id in sorted(model.rooms.keys()):
        room = model.rooms[room_id]
        if room.polygon.is_empty:
            continue
        area = room.area
        perimeter = room.perimeter
        total_area += area
        entry = RoomScheduleEntry(
            room_number='R{:02d}'.format(room_idx),
            room_name=room.room_type.value,
            floor=room.floor_id or '',
            area=area, perimeter=perimeter,
            privacy=_classify_privacy(room.room_type.value),
            natural_light=_classify_light(room.room_type.value),
            ventilation=_classify_ventilation(room.room_type.value),
            vastu_zone='')
        entries.append(entry)
        room_idx += 1
    building_name = ''
    if model.building is not None:
        building_name = model.building.name
    return RoomSchedule(
        entries=tuple(entries), building_name=building_name,
        date='', total_area=total_area)
