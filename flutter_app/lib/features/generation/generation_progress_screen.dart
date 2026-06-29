import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/colors.dart';
import '../../core/theme/typography.dart';
import 'generation_status.dart';
import 'generation_progress_indicator.dart';
import 'generation_stage_card.dart';

class GenerationProgressScreen extends ConsumerStatefulWidget {
  final String prompt;
  const GenerationProgressScreen({super.key, required this.prompt});

  @override
  ConsumerState<GenerationProgressScreen> createState() => _GenerationProgressScreenState();
}

class _GenerationProgressScreenState extends ConsumerState<GenerationProgressScreen>
    with TickerProviderStateMixin {
  late GenerationStatus _status;
  late AnimationController _fadeController;
  late AnimationController _slideController;

  @override
  void initState() {
    super.initState();
    _status = const GenerationStatus();
    _fadeController = AnimationController(vsync: this, duration: const Duration(milliseconds: 500));
    _slideController = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
    _fadeController.forward();
    _slideController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _slideController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Craftshood AI', style: AppTypography.headlineMedium),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: FadeTransition(
        opacity: _fadeController,
        child: SlideTransition(
          position: Tween<Offset>(begin: const Offset(0, 0.1), end: Offset.zero).animate(
            CurvedAnimation(parent: _slideController, curve: Curves.easeOut),
          ),
          child: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const SizedBox(height: 24),
                  const Text('Generating your design...', style: AppTypography.headlineMedium),
                  const SizedBox(height: 8),
                  Text(
                    widget.prompt,
                    style: const AppTypography.bodyMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),
                  GenerationProgressIndicator(status: _status),
                  const SizedBox(height: 32),
                  const Divider(),
                  const SizedBox(height: 16),
                  ...GenerationStage.values
                      .where((s) => s != GenerationStage.error)
                      .map((stage) => GenerationStageCard(stage: stage, currentStage: _status.currentStage)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
