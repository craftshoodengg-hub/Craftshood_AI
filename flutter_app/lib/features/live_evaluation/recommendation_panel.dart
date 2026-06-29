import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/colors.dart';
import 'live_evaluation_controller.dart';

class RecommendationPanel extends ConsumerWidget {
  const RecommendationPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final evalData = ref.watch(liveEvaluationControllerProvider);
    if (!evalData.hasResults || evalData.issues.isEmpty) return const SizedBox.shrink();
    return DraggableScrollableSheet(
      initialChildSize: 0.15, minChildSize: 0.1, maxChildSize: 0.5, expand: false,
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
              const Text('Recommendations', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const Spacer(), Text('${evalData.issues.length}', style: TextStyle(color: AppColors.textSecondary)),
            ])),
            const Divider(),
            Expanded(child: ListView.builder(
              controller: scrollController, padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: evalData.issues.length,
              itemBuilder: (context, index) {
                final issue = evalData.issues[index];
                return Card(margin: const EdgeInsets.only(bottom: 8), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ExpansionTile(
                    title: Text(issue.title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                    subtitle: Text(issue.priority.toUpperCase(), style: TextStyle(fontSize: 10, color: _priorityColor(issue.priority))),
                    children: [
                      Padding(padding: const EdgeInsets.all(12), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Text(issue.description, style: const TextStyle(fontSize: 12)),
                        const SizedBox(height: 8),
                        Row(children: [
                          if (issue.targetRoom != null) _Chip('Room: ${issue.targetRoom}'),
                          if (issue.estimatedGain != null) _Chip('Gain: +${issue.estimatedGain!.toInt()}'),
                        ]),
                      ])),
                    ],
                  ),
                );
              },
            ))]),
        );
      },
    );
  }

  Color _priorityColor(String priority) {
    switch (priority.toLowerCase()) {
      case 'recommendation': return AppColors.error;
      case 'warning': return AppColors.accentDark;
      case 'suggestion': return AppColors.primaryLight;
      default: return AppColors.textSecondary;
    }
  }
}

class _Chip extends StatelessWidget {
  final String label; const _Chip(this.label);
  @override
  Widget build(BuildContext context) => Container(margin: const EdgeInsets.only(right: 4), padding:
    const EdgeInsets.symmetric(horizontal: 6, vertical: 2), decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(6)),
    child: Text(label, style: const TextStyle(fontSize: 9)));
}
