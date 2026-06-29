import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';
import '../../core/theme/typography.dart';
import '../floorplan/floorplan_painter.dart';
import 'editor_controller.dart';

class PropertyPanel extends StatelessWidget {
  final EditorController controller;
  const PropertyPanel({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<EditorState>(
      valueListenable: controller,
      builder: (context, state, _) {
        final room = state.selectedRoom;
        if (room == null) return const SizedBox.shrink();
        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10, offset: const Offset(0, -2))],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(room.name, style: AppTypography.titleLarge),
                  IconButton(icon: const Icon(Icons.close), onPressed: () => controller.selectRoom(null)),
                ],
              ),
              const SizedBox(height: 12),
              _buildRow('Area', '${room.area.toStringAsFixed(0)} sqft'),
              _buildRow('Type', _formatType(room.type)),
              _buildRow('Width', '${room.rect.width.toStringAsFixed(0)} ft'),
              _buildRow('Length', '${room.rect.height.toStringAsFixed(0)} ft'),
              _buildRow('Floor', room.rect.top < 200 ? 'Ground' : 'Upper'),
              _buildRow('Privacy', _getPrivacy(room.type)),
              const SizedBox(height: 8),
              Text('Vastu: ${_getVastu(room.type)}', style: AppTypography.bodyMedium),
            ],
          ),
        );
      },
    );
  }

  Widget _buildRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(label, style: const TextStyle(color: AppColors.textSecondary)), Text(value, style: AppTypography.bodyMedium)],
      ),
    );
  }

  String _formatType(String type) => type.replaceAll('_', ' ').split(' ').map((w) => w[0].toUpperCase() + w.substring(1)).join(' ');
  String _getPrivacy(String type) {
    if (['living', 'dining', 'entrance'].contains(type)) return 'Public';
    if (['bedroom', 'master_bedroom', 'bathroom'].contains(type)) return 'Private';
    if (['parking', 'utility', 'stair', 'corridor'].contains(type)) return 'Service';
    return 'Semi-Private';
  }
  String _getVastu(String type) {
    const m = {'kitchen': 'South-East', 'pooja': 'North-East', 'master_bedroom': 'South-West', 'living': 'North', 'bedroom': 'West', 'bathroom': 'North-West'};
    return m[type] ?? 'Any';
  }
}
