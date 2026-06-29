"""Unit tests for Demo CLI."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import patch
import pytest

from building_model_v2.ai.generation_pipeline import GenerationPipeline
from building_model_v2.ai.generation_result import GenerationResult


class TestDemoPipeline:
    def test_empty_prompt(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("")
        assert isinstance(result, GenerationResult)
        assert result.prompt == ""

    def test_valid_prompt(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK modern duplex")
        assert isinstance(result, GenerationResult)
        assert result.success is True
        assert result.final_score >= 0

    def test_invalid_prompt(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("asdfghjkl")
        assert isinstance(result, GenerationResult)
        # Should still return a result even with garbage input
        assert result.prompt == "asdfghjkl"

    def test_deterministic_output(self):
        pipeline = GenerationPipeline()
        r1 = pipeline.generate("3BHK house")
        r2 = pipeline.generate("3BHK house")
        assert r1.final_score == r2.final_score
        assert r1.quality == r2.quality

    def test_serialization(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("2BHK apartment")
        d = result.to_dict()
        assert "prompt" in d
        assert "success" in d
        assert "quality" in d
        assert "final_score" in d

    def test_json_roundtrip(self, tmp_path):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house")
        d = result.to_dict()
        json_str = json.dumps(d)
        loaded = json.loads(json_str)
        assert loaded["prompt"] == "3BHK house"

    def test_save_to_file(self, tmp_path):
        pipeline = GenerationPipeline()
        result = pipeline.generate("2BHK house")
        output_file = tmp_path / "output.json"
        with open(output_file, "w") as f:
            json.dump(result.to_dict(), f, default=str)
        assert output_file.exists()
        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded["prompt"] == "2BHK house"

    def test_quality_classification(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK modern duplex")
        assert result.quality in ("Excellent", "Good", "Fair", "Poor")

    def test_iteration_count(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house")
        assert result.iteration_count >= 0

    def test_metadata_present(self):
        pipeline = GenerationPipeline()
        result = pipeline.generate("3BHK house")
        assert "warnings" in result.metadata
        assert "pipeline_version" in result.metadata
