import 'package:flutter/material.dart';
import 'room_widget.dart';

class RoomRect {
  final String id; final String name; final String type; final Rect rect; final double area;
  const RoomRect({required this.id, required this.name, required this.type, required this.rect, required this.area});
}

class FloorPlanPainter extends CustomPainter {
  final List<RoomRect> rooms; final String? selectedRoomId; final double zoomLevel;
  FloorPlanPainter({required this.rooms, this.selectedRoomId, this.zoomLevel = 1.0});

  @override
  void paint(Canvas canvas, Size size) {
    if (rooms.isEmpty) return;
    double minX = double.infinity, minY = double.infinity, maxX = double.negativeInfinity, maxY = double.negativeInfinity;
    for (final room in rooms) {
      if (room.rect.left < minX) minX = room.rect.left;
      if (room.rect.top < minY) minY = room.rect.top;
      if (room.rect.right > maxX) maxX = room.rect.right;
      if (room.rect.bottom > maxY) maxY = room.rect.bottom;
    }
    final contentCenterX = (minX + maxX) / 2;
    final contentCenterY = (minY + maxY) / 2;
    canvas.save();
    canvas.translate(size.width / 2, size.height / 2);
    canvas.scale(zoomLevel);
    canvas.translate(-contentCenterX, -contentCenterY);
    for (final room in rooms) {
      final style = RoomStyle.forType(room.type);
      final isSelected = room.id == selectedRoomId;
      final fillPaint = Paint()..color = isSelected ? RoomStyle.selectedFill : style.fillColor..style = PaintingStyle.fill;
      canvas.drawRRect(RRect.fromRectAndRadius(room.rect, const Radius.circular(4)), fillPaint);
      final borderPaint = Paint()..color = isSelected ? RoomStyle.selectedBorder : style.borderColor..style = PaintingStyle.stroke..strokeWidth = isSelected ? 2.5 : 1.0;
      canvas.drawRRect(RRect.fromRectAndRadius(room.rect, const Radius.circular(4)), borderPaint);
      final textPainter = TextPainter(
        text: TextSpan(text: '${room.name}\n${room.area.toStringAsFixed(0)} sqft', style: TextStyle(color: isSelected ? RoomStyle.selectedBorder : style.labelColor, fontSize: 8, fontWeight: isSelected ? FontWeight.bold : FontWeight.w500)),
        textDirection: TextDirection.ltr, textAlign: TextAlign.center,
      );
      textPainter.layout(maxWidth: room.rect.width);
      textPainter.paint(canvas, Offset(room.rect.center.dx - textPainter.width / 2, room.rect.center.dy - textPainter.height / 2));
    }
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant FloorPlanPainter oldDelegate) =>
      oldDelegate.selectedRoomId != selectedRoomId || oldDelegate.zoomLevel != zoomLevel || oldDelegate.rooms != rooms;
}
