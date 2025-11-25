"""Session storage service for state persistence."""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.config import settings
from app.agents.state import SessionState

logger = logging.getLogger(__name__)

# Try to import Redis, fall back to in-memory if not available
try:
    import redis
    redis_client = None
    if settings.redis_url:
        try:
            redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            redis_client.ping()  # Test connection
            logger.info("Using Redis for session storage")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
            redis_client = None
except ImportError:
    logger.warning("Redis not available. Using in-memory storage.")
    redis_client = None

# In-memory storage fallback
_in_memory_storage: Dict[str, Dict[str, Any]] = {}
_session_ttl = timedelta(hours=24)


def _serialize_state(state: SessionState) -> str:
    """Serialize SessionState to JSON string."""
    # Convert to dict and handle special types
    state_dict = dict(state)
    
    # Convert messages to serializable format
    if "messages" in state_dict:
        messages = state_dict["messages"]
        serialized_messages = []
        for msg in messages:
            if hasattr(msg, "content") and hasattr(msg, "type"):
                serialized_messages.append({
                    "type": msg.type,
                    "content": msg.content
                })
        state_dict["messages"] = serialized_messages
    
    return json.dumps(state_dict, default=str)


def _deserialize_state(state_json: str) -> SessionState:
    """Deserialize JSON string to SessionState."""
    state_dict = json.loads(state_json)
    
    # Reconstruct messages from serialized format
    if "messages" in state_dict:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        messages = []
        for msg_dict in state_dict["messages"]:
            msg_type = msg_dict.get("type", "")
            content = msg_dict.get("content", "")
            if msg_type == "human":
                messages.append(HumanMessage(content=content))
            elif msg_type == "ai":
                messages.append(AIMessage(content=content))
            elif msg_type == "system":
                messages.append(SystemMessage(content=content))
        state_dict["messages"] = messages
    
    # TypedDict is just a type hint, return dict directly
    return state_dict  # type: ignore


async def store_session(session_id: str, state: SessionState) -> None:
    """Store session state in Redis or in-memory storage."""
    try:
        state_json = _serialize_state(state)
        
        if redis_client:
            # Store in Redis with TTL
            redis_client.setex(
                f"session:{session_id}",
                int(_session_ttl.total_seconds()),
                state_json
            )
        else:
            # Store in memory
            now = datetime.now()
            if session_id not in _in_memory_storage:
                # New session, store creation time
                _in_memory_storage[session_id] = {
                    "state": state_json,
                    "expires_at": now + _session_ttl,
                    "created_at": now,
                }
            else:
                # Update existing session
                existing = _in_memory_storage[session_id]
                existing["state"] = state_json
                existing["expires_at"] = now + _session_ttl
                if "created_at" not in existing:
                    existing["created_at"] = now
            # Clean up expired sessions
            _cleanup_expired_sessions()
        
        logger.debug(f"Stored session {session_id}")
    except Exception as e:
        logger.error(f"Error storing session {session_id}: {str(e)}", exc_info=True)
        raise


async def load_session(session_id: str) -> Optional[SessionState]:
    """Load session state from storage."""
    try:
        state_json = None
        
        if redis_client:
            # Load from Redis
            state_json = redis_client.get(f"session:{session_id}")
        else:
            # Load from memory
            if session_id in _in_memory_storage:
                session_data = _in_memory_storage[session_id]
                if datetime.now() < session_data["expires_at"]:
                    state_json = session_data["state"]
                else:
                    # Expired, remove it
                    del _in_memory_storage[session_id]
        
        if state_json:
            return _deserialize_state(state_json)
        return None
    except Exception as e:
        logger.error(f"Error loading session {session_id}: {str(e)}", exc_info=True)
        return None


async def delete_session(session_id: str) -> None:
    """Delete a session from storage."""
    try:
        if redis_client:
            redis_client.delete(f"session:{session_id}")
        else:
            _in_memory_storage.pop(session_id, None)
        logger.debug(f"Deleted session {session_id}")
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}", exc_info=True)


def _cleanup_expired_sessions() -> None:
    """Clean up expired sessions from in-memory storage."""
    now = datetime.now()
    expired_keys = [
        key for key, data in _in_memory_storage.items()
        if now >= data["expires_at"]
    ]
    for key in expired_keys:
        del _in_memory_storage[key]


async def list_sessions() -> list[Dict[str, Any]]:
    """List all sessions with summary information."""
    try:
        sessions = []
        
        if redis_client:
            # Get all session keys from Redis
            keys = redis_client.keys("session:*")
            for key in keys:
                session_id = key.replace("session:", "")
                state_json = redis_client.get(key)
                if state_json:
                    try:
                        state = _deserialize_state(state_json)
                        # Extract summary information
                        sessions.append({
                            "session_id": session_id,
                            "topic": state.get("topic"),
                            "year_level": state.get("year_level"),
                            "subject": state.get("subject"),
                            "status": state.get("status", "unknown"),
                            "created_at": datetime.now(),  # Redis doesn't store creation time
                            "updated_at": datetime.now(),
                        })
                    except Exception as e:
                        logger.warning(f"Error parsing session {session_id}: {e}")
        else:
            # List from in-memory storage
            now = datetime.now()
            for session_id, session_data in _in_memory_storage.items():
                if now < session_data["expires_at"]:
                    try:
                        state = _deserialize_state(session_data["state"])
                        sessions.append({
                            "session_id": session_id,
                            "topic": state.get("topic"),
                            "year_level": state.get("year_level"),
                            "subject": state.get("subject"),
                            "status": state.get("status", "unknown"),
                            "created_at": session_data.get("created_at", datetime.now()),
                            "updated_at": session_data.get("expires_at", datetime.now()) - _session_ttl,
                        })
                    except Exception as e:
                        logger.warning(f"Error parsing session {session_id}: {e}")
        
        # Sort by updated_at descending (most recent first)
        sessions.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=True)
        return sessions
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}", exc_info=True)
        return []


def create_initial_state(session_id: str) -> SessionState:
    """Create initial SessionState with default values."""
    from langchain_core.messages import SystemMessage
    
    # TypedDict is just a type hint, return dict directly
    return {  # type: ignore
        "session_id": session_id,
        "status": "collecting_info",
        "messages": [SystemMessage(content="You are a helpful educational assistant.")],
        "user_input": None,
        "learning_objective": None,
        "topic": None,
        "year_level": None,
        "subject": None,
        "curriculum_outcomes": [],
        "curriculum_codes": [],
        "prerequisites": [],
        "misconceptions": [],
        "cultural_safety_flags": [],
        "accessibility_metadata": {},
        "script": None,
        "script_scenes": [],
        "fact_check_results": {},
        "confidence_score": None,
        "refinement_iterations": 0,
        "ready_to_generate": False,
        "needs_refinement": False,
        "max_refinement_iterations": 3,
        "errors": [],
        "warnings": [],
        "metadata": {},
    }

