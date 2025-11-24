"""Pipeline data models for context and configuration."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PipelineConfig(BaseModel):
    """Configuration for pipeline execution."""
    
    enable_curriculum_aligner: bool = True
    enable_misconception_checker: bool = True
    enable_script_generator: bool = True
    enable_fact_checker: bool = True
    enable_cultural_safety: bool = True
    enable_accessibility: bool = True
    
    module_order: Optional[List[str]] = None
    
    class Config:
        extra = "allow"


class PipelineContext(BaseModel):
    """Shared context passed between pipeline modules."""
    
    # Input data
    topic: str
    year_level: int
    learning_objective: str
    subject: Optional[str] = None
    
    # Module outputs (accumulated)
    curriculum_outcomes: List[Dict[str, Any]] = Field(default_factory=list)
    curriculum_codes: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    
    misconceptions: List[Dict[str, Any]] = Field(default_factory=list)
    misconception_warnings: List[str] = Field(default_factory=list)
    
    generated_script: Optional[str] = None
    script_scenes: List[Dict[str, Any]] = Field(default_factory=list)
    
    fact_check_results: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    citations: List[str] = Field(default_factory=list)
    
    cultural_safety_flags: List[str] = Field(default_factory=list)
    cultural_suggestions: List[str] = Field(default_factory=list)
    
    accessibility_metadata: Dict[str, Any] = Field(default_factory=dict)
    alt_texts: List[str] = Field(default_factory=list)
    captions: List[str] = Field(default_factory=list)
    
    # Metadata
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_output(self) -> Dict[str, Any]:
        """Convert context to final output format."""
        return {
            "topic": self.topic,
            "year_level": self.year_level,
            "learning_objective": self.learning_objective,
            "script": self.generated_script,
            "scenes": self.script_scenes,
            "curriculum": {
                "outcomes": self.curriculum_outcomes,
                "codes": self.curriculum_codes,
                "prerequisites": self.prerequisites,
            },
            "misconceptions": {
                "addressed": self.misconceptions,
                "warnings": self.misconception_warnings,
            },
            "fact_checking": {
                "results": self.fact_check_results,
                "confidence_score": self.confidence_score,
                "citations": self.citations,
            },
            "cultural_safety": {
                "flags": self.cultural_safety_flags,
                "suggestions": self.cultural_suggestions,
            },
            "accessibility": {
                "alt_texts": self.alt_texts,
                "captions": self.captions,
                "metadata": self.accessibility_metadata,
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }



