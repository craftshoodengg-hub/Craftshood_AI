import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/colors.dart';
import 'live_evaluation_controller.dart';

class EvaluationOverlay extends ConsumerWidget {
  const EvaluationOverlay({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final evalData = ref.watch(liveEvaluationControllerProvider);
    if (!evalData.hasResults && !evalData.hasError) return const SizedBox.shrink();
    return Positioned(top: 8, right: 8, child: Card(
      elevation: 4, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(padding: const EdgeInsets.all(12), child: evalData.hasError
        ? Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.error_outline, color: AppColors.error, size: 16), SizedBox(width: 4), Text('Eval unavailable', style: TextStyle(fontSize: 11, color: AppColors.textSecondary))])
        : Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
            Row(children: [Icon(Icons.analytics_outlined, size: 16, color: AppColors.primary), SizedBox(width: 4),
              Text('Live Score: ${evalData.overallScore.toInt()}', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
              if (evalData.isLoading) ...[SizedBox(width: 4), SizedBox(width: 10, height: 10, child: CircularProgressIndicator(strokeWidth: 2))]]),
            SizedBox(height: 4),
            Text('Layout: ${evalData.layoutScore.toInt()}', style: TextStyle(fontSize: 10, color: AppColors.textSecondary)),
          ]),
      ),
    ));
  }
}
