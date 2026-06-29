import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';
import 'generation_status.dart';

class GenerationProgressIndicator extends StatelessWidget {
  final GenerationStatus status;
  const GenerationProgressIndicator({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: 120,
          height: 120,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 120,
                height: 120,
                child: CircularProgressIndicator(
                  value: status.progress,
                  strokeWidth: 8,
                  backgroundColor: AppColors.surface,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    status.hasError ? AppColors.error : AppColors.accent,
                  ),
                ),
              ),
              Text(
                '\${(status.progress * 100).toInt()}%',
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.primary),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Text(
          status.currentStage.displayName,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          textAlign: TextAlign.center,
        ),
        if (status.message.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(
            status.message,
            style: const TextStyle(fontSize: 14, color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
        ],
      ],
    );
  }
}
