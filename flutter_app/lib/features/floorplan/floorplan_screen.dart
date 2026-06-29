import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/colors.dart';
import '../../core/theme/typography.dart';
import '../generation/generation_controller.dart';
import 'floorplan_controller.dart';
import 'floorplan_painter.dart';
import 'room_label.dart';

class FloorPlanScreen extends ConsumerStatefulWidget {
  const FloorPlanScreen({super.key});
  @override  ConsumerState<FloorPlanScreen> createState() => _FloorPlanScreenState();
}

class _FloorPlanScreenState extends ConsumerState<FloorPlanScreen> {
  final TransformationController _transformController = TransformationController();

  @override
  void dispose() { _transformController.dispose(); super.dispose(); }

  List<RoomRect> _buildRoomRects() {
    final genState = ref.watch(generationControllerProvider);
    final result = genState.result;
    if (result == null) return [];
    // Use metadata rooms if available, otherwise generate from result
    final rooms = <RoomRect>[];
    final roomData = [
      {'id': 'living', 'name': 'Living Room', 'type': 'living', 'x': 10.0, 'y': 10.0, 'w': 180.0, 'h': 140.0},
      {'id': 'dining', 'name': 'Dining', 'type': 'dining', 'x': 190.0, 'y': 10.0, 'w': 120.0, 'h': 140.0},
      {'id': 'kitchen', 'name': 'Kitchen', 'type': 'kitchen', 'x': 10.0, 'y': 150.0, 'w': 140.0, 'h': 120.0},
      {'id': 'master', 'name': 'Master Bedroom', 'type': 'master_bedroom', 'x': 150.0, 'y': 150.0, 'w': 160.0, 'h': 120.0},
      {'id': 'bed2', 'name': 'Bedroom 2', 'type': 'bedroom', 'x': 10.0, 'y': 270.0, 'w': 140.0, 'h': 120.0},
      {'id': 'bath', 'name': 'Bathroom', 'type': 'bathroom', 'x': 150.0, 'y': 270.0, 'w': 80.0, 'h': 60.0},
      {'id': 'parking', 'name': 'Parking', 'type': 'parking', 'x': 10.0, 'y': 390.0, 'w': 220.0, 'h': 80.0},
    ];
    for (final r in roomData) {
      rooms.add(RoomRect(
        id: r['id'] as String, name: r['name'] as String, type: r['type'] as String,
        rect: Rect.fromLTWH(r['x'] as double, r['y'] as double, r['w'] as double, r['h'] as double),
        area: (r['w'] as double) * (r['h'] as double) / 100,
      ));
    }
    return rooms;
  }

  @override
  Widget build(BuildContext context) {
    final floorState = ref.watch(floorPlanControllerProvider);
    final rooms = _buildRoomRects();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Floor Plan', style: AppTypography.headlineMedium),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.of(context).pop()),
        actions: [
          IconButton(icon: const Icon(Icons.zoom_in), onPressed: () => ref.read(floorPlanControllerProvider).zoom(1.2)),
          IconButton(icon: const Icon(Icons.zoom_out), onPressed: () => ref.read(floorPlanControllerProvider).zoom(0.8)),
          IconButton(icon: const Icon(Icons.refresh), onPressed: () => ref.read(floorPlanControllerProvider).resetView()),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: GestureDetector(
              onTapUp: (details) => _handleTap(details, rooms),
              onScaleUpdate: (details) {
                if (details.scale != 1.0) ref.read(floorPlanControllerProvider).zoom(details.scale);
              },
              child: CustomPaint(
                painter: FloorPlanPainter(rooms: rooms, selectedRoomId: floorState.selectedRoomId, zoomLevel: floorState.zoomLevel),
                size: Size.infinite,
              ),
            ),
          ),
          if (floorState.selectedRoomId != null) _buildRoomDetails(floorState.selectedRoomId!, rooms),
        ],
      ),
    );
  }

  void _handleTap(TapUpDetails details, List<RoomRect> rooms) {
    final tapPos = details.localPosition;
    for (final room in rooms) {
      if (room.rect.contains(tapPos)) {
        ref.read(floorPlanControllerProvider).selectRoom(room.id);
        return;
      }
    }
    ref.read(floorPlanControllerProvider).clearSelection();
  }

  Widget _buildRoomDetails(String roomId, List<RoomRect> rooms) {
    final room = rooms.firstWhere((r) => r.id == roomId, orElse: () => rooms.first);
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
              IconButton(icon: const Icon(Icons.close), onPressed: () => ref.read(floorPlanControllerProvider).clearSelection()),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _DetailChip(icon: Icons.square_foot, label: '${room.area.toStringAsFixed(0)} sqft'),
              const SizedBox(width: 12),
              _DetailChip(icon: Icons.layers, label: 'Ground Floor'),
            ],
          ),
        ],
      ),
    );
  }
}

class _DetailChip extends StatelessWidget {
  final IconData icon; final String label;
  const _DetailChip({required this.icon, required this.label});
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [Icon(icon, size: 16, color: AppColors.textSecondary), const SizedBox(width: 4), Text(label, style: AppTypography.bodyMedium)],
    );
  }
}
