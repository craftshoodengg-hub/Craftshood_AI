import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/colors.dart';
import '../../core/theme/typography.dart';
import '../generation/generation_controller.dart';
import 'score_card.dart';
import 'metrics_grid.dart';
import 'room_summary_card.dart';
import 'improvement_card.dart';
import '../floorplan/floorplan_screen.dart';

class ResultsScreen extends ConsumerWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final genState = ref.watch(generationControllerProvider);
    final result = genState.result;
    if (result == null) {
      return Scaffold(appBar: AppBar(title: const Text('Results')), body: const Center(child: Text('No results available.')));
    }
    return Scaffold(
      appBar: AppBar(title: const Text('Design Results', style: AppTypography.headlineMedium), leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.of(context).pop())),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ScoreCard(score: result.finalScore, quality: result.quality),
              const SizedBox(height: 24),
              const Text('Metrics', style: AppTypography.titleLarge),
              const SizedBox(height: 12),
              MetricsGrid(evaluationScore: result.finalScore * 0.9, layoutScore: result.layoutScore),
              const SizedBox(height: 24),
              const Text('Room Summary', style: AppTypography.titleLarge),
              const SizedBox(height: 12),
              _buildRoomGrid(),
              const SizedBox(height: 24),
              const Text('Recommendations', style: AppTypography.titleLarge),
              const SizedBox(height: 12),
              ..._buildImprovements(),
              const SizedBox(height: 24),
              _buildActionButtons(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRoomGrid() {
    final rooms = [
      {'name': 'Living Room', 'type': 'living', 'area': 180.0, 'privacy': 'Public', 'floor': 'Ground'},
      {'name': 'Kitchen', 'type': 'kitchen', 'area': 140.0, 'privacy': 'Semi-Private', 'floor': 'Ground'},
      {'name': 'Master Bedroom', 'type': 'master_bedroom', 'area': 180.0, 'privacy': 'Private', 'floor': 'Ground'},
      {'name': 'Bedroom 2', 'type': 'bedroom', 'area': 140.0, 'privacy': 'Private', 'floor': 'Upper'},
      {'name': 'Bathroom', 'type': 'bathroom', 'area': 45.0, 'privacy': 'Private', 'floor': 'Ground'},
      {'name': 'Parking', 'type': 'parking', 'area': 220.0, 'privacy': 'Service', 'floor': 'Ground'},
    ];
    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = constraints.maxWidth > 600 ? 3 : 2;
        return GridView.builder(
          shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: crossAxisCount, childAspectRatio: 1.3, crossAxisSpacing: 12, mainAxisSpacing: 12),
          itemCount: rooms.length,
          itemBuilder: (context, index) {
            final r = rooms[index];
            return RoomSummaryCard(name: r['name'] as String, type: r['type'] as String, area: r['area'] as double, privacy: r['privacy'] as String, floor: r['floor'] as String);
          },
        );
      },
    );
  }

  List<Widget> _buildImprovements() {
    final items = [
      {'title': 'Increase Kitchen Ventilation', 'desc': 'Add window for cross ventilation.', 'priority': 'Recommendation', 'code': 'ENV_VENT', 'target': 'Kitchen'},
      {'title': 'Optimize Bedroom Privacy', 'desc': 'Place bedrooms away from entrance.', 'priority': 'Suggestion', 'code': 'PRIV_BED', 'target': 'Bedrooms'},
      {'title': 'Add Natural Light', 'desc': 'Increase window area in living room.', 'priority': 'Warning', 'code': 'LIGHT_LIV', 'target': 'Living Room'},
    ];
    return items.map((i) => Padding(padding: const EdgeInsets.only(bottom: 8), child: ImprovementCard(title: i['title'] as String, description: i['desc'] as String, priority: i['priority'] as String, constraintCode: i['code'] as String, targetRoom: i['target'] as String))).toList();
  }

  Widget _buildActionButtons(BuildContext context) {
    return Column(children: [
      SizedBox(width: double.infinity, height: 56, child: ElevatedButton.icon(onPressed: () => _showPlaceholder(context, 'Floor Plan'), icon: const Icon(Icons.map), label: const Text('Open Floor Plan'), style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))))),
      const SizedBox(height: 12),
      Row(children: [Expanded(child: OutlinedButton.icon(onPressed: () => _showPlaceholder(context, 'SVG'), icon: const Icon(Icons.image), label: const Text('Export SVG'))), const SizedBox(width: 12), Expanded(child: OutlinedButton.icon(onPressed: () => _showPlaceholder(context, 'DXF'), icon: const Icon(Icons.file_present), label: const Text('Export DXF')))]),
      const SizedBox(height: 12),
      TextButton.icon(onPressed: () => Navigator.of(context).pop(), icon: const Icon(Icons.refresh), label: const Text('Generate Again')),
    ]);
  }

  void _showPlaceholder(BuildContext context, String feature) {
    if (feature == 'Floor Plan') {
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => const FloorPlanScreen()));
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('\$feature coming in Phase 12B'), backgroundColor: AppColors.primary));
  }
}
