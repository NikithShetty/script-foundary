"""Script data models for input and output."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ScriptInput(BaseModel):
    """Input model for script generation request."""
    
    topic: str = Field(..., description="The topic for the educational script")
    year_level: str = Field(..., description="Year level (e.g., '1', '2', 'university level')")
    learning_objective: str = Field(..., description="Learning objective for the script")
    subject: Optional[str] = Field(None, description="Subject area (e.g., 'Science', 'Mathematics')")
    
    # Optional feature toggles
    enable_curriculum_aligner: bool = True
    enable_misconception_checker: bool = True
    enable_script_generator: bool = True
    enable_fact_checker: bool = True
    enable_cultural_safety: bool = True
    enable_accessibility: bool = True


class Scene(BaseModel):
    """Model for a single scene in the script."""
    
    scene_number: int
    title: str
    visual_description: str
    narration: str
    text_overlay: Optional[str] = None
    accessibility_cue: Optional[str] = None
    duration_estimate: Optional[int] = None  # in seconds


class ScriptOutput(BaseModel):
    """Output model for generated script."""
    
    topic: str
    year_level: str
    learning_objective: str
    script: str
    scenes: List[Scene]
    
    curriculum: dict
    misconceptions: dict
    fact_checking: dict
    cultural_safety: dict
    accessibility: dict
    
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)



