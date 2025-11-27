"""SessionState definition for LangGraph workflow."""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class SessionState(TypedDict):
    """State shared across all nodes in the workflow."""

    # Session identification
    session_id: str
    status: str  # "collecting_info", "generating", "fact_checking", "refining", "completed", "failed"

    # Conversation management
    messages: Annotated[List[BaseMessage], add_messages]  # LangGraph message handling
    user_input: Optional[str]  # Latest user message

    # Collected information (from educator)
    learning_objective: Optional[str]
    topic: Optional[str]
    year_level: Optional[str]
    subject: Optional[str]  # "Science", "Math", "English", etc.
    script_pace: Optional[
        str
    ]  # "slow", "normal", "fast" - defaults to "slow" for first-time learners

    # Supporting information (from agents)
    curriculum_outcomes: List[Dict[str, Any]]
    curriculum_codes: List[str]
    prerequisites: List[str]
    misconceptions: List[Dict[str, Any]]
    cultural_safety_flags: List[str]
    accessibility_metadata: Dict[str, Any]

    # Generated content
    script: Optional[str]
    script_scenes: List[Dict[str, Any]]

    # Fact checking results
    fact_check_results: Dict[str, Any]
    confidence_score: Optional[float]  # 0.0 to 1.0
    refinement_iterations: int  # Track refinement count

    # Control flow flags
    ready_to_generate: bool
    needs_refinement: bool
    max_refinement_iterations: int  # Default: 3
    is_modification_request: bool  # Track user-requested modifications
    modification_request: Optional[str]  # Store the user's change request text

    # Error handling
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
