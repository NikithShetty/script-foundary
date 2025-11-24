"""Conditional edge functions for LangGraph workflow routing."""

from app.agents.state import SessionState


def check_if_ready_to_generate(state: SessionState) -> str:
    """
    Determine next step after information gathering.
    Returns: "continue_conversation" | "gather_curriculum" | "ready"
    """
    # Check if we have topic and year_level but no curriculum
    if state.get("topic") and state.get("year_level") and \
       not state.get("curriculum_outcomes"):
        return "gather_curriculum"
    
    # Check if all required fields are present
    required_fields = ["topic", "year_level", "learning_objective"]
    all_present = all(state.get(field) for field in required_fields)
    
    if all_present:
        return "ready"
    
    return "continue_conversation"


def check_fact_check_results(state: SessionState) -> str:
    """
    Determine if script needs refinement based on fact-check results.
    Returns: "refine" | "complete"
    """
    max_iterations = state.get("max_refinement_iterations", 3)
    current_iterations = state.get("refinement_iterations", 0)
    
    # Check if we've exceeded max iterations
    if current_iterations >= max_iterations:
        return "complete"  # Give up after max iterations
    
    # Check if refinement is needed
    needs_refinement = state.get("needs_refinement", False)
    confidence_score = state.get("confidence_score", 1.0)
    
    if needs_refinement and confidence_score < 0.8:
        return "refine"
    
    return "complete"

