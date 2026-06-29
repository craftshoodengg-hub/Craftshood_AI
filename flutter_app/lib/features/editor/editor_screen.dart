import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';
import '../../core/theme/typography.dart';
import '../floorplan/floorplan_painter.dart';
import 'editor_controller.dart';
import 'editing_toolbar.dart';
import 'property_panel.dart';

class EditorScreen extends StatefulWidget {
  final List<RoomRect> initialRooms;
  const EditorScreen({super.key, required this.initialRooms});

  @override
  State<EditorScreen> createState() => _EditorScreenState();
}

class _EditorScreenState extends State<EditorScreen> {
  late final EditorController _controller;

  @override
  void initState() {
    super.initState();
    _controller = EditorController();
    _controller.initRooms(widget.initialRooms);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Floor Plan', style: AppTypography.headlineMedium),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.of(context).pop()),
        actions: [
          ValueListenableBuilder<EditorState>(
            valueListenable: _controller,
            builder: (context, state, _) => Row(children: [
              IconButton(icon: const Icon(Icons.undo), onPressed: _controller.canUndo ? () => _controller.undo() : null),
              IconButton(icon: const Icon(Icons.redo), onPressed: _controller.canRedo ? () => _controller.redo() : null),
            ]),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Floor plan canvas
          Positioned.fill(
            child: GestureDetector(
              onTapUp: (details) => _handleTap(details),
              onPanUpdate: (details) => _handlePan(details),
              onScaleUpdate: (details) {
                if (details.scale != 1.0) _controller.zoom(details.scale);
              },
              child: CustomPaint(
                painter: FloorPlanPainter(
                  rooms: _controller.value.rooms,
                  selectedRoomId: _controller.value.selectedRoomId,
                  zoomLevel: _controller.value.zoomLevel,
                ),
                size: Size.infinite,
              ),
            ),
          ),
          // Floating toolbar
          Positioned(
            top: 16,
            left: 0,
            right: 0,
            child: Center(child: EditingToolbar(controller: _controller)),
          ),
          // Property panel at bottom
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: PropertyPanel(controller: _controller),
          ),
        ],
      ),
    );
  }

  void _handleTap(TapUpDetails details) {
    final tapPos = details.localPosition;
    for (final room in _controller.value.rooms) {
      if (room.rect.contains(tapPos)) {
        _controller.selectRoom(room.id);
        return;
      }
    }
    _controller.selectRoom(null);
  }

  void _handlePan(DragUpdateDetails details) {
    final state = _controller.value;
    if (state.selectedRoomId != null && state.mode == EditingMode.move) {
      _controller.moveRoom(state.selectedRoomId!, details.delta.dx, details.delta.dy);
    } else {
      _controller.pan(-details.delta);
    }
  }
}
