import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

@immutable
class FloorPlanState {
  final String? selectedRoomId;
  final double zoomLevel;
  final Offset panOffset;
  const FloorPlanState({this.selectedRoomId, this.zoomLevel = 1.0, this.panOffset = Offset.zero});

  FloorPlanState copyWith({String? selectedRoomId, double? zoomLevel, Offset? panOffset}) {
    return FloorPlanState(
      selectedRoomId: selectedRoomId,
      zoomLevel: zoomLevel ?? this.zoomLevel,
      panOffset: panOffset ?? this.panOffset,
    );
  }

  FloorPlanState clearSelection() => copyWith(selectedRoomId: null);
}

class FloorPlanController extends ValueNotifier<FloorPlanState> {
  FloorPlanController() : super(const FloorPlanState());

  void selectRoom(String? roomId) => value = value.copyWith(selectedRoomId: roomId);
  void clearSelection() => value = value.clearSelection();
  void zoom(double factor) => value = value.copyWith(zoomLevel: (value.zoomLevel * factor).clamp(0.5, 5.0));
  void pan(Offset delta) => value = value.copyWith(panOffset: value.panOffset + delta);
  void resetView() => value = const FloorPlanState();
}

final floorPlanControllerProvider = Provider<FloorPlanController>((ref) => FloorPlanController());
