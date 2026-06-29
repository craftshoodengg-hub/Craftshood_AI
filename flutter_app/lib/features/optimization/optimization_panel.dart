import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/colors.dart';
import '../../core/theme/typography.dart';
import 'optimization_controller.dart';
import 'optimization_action.dart';

class OptimizationPanel extends ConsumerWidget {
  const OptimizationPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final optState = ref.watch(optimizationControllerProvider);
    if (optState.pendingActions.isEmpty) return const SizedBox.shrink();
    return DraggableScrollableSheet(
      initialChildSize: 0.2, minChildSize: 0.1, maxChildSize: 0.6, expand: false,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10, offset: const Offset(0, -2))],
          ),
          child: Column(children: [
            Container(width: 40, height: 4, margin: const EdgeInsets.symmetric(vertical: 8), decoration: BoxDecoration(color: AppColors.divider, borderRadius: BorderRadius.circular(2))),
            Padding(padding: const EdgeInsets.symmetric(horizontal: 16), child: Row(children: [
              Text('Optimizations', style: AppTypography.titleLarge),
              const Spacer(),
              if (optState.projectedScore != null)
                Chip(label: Text('${optState.projectedScore!.toInt()}', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)), backgroundColor: AppColors.primary.withOpacity(0.1)),
            ])),
            const Divider(),
            if (optState.isLoading) const Padding(padding: const EdgeInsets.all(16), child: Center(child: CircularProgressIndicator())),
            Expanded(child: ListView.builder(
              controller: scrollController, padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: optState.pendingActions.length,
              itemBuilder: (context, index) {
                final action = optState.pendingActions[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ListTile(
                    title: Text(action.title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                    subtitle: Text(action.description, style: TextStyle(fontSize: 11, color: AppColors.textSecondary), maxLines: 2, overflow: TextOverflow.ellipsis),
                    trailing: ElevatedButton(
                      onPressed: optState.isLoading ? null : () => ref.read(optimizationControllerProvider).applyAction(action),
                      style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.minimumSize: const Size(60, 32), padding: const EdgeInsets.symmetric(horizontal: 12)),
                      child: const Text('Apply', style: TextStyle(fontSize: 11)),
                    ),
                    leading: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                      Text('+${(action.estimatedScoreGain * 100).toInt()}', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.success)),
                    ]),
                  ),
                );
              },
            ))]),
        );
      },
    );
  }
}
