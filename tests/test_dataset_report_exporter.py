"""Tests for the DWG dataset report exporter."""
from __future__ import annotations

from pathlib import Path

from building_model_v2.pipeline.dwg_knowledge import DatasetReportExporter


def test_to_json_produces_pretty_output() -> None:
    exporter = DatasetReportExporter()
    summary = {
        "files_scanned": 1,
        "files_failed": 0,
        "entity_totals": {"entity_count": 2},
        "layer_names": {"A-WALL": 1},
        "block_names": {},
        "text_values": {"Door": 1},
        "file_summaries": [
            {
                "file_path": "a.dxf",
                "entity_count": 2,
                "layers": ["A-WALL"],
                "blocks": [],
                "texts": ["Door"],
            }
        ],
    }

    json_text = exporter.to_json(summary)

    assert json_text.startswith("{")
    assert "\n  \"files_scanned\"" in json_text
    assert "\"A-WALL\"" in json_text
    assert "\"Door\"" in json_text


def test_to_markdown_includes_sections() -> None:
    exporter = DatasetReportExporter()
    summary = {
        "files_scanned": 1,
        "files_failed": 0,
        "entity_totals": {"entity_count": 2},
        "layer_names": {"A-WALL": 1},
        "block_names": {"DOOR_BLOCK": 1},
        "text_values": {"Door": 1},
        "failed_files": [],
        "file_summaries": [
            {
                "file_path": "a.dxf",
                "entity_count": 2,
                "layers": ["A-WALL"],
                "blocks": ["DOOR_BLOCK"],
                "texts": ["Door"],
            }
        ],
    }

    markdown = exporter.to_markdown(summary)

    assert "# DWG Dataset Analysis Report" in markdown
    assert "## Entity Totals" in markdown
    assert "## Top Layers" in markdown
    assert "## Top Blocks" in markdown
    assert "## Top Text Values" in markdown
    assert "## Failed Files" in markdown
    assert "## File Summaries" in markdown
    assert "**A-WALL**: 1" in markdown
    assert "**DOOR_BLOCK**: 1" in markdown
    assert "**Door**: 1" in markdown
    assert "### a.dxf" in markdown


def test_save_json_writes_file(tmp_path: Path) -> None:
    exporter = DatasetReportExporter()
    summary = {"files_scanned": 0, "files_failed": 0, "entity_totals": {}, "layer_names": {}, "block_names": {}, "text_values": {}, "file_summaries": []}
    path = str(tmp_path / "report.json")

    output_path = exporter.save_json(summary, path)

    assert output_path == path
    content = Path(output_path).read_text(encoding="utf-8")
    assert "\"files_scanned\"" in content
    assert "No items available" not in content


def test_save_markdown_writes_file(tmp_path: Path) -> None:
    exporter = DatasetReportExporter()
    summary = {
        "files_scanned": 0,
        "files_failed": 0,
        "failed_files": [],
        "entity_totals": {},
        "layer_names": {},
        "block_names": {},
        "text_values": {},
        "file_summaries": [],
    }
    path = str(tmp_path / "report.md")

    output_path = exporter.save_markdown(summary, path)

    assert output_path == path
    content = Path(output_path).read_text(encoding="utf-8")
    assert "# DWG Dataset Analysis Report" in content
    assert "No entity totals available." in content
    assert "No items available." in content
    assert "No failed files." in content
    assert "No file summaries available." in content


def test_markdown_includes_failed_files_section() -> None:
    exporter = DatasetReportExporter()
    summary = {
        "files_scanned": 0,
        "files_failed": 1,
        "failed_files": [
            {
                "file_path": "invalid.dwg",
                "reason": "Failed to read DWG file 'invalid.dwg'. Native DWG may require conversion to DXF before analysis.",
            }
        ],
        "entity_totals": {},
        "layer_names": {},
        "block_names": {},
        "text_values": {},
        "file_summaries": [],
    }

    markdown = exporter.to_markdown(summary)

    assert "## Failed Files" in markdown
    assert "invalid.dwg" in markdown
    assert "Failed to read DWG file" in markdown


def test_to_json_is_deterministic() -> None:
    exporter = DatasetReportExporter()
    summary = {
        "files_scanned": 1,
        "files_failed": 1,
        "failed_files": [{"file_path": "bad.dwg", "reason": "Failed to read DWG file"}],
        "entity_totals": {"entity_count": 2, "lines": 1},
        "layer_names": {"A-WALL": 1, "B-WALL": 2},
        "block_names": {"DOOR_BLOCK": 1},
        "text_values": {"Door": 1},
        "file_summaries": [
            {
                "file_path": "b.dxf",
                "entity_count": 1,
                "layers": ["B-WALL"],
                "blocks": [],
                "texts": [],
            },
            {
                "file_path": "a.dxf",
                "entity_count": 1,
                "layers": ["A-WALL"],
                "blocks": [],
                "texts": [],
            },
        ],
    }

    first = exporter.to_json(summary)
    second = exporter.to_json(summary)

    assert first == second
