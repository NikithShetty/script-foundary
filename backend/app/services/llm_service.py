"""LLM service for script generation using CurricuLLM or OpenAI."""

import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import settings


def get_llm_client():
    """Get LLM client (CurricuLLM or OpenAI) based on available API key.
    CurricuLLM is prioritized as it's OpenAI-compliant and optimized for educational content."""
    curricullm_key = settings.curricullm_api_key
    curricullm_url = settings.curricullm_api_url
    openai_key = settings.openai_api_key
    
    # Prioritize CurricuLLM for script generators (OpenAI-compliant API)
    if curricullm_key:
        return OpenAI(api_key=curricullm_key, base_url=curricullm_url), "openai"
    elif openai_key:
        return OpenAI(api_key=openai_key), "openai"
    else:
        raise ValueError("No LLM API key found. Set CURRICULLM_API_KEY or OPENAI_API_KEY")


def generate_script(prompt: str) -> Dict[str, Any]:
    """
    Generate script using LLM.
    
    Args:
        prompt: System prompt for script generation
        
    Returns:
        Dictionary with script and scenes
    """
    client, provider = get_llm_client()
    
    try:
        # Check for CurricuLLM model first, then OpenAI model
        model = settings.curricullm_model or settings.openai_model
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educational script writer."},
                {"role": "user", "content": prompt}
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
    scenes = []
    lines = script.split("\n")
    current_scene = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect scene headers
        if line.upper().startswith("SCENE"):
            if current_scene:
                scenes.append(current_scene)
            current_scene = {
                "scene_number": len(scenes) + 1,
                "title": line,
                "visual_description": "",
                "narration": "",
                "text_overlay": "",
            }
        elif current_scene:
            # Parse scene content
            if "visual" in line.lower() or "image" in line.lower():
                current_scene["visual_description"] += line + " "
            elif "narration" in line.lower() or "voice" in line.lower():
                current_scene["narration"] += line + " "
            elif "overlay" in line.lower() or "text" in line.lower():
                current_scene["text_overlay"] += line + " "
            else:
                # Default to narration
                current_scene["narration"] += line + " "
    
    if current_scene:
        scenes.append(current_scene)
    
    # If no scenes found, create one from entire script
    if not scenes:
        scenes.append({
            "scene_number": 1,
            "title": "Main Content",
            "visual_description": "Educational content visualization",
            "narration": script,
            "text_overlay": "",
        })
    
    return scenes


async def extract_information_from_message(
    message: str,
    current_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Extract structured information from a natural language message.
    
    Args:
        message: User message
        current_state: Current session state
        
    Returns:
        Dictionary with extracted fields
    """
    client, provider = get_llm_client()
    
    # Build prompt for information extraction
    prompt = f"""Extract structured information from the following educator message. 
Return a JSON object with any of these fields if mentioned: topic, year_level, learning_objective, subject.

Current state:
- Topic: {current_state.get('topic', 'Not set')}
- Year Level: {current_state.get('year_level', 'Not set')}
- Learning Objective: {current_state.get('learning_objective', 'Not set')}
- Subject: {current_state.get('subject', 'Not set')}

Educator message: {message}

Extract only the fields that are explicitly mentioned or can be clearly inferred. 
Return JSON format: {{"topic": "...", "year_level": ..., "learning_objective": "...", "subject": "..."}}
Only include fields that have values."""
    
    try:
        # Check for CurricuLLM model first, then OpenAI model
        model = settings.curricullm_model or settings.openai_model
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an information extraction assistant. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500,
        )
        content = response.choices[0].message.content
        
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
        return extracted
    except Exception as e:
        # Return empty dict on error
        return {}


async def generate_conversation_response(
    state: Dict[str, Any],
    missing_fields: List[str]
) -> str:
    """
    Generate a conversational response based on current state and missing fields.
    
    Args:
        state: Current session state
        missing_fields: List of missing required fields
        
    Returns:
        Assistant response message
    """
    client, provider = get_llm_client()
    
    # Build context
    topic = state.get("topic", "Not specified")
    year_level = state.get("year_level", "Not specified")
    learning_objective = state.get("learning_objective", "Not specified")
    subject = state.get("subject", "Not specified")
    
    prompt = f"""You are a helpful educational assistant helping an educator create an educational video script.

Current information collected:
- Topic: {topic}
- Year Level: {year_level}
- Learning Objective: {learning_objective}
- Subject: {subject}

Missing required information: {', '.join(missing_fields) if missing_fields else 'None'}

Generate a friendly, helpful response that:
1. Acknowledges what information has been collected
2. Asks for any missing required information in a natural, conversational way
3. If all information is collected, confirm readiness to generate the script

Keep the response concise and friendly."""
    
    try:
        # Check for CurricuLLM model first, then OpenAI model
        model = settings.curricullm_model or settings.openai_model
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful educational assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        content = response.choices[0].message.content
        
        return content
    except Exception as e:
        return "I'm here to help you create an educational script. Please provide the topic, year level, and learning objective."



