import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';
import 'generation_status.dart';

class GenerationStageCard extends StatelessWidget {
  final GenerationStage stage;
  final GenerationStage currentStage;
  const GenerationStageCard({super.key, required this.stage, required this.currentStage});

  bool get _isCompleted => stage.index < currentStage.index;
  bool get _isCurrent => stage == currentStage;
  bool get _isFuture => stage.index > currentStage.index;

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: _isCurrent ? AppColors.primary.withOpacity(0.05) : AppColors.card,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _isCurrent ? AppColors.primary : AppColors.divider,
          width: _isCurrent ? 2 : 1,
        ),
      ),
      child: ListTile(
        leading: AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: _buildIcon(),
        ),
        title: Text(
          stage.displayName,
          style: TextStyle(
            fontWeight: _isCurrent ? FontWeight.w600 : FontWeight.normal,
            color: _isFuture ? AppColors.textSecondary : AppColors.textPrimary,
          ),
        ),
        trailing: _isCurrent && !stage.isTerminal
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.accent),
              )
            : null,
      ),
    );
  }

  Widget _buildIcon() {
    if (_isCompleted) {
      return const Icon(Icons.check_circle, color: AppColors.success, key: ValueKey('check'));
    }
    if (_isCurrent) {
      return const Icon(Icons.radio_button_checked, color: AppColors.primary, key: ValueKey('current'));
    }
    return const Icon(Icons.radio_button_unchecked, color: AppColors.textSecondary, key: ValueKey('future'));
  }
}
