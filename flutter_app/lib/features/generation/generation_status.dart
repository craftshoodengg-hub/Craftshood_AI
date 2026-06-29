import 'package:flutter/foundation.dart';

enum GenerationStage {
  understandingRequirements,
  creatingSpaceProgram,
  generatingLayout,
  evaluatingDesign,
  optimizingLayout,
  finalizingResult,
  completed,
  error,
}

extension GenerationStageExtension on GenerationStage {
  String get displayName {
    switch (this) {
      case GenerationStage.understandingRequirements: return 'Understanding Requirements';
      case GenerationStage.creatingSpaceProgram: return 'Creating Space Program';
      case GenerationStage.generatingLayout: return 'Generating Initial Layout';
      case GenerationStage.evaluatingDesign: return 'Evaluating Design';
      case GenerationStage.optimizingLayout: return 'Optimizing Layout';
      case GenerationStage.finalizingResult: return 'Finalizing Result';
      case GenerationStage.completed: return 'Completed';
      case GenerationStage.error: return 'Error';
    }
  }

  double get progress {
    switch (this) {
      case GenerationStage.understandingRequirements: return 0.15;
      case GenerationStage.creatingSpaceProgram: return 0.30;
      case GenerationStage.generatingLayout: return 0.55;
      case GenerationStage.evaluatingDesign: return 0.75;
      case GenerationStage.optimizingLayout: return 0.90;
      case GenerationStage.finalizingResult:
      case GenerationStage.completed: return 1.0;
      case GenerationStage.error: return 0.0;
    }
  }

  bool get isTerminal => this == GenerationStage.completed || this == GenerationStage.error;
}

@immutable
class GenerationStatus {
  final GenerationStage currentStage;
  final String message;
  final Duration elapsedTime;
  final bool hasError;
  final String? errorMessage;

  const GenerationStatus({
    this.currentStage = GenerationStage.understandingRequirements,
    this.message = '',
    this.elapsedTime = Duration.zero,
    this.hasError = false,
    this.errorMessage,
  });

  double get progress => currentStage.progress;

  GenerationStatus copyWith({
    GenerationStage? currentStage,
    String? message,
    Duration? elapsedTime,
    bool? hasError,
    String? errorMessage,
  }) {
    return GenerationStatus(
      currentStage: currentStage ?? this.currentStage,
      message: message ?? this.message,
      elapsedTime: elapsedTime ?? this.elapsedTime,
      hasError: hasError ?? this.hasError,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}
