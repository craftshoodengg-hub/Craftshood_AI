import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/colors.dart';
import '../../core/theme/typography.dart';
import '../generation/generation_controller.dart';
import 'prompt_input.dart';
import 'generate_button.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});
  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final _promptController = TextEditingController();

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  void _onGenerate() {
    final prompt = _promptController.text.trim();
    if (prompt.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a design prompt.'), backgroundColor: AppColors.error),
      );
      return;
    }
    ref.read(generationControllerProvider.notifier).generate(prompt);
  }

  @override
  Widget build(BuildContext context) {
    final genState = ref.watch(generationControllerProvider);

    ref.listen<GenerationStateData>(generationControllerProvider, (_, next) {
      if (next.state == GenerationState.error && next.errorMessage != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.errorMessage!), backgroundColor: AppColors.error),
        );
      }
    });

    return Scaffold(
      appBar: AppBar(title: const Text('Craftshood AI', style: AppTypography.headlineMedium)),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Describe your dream home.', style: AppTypography.headlineLarge),
              const SizedBox(height: 8),
              const Text('Enter your requirements in natural language and we will generate a floor plan for you.',
                  style: AppTypography.bodyMedium),
              const SizedBox(height: 24),
              PromptInput(controller: _promptController),
              const SizedBox(height: 16),
              GenerateButton(onPressed: _onGenerate, isLoading: genState.state == GenerationState.loading),
              const SizedBox(height: 32),
              const Text('Templates', style: AppTypography.titleLarge),
              const SizedBox(height: 8),
              const Card(child: ListTile(title: Text('2BHK Apartment'), subtitle: Text('Modern apartment with parking'))),
              const Card(child: ListTile(title: Text('3BHK Villa'), subtitle: Text('East-facing villa with pooja room'))),
              const Card(child: ListTile(title: Text('4BHK Duplex'), subtitle: Text('Traditional duplex with parking'))),
            ],
          ),
        ),
      ),
    );
  }
}
