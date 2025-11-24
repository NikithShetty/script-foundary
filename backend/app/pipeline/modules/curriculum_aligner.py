"""Module 1: Curriculum Aligner - Aligns content with Australian curriculum."""

from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.base import PipelineModule
from app.services.curriculum_api import get_curriculum_outcomes, get_prerequisites


class CurriculumAligner(PipelineModule):
    """Aligns script content with CurricuLLM-AU curriculum outcomes."""
    
    def __init__(self):
        super().__init__("CurriculumAligner")
    
    def process(self, context: PipelineContext, config: PipelineConfig) -> PipelineContext:
        """
        Fetch curriculum outcomes and align with topic/year level.
        
        Args:
            context: Pipeline context
            config: Pipeline configuration
            
        Returns:
            Updated context with curriculum data
        """
        try:
            # Fetch curriculum outcomes from API
            outcomes = get_curriculum_outcomes(
                topic=context.topic,
                year_level=context.year_level,
                subject=context.subject,
            )
            
            context.curriculum_outcomes = outcomes
            context.curriculum_codes = [outcome.get("code", "") for outcome in outcomes if outcome.get("code")]
            
            # Get prerequisites
            prerequisites = get_prerequisites(context.topic, context.year_level)
            context.prerequisites = prerequisites
            
        except Exception as e:
            context = self.handle_error(context, e, f"Failed to align curriculum: {str(e)}")
        
        return context

