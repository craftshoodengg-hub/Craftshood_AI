"""Export DWG dataset analysis summaries to JSON and Markdown."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DatasetReportExporter:
    """Export dataset analyzer summaries as JSON and Markdown."""

    def to_json(self, summary: dict[str, Any]) -> str:
        return json.dumps(summary, indent=2, sort_keys=True)

    def to_markdown(self, summary: dict[str, Any]) -> str:
        title = "# DWG Dataset Analysis Report"
        lines: list[str] = [title, ""]

        files_scanned = summary.get("files_scanned", 0)
        files_failed = summary.get("files_failed", 0)
        lines.append(f"- **Files scanned:** {files_scanned}")
        lines.append(f"- **Files failed:** {files_failed}")
        lines.append("")

        lines.append("## Entity Totals")
        entity_totals = summary.get("entity_totals", {})
        if entity_totals:
            for key, value in sorted(entity_totals.items()):
                lines.append(f"- **{key}**: {value}")
        else:
            lines.append("No entity totals available.")
        lines.append("")

        lines.append("## Top Layers")
        lines.extend(self._format_top_counts(summary.get("layer_names", {})))
        lines.append("")

        lines.append("## Top Blocks")
        lines.extend(self._format_top_counts(summary.get("block_names", {})))
        lines.append("")

        lines.append("## Top Text Values")
        lines.extend(self._format_top_counts(summary.get("text_values", {})))
        lines.append("")

        lines.append("## Room Statistics")
        room_totals = summary.get("room_totals", {})
        total_rooms = summary.get("total_rooms", 0)
        lines.append(f"- **Total Rooms:** {total_rooms}")
        if room_totals:
            for room_type in [
                "Bedroom",
                "Kitchen",
                "Living",
                "Dining",
                "Toilet",
                "Balcony",
                "Parking",
                "Utility",
                "Pooja",
                "Stair",
                "Store",
            ]:
                lines.append(f"- **{room_type}**: {room_totals.get(room_type, 0)}")
        else:
            lines.append("No room statistics available.")
        lines.append("")

        lines.append("## Plot Statistics")
        plot_stats = summary.get("plot_statistics", {})
        total_detected = plot_stats.get("total_detected", 0)
        lines.append(f"- **Detected Plots:** {total_detected}")
        if total_detected > 0:
            lines.append(f"- **Average Width:** {plot_stats.get('average_width')}")
            lines.append(f"- **Average Depth:** {plot_stats.get('average_depth')}")
            lines.append(f"- **Average Area:** {plot_stats.get('average_area')}")
            orientations = plot_stats.get("orientations", {})
            lines.append(f"- **North Facing:** {orientations.get('North', 0)}")
            lines.append(f"- **South Facing:** {orientations.get('South', 0)}")
            lines.append(f"- **East Facing:** {orientations.get('East', 0)}")
            lines.append(f"- **West Facing:** {orientations.get('West', 0)}")
            largest_plot = plot_stats.get("largest_plot")
            smallest_plot = plot_stats.get("smallest_plot")
            if largest_plot:
                lines.append(f"- **Largest Plot:** {largest_plot.get('width')} x {largest_plot.get('depth')} = {largest_plot.get('area')} ({largest_plot.get('file')})")
            if smallest_plot:
                lines.append(f"- **Smallest Plot:** {smallest_plot.get('width')} x {smallest_plot.get('depth')} = {smallest_plot.get('area')} ({smallest_plot.get('file')})")
        else:
            lines.append("No plot information detected.")
        lines.append("")

        lines.append("## Door & Window Statistics")
        door_window_stats = summary.get("door_window_statistics", {})
        lines.append(f"- **Total Doors:** {door_window_stats.get('total_doors', 0)}")
        lines.append(f"- **Total Windows:** {door_window_stats.get('total_windows', 0)}")
        lines.append(f"- **Files with Doors:** {door_window_stats.get('files_with_doors', 0)}")
        lines.append(f"- **Files with Windows:** {door_window_stats.get('files_with_windows', 0)}")
        lines.append(f"- **Average Doors per File:** {door_window_stats.get('average_doors_per_file', 0.0)}")
        lines.append(f"- **Average Windows per File:** {door_window_stats.get('average_windows_per_file', 0.0)}")
        lines.append("")

        lines.append("## Failed Files")
        failed_files = summary.get("failed_files", [])
        if failed_files:
            for failed in failed_files:
                lines.append(f"- **{failed.get('file_path', '<unknown>')}**: {failed.get('reason', 'Unknown reason')}")
        else:
            lines.append("No failed files.")
        lines.append("")

        lines.append("## File Summaries")
        file_summaries = summary.get("file_summaries", [])
        if file_summaries:
            for file_summary in file_summaries:
                lines.extend(self._format_file_summary(file_summary))
        else:
            lines.append("No file summaries available.")

        return "\n".join(lines)

    def save_json(self, summary: dict[str, Any], output_path: str) -> str:
        path = Path(output_path)
        path.write_text(self.to_json(summary), encoding="utf-8")
        return str(path)

    def save_markdown(self, summary: dict[str, Any], output_path: str) -> str:
        path = Path(output_path)
        path.write_text(self.to_markdown(summary), encoding="utf-8")
        return str(path)

    def _format_top_counts(self, counts: dict[str, int]) -> list[str]:
        if not counts:
            return ["No items available."]

        items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return [f"- **{name}**: {count}" for name, count in items]

    def _format_file_summary(self, file_summary: dict[str, Any]) -> list[str]:
        lines = [f"### {file_summary.get('file_path', '<unknown>')}", ""]
        lines.append(f"- Entity count: {file_summary.get('entity_count', 0)}")
        layers = file_summary.get("layers", [])
        blocks = file_summary.get("blocks", [])
        texts = file_summary.get("texts", [])
        lines.append(f"- Layers: {', '.join(layers) if layers else 'None'}")
        lines.append(f"- Blocks: {', '.join(blocks) if blocks else 'None'}")
        lines.append(f"- Texts: {', '.join(texts) if texts else 'None'}")
        lines.append("")
        return lines
