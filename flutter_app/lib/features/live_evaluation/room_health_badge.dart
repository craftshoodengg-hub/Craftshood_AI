import 'package:flutter/material.dart';

enum RoomHealth { good, warning, error, notEvaluated }

class RoomHealthBadge {
  static final Map<RoomHealth, Color> _fillColors = {
    RoomHealth.good: const Color(0x33388E3C), RoomHealth.warning: const Color(0x33FFA000),
    RoomHealth.error: const Color(0x33D32F2F), RoomHealth.notEvaluated: Colors.transparent,
  };
  static final Map<RoomHealth, Color> _borderColors = {
    RoomHealth.good: const Color(0xFF388E3C), RoomHealth.warning: const Color(0xFFFFA000),
    RoomHealth.error: const Color(0xFFD32F2F), RoomHealth.notEvaluated: const Color(0xFFBDBDBD),
  };
  static Color fill(RoomHealth h) => _fillColors[h]!;
  static Color border(RoomHealth h) => _borderColors[h]!;
  static RoomHealth fromIssueCount(int errors, int warnings) {
    if (errors > 0) return RoomHealth.error;
    if (warnings > 0) return RoomHealth.warning;
    return RoomHealth.good;
  }
}
