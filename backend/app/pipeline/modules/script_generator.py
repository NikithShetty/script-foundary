"""Module 3: Script Generator - Core script generation using LLM with FAME framework."""

from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.base import PipelineModule
from app.utils.prompts import get_fame_prompt
from app.services.llm_service import generate_script


class ScriptGenerator(PipelineModule):
    """Generates educational scripts using LLM with FAME framework."""
    
    def __init__(self):
        super().__init__("ScriptGenerator")
    
    def process(self, context: PipelineContext, config: PipelineConfig) -> PipelineContext:
        """
        Generate script using LLM with pedagogical framework.
        
        Args:
            context: Pipeline context
            config: Pipeline configuration
            
        Returns:
            Updated context with generated script
        """
        try:
            # Build prompt with context from previous modules
            prompt = get_fame_prompt(
                topic=context.topic,
                year_level=context.year_level,
                learning_objective=context.learning_objective,
                curriculum_codes=context.curriculum_codes,
                misconceptions=context.misconceptions,
            )
            
            # Generate script using LLM service (uses curriculum model)
            script_data = generate_script(prompt, node_name="script_generation")
            
            context.generated_script = script_data.get("script", "")
            context.script_scenes = script_data.get("scenes", [])
            
            # If no script was generated, add a warning
            if not context.generated_script:
                context.warnings.append("Script generator did not produce output. Check LLM API configuration.")
            
        except Exception as e:
            context = self.handle_error(context, e, f"Failed to generate script: {str(e)}")
            # Add fallback message
            if not context.generated_script:
                context.generated_script = f"# Educational Script: {context.topic}\n\nScript generation failed. Please check your API keys and try again."
                context.warnings.append(f"Script generation error: {str(e)}")
        
        return context
