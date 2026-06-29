import 'package:flutter_test/flutter_test.dart';
import 'package:craftshood_ai/features/optimization/optimization_controller.dart';
import 'package:craftshood_ai/features/optimization/optimization_action.dart';
import 'package:craftshood_ai/core/api/api_client.dart';

class MockApiClient extends ApiClient {
  Map<String, dynamic>? _nextResponse;
  Exception? _nextError;
  void setResponse(Map<String, dynamic> resp) => _nextResponse = resp;
  void setError(Exception err) => _nextError = err;

  @override
  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    if (_nextError != null) throw _nextError!;
    return _nextResponse ?? {'after_score': 80.0, 'rooms': []};
  }
}

void main() {
  group('OptimizationActionData', () {
    test('creates from backend response', () {
      final json = {'id': 'a1', 'title': 'Fix Room', 'description': 'Fix the room', 'target_entity_id': 'r1', 'target_entity_type': 'room', 'constraint_codes': ['CODE1'], 'current_score': 0.5, 'estimated_score_gain': 0.2, 'priority': 1, 'confidence': 0.9};
      final action = OptimizationActionData.fromBackend(json);
      expect(action.id, 'a1');
      expect(action.title, 'Fix Room');
      expect(action.estimatedScoreGain, 0.2);
      expect(action.priority, 1);
    });

    test('handles empty response', () {
      final action = OptimizationActionData.fromBackend({});
      expect(action.id, '');
      expect(action.priority, 0);
    });
  });

  group('OptimizationController', () {
    test('initial state is idle', () {
      final ctrl = OptimizationController(MockApiClient());
      expect(ctrl.value.state, OptimizationState.idle);
      expect(ctrl.value.pendingActions, isEmpty);
    });

    test('setPendingActions populates actions', () {
      final ctrl = OptimizationController(MockApiClient());
      final actions = [OptimizationActionData(id: 'a1', title: 'T', description: 'D', targetEntityId: 'r1', targetEntityType: 'room')];
      ctrl.setPendingActions(actions, 50.0, 80.0);
      expect(ctrl.value.pendingActions.length, 1);
      expect(ctrl.value.currentScore, 50.0);
      expect(ctrl.value.projectedScore, 80.0);
    });

    test('applyAction updates state to applied', () async {
      final mock = MockApiClient();
      mock.setResponse({'after_score': 85.0, 'rooms': []});
      final ctrl = OptimizationController(mock);
      final action = OptimizationActionData(id: 'a1', title: 'Fix', description: 'Fix room', targetEntityId: 'r1', targetEntityType: 'room', estimatedScoreGain: 0.15);
      ctrl.setPendingActions([action], 70.0, 85.0);
      await ctrl.applyAction(action);
      expect(ctrl.value.state, OptimizationState.applied);
      expect(ctrl.value.currentScore, 85.0);
      expect(ctrl.value.history.length, 1);
    });

    test('applyAction handles error', () async {
      final mock = MockApiClient();
      mock.setError(Exception('Server error'));
      final ctrl = OptimizationController(mock);
      final action = OptimizationActionData(id: 'a1', title: 'Fix', description: 'Fix', targetEntityId: 'r1', targetEntityType: 'room');
      ctrl.setPendingActions([action], 70.0, 85.0);
      await ctrl.applyAction(action);
      expect(ctrl.value.state, OptimizationState.error);
    });

    test('undo restores previous state', () async {
      final mock = MockApiClient();
      mock.setResponse({'after_score': 85.0, 'rooms': []});
      final ctrl = OptimizationController(mock);
      final action = OptimizationActionData(id: 'a1', title: 'Fix', description: 'Fix', targetEntityId: 'r1', targetEntityType: 'room');
      ctrl.setPendingActions([action], 70.0, 85.0);
      await ctrl.applyAction(action);
      ctrl.undo();
      expect(ctrl.value.history.length, 0);
    });

    test('reset clears all state', () async {
      final mock = MockApiClient();
      mock.setResponse({'after_score': 85.0, 'rooms': []});
      final ctrl = OptimizationController(mock);
      final action = OptimizationActionData(id: 'a1', title: 'Fix', description: 'Fix', targetEntityId: 'r1', targetEntityType: 'room');
      ctrl.setPendingActions([action], 70.0, 85.0);
      await ctrl.applyAction(action);
      ctrl.reset();
      expect(ctrl.value.state, OptimizationState.idle);
      expect(ctrl.value.history, isEmpty);
    });

    test('canUndo reflects history', () async {
      final mock = MockApiClient();
      mock.setResponse({'after_score': 85.0, 'rooms': []});
      final ctrl = OptimizationController(mock);
      expect(ctrl.value.canUndo, false);
      final action = OptimizationActionData(id: 'a1', title: 'Fix', description: 'Fix', targetEntityId: 'r1', targetEntityType: 'room');
      ctrl.setPendingActions([action], 70.0, 85.0);
      await ctrl.applyAction(action);
      expect(ctrl.value.canUndo, true);
    });

    test('removes applied action from pending', () async {
      final mock = MockApiClient();
      mock.setResponse({'after_score': 85.0, 'rooms': []});
      final ctrl = OptimizationController(mock);
      final action = OptimizationActionData(id: 'a1', title: 'Fix', description: 'Fix', targetEntityId: 'r1', targetEntityType: 'room');
      ctrl.setPendingActions([action], 70.0, 85.0);
      await ctrl.applyAction(action);
      expect(ctrl.value.pendingActions, isEmpty);
    });
  });

  group('OptimizationHistoryEntry', () {
    test('calculates score delta', () {
      final entry = OptimizationHistoryEntry(actionId: 'a1', actionTitle: 'Fix', beforeScore: 70.0, afterScore: 85.0, timestamp: DateTime.now());
      expect(entry.afterScore - entry.beforeScore, 15.0);
    });
  });
}
