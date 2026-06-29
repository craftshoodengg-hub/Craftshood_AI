"""Pydantic models for Craftshood AI REST API.

Request/response models for the generation endpoint.
No business logic. Only data validation.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request model for the generate endpoint."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language design prompt",
        examples=["Modern east-facing 3BHK villa with parking and pooja room."],
    )


class GenerateResponse(BaseModel):
    """Response model for the generate endpoint."""

    prompt: str = Field(description="Original prompt")
    success: bool = Field(description="Whether generation succeeded")
    quality: str = Field(description="Quality classification")
    final_score: float = Field(description="Combined quality score (0-100)")
    iteration_count: int = Field(description="Number of optimization iterations")
    layout_score: float = Field(description="Layout-specific score (0-100)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class HealthResponse(BaseModel):
    """Response model for the health endpoint."""

    status: str = Field(default="ok", description="Service status")
    version: str = Field(default="1.0", description="API version")


class VersionResponse(BaseModel):
    """Response model for the version endpoint."""

    version: str = Field(default="1.0.0", description="Pipeline version")
    pipeline_version: str = Field(default="1.0.0", description="Generation pipeline version")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")


class EvaluateRequest(BaseModel):
    """Request model for the evaluate endpoint."""
    rooms: list[dict[str, Any]] = Field(default_factory=list, description="List of room data")
    building: dict[str, Any] = Field(default_factory=dict, description="Building metadata")
    floors: int = Field(default=1, description="Number of floors")


class EvaluateResponse(BaseModel):
    """Response model for the evaluate endpoint."""
    overall_score: float = Field(default=0.0, description="Overall evaluation score")
    layout_score: float = Field(default=0.0, description="Layout-specific score")
    category_scores: Dict[str, float] = Field(default_factory=dict, description="Scores by category")
    issues: list[dict[str, Any]] = Field(default_factory=list, description="Evaluation issues")


class OptimizeRequest(BaseModel):
    """Request model for the optimize endpoint."""
    action: dict[str, Any] = Field(default_factory=dict, description="Optimization action to apply")
    rooms: list[dict[str, Any]] = Field(default_factory=list, description="Current rooms state")
    building: dict[str, Any] = Field(default_factory=dict, description="Building metadata")


class OptimizeResponse(BaseModel):
    """Response model for the optimize endpoint."""
    after_score: float = Field(default=0.0, description="Score after optimization")
    before_score: float = Field(default=0.0, description="Score before optimization")
    rooms: list[dict[str, Any]] = Field(default_factory=list, description="Updated room states")
    applied_actions: list[str] = Field(default_factory=list, description="IDs of applied actions")
    improved: bool = Field(default=False, description="Whether optimization improved the score")
    improvement_plan: dict[str, Any] = Field(default_factory=dict, description="Updated improvement plan")
