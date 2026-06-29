import 'package:flutter/material.dart';

class RoomStyle {
  final String type;
  final Color fillColor;
  final Color borderColor;
  final Color labelColor;

  const RoomStyle({required this.type, required this.fillColor, required this.borderColor, required this.labelColor});

  static const Map<String, Color> _typeColors = {
    'living': Color(0xFF42A5F5), 'dining': Color(0xFF66BB6A), 'kitchen': Color(0xFFFFCA28),
    'bedroom': Color(0xFFAB47BC), 'master_bedroom': Color(0xFF7E57C2), 'bathroom': Color(0xFF29B6F6),
    'common_bathroom': Color(0xFF4DD0E1), 'parking': Color(0xFF78909C), 'utility': Color(0xFF8D6E63),
    'office': Color(0xFF5C6BC0), 'pooja': Color(0xFFFFB74D), 'stair': Color(0xFF90A4AE),
    'balcony': Color(0xFF81C784), 'entrance': Color(0xFFA1887F), 'corridor': Color(0xFFBDBDBD), 'store': Color(0xFFAED581),
  };

  factory RoomStyle.forType(String type) {
    final color = _typeColors[type] ?? const Color(0xFF90A4AE);
    return RoomStyle(
      type: type, fillColor: color.withOpacity(0.12),
      borderColor: color.withOpacity(0.6), labelColor: color.withOpacity(0.9),
    );
  }

  static const selectedBorder = Color(0xFFFFC107);
  static const selectedFill = Color(0x33FFC107);
}
