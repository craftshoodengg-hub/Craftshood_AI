import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:craftshood_ai/features/floorplan/floorplan_controller.dart';
import 'package:craftshood_ai/features/floorplan/floorplan_painter.dart';
import 'package:craftshood_ai/features/floorplan/room_widget.dart';

void main() {
  group('FloorPlanController', () {
    test('initial state is default', () {
      final controller = FloorPlanController();
      expect(controller.value.selectedRoomId, null);
      expect(controller.value.zoomLevel, 1.0);
      expect(controller.value.panOffset, Offset.zero);
    });

    test('selectRoom updates selectedRoomId', () {
      final controller = FloorPlanController();
      controller.selectRoom('room1');
      expect(controller.value.selectedRoomId, 'room1');
    });

    test('clearSelection resets selectedRoomId', () {
      final controller = FloorPlanController();
      controller.selectRoom('room1');
      controller.clearSelection();
      expect(controller.value.selectedRoomId, null);
    });

    test('zoom increases zoomLevel', () {
      final controller = FloorPlanController();
      controller.zoom(1.5);
      expect(controller.value.zoomLevel, 1.5);
    });

    test('zoom clamps at 5.0', () {
      final controller = FloorPlanController();
      controller.zoom(10.0);
      expect(controller.value.zoomLevel, 5.0);
    });

    test('zoom clamps at 0.5', () {
      final controller = FloorPlanController();
      controller.zoom(0.1);
      expect(controller.value.zoomLevel, 0.5);
    });

    test('zoom out decreases zoomLevel', () {
      final controller = FloorPlanController();
      controller.zoom(0.5);
      expect(controller.value.zoomLevel, 0.5);
    });

    test('pan updates panOffset', () {
      final controller = FloorPlanController();
      controller.pan(const Offset(10, 20));
      expect(controller.value.panOffset, const Offset(10, 20));
    });

    test('resetView resets all state', () {
      final controller = FloorPlanController();
      controller.selectRoom('room1');
      controller.zoom(2.0);
      controller.pan(const Offset(5, 5));
      controller.resetView();
      expect(controller.value.selectedRoomId, null);
      expect(controller.value.zoomLevel, 1.0);
      expect(controller.value.panOffset, Offset.zero);
    });
  });

  group('RoomStyle', () {
    test('forType returns correct colors for living', () {
      final style = RoomStyle.forType('living');
      expect(style.type, 'living');
    });

    test('forType returns default for unknown type', () {
      final style = RoomStyle.forType('unknown_type');
      expect(style.type, 'unknown_type');
    });

    test('forType handles many room types', () {
      for (final type in ['bedroom', 'kitchen', 'bathroom', 'parking', 'office']) {
        final style = RoomStyle.forType(type);
        expect(style.type, type);
      }
    });

    test('selected colors are defined', () {
      expect(RoomStyle.selectedBorder, isNotNull);
      expect(RoomStyle.selectedFill, isNotNull);
    });
  });

  group('FloorPlanPainter', () {
    test('shouldRepaint changes when rooms change', () {
      final painter1 = FloorPlanPainter(rooms: []);
      final painter2 = FloorPlanPainter(rooms: [const RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.zero, area: 100)]);
      expect(painter2.shouldRepaint(painter1), true);
    });

    test('shouldRepaint changes when selection changes', () {
      const rooms = [RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.zero, area: 100)];
      final painter1 = FloorPlanPainter(rooms: rooms, selectedRoomId: null);
      final painter2 = FloorPlanPainter(rooms: rooms, selectedRoomId: '1');
      expect(painter2.shouldRepaint(painter1), true);
    });

    test('shouldRepaint changes when zoom changes', () {
      const rooms = [RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.zero, area: 100)];
      final painter1 = FloorPlanPainter(rooms: rooms, zoomLevel: 1.0);
      final painter2 = FloorPlanPainter(rooms: rooms, zoomLevel: 2.0);
      expect(painter2.shouldRepaint(painter1), true);
    });

    test('shouldNotRepaint when nothing changes', () {
      const rooms = [RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.zero, area: 100)];
      final painter1 = FloorPlanPainter(rooms: rooms, zoomLevel: 1.0);
      final painter2 = FloorPlanPainter(rooms: rooms, zoomLevel: 1.0);
      expect(painter2.shouldRepaint(painter1), false);
    });
  });

  group('RoomRect', () {
    test('creates with required fields', () {
      const room = RoomRect(id: 'bed1', name: 'Bedroom', type: 'bedroom', rect: Rect.fromLTWH(0, 0, 100, 100), area: 100);
      expect(room.id, 'bed1');
      expect(room.area, 100);
    });
  });
}
