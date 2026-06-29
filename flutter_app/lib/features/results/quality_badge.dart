import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class QualityBadge extends StatelessWidget {
  final String quality;
  const QualityBadge({super.key, required this.quality});

  Color get _backgroundColor {
    switch (quality.toLowerCase()) {
      case 'excellent': return AppColors.success.withOpacity(0.15);
      case 'good': return AppColors.primary.withOpacity(0.15);
      case 'fair': return AppColors.accent.withOpacity(0.15);
      default: return AppColors.error.withOpacity(0.15);
    }
  }

  Color get _textColor {
    switch (quality.toLowerCase()) {
      case 'excellent': return AppColors.success;
      case 'good': return AppColors.primary;
      case 'fair': return AppColors.accentDark;
      default: return AppColors.error;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: _backgroundColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        quality.toUpperCase(),
        style: TextStyle(
          color: _textColor,
          fontWeight: FontWeight.bold,
          fontSize: 12,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}
