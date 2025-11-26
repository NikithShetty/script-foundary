"""LangGraph workflow creation and compilation."""

from langgraph.graph import StateGraph, END
from app.agents.state import SessionState
from app.agents.nodes import (
    conversation_node,
    curriculum_agent_node,
    script_generation_node,
    fact_checking_node,
)
from app.agents.conditions import (
    check_readiness,
    check_fact_check_results,
)


def create_script_generation_workflow():
    """Create the LangGraph workflow for script generation."""

    workflow = StateGraph(SessionState)

    # Add all nodes
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("curriculum_agent", curriculum_agent_node)
    workflow.add_node("script_generation", script_generation_node)
    workflow.add_node("fact_checking", fact_checking_node)

    # Set entry point
    workflow.set_entry_point("conversation")

    # Conditional edge: Conversation → Route based on completeness and curriculum needs
    workflow.add_conditional_edges(
        "conversation",
        check_readiness,
        {
            "continue_conversation": END,  # Missing required info, return to user
            "gather_curriculum": "curriculum_agent",  # Need curriculum
            "ready": "script_generation",  # All info ready
        },
    )

    # Sequential edges
    workflow.add_edge("script_generation", "fact_checking")

    # Conditional edge: Curriculum Agent → Check readiness after curriculum fetch
    workflow.add_conditional_edges(
        "curriculum_agent",
        check_readiness,
        {
            "continue_conversation": "conversation",  # Need more info, loop back to conversation
            "gather_curriculum": "curriculum_agent",  # Need curriculum (shouldn't happen, but handle edge case)
            "ready": "script_generation",  # All info ready
        },
    )

    # Conditional edge: Fact Checking → Refine or Complete
    workflow.add_conditional_edges(
        "fact_checking",
        check_fact_check_results,
        {
            "refine": "script_generation",  # Needs refinement
            "complete": END,  # Script is ready
        },
    )

    return workflow.compile()
