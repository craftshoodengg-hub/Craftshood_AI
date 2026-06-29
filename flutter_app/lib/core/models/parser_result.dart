import 'package:json_annotation/json_annotation.dart';
part 'parser_result.g.dart';

@JsonSerializable()
class ParserResult {
  final String prompt;
  final double confidence;
  final Map<String, dynamic> extractedFields;
  final List<String> missingFields;
  final List<String> warnings;
  final bool isComplete;

  ParserResult({
    required this.prompt,
    required this.confidence,
    this.extractedFields = const {},
    this.missingFields = const [],
    this.warnings = const [],
    required this.isComplete,
  });

  factory ParserResult.fromJson(Map<String, dynamic> json) => _$ParserResultFromJson(json);
  Map<String, dynamic> toJson() => _$ParserResultToJson(this);
}
