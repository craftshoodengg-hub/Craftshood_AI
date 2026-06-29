import 'package:json_annotation/json_annotation.dart';
part 'generation_request.g.dart';

@JsonSerializable()
class GenerationRequest {
  final String prompt;
  GenerationRequest({required this.prompt});
  factory GenerationRequest.fromJson(Map<String, dynamic> json) => _$GenerationRequestFromJson(json);
  Map<String, dynamic> toJson() => _$GenerationRequestToJson(this);
}
