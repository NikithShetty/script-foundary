"""Conditional edge functions for LangGraph workflow routing."""

import logging
from app.agents.state import SessionState

logger = logging.getLogger(__name__)


def check_if_ready_to_generate(state: SessionState) -> str:
    """
    Determine next step after information gathering.
    Returns: "continue_conversation" | "gather_curriculum" | "ready"
    """
    topic = state.get("topic")
    year_level = state.get("year_level")
    curriculum_outcomes = state.get("curriculum_outcomes", [])
    
    logger.info("\n" + "=" * 80)
    logger.info("[DECISION] check_if_ready_to_generate")
    logger.info(f"  Topic: {topic}")
    logger.info(f"  Year Level: {year_level}")
    logger.info(f"  Has Curriculum: {len(curriculum_outcomes) > 0}")
    
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
        logger.info(f"  → DECISION: {decision} (all fields ready)")
    else:
        decision = "continue_conversation"
        missing = [f for f in required_fields if not state.get(f)]
        logger.info(f"  → DECISION: {decision} (missing: {missing})")
    
    logger.info("=" * 80)
    return decision


def check_after_conversation(state: SessionState) -> str:
    """
    Determine next step after conversation node.
    If we still need more info, end workflow to return response to user.
    If we have all required info, continue to information gathering.
    Returns: "end" | "continue"
    """
    required_fields = ["topic", "year_level", "learning_objective"]
    all_present = all(state.get(field) for field in required_fields)
    
    logger.info("\n" + "=" * 80)
    logger.info("[DECISION] check_after_conversation")
    logger.info(f"  Topic: {state.get('topic')}")
    logger.info(f"  Year Level: {state.get('year_level')}")
    logger.info(f"  Learning Objective: {state.get('learning_objective')}")
    
    if all_present:
        decision = "continue"
        logger.info(f"  → DECISION: {decision} (all required fields present, continue to information gathering)")
    else:
        decision = "end"
        missing = [f for f in required_fields if not state.get(f)]
        logger.info(f"  → DECISION: {decision} (missing fields: {missing}, return to user)")
    
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

