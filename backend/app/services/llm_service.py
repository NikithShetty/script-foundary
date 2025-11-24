"""LLM service for script generation using OpenAI or Anthropic."""

import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from anthropic import Anthropic


def get_llm_client():
    """Get LLM client (OpenAI or Anthropic) based on available API key."""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key:
        return OpenAI(api_key=openai_key), "openai"
    elif anthropic_key:
        return Anthropic(api_key=anthropic_key), "anthropic"
    else:
        raise ValueError("No LLM API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")


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
        if provider == "openai":
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an expert educational script writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            content = response.choices[0].message.content
        else:  # anthropic
            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            content = response.content[0].text
        
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
        if provider == "openai":
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an information extraction assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
            )
            content = response.choices[0].message.content
        else:  # anthropic
            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                max_tokens=500,
                system="You are an expert at extracting structured information from educational requests.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            content = response.content[0].text
        
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
        if provider == "openai":
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are a helpful educational assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            content = response.choices[0].message.content
        else:  # anthropic
            response = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                max_tokens=300,
                system="You are a friendly and helpful educational assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            content = response.content[0].text
        
        return content
    except Exception as e:
        return "I'm here to help you create an educational script. Please provide the topic, year level, and learning objective."



