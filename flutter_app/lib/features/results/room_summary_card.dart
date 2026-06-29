import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class RoomSummaryCard extends StatelessWidget {
  final String name;
  final String type;
  final double area;
  final String privacy;
  final String floor;
  const RoomSummaryCard({super.key, required this.name, required this.type, required this.area, required this.privacy, required this.floor});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(8)),
                  child: Text(type, style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _InfoChip(icon: Icons.square_foot, label: '${area.toStringAsFixed(0)} sqft'),
                const SizedBox(width: 8),
                _InfoChip(icon: Icons.layers, label: floor),
              ],
            ),
            const SizedBox(height: 8),
            _InfoChip(icon: Icons.lock_outline, label: privacy),
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon; final String label;
  const _InfoChip({required this.icon, required this.label});
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: AppColors.textSecondary),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
      ],
    );
  }
}
