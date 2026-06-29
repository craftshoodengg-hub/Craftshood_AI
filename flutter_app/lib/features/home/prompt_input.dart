import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class PromptInput extends StatelessWidget {
  final TextEditingController controller;
  final String? hintText;
  const PromptInput({super.key, required this.controller, this.hintText});

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      maxLines: 5,
      minLines: 3,
      decoration: InputDecoration(
        hintText: hintText ?? 'Modern east-facing 3BHK villa on a 40x60 plot with parking, pooja room and home office.',
        hintStyle: const TextStyle(color: AppColors.textSecondary, fontSize: 14),
        filled: true,
        fillColor: AppColors.surface,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
        contentPadding: const EdgeInsets.all(20),
      ),
    );
  }
}
