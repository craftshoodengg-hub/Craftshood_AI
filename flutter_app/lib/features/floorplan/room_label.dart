import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class RoomLabel extends StatelessWidget {
  final String name; final double area; final double scale;
  const RoomLabel({super.key, required this.name, required this.area, this.scale = 1.0});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(name, style: TextStyle(fontSize: 10 * scale, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        Text('${area.toStringAsFixed(0)} sqft', style: TextStyle(fontSize: 8 * scale, color: AppColors.textSecondary)),
      ],
    );
  }
}
