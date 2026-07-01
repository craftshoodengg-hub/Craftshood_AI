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
