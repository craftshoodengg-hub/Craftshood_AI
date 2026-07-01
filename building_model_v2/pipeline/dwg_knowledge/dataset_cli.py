"""Command-line entry point for DWG dataset analysis."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .dataset_analyzer import DatasetAnalyzer
from .dataset_report_exporter import DatasetReportExporter


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a DWG/DXF dataset and export reports.")
    parser.add_argument("--input", required=True, help="Input directory containing DWG/DXF files")
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory for report files (default: current working directory)",
    )
    parser.add_argument(
        "--recursive",
        dest="recursive",
        action="store_true",
        default=True,
        help="Scan directories recursively (default)",
    )
    parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Do not scan directories recursively",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files analyzed")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        input_path = Path(args.input)
        if not input_path.exists() or not input_path.is_dir():
            print(f"Invalid directory: {args.input}")
            return 1

        if args.limit is not None and args.limit < 0:
            print("Limit must be a non-negative integer.")
            return 1

        output_path = Path(args.output)
        if output_path.exists() and not output_path.is_dir():
            print(f"Output path is not a directory: {args.output}")
            return 1
        output_path.mkdir(parents=True, exist_ok=True)

        analyzer = DatasetAnalyzer()
        summary = analyzer.analyze_directory(
            str(input_path), recursive=args.recursive, limit=args.limit
        )

        exporter = DatasetReportExporter()
        json_path = output_path / "dataset_report.json"
        markdown_path = output_path / "dataset_report.md"

        exporter.save_json(summary, str(json_path))
        exporter.save_markdown(summary, str(markdown_path))

        print("------------------------------------")
        print("DWG Dataset Analysis Complete")
        print("------------------------------------")
        print(f"Files scanned: {summary.get('files_scanned', 0)}")
        print(f"Files failed: {summary.get('files_failed', 0)}")
        print(f"JSON report: {json_path}")
        print(f"Markdown report: {markdown_path}")
        print("------------------------------------")
        return 0
    except SystemExit:
        raise
    except Exception as exc:
        print(f"Unexpected exception: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
