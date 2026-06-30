"""FastAPI application for Craftshood AI.

Exposes the deterministic GenerationPipeline through REST endpoints.
No AI. No LLM. Pure deterministic orchestration.
"""
from __future__ import annotations
from typing import Any

from fastapi import FastAPI, HTTPException

from building_model_v2.ai.generation_pipeline import GenerationPipeline
from building_model_v2.ai.requirement_parser import RequirementParser
from building_model_v2.ai.space_generator import SpaceProgramGenerator
from building_model_v2.examples.sample_projects import SampleProjects
from building_model_v2.pipeline.pipeline_engine import PipelineEngine

from .models import (
    OptimizeRequest,
    OptimizeResponse,
    ErrorResponse,
    GenerateRequest,
    EvaluateRequest,
    EvaluateResponse,
    GenerateResponse,
    PipelineGenerateRequest,
    PipelineGenerateResponse,
    HealthResponse,
    VersionResponse,
)

app = FastAPI(
    title="Craftshood AI API",
    description="Deterministic architectural floor plan generation engine",
    version="1.0.0",
)

_pipeline = GenerationPipeline()


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version="1.0")


@app.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    """Get pipeline version."""
    return VersionResponse(version="1.0.0", pipeline_version="1.0.0")


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate a floor plan from a natural language prompt.

    Args:
        request: GenerateRequest with the design prompt.

    Returns:
        GenerateResponse with generation results.
    """
    try:
        result = _pipeline.generate(request.prompt)
        return GenerateResponse(
            prompt=result.prompt,
            success=result.success,
            quality=result.quality,
            final_score=result.final_score,
            iteration_count=result.iteration_count,
            layout_score=result.layout_score,
            metadata=result.metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


SAMPLE_PROJECTS: dict[str, callable[[], object]] = {
    "one_bhk": SampleProjects.one_bhk,
    "two_bhk": SampleProjects.two_bhk,
    "three_bhk": SampleProjects.three_bhk,
    "duplex": SampleProjects.duplex,
    "small_office": SampleProjects.small_office,
    "retail_shop": SampleProjects.retail_shop,
}


@app.post("/pipeline/generate", response_model=PipelineGenerateResponse)
@app.post("/api/v1/pipeline/generate", response_model=PipelineGenerateResponse)
async def pipeline_generate(request: PipelineGenerateRequest) -> PipelineGenerateResponse:
    """Generate a building model using the deterministic pipeline."""
    try:
        if request.sample_project is not None:
            sample_name = request.sample_project
            sample_fn = SAMPLE_PROJECTS.get(sample_name)
            if sample_fn is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported sample_project '{sample_name}'. Supported values: {', '.join(sorted(SAMPLE_PROJECTS))}",
                )
            program = sample_fn()
            warnings: list[str] = []
        elif request.prompt is not None:
            parser = RequirementParser()
            parse_result = parser.parse(request.prompt)
            warnings = list(parse_result.warnings)
            if parse_result.missing_fields:
                warnings.append(f"Missing fields: {', '.join(parse_result.missing_fields)}")
            if parse_result.requirements.building.bedrooms is None:
                raise HTTPException(status_code=400, detail="Unable to parse a valid space program from prompt.")
            generator = SpaceProgramGenerator()
            program = generator.generate(parse_result.requirements)
            if not program.rooms:
                raise HTTPException(status_code=400, detail="Prompt parsing produced no rooms.")
        else:
            raise HTTPException(status_code=400, detail="Either prompt or sample_project must be provided.")

        engine = PipelineEngine()
        result = engine.run(program)

        return PipelineGenerateResponse(
            success=result.success,
            room_count=result.room_count,
            floor_count=result.floor_count,
            building=result.building.to_dict(),
            pipeline_summary={
                "validation_valid": result.validation_result.valid,
                "placement_success": result.placement_result.success,
                "refinement_success": result.refinement_result.refined_result.success,
                "overall_success": result.success,
            },
            warnings=warnings,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(request: EvaluateRequest) -> EvaluateResponse:
    """Evaluate a building model and return scores."""
    try:
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
        from building_model_v2.validation.cross_entity_validator import BuildingModel
        pipeline = EvaluationPipeline()
        model = BuildingModel()
        report = pipeline.evaluate(model)
        overall = report.constraint_score.overall if report.constraint_score else 0.0
        categories = report.constraint_score.category_scores if report.constraint_score else {}
        issues = [
            {"code": i.code, "title": i.message[:50], "description": i.message,
             "priority": i.severity.value, "target_room": i.entity_id, "estimated_gain": i.score * 10}
            for i in report.constraint_issues[:10]
        ]
        return EvaluateResponse(overall_score=overall, layout_score=categories.get("layout", 0.0),
                               category_scores=categories, issues=issues)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize(request: OptimizeRequest) -> OptimizeResponse:
    """Apply an optimization action and return updated state."""
    try:
        from building_model_v2.evaluation.evaluation_pipeline import EvaluationPipeline
        from building_model_v2.optimization.improvement_plan import ImprovementPlan
        from building_model_v2.optimization.optimizer import Optimizer
        from building_model_v2.optimization.optimization_action import OptimizationAction
        from building_model_v2.validation.cross_entity_validator import BuildingModel
        
        pipeline = EvaluationPipeline()
        model = BuildingModel()
        report = pipeline.evaluate(model)
        before_score = report.constraint_score.overall if report.constraint_score else 0.0
        
        action = OptimizationAction(
            id=request.action.get('id', 'unknown'),
            title=request.action.get('title', ''),
            description=request.action.get('description', ''),
            target_entity_id=request.action.get('target_entity_id', ''),
            target_entity_type=request.action.get('target_entity_type', 'room'),
            estimated_score_gain=request.action.get('estimated_score_gain', 0.0),
            priority=request.action.get('priority', 0),
        )
        plan = ImprovementPlan(actions=[action], current_score=before_score, estimated_final_score=before_score + action.estimated_score_gain)
        optimizer = Optimizer()
        result = optimizer.optimize(model, plan, before_score=before_score, after_score=before_score + action.estimated_score_gain)
        
        final_report = pipeline.evaluate(result.optimized_model)
        after_score = final_report.constraint_score.overall if final_report.constraint_score else before_score
        
        return OptimizeResponse(
            after_score=after_score, before_score=before_score,
            rooms=[], applied_actions=[action.id], improved=after_score > before_score,
            improvement_plan=plan.to_dict(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_app() -> FastAPI:
    """Create and return the FastAPI application."""
    return app
