import 'package:json_annotation/json_annotation.dart';
part 'optimization_action.g.dart';

@JsonSerializable()
class OptimizationActionData {
  final String id;
  final String title;
  final String description;
  final String targetEntityId;
  final String targetEntityType;
  final List<String> constraintCodes;
  final double currentScore;
  final double estimatedScoreGain;
  final int priority;
  final double confidence;
  final Map<String, dynamic> metadata;

  OptimizationActionData({
    required this.id, required this.title, required this.description,
    required this.targetEntityId, required this.targetEntityType,
    this.constraintCodes = const [], this.currentScore = 0.0, this.estimatedScoreGain = 0.0,
    this.priority = 0, this.confidence = 0.0, this.metadata = const {},
  });

  factory OptimizationActionData.fromJson(Map<String, dynamic> json) => _$OptimizationActionDataFromJson(json);
  Map<String, dynamic> toJson() => _$OptimizationActionDataToJson(this);

  factory OptimizationActionData.fromBackend(Map<String, dynamic> json) => OptimizationActionData(
    id: json['id'] ?? '', title: json['title'] ?? '', description: json['description'] ?? '',
    targetEntityId: json['target_entity_id'] ?? '', targetEntityType: json['target_entity_type'] ?? '',
    constraintCodes: List<String>.from(json['constraint_codes'] ?? []),
    currentScore: (json['current_score'] as num?)?.toDouble() ?? 0.0,
    estimatedScoreGain: (json['estimated_score_gain'] as num?)?.toDouble() ?? 0.0,
    priority: json['priority'] ?? 0, confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    metadata: Map<String, dynamic>.from(json['metadata'] ?? {}),
  );
}
