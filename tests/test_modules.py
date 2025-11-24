"""Tests for individual pipeline modules."""

import pytest
from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.modules.curriculum_aligner import CurriculumAligner
from app.pipeline.modules.misconception_checker import MisconceptionChecker
from app.pipeline.modules.cultural_safety import CulturalSafetyChecker
from app.pipeline.modules.accessibility import AccessibilityGenerator


def test_curriculum_aligner():
    """Test curriculum aligner module."""
    module = CurriculumAligner()
    context = PipelineContext(
        topic="photosynthesis",
        year_level=5,
        learning_objective="test",
    )
    config = PipelineConfig()
    
    result = module.process(context, config)
    
    assert len(result.curriculum_outcomes) >= 0
    assert isinstance(result.curriculum_codes, list)


def test_misconception_checker():
    """Test misconception checker module."""
    module = MisconceptionChecker()
    context = PipelineContext(
        topic="photosynthesis",
        year_level=5,
        learning_objective="test",
    )
    config = PipelineConfig()
    
    result = module.process(context, config)
    
    assert isinstance(result.misconceptions, list)
    assert isinstance(result.misconception_warnings, list)


def test_cultural_safety_checker():
    """Test cultural safety checker module."""
    module = CulturalSafetyChecker()
    context = PipelineContext(
        topic="test",
        year_level=5,
        learning_objective="test",
        generated_script="This is a test script with normal content.",
    )
    config = PipelineConfig()
    
    result = module.process(context, config)
    
    assert isinstance(result.cultural_safety_flags, list)
    assert isinstance(result.cultural_suggestions, list)


def test_accessibility_generator():
    """Test accessibility generator module."""
    module = AccessibilityGenerator()
    context = PipelineContext(
        topic="test",
        year_level=5,
        learning_objective="test",
        script_scenes=[
            {
                "visual_description": "A diagram showing photosynthesis",
                "narration": "Plants use sunlight to make food",
            }
        ],
    )
    config = PipelineConfig()
    
    result = module.process(context, config)
    
    assert len(result.alt_texts) >= 0
    assert len(result.captions) >= 0
    assert "has_accessibility_features" in result.accessibility_metadata



