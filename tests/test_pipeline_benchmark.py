"""Tests for the deterministic pipeline benchmark suite."""
from __future__ import annotations

from benchmark.pipeline_benchmark import BenchmarkResult, PipelineBenchmark
from building_model_v2.examples.sample_projects import SampleProjects


class TestPipelineBenchmark:
    def test_benchmark_executes(self) -> None:
        benchmark = PipelineBenchmark()
        result = benchmark.benchmark_one_bhk()
        assert isinstance(result, BenchmarkResult)
        assert result.project_name == "one_bhk"
        assert result.execution_time >= 0
        assert result.room_count >= 1
        assert result.floor_count >= 0
        assert result.success is True

    def test_benchmark_deterministic_success(self) -> None:
        benchmark = PipelineBenchmark()
        result1 = benchmark.benchmark_two_bhk()
        result2 = benchmark.benchmark_two_bhk()
        assert result1.success == result2.success
        assert result1.room_count == result2.room_count
        assert result1.floor_count == result2.floor_count
        assert result1.project_name == result2.project_name

    def test_benchmark_serialization(self) -> None:
        benchmark = PipelineBenchmark()
        result = benchmark.benchmark_three_bhk()
        data = result.to_dict()
        restored = BenchmarkResult.from_dict(data)
        assert restored == result
        assert restored.project_name == "three_bhk"
        assert restored.execution_time >= 0

    def test_all_sample_projects_benchmarked(self) -> None:
        benchmark = PipelineBenchmark()
        project_names = {
            "one_bhk": benchmark.benchmark_one_bhk(),
            "two_bhk": benchmark.benchmark_two_bhk(),
            "three_bhk": benchmark.benchmark_three_bhk(),
            "duplex": benchmark.benchmark_duplex(),
            "small_office": benchmark.benchmark_small_office(),
            "retail_shop": benchmark.benchmark_retail_shop(),
        }

        expected_samples = {
            "one_bhk": SampleProjects.one_bhk,
            "two_bhk": SampleProjects.two_bhk,
            "three_bhk": SampleProjects.three_bhk,
            "duplex": SampleProjects.duplex,
            "small_office": SampleProjects.small_office,
            "retail_shop": SampleProjects.retail_shop,
        }

        for name, result in project_names.items():
            assert result.project_name == name
            assert result.execution_time >= 0
            assert isinstance(result.success, bool)
            assert result.room_count >= 1
            assert result.floor_count >= 0
