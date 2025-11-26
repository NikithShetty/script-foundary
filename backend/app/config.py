"""Configuration management with feature flags."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Any


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
    session_ttl_hours: int = 24  # Session TTL in hours (default: 24 hours)
    
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
    # General model: Used by default for most nodes (prioritized)
    general_model: str = "gpt-4"  # Default general model (OpenAI)
    general_model_provider: str = "openai"  # Provider for general model: "openai" or "curricullm"
    
    # Curriculum model: Used specifically for curriculum_agent and script_generation nodes
    curriculum_model: Optional[str] = None  # Curriculum-specific model (CurricuLLM)
    curriculum_model_provider: str = "curricullm"  # Provider for curriculum model: "curricullm" or "openai"
    
    # Legacy settings (for backward compatibility)
    openai_model: str = "gpt-4"
    anthropic_model: str = "claude-3-sonnet-20240229"
    curricullm_model: Optional[str] = None
    
    # LangGraph Settings
    graph_recursion_limit: int = 2
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding='utf-8',
        case_sensitive=False
    )


# Global settings instance
# Add debug logging to verify .env file loading
import logging
_logger = logging.getLogger(__name__)

# Check if .env file exists
_env_file_path = Path(__file__).parent.parent / ".env"
if _env_file_path.exists():
    _logger.info(f"Found .env file at: {_env_file_path}")
else:
    _logger.warning(f".env file not found at: {_env_file_path}")

settings = Settings()

# Log loaded settings (mask sensitive values)
if settings.debug:
    def _mask_value(key: str, value: Any) -> str:
        """Mask sensitive values."""
        if value is None:
            return "None"
        value_str = str(value)
        sensitive_keywords = ['key', 'password', 'secret', 'token', 'api_key', 'auth']
        key_lower = key.lower()
        if any(keyword in key_lower for keyword in sensitive_keywords):
            if value_str and len(value_str) > 8:
                return f"{value_str[:4]}...{value_str[-4:]}"
            return "***" if value_str else "None"
        return value_str
    
    _logger.info("=" * 60)
    _logger.info("Loaded Settings from .env file:")
    _logger.info("=" * 60)
    for field_name, field_value in settings.model_dump().items():
        masked = _mask_value(field_name, field_value)
        _logger.info(f"  {field_name}={masked}")
    _logger.info("=" * 60)


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



