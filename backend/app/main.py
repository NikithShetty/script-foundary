"""FastAPI main application entry point."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.models.script import ScriptInput, ScriptOutput
from app.models.pipeline import PipelineConfig
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    SessionStatus,
    ScriptResponse,
    GenerationStatus,
    AgentAction,
)
from app.pipeline.core import run_pipeline
from app.config import settings, get_pipeline_config_from_settings
from app.utils.validators import (
    validate_year_level,
    validate_topic,
    validate_learning_objective,
)
from app.agents.workflow import create_script_generation_workflow
from app.services.session_storage import (
    store_session,
    load_session,
    delete_session,
    create_initial_state,
)
from app.agents.nodes import identify_missing_fields
import logging
import os
import uuid
from datetime import datetime
from typing import Any

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


# Print loaded settings values on startup if debug is enabled
if settings.debug:
    def mask_sensitive_value(key: str, value: Any) -> str:
        """Mask sensitive values in environment variables."""
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
    
    logger.info("=" * 60)
    logger.info("DEBUG MODE: Loaded Settings Values (from .env file + environment)")
    logger.info("=" * 60)
    
    # Show actual settings values (these come from .env file + os.environ)
    for field_name, field_value in settings.model_dump().items():
        masked = mask_sensitive_value(field_name, field_value)
        logger.info(f"  {field_name}={masked}")
    
    logger.info("=" * 60)


# Create workflow instance (singleton)
workflow = create_script_generation_workflow()


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


# ============================================================================
# Chat Session Endpoints
# ============================================================================

@app.post("/api/v1/chat/sessions", response_model=SessionStatus)
async def create_session():
    """
    Create a new conversation session.
    
    Returns:
        Session status with session_id
    """
    try:
        session_id = str(uuid.uuid4())
        initial_state = create_initial_state(session_id)
        
        # Store initial state
        await store_session(session_id, initial_state)
        
        return SessionStatus(
            session_id=session_id,
            status=initial_state["status"],
            collected_data={
                "topic": initial_state.get("topic"),
                "year_level": initial_state.get("year_level"),
                "learning_objective": initial_state.get("learning_objective"),
                "subject": initial_state.get("subject"),
            },
            missing_fields=identify_missing_fields(initial_state),
            conversation_history=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@app.post("/api/v1/chat/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(session_id: str, request: ChatRequest):
    """
    Send message to orchestrator and process through workflow.
    
    Args:
        session_id: Session identifier
        request: Chat request with message
        
    Returns:
        Chat response with assistant message and state
    """
    try:
        # Load session state
        state = await load_session(session_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Update with user input
        state["user_input"] = request.message
        
        # Invoke workflow with recursion limit
        config = {
            "configurable": {"thread_id": session_id},
            "recursion_limit": settings.graph_recursion_limit
        }
        result = await workflow.ainvoke(state, config)
        
        # Save updated state
        await store_session(session_id, result)
        
        # Extract latest assistant message
        messages = result.get("messages", [])
        assistant_message = None
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "ai":
                assistant_message = msg.content
                break
        
        if not assistant_message:
            assistant_message = "I'm processing your request..."
        
        # Build agent actions list
        agent_actions = []
        if result.get("status") == "gathering_curriculum":
            agent_actions.append(AgentAction(
                agent="curriculum_agent",
                action="fetching_curriculum",
                status="in_progress"
            ))
        elif result.get("status") == "generating":
            subject = result.get("subject", "default")
            agent_actions.append(AgentAction(
                agent=f"{subject.lower()}_script_agent",
                action="generating_script",
                status="in_progress"
            ))
        elif result.get("status") == "fact_checking":
            agent_actions.append(AgentAction(
                agent="fact_checker_agent",
                action="verifying_facts",
                status="in_progress"
            ))
        
        # Format response
        return ChatResponse(
            message_id=str(uuid.uuid4()),
            role="assistant",
            content=assistant_message,
            session_id=session_id,
            collected_data={
                "topic": result.get("topic"),
                "year_level": result.get("year_level"),
                "learning_objective": result.get("learning_objective"),
                "subject": result.get("subject"),
            },
            status=result.get("status", "collecting_info"),
            missing_fields=identify_missing_fields(result),
            ready_to_generate=result.get("ready_to_generate", False),
            agent_actions=agent_actions,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@app.get("/api/v1/chat/sessions/{session_id}", response_model=SessionStatus)
async def get_session(session_id: str):
    """
    Get current session status and collected data.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session status
    """
    try:
        state = await load_session(session_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Format conversation history
        conversation_history = []
        for msg in state.get("messages", []):
            if hasattr(msg, "type") and hasattr(msg, "content"):
                conversation_history.append({
                    "role": msg.type,
                    "content": msg.content
                })
        
        # Build generation progress
        generation_progress = None
        if state.get("status") in ["generating", "fact_checking", "needs_refinement"]:
            progress_map = {
                "generating": 0.5,
                "fact_checking": 0.75,
                "needs_refinement": 0.6,
            }
            generation_progress = {
                "current_step": state.get("status"),
                "current_agent": _get_current_agent(state),
                "progress": progress_map.get(state.get("status"), 0.0),
            }
        
        return SessionStatus(
            session_id=session_id,
            status=state.get("status", "collecting_info"),
            collected_data={
                "topic": state.get("topic"),
                "year_level": state.get("year_level"),
                "learning_objective": state.get("learning_objective"),
                "subject": state.get("subject"),
            },
            missing_fields=identify_missing_fields(state),
            conversation_history=conversation_history,
            generation_progress=generation_progress,
            created_at=datetime.now(),  # TODO: Store actual created_at in state
            updated_at=datetime.now(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@app.get("/api/v1/chat/sessions/{session_id}/script", response_model=ScriptResponse)
async def get_script(session_id: str):
    """
    Retrieve generated script when status is "completed".
    
    Args:
        session_id: Session identifier
        
    Returns:
        Complete script with all metadata
    """
    try:
        state = await load_session(session_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        if state.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Script not ready. Current status: {state.get('status')}"
            )
        
        script = state.get("script")
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found in session"
            )
        
        return ScriptResponse(
            session_id=session_id,
            topic=state.get("topic", ""),
            year_level=state.get("year_level", 0),
            learning_objective=state.get("learning_objective", ""),
            script=script,
            scenes=state.get("script_scenes", []),
            curriculum={
                "outcomes": state.get("curriculum_outcomes", []),
                "codes": state.get("curriculum_codes", []),
            },
            fact_checking={
                "confidence_score": state.get("confidence_score", 0.0),
                "results": state.get("fact_check_results", {}),
            },
            misconceptions={"misconceptions": state.get("misconceptions", [])},
            cultural_safety={"flags": state.get("cultural_safety_flags", [])},
            accessibility={"metadata": state.get("accessibility_metadata", {})},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting script: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get script: {str(e)}"
        )


@app.get("/api/v1/chat/sessions/{session_id}/generation/status", response_model=GenerationStatus)
async def get_generation_status(session_id: str):
    """
    Poll for generation status (for long-running operations).
    
    Args:
        session_id: Session identifier
        
    Returns:
        Generation status with progress
    """
    try:
        state = await load_session(session_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        status_value = state.get("status", "collecting_info")
        progress_map = {
            "collecting_info": 0.1,
            "gathering_curriculum": 0.2,
            "ready_to_generate": 0.3,
            "generating": 0.5,
            "script_generated": 0.6,
            "fact_checking": 0.75,
            "needs_refinement": 0.6,
            "completed": 1.0,
            "failed": 0.0,
        }
        
        return GenerationStatus(
            status=status_value,
            progress=progress_map.get(status_value, 0.0),
            current_step=status_value,
            current_agent=_get_current_agent(state),
            estimated_time_remaining=None,  # TODO: Calculate based on progress
            errors=state.get("errors", []),
            warnings=state.get("warnings", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generation status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get generation status: {str(e)}"
        )


def _get_current_agent(state: dict) -> str:
    """Get the name of the current agent based on state."""
    status_value = state.get("status", "")
    if status_value == "gathering_curriculum":
        return "curriculum_agent"
    elif status_value == "generating":
        subject = state.get("subject", "default")
        return f"{subject.lower()}_script_agent"
    elif status_value == "fact_checking":
        return "fact_checker_agent"
    else:
        return "orchestrator_agent"


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
