"""Deterministic pipeline benchmark suite."""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from building_model_v2.examples.sample_projects import SampleProjects
from building_model_v2.pipeline.pipeline_engine import PipelineEngine


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    project_name: str
    execution_time: float
    room_count: int
    floor_count: int
    success: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "project_name": self.project_name,
            "execution_time": self.execution_time,
            "room_count": self.room_count,
            "floor_count": self.floor_count,
            "success": self.success,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> BenchmarkResult:
        return cls(
            project_name=str(data["project_name"]),
            execution_time=float(data["execution_time"]),
            room_count=int(data["room_count"]),
            floor_count=int(data["floor_count"]),
            success=bool(data["success"]),
        )


class PipelineBenchmark:
    """Benchmark runner for deterministic sample projects."""

    def __init__(self) -> None:
        self._engine = PipelineEngine()

    def benchmark_one_bhk(self) -> BenchmarkResult:
        return self._benchmark_sample("one_bhk", SampleProjects.one_bhk)

    def benchmark_two_bhk(self) -> BenchmarkResult:
        return self._benchmark_sample("two_bhk", SampleProjects.two_bhk)

    def benchmark_three_bhk(self) -> BenchmarkResult:
        return self._benchmark_sample("three_bhk", SampleProjects.three_bhk)

    def benchmark_duplex(self) -> BenchmarkResult:
        return self._benchmark_sample("duplex", SampleProjects.duplex)

    def benchmark_small_office(self) -> BenchmarkResult:
        return self._benchmark_sample("small_office", SampleProjects.small_office)

    def benchmark_retail_shop(self) -> BenchmarkResult:
        return self._benchmark_sample("retail_shop", SampleProjects.retail_shop)

    def _benchmark_sample(self, project_name: str, sample_callable: callable[[], object]) -> BenchmarkResult:
        program = sample_callable()
        start = perf_counter()
        result = self._engine.run(program)
        end = perf_counter()
        return BenchmarkResult(
            project_name=project_name,
            execution_time=end - start,
            room_count=result.room_count,
            floor_count=result.floor_count,
            success=result.success,
        )
