"""Configuration management with feature flags."""

import os
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings with feature flags."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    curricullm_api_key: Optional[str] = None
    curricullm_api_url: str = "https://api.curricullm.com"
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/scriptfoundary"
    
    # Redis
    redis_url: Optional[str] = None
    
    # Vector Store
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: Optional[str] = None
    use_faiss: bool = True
    faiss_index_path: str = "./data/faiss_index"
    
    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # CORS - reads from ALLOWED_ORIGINS environment variable
    # Supports single endpoint or comma-separated list
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Feature Flags
    enable_curriculum_aligner: bool = True
    enable_misconception_checker: bool = True
    enable_script_generator: bool = True
    enable_fact_checker: bool = True
    enable_cultural_safety: bool = True
    enable_accessibility: bool = True
    
    # LLM Settings
    openai_model: str = "gpt-4"
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_pipeline_config_from_settings() -> dict:
    """
    Get pipeline configuration from settings.
    
    Returns:
        Dictionary with pipeline configuration
    """
    from app.models.pipeline import PipelineConfig
    
    return PipelineConfig(
        enable_curriculum_aligner=settings.enable_curriculum_aligner,
        enable_misconception_checker=settings.enable_misconception_checker,
        enable_script_generator=settings.enable_script_generator,
        enable_fact_checker=settings.enable_fact_checker,
        enable_cultural_safety=settings.enable_cultural_safety,
        enable_accessibility=settings.enable_accessibility,
    ).model_dump()



