"""Evaluation Pipeline for Building Model v2.

Orchestrates the complete evaluation pipeline:
Validation → Constraints → Scoring → Report.
"""

from __future__ import annotations

from ..constraints.accessibility_constraints import (
    AccessibleBathroomConstraint,
    MinimumAccessibleDoorWidthConstraint,
    MinimumHallwayWidthConstraint,
    RampSlopeConstraint,
    StairHandrailConstraint,
    WheelchairTurningRadiusConstraint,
)
from ..constraints.building_code_constraints import (
    CeilingHeightConstraint,
    MaximumTravelDistanceConstraint,
    MinimumDoorWidthConstraint,
    MinimumRoomAreaConstraint,
    MinimumWindowAreaConfig,
    MinimumWindowAreaConstraint,
    StairWidthConstraint,
)
from ..constraints.constraint_engine import ConstraintEngine
from ..constraints.constraint_result import ConstraintResult
from ..constraints.functional_constraints import (
    EmptyBuildingConstraint,
    EmptyFloorConstraint,
    IsolatedRoomConstraint,
    RoomWithoutDoorConstraint,
    RoomWithoutWindowConstraint,
    UnconnectedFloorConstraint,
)
from ..constraints.scoring import ConstraintScore, ConstraintScoreEngine, ConstraintWeightProfile
from ..validation.validation_pipeline import ValidationPipeline, ValidationPipelineConfig
from ..validation.validation_result import ValidationResult
from ..validation.cross_entity_validator import BuildingModel
from .evaluation_report import EvaluationReport
from .evaluation_summary import EvaluationSummary


class EvaluationPipelineConfig:
    """Configuration for the evaluation pipeline.
    
    Attributes:
        validation_config: Configuration for validation pipeline.
        weight_profile: Weight profile for scoring.
        enable_all_constraints: Whether to register all default constraints.
    """
    
    def __init__(
        self,
        validation_config: ValidationPipelineConfig | None = None,
        weight_profile: ConstraintWeightProfile | None = None,
        enable_all_constraints: bool = True,
    ) -> None:
        """Initialize the evaluation pipeline configuration.
        
        Args:
            validation_config: Validation pipeline configuration.
            weight_profile: Weight profile for scoring.
            enable_all_constraints: Whether to register all constraints.
        """
        self.validation_config = validation_config
        self.weight_profile = weight_profile or ConstraintWeightProfile.equal_weights()
        self.enable_all_constraints = enable_all_constraints


class EvaluationPipeline:
    """Orchestrates the complete evaluation pipeline.
    
    Pipeline steps:
        1. Run ValidationPipeline
        2. Run ConstraintEngine
        3. Run ConstraintScoreEngine
        4. Build EvaluationSummary
        5. Build EvaluationReport
        6. Return EvaluationReport
    """
    
    def __init__(self, config: EvaluationPipelineConfig | None = None) -> None:
        """Initialize the evaluation pipeline.
        
        Args:
            config: Pipeline configuration.
        """
        self._config = config or EvaluationPipelineConfig()
        self._validation_pipeline = ValidationPipeline(
            config=self._config.validation_config,
        )
        self._constraint_engine = ConstraintEngine()
        self._score_engine = ConstraintScoreEngine()
        
        if self._config.enable_all_constraints:
            self._register_default_constraints()
    
    def _register_default_constraints(self) -> None:
        """Register all default constraints."""
        # Functional constraints
        self._constraint_engine.register(EmptyBuildingConstraint())
        self._constraint_engine.register(EmptyFloorConstraint())
        self._constraint_engine.register(IsolatedRoomConstraint())
        self._constraint_engine.register(RoomWithoutDoorConstraint())
        self._constraint_engine.register(RoomWithoutWindowConstraint())
        self._constraint_engine.register(UnconnectedFloorConstraint())
        
        # Building code constraints
        self._constraint_engine.register(MinimumRoomAreaConstraint())
        self._constraint_engine.register(MinimumDoorWidthConstraint())
        self._constraint_engine.register(MinimumWindowAreaConstraint())
        self._constraint_engine.register(StairWidthConstraint())
        self._constraint_engine.register(CeilingHeightConstraint())
        self._constraint_engine.register(MaximumTravelDistanceConstraint())
        
        # Accessibility constraints
        self._constraint_engine.register(MinimumAccessibleDoorWidthConstraint())
        self._constraint_engine.register(MinimumHallwayWidthConstraint())
        self._constraint_engine.register(WheelchairTurningRadiusConstraint())
        self._constraint_engine.register(RampSlopeConstraint())
        self._constraint_engine.register(AccessibleBathroomConstraint())
        self._constraint_engine.register(StairHandrailConstraint())
        
        # Structural constraints
        from ..constraints.structural_constraints import (
            ColumnAlignmentConstraint,
            ColumnSpacingConstraint,
            LargeUnsupportedRoomConstraint,
            MaximumWallSpanConstraint,
            StairSupportConstraint,
            StructuralSymmetryConstraint,
            WallContinuityConstraint,
        )
        self._constraint_engine.register(MaximumWallSpanConstraint())
        self._constraint_engine.register(ColumnSpacingConstraint())
        self._constraint_engine.register(LargeUnsupportedRoomConstraint())
        self._constraint_engine.register(WallContinuityConstraint())
        self._constraint_engine.register(ColumnAlignmentConstraint())
        self._constraint_engine.register(StairSupportConstraint())
        self._constraint_engine.register(StructuralSymmetryConstraint())

        # Vastu constraints
        from ..constraints.vastu_constraints import (
            BrahmasthanConstraint,
            EntranceDirectionConstraint,
            KitchenPlacementConstraint,
            MasterBedroomConstraint,
            PoojaRoomConstraint,
            StaircaseConstraint,
            ToiletPlacementConstraint,
        )
        self._constraint_engine.register(EntranceDirectionConstraint())
        self._constraint_engine.register(KitchenPlacementConstraint())
        self._constraint_engine.register(MasterBedroomConstraint())
        self._constraint_engine.register(PoojaRoomConstraint())
        self._constraint_engine.register(StaircaseConstraint())
        self._constraint_engine.register(ToiletPlacementConstraint())
        self._constraint_engine.register(BrahmasthanConstraint())
    
    def evaluate(self, building_model: BuildingModel) -> EvaluationReport:
        """Evaluate a building model.
        
        Runs the complete evaluation pipeline and returns a report.
        
        Args:
            building_model: The building model to evaluate.
        
        Returns:
            The evaluation report.
        """
        # Step 1: Run validation
        validation_result = self._validation_pipeline.validate(building_model)
        
        # Step 2: Run constraints
        constraint_result = self._constraint_engine.evaluate(building_model)
        
        # Step 3: Run scoring
        constraint_score = self._score_engine.evaluate(
            constraint_result,
            weight_profile=self._config.weight_profile,
        )
        
        # Step 4: Build summary
        summary = EvaluationSummary.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
        )
        
        # Step 5: Build report
        report = EvaluationReport.create(
            validation_result=validation_result,
            constraint_result=constraint_result,
            constraint_score=constraint_score,
            summary=summary,
        )
        
        return report
    
    @property
    def validation_pipeline(self) -> ValidationPipeline:
        """Get the validation pipeline.
        
        Returns:
            The validation pipeline.
        """
        return self._validation_pipeline
    
    @property
    def constraint_engine(self) -> ConstraintEngine:
        """Get the constraint engine.
        
        Returns:
            The constraint engine.
        """
        return self._constraint_engine
    
    @property
    def score_engine(self) -> ConstraintScoreEngine:
        """Get the score engine.
        
        Returns:
            The score engine.
        """
        return self._score_engine