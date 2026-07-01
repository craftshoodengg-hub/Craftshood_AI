"""Tests for the DWG dataset CLI runner."""
from __future__ import annotations

from pathlib import Path

import ezdxf
import pytest

from building_model_v2.pipeline.dwg_knowledge.dataset_cli import main


def _create_dxf(path: Path, layer: str = "A-WALL") -> None:
    document = ezdxf.new()
    modelspace = document.modelspace()
    modelspace.add_line((0, 0), (1, 0), dxfattribs={"layer": layer})
    document.saveas(path)


def test_invalid_directory_returns_1() -> None:
    exit_code = main(["--input", "nonexistent_dir", "--output", "."] )

    assert exit_code == 1


def test_empty_directory_generates_reports(tmp_path: Path) -> None:
    exit_code = main(["--input", str(tmp_path), "--output", str(tmp_path / "out")])

    assert exit_code == 0
    assert (tmp_path / "out" / "dataset_report.json").exists()
    assert (tmp_path / "out" / "dataset_report.md").exists()


def test_directory_with_dxf_files_generates_reports(tmp_path: Path) -> None:
    _create_dxf(tmp_path / "one.dxf")
    exit_code = main(["--input", str(tmp_path), "--output", str(tmp_path / "out")])

    assert exit_code == 0
    assert (tmp_path / "out" / "dataset_report.json").exists()
    assert (tmp_path / "out" / "dataset_report.md").exists()
    json_text = (tmp_path / "out" / "dataset_report.json").read_text(encoding="utf-8")
    assert "files_scanned" in json_text


def test_custom_output_directory(tmp_path: Path) -> None:
    _create_dxf(tmp_path / "one.dxf")
    out_dir = tmp_path / "custom_out"

    exit_code = main(["--input", str(tmp_path), "--output", str(out_dir)])

    assert exit_code == 0
    assert out_dir.exists()
    assert (out_dir / "dataset_report.json").exists()
    assert (out_dir / "dataset_report.md").exists()


def test_limit_option_respected(tmp_path: Path) -> None:
    _create_dxf(tmp_path / "a.dxf")
    _create_dxf(tmp_path / "b.dxf")
    exit_code = main(["--input", str(tmp_path), "--output", str(tmp_path / "out"), "--limit", "1"])

    assert exit_code == 0
    summary = (tmp_path / "out" / "dataset_report.json").read_text(encoding="utf-8")
    assert "\"files_scanned\": 1" in summary


def test_recursive_option_controls_scanning(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    _create_dxf(tmp_path / "root.dxf")
    _create_dxf(nested / "child.dxf")

    exit_code_non_recursive = main([
        "--input", str(tmp_path),
        "--output", str(tmp_path / "out1"),
        "--no-recursive",
    ])
    assert exit_code_non_recursive == 0
    summary_non_recursive = (tmp_path / "out1" / "dataset_report.json").read_text(encoding="utf-8")
    assert "\"files_scanned\": 1" in summary_non_recursive

    exit_code_recursive = main([
        "--input", str(tmp_path),
        "--output", str(tmp_path / "out2"),
    ])
    assert exit_code_recursive == 0
    summary_recursive = (tmp_path / "out2" / "dataset_report.json").read_text(encoding="utf-8")
    assert "\"files_scanned\": 2" in summary_recursive


def test_generated_report_files_contains_expected_sections(tmp_path: Path) -> None:
    _create_dxf(tmp_path / "one.dxf")
    exit_code = main(["--input", str(tmp_path), "--output", str(tmp_path / "out")])

    assert exit_code == 0
    markdown = (tmp_path / "out" / "dataset_report.md").read_text(encoding="utf-8")
    assert "# DWG Dataset Analysis Report" in markdown
    assert "Files scanned:" in markdown or "files_scanned" in markdown
