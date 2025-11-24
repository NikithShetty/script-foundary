"""FastAPI main application entry point."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.models.script import ScriptInput, ScriptOutput
from app.models.pipeline import PipelineConfig
from app.pipeline.core import run_pipeline
from app.config import settings, get_pipeline_config_from_settings
from app.utils.validators import (
    validate_year_level,
    validate_topic,
    validate_learning_objective,
)
import logging
import os

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Educational Script Generator API",
    description="Evidence-based educational script generation with curriculum alignment",
    version="1.0.0",
)

# CORS middleware - reads from ALLOWED_ORIGINS environment variable
# Supports single endpoint or comma-separated list
cors_origins = [
    origin.strip() 
    for origin in settings.allowed_origins.split(",") 
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Print environment variables on startup if debug is enabled
if settings.debug:
    def mask_sensitive_value(key: str, value: str) -> str:
        """Mask sensitive values in environment variables."""
        sensitive_keywords = ['key', 'password', 'secret', 'token', 'api_key', 'auth']
        key_lower = key.lower()
        if any(keyword in key_lower for keyword in sensitive_keywords):
            if value and len(value) > 8:
                return f"{value[:4]}...{value[-4:]}"
            return "***" if value else ""
        return value
    
    logger.info("=" * 60)
    logger.info("DEBUG MODE: Environment Variables")
    logger.info("=" * 60)
    
    # Get all environment variables
    env_vars = dict(os.environ)
    
    # Sort for better readability
    for key in sorted(env_vars.keys()):
        value = env_vars[key]
        masked_value = mask_sensitive_value(key, value)
        logger.info(f"  {key}={masked_value}")
    
    logger.info("=" * 60)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "script-generator-api"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Educational Script Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/api/v1/scripts/generate", response_model=ScriptOutput)
async def generate_script(input_data: ScriptInput):
    """
    Generate educational script with all enabled modules.
    
    Args:
        input_data: Script generation input
        
    Returns:
        Generated script with all metadata
    """
    # Validate input
    if not validate_topic(input_data.topic):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid topic: must be a non-empty string"
        )
    
    if not validate_year_level(input_data.year_level):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid year level: must be between 1 and 12"
        )
    
    if not validate_learning_objective(input_data.learning_objective):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid learning objective: must be a non-empty string"
        )
    
    try:
        # Create pipeline configuration
        config_dict = get_pipeline_config_from_settings()
        config_dict.update({
            "enable_curriculum_aligner": input_data.enable_curriculum_aligner,
            "enable_misconception_checker": input_data.enable_misconception_checker,
            "enable_script_generator": input_data.enable_script_generator,
            "enable_fact_checker": input_data.enable_fact_checker,
            "enable_cultural_safety": input_data.enable_cultural_safety,
            "enable_accessibility": input_data.enable_accessibility,
        })
        config = PipelineConfig(**config_dict)
        
        # Prepare input data
        input_dict = {
            "topic": input_data.topic,
            "year_level": input_data.year_level,
            "learning_objective": input_data.learning_objective,
            "subject": input_data.subject,
        }
        
        # Run pipeline
        logger.info(f"Running pipeline for topic: {input_data.topic}, year: {input_data.year_level}")
        context = run_pipeline(input_dict, config)
        
        # Convert to output format
        output_dict = context.to_output()
        
        # Create response
        return ScriptOutput(**output_dict)
        
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate script: {str(e)}"
        )


@app.get("/api/v1/curriculum/search")
async def search_curriculum(topic: str, year_level: int, subject: str = None):
    """
    Search curriculum outcomes for a topic.
    
    Args:
        topic: Topic to search for
        year_level: Year level
        subject: Optional subject area
        
    Returns:
        List of curriculum outcomes
    """
    from app.services.curriculum_api import get_curriculum_outcomes
    
    try:
        outcomes = get_curriculum_outcomes(topic, year_level, subject)
        return {"outcomes": outcomes}
    except Exception as e:
        logger.error(f"Error searching curriculum: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search curriculum: {str(e)}"
        )


@app.get("/api/v1/misconceptions/{topic}")
async def get_misconceptions(topic: str):
    """
    Get misconceptions for a topic.
    
    Args:
        topic: Topic to get misconceptions for
        
    Returns:
        List of misconceptions
    """
    from app.pipeline.modules.misconception_checker import MisconceptionChecker
    
    try:
        checker = MisconceptionChecker()
        misconceptions = checker._find_misconceptions(topic)
        return {"misconceptions": misconceptions}
    except Exception as e:
        logger.error(f"Error getting misconceptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get misconceptions: {str(e)}"
        )


@app.post("/api/v1/fact-check")
async def fact_check_text(request: dict):
    """
    Fact-check a piece of text.
    
    Args:
        request: Dictionary with "text" key containing text to fact-check
        
    Returns:
        Fact-check results
    """
    from app.services.fact_check_service import extract_factual_claims, check_fact
    
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text field is required"
            )
        
        claims = extract_factual_claims(text)
        results = [check_fact(claim) for claim in claims]
        
        verified_count = sum(1 for r in results if r.get("verified", False))
        confidence = (verified_count / len(results) * 100) if results else 100.0
        
        return {
            "claims": results,
            "confidence_score": confidence,
            "total_claims": len(results),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fact-checking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fact-check: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
