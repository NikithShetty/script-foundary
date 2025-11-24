"""LangGraph workflow creation and compilation."""

from langgraph.graph import StateGraph, END
from app.agents.state import SessionState
from app.agents.nodes import (
    conversation_node,
    curriculum_agent_node,
    information_gathering_node,
    script_generation_node,
    fact_checking_node,
)
from app.agents.conditions import (
    check_if_ready_to_generate,
    check_fact_check_results,
)
from app.config import settings


def create_script_generation_workflow():
    """Create the LangGraph workflow for script generation."""
    
    workflow = StateGraph(SessionState)
    
    # Add all nodes
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("curriculum_agent", curriculum_agent_node)
    workflow.add_node("information_gathering", information_gathering_node)
    workflow.add_node("script_generation", script_generation_node)
    workflow.add_node("fact_checking", fact_checking_node)
    
    # Set entry point
    workflow.set_entry_point("conversation")
    
    # Sequential edges
    workflow.add_edge("conversation", "information_gathering")
    workflow.add_edge("curriculum_agent", "information_gathering")
    workflow.add_edge("script_generation", "fact_checking")
    
    # Conditional edge: Information Gathering → Check readiness
    workflow.add_conditional_edges(
        "information_gathering",
        check_if_ready_to_generate,
        {
            "continue_conversation": "conversation",  # Need more info
            "gather_curriculum": "curriculum_agent",  # Need curriculum
            "ready": "script_generation"  # All info ready
        }
    )
    
    # Conditional edge: Fact Checking → Refine or Complete
    workflow.add_conditional_edges(
        "fact_checking",
        check_fact_check_results,
        {
            "refine": "script_generation",  # Needs refinement
            "complete": END  # Script is ready
        }
    )
    
    return workflow.compile()

