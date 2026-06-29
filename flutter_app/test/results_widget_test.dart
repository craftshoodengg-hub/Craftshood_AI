import 'package:flutter_test/flutter_test.dart';
import 'package:craftshood_ai/features/results/quality_badge.dart';
import 'package:craftshood_ai/features/results/score_card.dart';
import 'package:craftshood_ai/features/results/metrics_grid.dart';
import 'package:craftshood_ai/features/results/room_summary_card.dart';
import 'package:craftshood_ai/features/results/improvement_card.dart';

void main() {
  group('QualityBadge', () {
    testWidgets('displays quality text', (tester) async {
      await tester.pumpWidget(const MaterialApp(home: Scaffold(body: QualityBadge(quality: 'Excellent'))));
      expect(find.text('EXCELLENT'), findsOneWidget);
    });

    testWidgets('displays different qualities', (tester) async {
      await tester.pumpWidget(const MaterialApp(home: Scaffold(body: QualityBadge(quality: 'Good'))));
      expect(find.text('GOOD'), findsOneWidget);
    });
  });

  group('ScoreCard', () {
    testWidgets('displays score', (tester) async {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: ScoreCard(score: 96.0, quality: 'Excellent'))));
      expect(find.text('96'), findsOneWidget);
    });
  });

  group('MetricsGrid', () {
    testWidgets('displays metrics', (tester) async {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: MetricsGrid(evaluationScore: 85.0, layoutScore: 90.0))));
      expect(find.text('Evaluation'), findsOneWidget);
      expect(find.text('Layout'), findsOneWidget);
    });
  });

  group('RoomSummaryCard', () {
    testWidgets('displays room info', (tester) async {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: RoomSummaryCard(name: 'Living Room', type: 'living', area: 180.0, privacy: 'Public', floor: 'Ground'))));
      expect(find.text('Living Room'), findsOneWidget);
    });
  });

  group('ImprovementCard', () {
    testWidgets('displays improvement title', (tester) async {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: ImprovementCard(title: 'Test', description: 'Desc', priority: 'Warning', constraintCode: 'CODE', targetRoom: 'Kitchen'))));
      expect(find.text('Test'), findsOneWidget);
    });
  });
}
