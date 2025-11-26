"""Conditional edge functions for LangGraph workflow routing."""

import logging
from app.agents.state import SessionState

logger = logging.getLogger(__name__)


def check_readiness(state: SessionState) -> str:
    """
    Unified function to check if we're ready to proceed to script generation.
    Used after both conversation and curriculum_agent nodes.

    Returns: "continue_conversation" | "gather_curriculum" | "ready" | "modify_script"

    Note: The workflow handles context-specific routing:
    - After conversation: "continue_conversation" → END (return to user)
    - After curriculum_agent: "continue_conversation" → conversation (loop back)
    - "modify_script" → script_generation (for user-requested modifications)
    """
    topic = state.get("topic")
    year_level = state.get("year_level")
    learning_objective = state.get("learning_objective")
    curriculum_outcomes = state.get("curriculum_outcomes", [])
    is_modification_request = state.get("is_modification_request", False)
    existing_script = state.get("script")

    logger.info("\n" + "=" * 80)
    logger.info("[DECISION] check_readiness")
    logger.info(f"  Topic: {topic}")
    logger.info(f"  Year Level: {year_level}")
    logger.info(f"  Learning Objective: {learning_objective}")
    logger.info(f"  Has Curriculum: {len(curriculum_outcomes) > 0}")
    logger.info(f"  Is Modification Request: {is_modification_request}")
    logger.info(f"  Has Existing Script: {bool(existing_script)}")

    # Check if this is a modification request
    if is_modification_request and existing_script:
        decision = "modify_script"
        logger.info(f"  → DECISION: {decision} (user requested script modification)")
        logger.info("=" * 80)
        return decision

    # Check if we have topic and year_level but no curriculum
    if topic and year_level and not curriculum_outcomes:
        decision = "gather_curriculum"
        logger.info(f"  → DECISION: {decision} (need curriculum)")
        logger.info("=" * 80)
        return decision

    # Check if all required fields are present
    required_fields = ["topic", "year_level", "learning_objective"]
    all_present = all(state.get(field) for field in required_fields)

    if all_present:
        decision = "ready"
        logger.info(
            f"  → DECISION: {decision} (all fields ready, proceed to script generation)"
        )
    else:
        decision = "continue_conversation"
        missing = [f for f in required_fields if not state.get(f)]
        logger.info(f"  → DECISION: {decision} (missing fields: {missing})")

    logger.info("=" * 80)
    return decision


def check_fact_check_results(state: SessionState) -> str:
    """
    Determine if script needs refinement based on fact-check results.
    Returns: "refine" | "complete"
    """
    max_iterations = state.get("max_refinement_iterations", 3)
    current_iterations = state.get("refinement_iterations", 0)
    needs_refinement = state.get("needs_refinement", False)
    confidence_score = state.get("confidence_score", 1.0)

    logger.info("\n" + "=" * 80)
    logger.info("[DECISION] check_fact_check_results")
    logger.info(f"  Current Iterations: {current_iterations}/{max_iterations}")
    logger.info(f"  Needs Refinement: {needs_refinement}")
    logger.info(f"  Confidence Score: {confidence_score:.2f}")

    # Check if we've exceeded max iterations
    if current_iterations >= max_iterations:
        decision = "complete"
        logger.info(f"  → DECISION: {decision} (max iterations reached)")
        logger.info("=" * 80)
        return decision

    # Check if refinement is needed
    if needs_refinement and confidence_score < 0.8:
        decision = "refine"
        logger.info(f"  → DECISION: {decision} (low confidence)")
    else:
        decision = "complete"
        logger.info(f"  → DECISION: {decision} (confidence acceptable)")

    logger.info("=" * 80)
    return decision
