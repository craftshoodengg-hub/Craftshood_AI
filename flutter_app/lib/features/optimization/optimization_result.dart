import 'package:json_annotation/json_annotation.dart';
import '../floorplan/floorplan_painter.dart';
part 'optimization_result.g.dart';

@JsonSerializable()
class OptimizationResultData {
  final List<RoomRect> rooms;
  final double beforeScore;
  final double afterScore;
  final List<String> appliedActions;
  final bool improved;

  OptimizationResultData({
    required this.rooms, required this.beforeScore, required this.afterScore,
    this.appliedActions = const [], this.improved = false,
  });

  factory OptimizationResultData.fromJson(Map<String, dynamic> json) => _$OptimizationResultDataFromJson(json);
  Map<String, dynamic> toJson() => _$OptimizationResultDataToJson(this);

  double get scoreDelta => afterScore - beforeScore;
}
