import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class ImprovementCard extends StatefulWidget {
  final String title;
  final String description;
  final String priority;
  final String constraintCode;
  final String targetRoom;
  const ImprovementCard({super.key, required this.title, required this.description, required this.priority, required this.constraintCode, required this.targetRoom});

  @override
  State<ImprovementCard> createState() => _ImprovementCardState();
}

class _ImprovementCardState extends State<ImprovementCard> {
  bool _expanded = false;

  Color get _priorityColor {
    switch (widget.priority.toLowerCase()) {
      case 'recommendation': return AppColors.error;
      case 'warning': return AppColors.accentDark;
      case 'suggestion': return AppColors.primaryLight;
      default: return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => setState(() => _expanded = !_expanded),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(color: _priorityColor.withOpacity(0.15), borderRadius: BorderRadius.circular(8)),
                    child: Text(widget.priority.toUpperCase(), style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: _priorityColor)),
                  ),
                  const SizedBox(width: 8),
                  Expanded(child: Text(widget.title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600))),
                  Icon(_expanded ? Icons.expand_less : Icons.expand_more, color: AppColors.textSecondary),
                ],
              ),
              if (_expanded) ...[
                const SizedBox(height: 12),
                Text(widget.description, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                const SizedBox(height: 8),
                Row(
                  children: [
                    _Tag('Code', widget.constraintCode),
                    const SizedBox(width: 8),
                    _Tag('Target', widget.targetRoom),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  final String label; final String value;
  const _Tag(this.label, this.value);
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(8)),
      child: Text('$label: $value', style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
    );
  }
}
