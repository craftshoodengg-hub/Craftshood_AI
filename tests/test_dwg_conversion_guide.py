"""Tests for the DWG conversion guide helper module."""
from __future__ import annotations

from pathlib import Path

from building_model_v2.pipeline.dwg_knowledge import (
    recommended_converted_folder,
    conversion_instructions,
    validate_converted_folder,
)


def test_recommended_converted_folder_returns_converted_subfolder(tmp_path: Path) -> None:
    source = str(tmp_path / "dwg_source")
    expected = str((tmp_path / "dwg_source") / "converted_dxf")

    actual = recommended_converted_folder(source)

    assert actual == expected


def test_conversion_instructions_contains_source_and_output_paths(tmp_path: Path) -> None:
    source = str(tmp_path / "dwg_source")
    output = str(tmp_path / "converted_dxf")

    instructions = conversion_instructions(source, output)

    assert source in instructions
    assert output in instructions
    assert "ODA DWG to DXF Conversion Guide" in instructions
    assert "does not perform the conversion" in instructions


def test_validate_converted_folder_with_empty_folder(tmp_path: Path) -> None:
    folder = tmp_path / "converted_dxf"
    folder.mkdir()

    result = validate_converted_folder(str(folder))

    assert result == {
        "exists": True,
        "dxf_count": 0,
        "dwg_count": 0,
        "ready": False,
    }


def test_validate_converted_folder_counts_dxf_and_dwg_files(tmp_path: Path) -> None:
    folder = tmp_path / "converted_dxf"
    folder.mkdir()
    (folder / "one.dxf").write_text("test", encoding="utf-8")
    (folder / "two.dxf").write_text("test", encoding="utf-8")
    (folder / "legacy.dwg").write_text("test", encoding="utf-8")
    nested = folder / "nested"
    nested.mkdir()
    (nested / "nested.dxf").write_text("test", encoding="utf-8")

    result = validate_converted_folder(str(folder))

    assert result == {
        "exists": True,
        "dxf_count": 3,
        "dwg_count": 1,
        "ready": True,
    }


def test_validate_converted_folder_nonexistent_folder(tmp_path: Path) -> None:
    result = validate_converted_folder(str(tmp_path / "missing"))

    assert result == {
        "exists": False,
        "dxf_count": 0,
        "dwg_count": 0,
        "ready": False,
    }
