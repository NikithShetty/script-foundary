"""LangGraph node implementations for the workflow."""

import logging
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.state import SessionState
from app.services.llm_service import (
    extract_information_from_message,
    generate_conversation_response,
)
from app.services.curriculum_api import get_curriculum_outcomes, get_prerequisites
from app.services.fact_check_service import extract_factual_claims, check_fact
from app.agents.generators import (
    ScienceScriptAgent,
    MathScriptAgent,
    EnglishScriptAgent,
    DefaultScriptAgent,
)

logger = logging.getLogger(__name__)


def get_script_generator_for_subject(
    subject: str, node_name: str = "script_generation"
):
    """
    Get the appropriate script generator for a subject.

    Args:
        subject: Subject name
        node_name: Node name for LLM configuration (default: "script_generation")
    """
    if not subject:
        return DefaultScriptAgent(node_name=node_name)

    subject_lower = subject.lower()
    if "science" in subject_lower:
        return ScienceScriptAgent(node_name=node_name)
    elif "math" in subject_lower or "mathematics" in subject_lower:
        return MathScriptAgent(node_name=node_name)
    elif "english" in subject_lower or "language" in subject_lower:
        return EnglishScriptAgent(node_name=node_name)
    else:
        return DefaultScriptAgent(node_name=node_name)


def identify_missing_fields(state: SessionState) -> list:
    """Identify missing required fields."""
    required_fields = {
        "topic": state.get("topic"),
        "year_level": state.get("year_level"),
        "learning_objective": state.get("learning_objective"),
    }
    return [field for field, value in required_fields.items() if not value]


def update_readiness_status(state: SessionState) -> SessionState:
    """
    Update status and ready_to_generate flag based on current state.
    This replaces the logic that was in information_gathering_node.
    """
    # Check completeness of required fields
    has_topic = bool(state.get("topic"))
    has_year_level = bool(state.get("year_level"))
    has_learning_objective = bool(state.get("learning_objective"))

    # Check if all required info is present
    required_fields = {
        "topic": has_topic,
        "year_level": has_year_level,
        "learning_objective": has_learning_objective,
    }

    all_ready = all(required_fields.values())
    state["ready_to_generate"] = all_ready

    # Update status based on readiness
    if all_ready:
        state["status"] = "ready_to_generate"
    else:
        state["status"] = "collecting_info"

    return state


async def conversation_node(state: SessionState) -> SessionState:
    """
    Handle conversation with educator.
    Extracts information and generates responses.
    """
    try:
        # Extract user message
        user_message = state.get("user_input", "")
        if not user_message:
            state["errors"].append("No user input provided")
            state["status"] = "failed"
            return state

        messages = state.get("messages", [])

        # Add user message to conversation history
        messages.append(HumanMessage(content=user_message))

        # Use LLM to extract structured information
        extracted_info = await extract_information_from_message(
            message=user_message, current_state=state, node_name="conversation"
        )

        # Update state with extracted fields
        if extracted_info.get("topic"):
            state["topic"] = extracted_info["topic"]
        if extracted_info.get("year_level"):
            state["year_level"] = extracted_info["year_level"]
        if extracted_info.get("learning_objective"):
            state["learning_objective"] = extracted_info["learning_objective"]
        if extracted_info.get("subject"):
            state["subject"] = extracted_info["subject"]

        # Generate appropriate response
        missing_fields = identify_missing_fields(state)
        response = await generate_conversation_response(
            state=state, missing_fields=missing_fields, node_name="conversation"
        )

        # Add assistant response to conversation
        messages.append(AIMessage(content=response))
        state["messages"] = messages

        # Update readiness status after extracting information
        # This ensures status and ready_to_generate are kept in sync
        state = update_readiness_status(state)

        return state
    except Exception as e:
        logger.error(f"Error in conversation_node: {str(e)}", exc_info=True)
        state["errors"].append(f"conversation_node: {str(e)}")
        state["status"] = "failed"
        return state


async def curriculum_agent_node(state: SessionState) -> SessionState:
    """
    Fetch curriculum information from CurricuLLM-AU API.
    Can be called by orchestrator or script generator.
    """
    try:
        topic = state.get("topic")
        year_level = state.get("year_level")
        subject = state.get("subject")

        # Set status to indicate we're gathering curriculum
        # This replaces the status update that was in information_gathering_node
        state["status"] = "gathering_curriculum"

        # Validate required fields
        if not topic or not year_level:
            state["warnings"].append(
                "Cannot fetch curriculum: missing topic or year_level"
            )
            return state

        # Call curriculum API (existing service)
        outcomes = get_curriculum_outcomes(
            topic=topic, year_level=year_level, subject=subject
        )

        # Update state
        state["curriculum_outcomes"] = outcomes
        state["curriculum_codes"] = [
            outcome.get("code", "") for outcome in outcomes if outcome.get("code")
        ]

        # Get prerequisites if available
        prerequisites = get_prerequisites(topic, year_level)
        state["prerequisites"] = prerequisites

        # Update readiness status after fetching curriculum
        # This replaces the state updates that were in information_gathering_node
        state = update_readiness_status(state)

        return state
    except Exception as e:
        logger.error(f"Error in curriculum_agent_node: {str(e)}", exc_info=True)
        state["warnings"].append(f"curriculum_agent_node: {str(e)}")
        return state


async def information_gathering_node(state: SessionState) -> SessionState:
    """
    Orchestrator checks what information is needed and coordinates gathering.
    """
    try:
        # Check completeness of required fields
        has_topic = bool(state.get("topic"))
        has_year_level = bool(state.get("year_level"))
        has_learning_objective = bool(state.get("learning_objective"))
        has_curriculum = len(state.get("curriculum_outcomes", [])) > 0

        # If we have basic info but no curriculum, mark for curriculum fetch
        if has_topic and has_year_level and not has_curriculum:
            state["status"] = "gathering_curriculum"
            return state

        # Check if all required info is present
        required_fields = {
            "topic": has_topic,
            "year_level": has_year_level,
            "learning_objective": has_learning_objective,
        }

        all_ready = all(required_fields.values())
        state["ready_to_generate"] = all_ready

        if all_ready:
            state["status"] = "ready_to_generate"
        else:
            state["status"] = "collecting_info"

        return state
    except Exception as e:
        logger.error(f"Error in information_gathering_node: {str(e)}", exc_info=True)
        state["errors"].append(f"information_gathering_node: {str(e)}")
        state["status"] = "failed"
        return state


async def script_generation_node(state: SessionState) -> SessionState:
    """
    Generate script using subject-specific agent.
    Can be called for initial generation or refinement.
    """
    try:
        state["status"] = "generating"

        # Select appropriate script generator based on subject
        subject = state.get("subject", "")
        script_generator = get_script_generator_for_subject(
            subject, node_name="script_generation"
        )

        # Build context for script generation
        context = {
            "topic": state["topic"],
            "year_level": state["year_level"],
            "learning_objective": state["learning_objective"],
            "subject": state.get("subject"),
            "curriculum_outcomes": state.get("curriculum_outcomes", []),
            "curriculum_codes": state.get("curriculum_codes", []),
            "misconceptions": state.get("misconceptions", []),
        }

        # If this is a refinement, include fact-check feedback
        if state.get("needs_refinement"):
            fact_check_results = state.get("fact_check_results", {})
            context["fact_check_issues"] = fact_check_results.get("issues", [])
            context["low_confidence_claims"] = fact_check_results.get(
                "low_confidence_claims", []
            )
            context["refinement_notes"] = (
                "Address the following fact-check issues in the script"
            )

        # Generate script using selected agent
        script_result = await script_generator.generate(context)

        # Update state
        state["script"] = script_result["script"]
        state["script_scenes"] = script_result.get("scenes", [])
        state["status"] = "script_generated"

        return state
    except Exception as e:
        logger.error(f"Error in script_generation_node: {str(e)}", exc_info=True)
        state["errors"].append(f"script_generation_node: {str(e)}")
        state["status"] = "failed"
        return state


async def fact_checking_node(state: SessionState) -> SessionState:
    """
    Verify factual accuracy of generated script.
    """
    try:
        state["status"] = "fact_checking"

        script = state.get("script", "")
        if not script:
            state["errors"].append("No script available for fact-checking")
            state["status"] = "failed"
            return state

        # Extract factual claims from script
        claims = extract_factual_claims(script)

        # Check each claim
        results = []
        verified_count = 0

        for claim in claims:
            result = check_fact(claim)  # Uses existing fact_check_service
            results.append(result)
            if result.get("verified", False):
                verified_count += 1

        # Calculate confidence score
        confidence_score = (verified_count / len(claims)) if claims else 1.0

        # Update state with results
        state["fact_check_results"] = {
            "claims": results,
            "confidence_score": confidence_score,
            "total_claims": len(claims),
            "verified_claims": verified_count,
            "issues": [r for r in results if not r.get("verified", False)],
            "low_confidence_claims": [
                r for r in results if r.get("confidence", 0) < 0.5
            ],
        }
        state["confidence_score"] = confidence_score

        # Determine if refinement is needed
        confidence_threshold = 0.8  # 80%
        state["needs_refinement"] = confidence_score < confidence_threshold

        if state["needs_refinement"]:
            state["refinement_iterations"] = state.get("refinement_iterations", 0) + 1
            state["status"] = "needs_refinement"
        else:
            state["status"] = "completed"

        return state
    except Exception as e:
        logger.error(f"Error in fact_checking_node: {str(e)}", exc_info=True)
        state["errors"].append(f"fact_checking_node: {str(e)}")
        state["status"] = "failed"
        return state
