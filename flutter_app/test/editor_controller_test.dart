import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:craftshood_ai/features/editor/editor_controller.dart';
import 'package:craftshood_ai/features/floorplan/floorplan_painter.dart';

void main() {
  group('EditorController', () {
    test('initial state is empty', () {
      final ctrl = EditorController();
      expect(ctrl.value.rooms, isEmpty);
      expect(ctrl.value.selectedRoomId, null);
      expect(ctrl.value.mode, EditingMode.select);
    });

    test('initRooms sets rooms', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.zero, area: 100)]);
      expect(ctrl.value.rooms.length, 1);
    });

    test('moveRoom translates rect', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.fromLTWH(10, 10, 50, 50), area: 100)]);
      ctrl.moveRoom('1', 5, 5);
      expect(ctrl.value.rooms.first.rect, Rect.fromLTWH(15, 15, 50, 50));
    });

    test('resizeRoom updates rect', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.fromLTWH(10, 10, 50, 50), area: 100)]);
      ctrl.resizeRoom('1', Rect.fromLTWH(10, 10, 100, 100));
      expect(ctrl.value.rooms.first.rect.width, 100);
    });

    test('renameRoom updates name', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'Test', type: 'bedroom', rect: Rect.zero, area: 100)]);
      ctrl.renameRoom('1', 'Living Room');
      expect(ctrl.value.rooms.first.name, 'Living Room');
    });

    test('deleteRoom removes room', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'A', type: 'bedroom', rect: Rect.zero, area: 100), const RoomRect(id: '2', name: 'B', type: 'kitchen', rect: Rect.zero, area: 100)]);
      ctrl.deleteRoom('1');
      expect(ctrl.value.rooms.length, 1);
      expect(ctrl.value.rooms.first.id, '2');
    });

    test('duplicateRoom adds copy', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'A', type: 'bedroom', rect: Rect.zero, area: 100)]);
      ctrl.duplicateRoom('1');
      expect(ctrl.value.rooms.length, 2);
      expect(ctrl.value.rooms.last.name, 'A (Copy)');
    });

    test('undo restores previous state', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'A', type: 'bedroom', rect: Rect.zero, area: 100)]);
      ctrl.renameRoom('1', 'B');
      ctrl.undo();
      expect(ctrl.value.rooms.first.name, 'A');
    });

    test('redo reapplies state', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'A', type: 'bedroom', rect: Rect.zero, area: 100)]);
      ctrl.renameRoom('1', 'B');
      ctrl.undo();
      ctrl.redo();
      expect(ctrl.value.rooms.first.name, 'B');
    });

    test('setMode updates mode', () {
      final ctrl = EditorController();
      ctrl.setMode(EditingMode.move);
      expect(ctrl.value.mode, EditingMode.move);
    });

    test('zoom clamps correctly', () {
      final ctrl = EditorController();
      ctrl.zoom(10);
      expect(ctrl.value.zoomLevel, 5.0);
      ctrl.zoom(0.01);
      expect(ctrl.value.zoomLevel, 0.5);
    });

    test('canUndo false initially', () {
      final ctrl = EditorController();
      expect(ctrl.canUndo, false);
    });

    test('selectedRoom returns correct room', () {
      final ctrl = EditorController();
      ctrl.initRooms([const RoomRect(id: '1', name: 'A', type: 'bedroom', rect: Rect.zero, area: 100)]);
      ctrl.selectRoom('1');
      expect(ctrl.value.selectedRoom?.name, 'A');
    });
  });

  group('EditingMode', () {
    test('has correct values', () {
      expect(EditingMode.values.length, 3);
    });
  });
}
