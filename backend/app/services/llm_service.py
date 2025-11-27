"""LLM service for script generation using CurricuLLM or OpenAI."""

import os
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


def log_llm_call(
    function_name: str, messages: list, model: str, response_content: str, **kwargs
):
    """Log LLM call details."""
    logger.info("=" * 80)
    logger.info(f"[LLM CALL] {function_name}")
    logger.info("=" * 80)
    logger.info(f"Model: {model}")
    logger.info(f"Temperature: {kwargs.get('temperature', 'N/A')}")
    logger.info(f"Max Tokens: {kwargs.get('max_tokens', 'N/A')}")
    logger.info("\n--- REQUEST ---")
    for msg in messages:
        content_preview = (
            msg["content"][:500] if len(msg["content"]) > 500 else msg["content"]
        )
        logger.info(f"{msg['role'].upper()}: {content_preview}")
        if len(msg["content"]) > 500:
            logger.info(f"  ... (truncated, total length: {len(msg['content'])} chars)")
    logger.info("\n--- RESPONSE ---")
    response_preview = (
        response_content[:1000] if len(response_content) > 1000 else response_content
    )
    logger.info(f"{response_preview}")
    if len(response_content) > 1000:
        logger.info(f"... (truncated, total length: {len(response_content)} chars)")
    logger.info("=" * 80)


def get_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    use_general: bool = True,
):
    """
    Get LLM client (CurricuLLM or OpenAI) based on available API key.

    Args:
        provider: Optional provider name ("curricullm" or "openai"). If None, uses default priority.
        model: Optional model name. If None, uses default model for the provider.
        use_general: If True, uses general model (prioritized). If False, uses curriculum model.
                    Only used when provider is None.

    Returns:
        Tuple of (client, provider_name, model_name)
    """
    curricullm_key = settings.curricullm_api_key
    curricullm_url = settings.curricullm_api_url
    openai_key = settings.openai_api_key

    # If provider is specified, use it
    if provider:
        provider_lower = provider.lower()
        if provider_lower == "curricullm":
            if not curricullm_key:
                raise ValueError("CurricuLLM API key not found. Set CURRICULLM_API_KEY")
            model_name = model or settings.curricullm_model or settings.openai_model
            return (
                OpenAI(api_key=curricullm_key, base_url=curricullm_url),
                "curricullm",
                model_name,
            )
        elif provider_lower == "openai":
            if not openai_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY")
            model_name = model or settings.openai_model
            return OpenAI(api_key=openai_key), "openai", model_name
        else:
            raise ValueError(
                f"Unknown provider: {provider}. Use 'curricullm' or 'openai'"
            )

    # Default behavior: Prioritize general model (OpenAI) over curriculum model
    if use_general:
        # Use general model (prioritized)
        general_provider = settings.general_model_provider.lower()
        if general_provider == "openai" and openai_key:
            model_name = model or settings.general_model or settings.openai_model
            return OpenAI(api_key=openai_key), "openai", model_name
        elif general_provider == "curricullm" and curricullm_key:
            model_name = (
                model
                or settings.general_model
                or settings.curricullm_model
                or settings.openai_model
            )
            return (
                OpenAI(api_key=curricullm_key, base_url=curricullm_url),
                "curricullm",
                model_name,
            )
        # Fallback: try OpenAI if general provider not available
        if openai_key:
            model_name = model or settings.general_model or settings.openai_model
            return OpenAI(api_key=openai_key), "openai", model_name
        # Fallback: try CurricuLLM if OpenAI not available
        if curricullm_key:
            model_name = (
                model
                or settings.general_model
                or settings.curricullm_model
                or settings.openai_model
            )
            return (
                OpenAI(api_key=curricullm_key, base_url=curricullm_url),
                "curricullm",
                model_name,
            )
    else:
        # Use curriculum model
        curriculum_provider = settings.curriculum_model_provider.lower()
        if curriculum_provider == "curricullm" and curricullm_key:
            model_name = (
                model
                or settings.curriculum_model
                or settings.curricullm_model
                or settings.openai_model
            )
            return (
                OpenAI(api_key=curricullm_key, base_url=curricullm_url),
                "curricullm",
                model_name,
            )
        elif curriculum_provider == "openai" and openai_key:
            model_name = model or settings.curriculum_model or settings.openai_model
            return OpenAI(api_key=openai_key), "openai", model_name
        # Fallback: try CurricuLLM if curriculum provider not available
        if curricullm_key:
            model_name = (
                model
                or settings.curriculum_model
                or settings.curricullm_model
                or settings.openai_model
            )
            return (
                OpenAI(api_key=curricullm_key, base_url=curricullm_url),
                "curricullm",
                model_name,
            )
        # Fallback: try OpenAI if CurricuLLM not available
        if openai_key:
            model_name = model or settings.curriculum_model or settings.openai_model
            return OpenAI(api_key=openai_key), "openai", model_name

    raise ValueError("No LLM API key found. Set CURRICULLM_API_KEY or OPENAI_API_KEY")


# Hardcoded LLM configuration for specific nodes/edges
# Format: "node_name": {"provider": "openai"|"curricullm", "model": "model_name" or None, "use_curriculum": bool}
# - provider: "openai" or "curricullm" (optional, overrides use_curriculum)
# - model: Model name string (e.g., "gpt-4", "gpt-3.5-turbo") or None to use default for provider
# - use_curriculum: If True, uses curriculum model. If False or not set, uses general model (default)
# If node not in this dict, uses default behavior (prioritizes general model)
#
# Special nodes that automatically use curriculum model:
# - "curriculum_agent": Uses curriculum model
# - "script_generation": Uses curriculum model
NODE_LLM_CONFIG = {
    # Curriculum-specific nodes use curriculum model
    "curriculum_agent": {"use_curriculum": True},
    "script_generation": {"use_curriculum": True},
    # Other nodes can be customized here if needed:
    # "conversation": {"provider": "openai", "model": None},  # Uses general model (default)
    # "fact_checking": {"provider": "openai", "model": "gpt-4"},  # Uses specific model
}


def get_llm_client_for_node(node_name: str):
    """
    Get LLM client configured for a specific node.

    Args:
        node_name: Name of the node (e.g., "conversation", "script_generation", "curriculum_agent")

    Returns:
        Tuple of (client, provider_name, model_name)
    """
    # Check if there's a hardcoded configuration for this node
    node_config = NODE_LLM_CONFIG.get(node_name)

    if node_config:
        # If provider is explicitly set, use it
        if "provider" in node_config:
            provider = node_config.get("provider")
            model = node_config.get("model")
            return get_llm_client(provider=provider, model=model)

        # If use_curriculum is set, use curriculum model
        if node_config.get("use_curriculum", False):
            model = node_config.get("model")
            return get_llm_client(provider=None, model=model, use_general=False)

        # Otherwise use general model with optional model override
        model = node_config.get("model")
        return get_llm_client(provider=None, model=model, use_general=True)

    # Default behavior: Use general model (prioritized)
    return get_llm_client(use_general=True)


def generate_script(prompt: str, node_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate script using LLM.

    Args:
        prompt: System prompt for script generation
        node_name: Optional node name for node-specific LLM configuration

    Returns:
        Dictionary with script and scenes
    """
    if node_name:
        client, provider, model = get_llm_client_for_node(node_name)
    else:
        client, provider, model = get_llm_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational script writer.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        content = response.choices[0].message.content

        # Parse response into structured format
        # For now, return basic structure - can be enhanced with better parsing
        return {
            "script": content,
            "scenes": _parse_scenes_from_script(content),
        }
    except Exception as e:
        raise Exception(f"Failed to generate script: {str(e)}")


def _parse_scenes_from_script(script: str) -> List[Dict[str, Any]]:
    """
    Parse scenes from generated script text.

    Args:
        script: Generated script text

    Returns:
        List of scene dictionaries
    """
    import re
    
    scenes = []
    lines = script.split("\n")
    current_scene = None
    current_section = None
    collecting_content = False

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            collecting_content = False
            continue

        # Detect scene headers (Scene 1:, **Scene 1:**, ## Scene 1, etc.)
        scene_match = (
            line_stripped.upper().startswith("SCENE") or
            line_stripped.startswith("##") or
            (line_stripped.startswith("**") and "Scene" in line_stripped and ":" in line_stripped)
        )
        
        if scene_match:
            if current_scene:
                scenes.append(current_scene)
            # Extract scene title
            title = line_stripped.replace("**", "").replace("#", "").strip()
            if title.startswith("Scene"):
                title = title.split(":", 1)[1].strip() if ":" in title else title
            current_scene = {
                "scene_number": len(scenes) + 1,
                "title": title or f"Scene {len(scenes) + 1}",
                "visual_description": "",
                "narration": "",
                "text_overlay": "",
                "accessibility_cue": "",
                "teacher_notes": "",
            }
            current_section = None
            collecting_content = False
            continue

        if not current_scene:
            continue

        # Detect section labels (Narration:, Visual Description:, **Narration:**, etc.)
        # Handle bold markdown labels
        if line_stripped.startswith("**") and ":" in line_stripped:
            label_match = re.match(r"^\*\*([^:]+):\*\*", line_stripped)
            if label_match:
                label = label_match.group(1).strip()
                content = line_stripped.split(":", 1)[1].replace("**", "").strip() if ":" in line_stripped else ""
            else:
                label = line_stripped.replace("**", "").split(":")[0].strip()
                content = ""
        # Handle regular colon labels
        elif ":" in line_stripped and not line_stripped.startswith("-") and not line_stripped.startswith("*"):
            parts = line_stripped.split(":", 1)
            label = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else ""
        else:
            label = None
            content = ""

        # Map labels to scene fields
        if label:
            label_lower = label.lower()
            if "narration" in label_lower:
                current_section = "narration"
                if content:
                    current_scene["narration"] = content
                collecting_content = True
            elif "visual" in label_lower and "description" in label_lower:
                current_section = "visual_description"
                if content:
                    current_scene["visual_description"] = content
                collecting_content = True
            elif "on-screen" in label_lower or ("text" in label_lower and "overlay" in label_lower):
                current_section = "text_overlay"
                if content:
                    current_scene["text_overlay"] = content
                collecting_content = True
            elif "accessibility" in label_lower:
                current_section = "accessibility_cue"
                if content:
                    current_scene["accessibility_cue"] = content
                collecting_content = True
            elif "teacher" in label_lower and "note" in label_lower:
                current_section = "teacher_notes"
                if content:
                    current_scene["teacher_notes"] = content
                collecting_content = True
            else:
                collecting_content = False
        elif collecting_content and current_section:
            # Continue collecting content for current section
            if current_scene.get(current_section):
                current_scene[current_section] += " " + line_stripped
            else:
                current_scene[current_section] = line_stripped

    if current_scene:
        scenes.append(current_scene)

    # If no scenes found, create one from entire script
    if not scenes:
        scenes.append(
            {
                "scene_number": 1,
                "title": "Main Content",
                "visual_description": "Educational content visualization",
                "narration": script,
                "text_overlay": "",
                "accessibility_cue": "",
                "teacher_notes": "",
            }
        )

    return scenes


async def detect_modification_intent(
    message: str, has_existing_script: bool, node_name: Optional[str] = None
) -> bool:
    """
    Detect if user message indicates a modification request for an existing script.
    
    Args:
        message: User message
        has_existing_script: Whether a script already exists in the session
        node_name: Optional node name for node-specific LLM configuration
    
    Returns:
        Boolean indicating if this is a modification request
    """
    if not has_existing_script:
        return False
    
    if node_name:
        client, provider, model = get_llm_client_for_node(node_name)
    else:
        client, provider, model = get_llm_client()
    
    prompt = f"""Analyze the following user message to determine if it indicates a request to modify or change an existing educational script.

User message: {message}

Consider the following as indicators of modification intent:
- Requests to change, modify, update, revise, or edit the script
- Requests to make it shorter, longer, simpler, more detailed
- Requests to add, remove, or change specific content
- Requests to change tone, style, or approach
- Requests to fix or correct something
- Any other indication that the user wants to alter the existing script

If the message is asking for a new script or providing new information for initial script creation, it is NOT a modification request.

Return only a JSON object with a single boolean field "is_modification_request".
Example: {{"is_modification_request": true}} or {{"is_modification_request": false}}"""

    try:
        messages_list = [
            {
                "role": "system",
                "content": "You are an intent detection assistant. Return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages_list,
            temperature=0.3,
            max_tokens=200,
        )
        content = response.choices[0].message.content
        
        # Log LLM call
        log_llm_call(
            "detect_modification_intent",
            messages_list,
            model,
            content,
            temperature=0.3,
            max_tokens=200,
        )
        
        # Parse JSON response
        import json
        
        # Try to extract JSON from response
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        return result.get("is_modification_request", False)
    except Exception as e:
        logger.error(f"Error detecting modification intent: {str(e)}", exc_info=True)
        # On error, return False to be safe (don't treat as modification)
        return False


async def extract_information_from_message(
    message: str, current_state: Dict[str, Any], node_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract structured information from a natural language message.

    Args:
        message: User message
        current_state: Current session state
        node_name: Optional node name for node-specific LLM configuration

    Returns:
        Dictionary with extracted fields
    """
    if node_name:
        client, provider, model = get_llm_client_for_node(node_name)
    else:
        client, provider, model = get_llm_client()

    # Build prompt for information extraction
    prompt = f"""Extract structured information from the following educator message. 
Return a JSON object with any of these fields if mentioned: topic, year_level, learning_objective, subject, script_pace.

Current state:
- Topic: {current_state.get("topic", "Not set")}
- Year Level: {current_state.get("year_level", "Not set")}
- Learning Objective: {current_state.get("learning_objective", "Not set")}
- Subject: {current_state.get("subject", "Not set")}
- Script Pace: {current_state.get("script_pace", "Not set")}

Educator message: {message}

Extract only the fields that are explicitly mentioned or can be clearly inferred. 
IMPORTANT: 
- year_level must always be a string (e.g., "8" not 8).
- script_pace should be one of: "slow", "normal", "fast". Only extract if the educator explicitly mentions pace, speed, or tone preferences.

Return JSON format: {{"topic": "...", "year_level": "...", "learning_objective": "...", "subject": "...", "script_pace": "..."}}
Only include fields that have values."""

    try:
        messages_list = [
            {
                "role": "system",
                "content": "You are an information extraction assistant. Return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages_list,
            temperature=0.3,
            max_tokens=500,
        )
        content = response.choices[0].message.content

        # Log LLM call
        log_llm_call(
            "extract_information_from_message",
            messages_list,
            model,
            content,
            temperature=0.3,
            max_tokens=500,
        )

        # Parse JSON response
        import json

        # Try to extract JSON from response
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        extracted = json.loads(content)

        # Ensure year_level is always a string
        if "year_level" in extracted and extracted["year_level"] is not None:
            extracted["year_level"] = str(extracted["year_level"])

        return extracted
    except Exception as e:
        # Return empty dict on error
        return {}


async def generate_conversation_response(
    state: Dict[str, Any], missing_fields: List[str], node_name: Optional[str] = None
) -> str:
    """
    Generate a conversational response based on current state and missing fields.

    Args:
        state: Current session state
        missing_fields: List of missing required fields
        node_name: Optional node name for node-specific LLM configuration

    Returns:
        Assistant response message
    """
    if node_name:
        client, provider, model = get_llm_client_for_node(node_name)
    else:
        client, provider, model = get_llm_client()

    # Build context
    topic = state.get("topic", "Not specified")
    year_level = state.get("year_level", "Not specified")
    learning_objective = state.get("learning_objective", "Not specified")
    subject = state.get("subject", "Not specified")
    is_modification_request = state.get("is_modification_request", False)
    modification_request = state.get("modification_request", "")
    has_existing_script = bool(state.get("script")) and state.get("status") == "completed"

    # Handle modification requests
    if is_modification_request and has_existing_script:
        prompt = f"""You are a helpful educational assistant. The user has requested to modify an existing script.

User's modification request: {modification_request}

Current script information:
- Topic: {topic}
- Year Level: {year_level}
- Learning Objective: {learning_objective}
- Subject: {subject}

Generate a friendly, helpful response that:
1. Acknowledges the modification request
2. Confirms that you will update the script according to their request
3. Indicates that the script will be regenerated and fact-checked

Keep the response concise and friendly."""
    else:
        prompt = f"""You are a helpful educational assistant helping an educator create an educational video script.

Current information collected:
- Topic: {topic}
- Year Level: {year_level}
- Learning Objective: {learning_objective}
- Subject: {subject}

Missing required information: {", ".join(missing_fields) if missing_fields else "None"}

Generate a friendly, helpful response that:
1. Acknowledges what information has been collected
2. Asks for any missing required information in a natural, conversational way
3. If all information is collected, confirm readiness to generate the script

Keep the response concise and friendly."""

    try:
        messages_list = [
            {"role": "system", "content": "You are a helpful educational assistant."},
            {"role": "user", "content": prompt},
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages_list,
            temperature=0.7,
            max_tokens=300,
        )
        content = response.choices[0].message.content

        # Log LLM call
        log_llm_call(
            "generate_conversation_response",
            messages_list,
            model,
            content,
            temperature=0.7,
            max_tokens=300,
        )

        return content
    except Exception as e:
        return "I'm here to help you create an educational script. Please provide the topic, year level, and learning objective."
