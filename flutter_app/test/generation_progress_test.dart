import 'package:flutter_test/flutter_test.dart';
import 'package:craftshood_ai/features/generation/generation_status.dart';

void main() {
  group('GenerationStage', () {
    test('displayName returns correct values', () {
      expect(GenerationStage.understandingRequirements.displayName, 'Understanding Requirements');
      expect(GenerationStage.creatingSpaceProgram.displayName, 'Creating Space Program');
      expect(GenerationStage.generatingLayout.displayName, 'Generating Initial Layout');
      expect(GenerationStage.evaluatingDesign.displayName, 'Evaluating Design');
      expect(GenerationStage.optimizingLayout.displayName, 'Optimizing Layout');
      expect(GenerationStage.finalizingResult.displayName, 'Finalizing Result');
      expect(GenerationStage.completed.displayName, 'Completed');
      expect(GenerationStage.error.displayName, 'Error');
    });

    test('progress returns correct values', () {
      expect(GenerationStage.understandingRequirements.progress, 0.15);
      expect(GenerationStage.creatingSpaceProgram.progress, 0.30);
      expect(GenerationStage.generatingLayout.progress, 0.55);
      expect(GenerationStage.evaluatingDesign.progress, 0.75);
      expect(GenerationStage.optimizingLayout.progress, 0.90);
      expect(GenerationStage.finalizingResult.progress, 1.0);
      expect(GenerationStage.completed.progress, 1.0);
      expect(GenerationStage.error.progress, 0.0);
    });

    test('isTerminal identifies terminal stages', () {
      expect(GenerationStage.completed.isTerminal, true);
      expect(GenerationStage.error.isTerminal, true);
      expect(GenerationStage.understandingRequirements.isTerminal, false);
      expect(GenerationStage.finalizingResult.isTerminal, false);
    });
  });

  group('GenerationStatus', () {
    test('default values', () {
      const status = GenerationStatus();
      expect(status.currentStage, GenerationStage.understandingRequirements);
      expect(status.progress, 0.15);
      expect(status.hasError, false);
      expect(status.elapsedTime, Duration.zero);
    });

    test('copyWith updates fields', () {
      const status = GenerationStatus();
      final updated = status.copyWith(
        currentStage: Stage.evaluatingDesign,
        message: 'Evaluating...',
        hasError: true,
      );
      expect(updated.currentStage, Stage.evaluatingDesign);
      expect(updated.message, 'Evaluating...');
      expect(updated.hasError, true);
      expect(updated.progress, 0.75);
    });

    test('progress reflects current stage', () {
      const status1 = GenerationStatus(currentStage: Stage.understandingRequirements);
      expect(status1.progress, 0.15);
      const status2 = GenerationStatus(currentStage: Stage.completed);
      expect(status2.progress, 1.0);
    });
  });
}
