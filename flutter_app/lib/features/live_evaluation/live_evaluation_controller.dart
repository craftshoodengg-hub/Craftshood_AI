import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../core/api/api_client.dart';
import '../../core/api/endpoints.dart';

enum EvaluationState { idle, loading, loaded, error }

@immutable
class LiveEvaluationData {
  final EvaluationState state;
  final double overallScore;
  final double layoutScore;
  final Map<String, double> categoryScores;
  final List<EvaluationIssue> issues;
  final String? errorMessage;
  final DateTime? lastUpdated;

  const LiveEvaluationData({
    this.state = EvaluationState.idle, this.overallScore = 0.0, this.layoutScore = 0.0,
    this.categoryScores = const {}, this.issues = const [], this.errorMessage, this.lastUpdated,
  });

  LiveEvaluationData copyWith({EvaluationState? state, double? overallScore, double? layoutScore,
    Map<String, double>? categoryScores, List<EvaluationIssue>? issues, String? errorMessage, DateTime? lastUpdated}) {
    return LiveEvaluationData(
      state: state ?? this.state, overallScore: overallScore ?? this.overallScore, layoutScore: layoutScore ?? this.layoutScore,
      categoryScores: categoryScores ?? this.categoryScores, issues: issues ?? this.issues,
      errorMessage: errorMessage, lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get isLoading => state == EvaluationState.loading;
  bool get hasError => state == EvaluationState.error;
  bool get hasResults => state == EvaluationState.loaded;
}

@immutable
class EvaluationIssue {
  final String code; final String title; final String description; final String priority;
  final String? targetRoom; final double? estimatedGain;
  const EvaluationIssue({required this.code, required this.title, required this.description, required this.priority, this.targetRoom, this.estimatedGain});
  factory EvaluationIssue.fromJson(Map<String, dynamic> json) => EvaluationIssue(
    code: json['code'] ?? '', title: json['title'] ?? '', description: json['description'] ?? '',
    priority: json['priority'] ?? 'info', targetRoom: json['target_room'], estimatedGain: (json['estimated_gain'] as num?)?.toDouble(),
  );
}

class LiveEvaluationController extends ValueNotifier<LiveEvaluationData> {
  final ApiClient _client; Timer? _debounceTimer;
  static const Duration _debounceDelay = Duration(milliseconds: 300);
  LiveEvaluationController(this._client) : super(const LiveEvaluationData());

  void evaluate(Map<String, dynamic> buildingModelData) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(_debounceDelay, () => _performEvaluation(buildingModelData));
  }

  Future<void> _performEvaluation(Map<String, dynamic> data) async {
    value = value.copyWith(state: EvaluationState.loading);
    try {
      final response = await _client.post(ApiEndpoints.evaluate, data);
      final overallScore = (response['overall_score'] as num?)?.toDouble() ?? 0.0;
      final layoutScore = (response['layout_score'] as num?)?.toDouble() ?? 0.0;
      final categories = <String, double>{};
      final catData = response['category_scores'] as Map<String, dynamic>?;
      if (catData != null) { for (final e in catData.entries) { categories[e.key] = (e.value as num).toDouble(); } }
      final issues = <EvaluationIssue>[];
      final issuesData = response['issues'] as List<dynamic>?;
      if (issuesData != null) { for (final item in issuesData) { issues.add(EvaluationIssue.fromJson(item as Map<String, dynamic>)); } }
      value = LiveEvaluationData(state: EvaluationState.loaded, overallScore: overallScore, layoutScore: layoutScore, categoryScores: categories, issues: issues, lastUpdated: DateTime.now());
    } catch (e) {
      value = value.copyWith(state: EvaluationState.error, errorMessage: e.toString());
    }
  }

  void cancelPending() => _debounceTimer?.cancel();
  @override
  void dispose() { _debounceTimer?.cancel(); super.dispose(); }
}

final liveEvaluationControllerProvider = Provider<LiveEvaluationController>((ref) => LiveEvaluationController(ref.watch(apiClientProvider)));
