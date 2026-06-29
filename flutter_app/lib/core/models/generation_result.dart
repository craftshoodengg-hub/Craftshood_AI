import 'package:json_annotation/json_annotation.dart';
part 'generation_result.g.dart';

@JsonSerializable()
class GenerationResult {
  final String prompt;
  final bool success;
  final String quality;
  final double finalScore;
  final int iterationCount;
  final double layoutScore;
  final Map<String, dynamic> metadata;

  GenerationResult({
    required this.prompt,
    required this.success,
    required this.quality,
    required this.finalScore,
    required this.iterationCount,
    required this.layoutScore,
    this.metadata = const {},
  });

  factory GenerationResult.fromJson(Map<String, dynamic> json) => _$GenerationResultFromJson(json);
  Map<String, dynamic> toJson() => _$GenerationResultToJson(this);
}
