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
    from app.config import settings

    max_iterations = state.get(
        "max_refinement_iterations", settings.max_refinement_iterations
    )
    current_iterations = state.get("refinement_iterations", 0)
    needs_refinement = state.get("needs_refinement", False)
    confidence_score = state.get("confidence_score", 1.0)

    logger.info("\n" + "=" * 80)
    logger.info("[DECISION] check_fact_check_results")
    logger.info(f"  Current Iterations: {current_iterations}/{max_iterations}")
    logger.info(f"  Needs Refinement: {needs_refinement}")
    logger.info(f"  Status in state: {state.get('status')}")
    logger.info(f"  Confidence Score: {confidence_score:.2f}")

    # Check if status is already set to "completed" by the node (e.g., max iterations exceeded)
    # This takes priority - if node already completed, route to END
    if state.get("status") == "completed":
        decision = "complete"
        logger.info(
            f"  → DECISION: {decision} (status already set to completed by node)"
        )
        logger.info("=" * 80)
        return decision

    # Check if we've exceeded max iterations
    # Note: State modifications (warnings, status) are handled in fact_checking_node
    # This function only returns routing decisions
    if current_iterations >= max_iterations:
        decision = "complete"
        logger.info(
            f"  → DECISION: {decision} (max iterations reached: {current_iterations}/{max_iterations})"
        )
        logger.info("=" * 80)
        return decision

    # Check if the NEXT iteration would exceed max (defensive check)
    # This handles the case where the node incremented but status wasn't updated correctly
    next_iteration = current_iterations + 1
    if next_iteration > max_iterations:
        decision = "complete"
        logger.info(
            f"  → DECISION: {decision} (next iteration {next_iteration} would exceed max {max_iterations})"
        )
        logger.info("=" * 80)
        return decision

    # Check if refinement is needed
    # But first, double-check we're not at max iterations (defensive)
    # This handles edge cases where state might be inconsistent
    if current_iterations >= max_iterations or next_iteration > max_iterations:
        decision = "complete"
        logger.info(
            f"  → DECISION: {decision} (defensive check: iterations {current_iterations}/{max_iterations}, next would be {next_iteration})"
        )
        logger.info("=" * 80)
        return decision

    confidence_threshold = settings.fact_checker_confidence_threshold
    if needs_refinement and confidence_score < confidence_threshold:
        decision = "refine"
        logger.info(
            f"  → DECISION: {decision} (low confidence: {confidence_score:.2f} < {confidence_threshold})"
        )
    else:
        decision = "complete"
        logger.info(
            f"  → DECISION: {decision} (confidence acceptable: {confidence_score:.2f} >= {confidence_threshold})"
        )

    logger.info("=" * 80)
    return decision
