import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class ScoreIndicator extends StatelessWidget {
  final String label; final double score; final Color color; final double size;
  const ScoreIndicator({super.key, required this.label, required this.score, required this.color, this.size = 80});

  @override
  Widget build(BuildContext context) {
    return Column(mainAxisSize: MainAxisSize.min, children: [
      SizedBox(width: size, height: size, child: Stack(alignment: Alignment.center, children: [
        SizedBox(width: size, height: size, child: TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: score / 100), duration: const Duration(milliseconds: 500),
          builder: (ctx, val, _) => CircularProgressIndicator(value: val, strokeWidth: 6, backgroundColor: AppColors.surface, valueColor: AlwaysStoppedAnimation<Color>(color)),
        )),
        Text(score.toInt().toString(), style: TextStyle(fontSize: size * 0.3, fontWeight: FontWeight.bold, color: color)),
      ])),
      const SizedBox(height: 4),
      Text(label, style: TextStyle(fontSize: 10, color: AppColors.textSecondary), textAlign: TextAlign.center),
    ]);
  }
}
