"""Chat session models for request and response."""

from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str = Field(..., description="User message content")


class AgentAction(BaseModel):
    """Model for agent action tracking."""
    agent: str
    action: str
    status: str


class ChatResponse(BaseModel):
    """Response model for chat message."""
    message_id: str
    role: Literal["assistant"]
    content: str
    session_id: str
    collected_data: Dict[str, Any]
    status: str
    missing_fields: List[str]
    ready_to_generate: bool
    agent_actions: List[AgentAction] = Field(default_factory=list)


class SessionStatus(BaseModel):
    """Model for session status response."""
    session_id: str
    status: str
    collected_data: Dict[str, Any]
    missing_fields: List[str]
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    generation_progress: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScriptResponse(BaseModel):
    """Model for script retrieval response."""
    session_id: str
    topic: str
    year_level: int
    learning_objective: str
    script: str
    scenes: List[Dict[str, Any]]
    curriculum: Dict[str, Any]
    fact_checking: Dict[str, Any]
    misconceptions: Dict[str, Any] = Field(default_factory=dict)
    cultural_safety: Dict[str, Any] = Field(default_factory=dict)
    accessibility: Dict[str, Any] = Field(default_factory=dict)


class GenerationStatus(BaseModel):
    """Model for generation status polling."""
    status: str
    progress: float = Field(ge=0.0, le=1.0)
    current_step: str
    current_agent: str
    estimated_time_remaining: Optional[int] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class SessionSummary(BaseModel):
    """Model for session summary in list view."""
    session_id: str
    topic: Optional[str] = None
    year_level: Optional[int] = None
    subject: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

