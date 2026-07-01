"""Helper utilities for DWG-to-DXF conversion guidance."""
from __future__ import annotations

from pathlib import Path


def recommended_converted_folder(source_folder: str) -> str:
    """Return the recommended DXF output folder for a DWG source folder."""
    return str(Path(source_folder) / "converted_dxf")


def conversion_instructions(source_folder: str, output_folder: str) -> str:
    """Return instructions for converting DWG files to DXF using ODA tools."""
    return (
        "ODA DWG to DXF Conversion Guide\n"
        "=================================\n"
        f"Source folder: {source_folder}\n"
        f"Output folder: {output_folder}\n\n"
        "Recommended workflow:\n"
        "1. Install the ODA File Converter or the ODA Cloud Converter.\n"
        "2. Set the source folder to the DWG folder path.\n"
        "3. Set the output folder to the desired DXF destination path.\n"
        "4. Configure the output format as DXF (AutoCAD DXF).\n"
        "5. Enable any desired options such as preserving layers, blocks, and text.\n"
        "6. Run the conversion and verify that DXF files appear in the output folder.\n\n"
        "Note: This helper only documents the expected workflow. It does not perform the conversion."
    )


def validate_converted_folder(output_folder: str) -> dict:
    """Validate the converted DXF output folder workflow."""
    folder = Path(output_folder)
    exists = folder.exists() and folder.is_dir()
    dxf_count = 0
    dwg_count = 0

    if exists:
        dxf_count = sum(1 for _ in folder.rglob("*.dxf"))
        dwg_count = sum(1 for _ in folder.rglob("*.dwg"))

    return {
        "exists": exists,
        "dxf_count": dxf_count,
        "dwg_count": dwg_count,
        "ready": dxf_count > 0,
    }
