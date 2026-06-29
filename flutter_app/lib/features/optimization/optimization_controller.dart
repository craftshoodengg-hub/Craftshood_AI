import 'package:flutter/foundation.dart';
import '../../core/api/api_client.dart';
import '../../core/api/endpoints.dart';
import '../floorplan/floorplan_painter.dart';
import 'optimization_action.dart';
import 'optimization_result.dart';

enum OptimizationState { idle, loading, optimizing, applied, error }

@immutable
class OptimizationHistoryEntry {
  final String actionId;
  final String actionTitle;
  final double beforeScore;
  final double afterScore;
  final DateTime timestamp;
  const OptimizationHistoryEntry({
    required this.actionId, required this.actionTitle,
    required this.beforeScore, required this.afterScore, required this.timestamp,
  });
}

@immutable
class OptimizationStateData {
  final OptimizationState state;
  final List<OptimizationActionData> pendingActions;
  final List<OptimizationHistoryEntry> history;
  final double currentScore;
  final double? projectedScore;
  final String? errorMessage;

  const OptimizationStateData({
    this.state = OptimizationState.idle,
    this.pendingActions = const [],
    this.history = const [],
    this.currentScore = 0.0,
    this.projectedScore,
    this.errorMessage,
  });

  OptimizationStateData copyWith({
    OptimizationState? state, List<OptimizationActionData>? pendingActions,
    List<OptimizationHistoryEntry>? history, double? currentScore,
    double? projectedScore, String? errorMessage,
  }) => OptimizationStateData(
    state: state ?? this.state, pendingActions: pendingActions ?? this.pendingActions,
    history: history ?? this.history, currentScore: currentScore ?? this.currentScore,
    projectedScore: projectedScore ?? this.projectedScore, errorMessage: errorMessage,
  );

  bool get isLoading => state == OptimizationState.optimization || state == OptimizationState.loading;
  bool get canUndo => history.isNotEmpty;
  int get historyCount => history.length;
}

class OptimizationController extends ValueNotifier<OptimizationStateData> {
  final ApiClient _client;
  List<OptimizationStateData> _undoStack = [];

  OptimizationController(this._client) : super(const OptimizationStateData());

  void setPendingActions(List<OptimizationActionData> actions, double currentScore, double projectedScore) {
    value = value.copyWith(pendingActions: actions, currentScore: currentScore, projectedScore: projectedScore, state: OptimizationState.idle);
  }

  Future<void> applyAction(OptimizationActionData action) async {
    _undoStack.add(value);
    value = value.copyWith(state: OptimizationState.optimizing);
    try {
      final response = await _client.post(ApiEndpoints.optimize, action.toJson());
      final afterScore = (response['after_score'] as num?)?.toDouble() ?? value.currentScore;
      final rooms = _parseRooms(response['rooms']);
      final result = OptimizationResultData(rooms: rooms, beforeScore: value.currentScore, afterScore: afterScore, appliedActions: [action.id], improved: afterScore > value.currentScore);
      final entry = OptimizationHistoryEntry(actionId: action.id, actionTitle: action.title, beforeScore: value.currentScore, afterScore: afterScore, timestamp: DateTime.now());
      value = OptimizationStateData(
        state: OptimizationState.applied,
        pendingActions: value.pendingActions.where((a) => a.id != action.id).toList(),
        history: [...value.history, entry],
        currentScore: afterScore,
        projectedScore: value.projectedScore,
      );
      notifyListeners();
    } catch (e) {
      value = value.copyWith(state: OptimizationState.error, errorMessage: e.toString());
    }
  }

  List<RoomRect> _parseRooms(dynamic roomsData) {
    if (roomsData is! List) return [];
    final rooms = <RoomRect>[];
    for (final item in roomsData) {
      if (item is Map<String, dynamic>) {
        final rect = item['rect'] as Map<String, dynamic>?;
        if (rect != null) {
          rooms.add(RoomRect(
            id: item['id'] ?? '', name: item['name'] ?? '', type: item['type'] ?? 'unknown',
            rect: Rect.fromLTWH((rect['x'] as num).toDouble(), (rect['y'] as num).toDouble(), (rect['width'] as num).toDouble(), (rect['height'] as num).toDouble()),
            area: (item['area'] as num?)?.toDouble() ?? 0,
          ));
        }
      }
    }
    return rooms;
  }

  void undo() {
    if (_undoStack.isEmpty) return;
    value = _undoStack.removeLast();
  }

  void reset() {
    value = const OptimizationStateData();
    _undoStack.clear();
  }
}

final optimizationControllerProvider = Provider<OptimizationController>((ref) => OptimizationController(ref.watch(apiClientProvider)));
