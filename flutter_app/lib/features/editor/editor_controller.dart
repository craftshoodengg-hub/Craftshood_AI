import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../floorplan/floorplan_painter.dart';

enum EditingMode { select, move, resize }

@immutable
class EditorState {
  final List<RoomRect> rooms;
  final String? selectedRoomId;
  final EditingMode mode;
  final double zoomLevel;
  final Offset panOffset;
  final bool hasError;
  final String? errorMessage;

  const EditorState({
    this.rooms = const [],
    this.selectedRoomId,
    this.mode = EditingMode.select,
    this.zoomLevel = 1.0,
    this.panOffset = Offset.zero,
    this.hasError = false,
    this.errorMessage,
  });

  EditorState copyWith({
    List<RoomRect>? rooms, String? selectedRoomId, EditingMode? mode,
    double? zoomLevel, Offset? panOffset, bool? hasError, String? errorMessage,
  }) {
    return EditorState(
      rooms: rooms ?? this.rooms, selectedRoomId: selectedRoomId ?? this.selectedRoomId,
      mode: mode ?? this.mode, zoomLevel: zoomLevel ?? this.zoomLevel, panOffset: panOffset ?? this.panOffset,
      hasError: hasError ?? false, errorMessage: errorMessage,
    );
  }

  RoomRect? get selectedRoom {
    if (selectedRoomId == null) return null;
    for (final r in rooms) { if (r.id == selectedRoomId) return r; }
    return null;
  }
}

class EditorController extends ValueNotifier<EditorState> {
  final List<EditorState> _undoStack = [];
  final List<EditorState> _redoStack = [];
  static const int maxHistory = 50;

  EditorController() : super(const EditorState());

  void initRooms(List<RoomRect> rooms) {
    value = EditorState(rooms: List.from(rooms));
    _undoStack.clear();
    _redoStack.clear();
  }

  void _pushUndo() {
    _undoStack.add(value);
    if (_undoStack.length > maxHistory) _undoStack.removeAt(0);
    _redoStack.clear();
  }

  void selectRoom(String? roomId) {
    value = value.copyWith(selectedRoomId: roomId, mode: roomId != null ? EditingMode.select : EditingMode.select);
  }

  void setMode(EditingMode mode) => value = value.copyWith(mode: mode);

  void updateRoom(RoomRect updated) {
    _pushUndo();
    final rooms = value.rooms.map((r) => r.id == updated.id ? updated : r).toList();
    value = value.copyWith(rooms: rooms);
  }

  void moveRoom(String roomId, double dx, double dy) {
    _pushUndo();
    final rooms = value.rooms.map((r) {
      if (r.id != roomId) return r;
      return RoomRect(id: r.id, name: r.name, type: r.type, rect: r.rect.translate(dx, dy), area: r.area);
    }).toList();
    value = value.copyWith(rooms: rooms);
  }

  void resizeRoom(String roomId, Rect newRect) {
    _pushUndo();
    final rooms = value.rooms.map((r) {
      if (r.id != roomId) return r;
      final area = newRect.width * newRect.height / 100;
      return RoomRect(id: r.id, name: r.name, type: r.type, rect: newRect, area: area);
    }).toList();
    value = value.copyWith(rooms: rooms);
  }

  void renameRoom(String roomId, String newName) {
    _pushUndo();
    final rooms = value.rooms.map((r) {
      if (r.id != roomId) return r;
      return RoomRect(id: r.id, name: newName, type: r.type, rect: r.rect, area: r.area);
    }).toList();
    value = value.copyWith(rooms: rooms);
  }

  void deleteRoom(String roomId) {
    _pushUndo();
    final rooms = value.rooms.where((r) => r.id != roomId).toList();
    value = value.copyWith(rooms: rooms, selectedRoomId: null);
  }

  void duplicateRoom(String roomId) {
    _pushUndo();
    final original = value.rooms.firstWhere((r) => r.id == roomId);
    final newId = '${roomId}_copy_${value.rooms.length}';
    final newRoom = RoomRect(
      id: newId, name: '${original.name} (Copy)', type: original.type,
      rect: original.rect.translate(20, 20), area: original.area,
    );
    value = value.copyWith(rooms: [...value.rooms, newRoom], selectedRoomId: newId);
  }

  void zoom(double factor) => value = value.copyWith(zoomLevel: (value.zoomLevel * factor).clamp(0.5, 5.0));
  void pan(Offset delta) => value = value.copyWith(panOffset: value.panOffset + delta);
  void resetView() => value = value.copyWith(zoomLevel: 1.0, panOffset: Offset.zero);

  void undo() {
    if (_undoStack.isEmpty) return;
    _redoStack.add(value);
    value = _undoStack.removeLast();
  }

  void redo() {
    if (_redoStack.isEmpty) return;
    _undoStack.add(value);
    value = _redoStack.removeLast();
  }

  bool get canUndo => _undoStack.isNotEmpty;
  bool get canRedo => _redoStack.isNotEmpty;
}

final editorControllerProvider = Provider<EditorController>((ref) => EditorController());
