import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';
import 'editor_controller.dart';

class EditingToolbar extends StatelessWidget {
  final EditorController controller;
  const EditingToolbar({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<EditorState>(
      valueListenable: controller,
      builder: (context, state, _) {
        return AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.15), blurRadius: 10, offset: const Offset(0, 4))],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _ToolButton(icon: Icons.near_me, label: 'Select', isActive: state.mode == EditingMode.select, onPressed: () => controller.setMode(EditingMode.select)),
              _ToolButton(icon: Icons.open_with, label: 'Move', isActive: state.mode == EditingMode.move, onPressed: () => controller.setMode(EditingMode.move)),
              _ToolButton(icon: Icons.crop_free, label: 'Resize', isActive: state.mode == EditingMode.resize, onPressed: () => controller.setMode(EditingMode.resize)),
              const SizedBox(width: 4, child: VerticalDivider(width: 1)),
              _ToolButton(icon: Icons.edit, label: 'Rename', onPressed: state.selectedRoomId != null ? () => _showRenameDialog(context, state.selectedRoomId!) : null),
              _ToolButton(icon: Icons.copy, label: 'Duplicate', onPressed: state.selectedRoomId != null ? () => controller.duplicateRoom(state.selectedRoomId!) : null),
              _ToolButton(icon: Icons.delete, label: 'Delete', onPressed: state.selectedRoomId != null ? () => controller.deleteRoom(state.selectedRoomId!) : null),
            ],
          ),
        );
      },
    );
  }

  void _showRenameDialog(BuildContext context, String roomId) {
    final room = controller.value.rooms.firstWhere((r) => r.id == roomId);
    final textCtrl = TextEditingController(text: room.name);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Rename Room'),
        content: TextField(controller: textCtrl, decoration: const InputDecoration(labelText: 'Room Name')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          TextButton(onPressed: () { controller.renameRoom(roomId, textCtrl.text); Navigator.pop(ctx); }, child: const Text('Save')),
        ],
      ),
    );
  }
}

class _ToolButton extends StatelessWidget {
  final IconData icon; final String label; final VoidCallback? onPressed; final bool isActive;
  const _ToolButton({required this.icon, required this.label, this.onPressed, this.isActive = false});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(icon, size: 20, color: isActive ? AppColors.primary : (onPressed != null ? AppColors.textPrimary : AppColors.textSecondary)),
      tooltip: label,
      onPressed: onPressed,
      splashRadius: 20,
    );
  }
}
