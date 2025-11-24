"""Pipeline orchestrator - functional approach."""

from typing import List
from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.base import PipelineModule
from app.pipeline.modules.curriculum_aligner import CurriculumAligner
from app.pipeline.modules.misconception_checker import MisconceptionChecker
from app.pipeline.modules.script_generator import ScriptGenerator
from app.pipeline.modules.fact_checker import FactChecker
from app.pipeline.modules.cultural_safety import CulturalSafetyChecker
from app.pipeline.modules.accessibility import AccessibilityGenerator


# Registry of all available modules
MODULE_REGISTRY: List[type[PipelineModule]] = [
    CurriculumAligner,
    MisconceptionChecker,
    ScriptGenerator,
    FactChecker,
    CulturalSafetyChecker,
    AccessibilityGenerator,
]


def get_enabled_modules(config: PipelineConfig) -> List[PipelineModule]:
    """
    Get list of enabled modules based on configuration.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        List of enabled module instances
    """
    modules = []
    for module_class in MODULE_REGISTRY:
        module = module_class()
        if module.is_enabled(config):
            modules.append(module)
    
    # Apply custom ordering if specified
    if config.module_order:
        module_dict = {m.name: m for m in modules}
        ordered_modules = []
        for name in config.module_order:
            if name in module_dict:
                ordered_modules.append(module_dict[name])
        # Add any modules not in the order list
        for module in modules:
            if module not in ordered_modules:
                ordered_modules.append(module)
        return ordered_modules
    
    return modules


def run_pipeline(input_data: dict, config: PipelineConfig) -> PipelineContext:
    """
    Run the complete pipeline with all enabled modules.
    
    Args:
        input_data: Input data dictionary with topic, year_level, learning_objective
        config: Pipeline configuration
        
    Returns:
        Final pipeline context with all results
    """
    # Initialize context from input
    context = PipelineContext(
        topic=input_data["topic"],
        year_level=input_data["year_level"],
        learning_objective=input_data["learning_objective"],
        subject=input_data.get("subject"),
    )
    
    # Get enabled modules
    modules = get_enabled_modules(config)
    
    # Process through each module
    for module in modules:
        try:
            context = module.process(context, config)
        except Exception as e:
            context = module.handle_error(context, e)
            # Continue pipeline even if one module fails
            continue
    
    return context



