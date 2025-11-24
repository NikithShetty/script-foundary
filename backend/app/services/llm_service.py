"""LLM service for script generation using OpenAI or Anthropic."""

import os
from typing import Dict, Any, List
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



