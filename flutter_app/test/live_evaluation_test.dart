import 'package:flutter_test/flutter_test.dart';
import 'package:craftshood_ai/features/live_evaluation/live_evaluation_controller.dart';
import 'package:craftshood_ai/features/live_evaluation/room_health_badge.dart';
import 'package:craftshood_ai/core/api/api_client.dart';

class MockApiClient extends ApiClient {
  Map<String, dynamic>? _nextResponse;
  Exception? _nextError;
  void setResponse(Map<String, dynamic> resp) => _nextResponse = resp;
  void setError(Exception err) => _nextError = err;

  @override
  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    if (_nextError != null) throw _nextError!;
    return _nextResponse ?? {'overall_score': 0, 'layout_score': 0, 'category_scores': {}, 'issues': []};
  }
}

void main() {
  group('LiveEvaluationController', () {
    test('initial state is idle', () {
      final ctrl = LiveEvaluationController(MockApiClient());
      expect(ctrl.value.state, EvaluationState.idle);
      expect(ctrl.value.overallScore, 0.0);
      expect(ctrl.value.isLoading, false);
    });

    test('sets loading state on evaluate', () async {
      final mock = MockApiClient();
      mock.setResponse({'overall_score': 85.0, 'layout_score': 90.0, 'category_scores': {}, 'issues': []});
      final ctrl = LiveEvaluationController(mock);
      ctrl.evaluate({'rooms': []});
      expect(ctrl.value.state, EvaluationState.loading);
      await Future.delayed(const Duration(milliseconds: 400));
      expect(ctrl.value.state, EvaluationState.loaded);
    });

    test('updates scores from response', () async {
      final mock = MockApiClient();
      mock.setResponse({'overall_score': 88.0, 'layout_score': 92.0, 'category_scores': {'vastu': 90.0}, 'issues': []});
      final ctrl = LiveEvaluationController(mock);
      ctrl.evaluate({'rooms': []});
      await Future.delayed(const Duration(milliseconds: 400));
      expect(ctrl.value.overallScore, 88.0);
      expect(ctrl.value.layoutScore, 92.0);
    });

    test('parses issues from response', () async {
      final mock = MockApiClient();
      mock.setResponse({'overall_score': 50.0, 'layout_score': 60.0, 'category_scores': {}, 'issues': [{'code': 'TEST_01', 'title': 'Test Issue', 'description': 'Test', 'priority': 'warning', 'target_room': 'Kitchen'}]});
      final ctrl = LiveEvaluationController(mock);
      ctrl.evaluate({'rooms': []});
      await Future.delayed(const Duration(milliseconds: 400));
      expect(ctrl.value.issues.length, 1);
      expect(ctrl.value.issues.first.code, 'TEST_01');
    });

    test('sets error state on failure', () async {
      final mock = MockApiClient();
      mock.setError(Exception('Server error'));
      final ctrl = LiveEvaluationController(mock);
      ctrl.evaluate({'rooms': []});
      await Future.delayed(const Duration(milliseconds: 400));
      expect(ctrl.value.state, EvaluationState.error);
      expect(ctrl.value.hasError, true);
    });

    test('debounces rapid edits', () async {
      final mock = MockApiClient();
      mock.setResponse({'overall_score': 70.0, 'layout_score': 75.0, 'category_scores': {}, 'issues': []});
      final ctrl = LiveEvaluationController(mock);
      for (int i = 0; i < 10; i++) { ctrl.evaluate({'rooms': []}); }
      await Future.delayed(const Duration(milliseconds: 500));
      expect(ctrl.value.state, EvaluationState.loaded);
    });

    test('cancelPending stops evaluation', () {
      final mock = MockApiClient();
      final ctrl = LiveEvaluationController(mock);
      ctrl.evaluate({'rooms': []});
      ctrl.cancelPending();
      expect(ctrl.value.state, EvaluationState.loading);
    });
  });

  group('EvaluationIssue', () {
    test('fromJson parses fields', () {
      final json = {'code': 'T01', 'title': 'Title', 'description': 'Desc', 'priority': 'warning', 'target_room': 'R1', 'estimated_gain': 5.5};
      final issue = EvaluationIssue.fromJson(json);
      expect(issue.code, 'T01');
      expect(issue.priority, 'warning');
      expect(issue.estimatedGain, 5.5);
    });

    test('fromJson handles missing fields', () {
      final issue = EvaluationIssue.fromJson({});
      expect(issue.code, '');
      expect(issue.priority, 'info');
    });
  });

  group('RoomHealthBadge', () {
    test('fromIssueCount maps correctly', () {
      expect(RoomHealthBadge.fromIssueCount(0, 0), RoomHealth.good);
      expect(RoomHealthBadge.fromIssueCount(0, 2), RoomHealth.warning);
      expect(RoomHealthBadge.fromIssueCount(1, 0), RoomHealth.error);
    });

    test('colors are defined', () {
      expect(RoomHealthBadge.fill(RoomHealth.good), isNotNull);
      expect(RoomHealthBadge.border(RoomHealth.error), isNotNull);
    });
  });
}
