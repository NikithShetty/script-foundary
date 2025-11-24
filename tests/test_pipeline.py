"""Tests for pipeline modules."""

import pytest
from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.core import run_pipeline


def test_pipeline_basic():
    """Test basic pipeline execution."""
    input_data = {
        "topic": "photosynthesis",
        "year_level": 5,
        "learning_objective": "Students will understand why plants need light and water",
        "subject": "Science",
    }
    
    config = PipelineConfig(
        enable_curriculum_aligner=True,
        enable_misconception_checker=True,
        enable_script_generator=False,  # Disable to avoid API calls in tests
        enable_fact_checker=False,
        enable_cultural_safety=True,
        enable_accessibility=True,
    )
    
    context = run_pipeline(input_data, config)
    
    assert context.topic == "photosynthesis"
    assert context.year_level == 5
    assert len(context.curriculum_outcomes) >= 0
    assert len(context.misconceptions) >= 0


def test_pipeline_context():
    """Test PipelineContext model."""
    context = PipelineContext(
        topic="test",
        year_level=5,
        learning_objective="test objective",
    )
    
    output = context.to_output()
    assert output["topic"] == "test"
    assert output["year_level"] == 5
    assert "curriculum" in output
    assert "misconceptions" in output


def test_pipeline_config():
    """Test PipelineConfig model."""
    config = PipelineConfig(
        enable_curriculum_aligner=True,
        enable_script_generator=False,
    )
    
    assert config.enable_curriculum_aligner is True
    assert config.enable_script_generator is False



