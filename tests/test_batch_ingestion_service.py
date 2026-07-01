"""Tests for the DWG batch ingestion service."""
from __future__ import annotations

from pathlib import Path

import ezdxf

from building_model_v2.pipeline.dwg_knowledge import (
    BatchIngestionService,
    DwgReference,
    EzDXFFeatureExtractor,
    KnowledgeRepository,
)


def _write_dxf(tmp_path: Path, name: str, entity_setup=None) -> Path:
    path = tmp_path / name
    document = ezdxf.new()
    modelspace = document.modelspace()
    if entity_setup is not None:
        entity_setup(modelspace)
    document.saveas(path)
    return path


def _write_dwg(tmp_path: Path, name: str) -> Path:
    return _write_dxf(tmp_path, name)


def _make_line_dxf(tmp_path: Path) -> Path:
    return _write_dxf(tmp_path, "line.dxf", lambda ms: ms.add_line((0, 0), (10, 0)))


def _make_circle_dxf(tmp_path: Path) -> Path:
    return _write_dxf(tmp_path, "circle.dxf", lambda ms: ms.add_circle((5, 5), radius=1))


def _make_block_dxf(tmp_path: Path) -> Path:
    path = tmp_path / "block.dxf"
    document = ezdxf.new()
    block = document.blocks.new("TEST_BLOCK")
    block.add_line((0, 0), (1, 0))
    document.modelspace().add_blockref("TEST_BLOCK", insert=(0, 0))
    document.saveas(path)
    return path


def test_empty_directory_imports_zero_files(tmp_path: Path) -> None:
    service = BatchIngestionService()
    imported = service.ingest_directory(str(tmp_path))

    assert imported == 0
    assert service.repository().count() == 0


def test_one_file_imports_single_reference(tmp_path: Path) -> None:
    _make_line_dxf(tmp_path)
    service = BatchIngestionService()

    imported = service.ingest_directory(str(tmp_path), recursive=False)

    assert imported == 1
    assert service.repository().count() == 1


def test_multiple_files_import_in_deterministic_order(tmp_path: Path) -> None:
    _write_dxf(tmp_path, "b.dxf", lambda ms: ms.add_line((0, 0), (1, 0)))
    _write_dxf(tmp_path, "a.dxf", lambda ms: ms.add_line((1, 0), (2, 0)))
    service = BatchIngestionService()

    imported = service.ingest_directory(str(tmp_path), recursive=False)
    references = service.repository().all()

    assert imported == 2
    assert [reference.source_file for reference in references] == ["a.dxf", "b.dxf"]


def test_recursive_search_finds_files_in_subdirectories(tmp_path: Path) -> None:
    subdir = tmp_path / "sub"
    subdir.mkdir()
    _make_line_dxf(subdir)
    service = BatchIngestionService()

    imported = service.ingest_directory(str(tmp_path), recursive=True)

    assert imported == 1
    assert service.repository().count() == 1


def test_invalid_files_are_skipped(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.dxf"
    invalid_path.write_text("not a dxf file", encoding="utf-8")
    _make_line_dxf(tmp_path)
    service = BatchIngestionService()

    imported = service.ingest_directory(str(tmp_path), recursive=False)

    assert imported == 1
    assert service.repository().count() == 1


def test_clear_resets_repository(tmp_path: Path) -> None:
    _make_line_dxf(tmp_path)
    service = BatchIngestionService()
    service.ingest_directory(str(tmp_path), recursive=False)

    assert service.repository().count() == 1
    service.clear()
    assert service.repository().count() == 0


def test_statistics_returns_counts_and_averages(tmp_path: Path) -> None:
    _make_line_dxf(tmp_path)
    _make_circle_dxf(tmp_path)
    _make_block_dxf(tmp_path)
    service = BatchIngestionService()
    service.ingest_directory(str(tmp_path), recursive=False)

    stats = service.statistics()

    assert stats["files"] == 3
    assert stats["project_types"]["unknown"] == 3
    assert stats["average_entity_count"] > 0.0
    assert stats["average_room_count"] == 0.0
