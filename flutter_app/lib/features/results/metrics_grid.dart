import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class MetricsGrid extends StatelessWidget {
  final double evaluationScore;
  final double layoutScore;
  const MetricsGrid({super.key, required this.evaluationScore, required this.layoutScore});

  @override
  Widget build(BuildContext context) {
    final metrics = [
      _MetricData('Evaluation', evaluationScore, AppColors.primary),
      _MetricData('Layout', layoutScore, AppColors.accent),
      _MetricData('Accessibility', 85.0, AppColors.success),
      _MetricData('Environmental', 78.0, AppColors.primaryLight),
      _MetricData('Vastu', 90.0, AppColors.accentDark),
      _MetricData('Structural', 82.0, AppColors.textSecondary),
    ];
    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = constraints.maxWidth > 600 ? 3 : 2;
        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount, childAspectRatio: 1.5, crossAxisSpacing: 12, mainAxisSpacing: 12,
          ),
          itemCount: metrics.length,
          itemBuilder: (context, index) => _MetricCard(metrics[index]),
        );
      },
    );
  }
}

class _MetricData {
  final String label; final double score; final Color color;
  _MetricData(this.label, this.score, this.color);
}

class _MetricCard extends StatelessWidget {
  final _MetricData data;
  const _MetricCard(this.data);
  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(data.score.toInt().toString(), style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: data.color)),
            const SizedBox(height: 4),
            Text(data.label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}
