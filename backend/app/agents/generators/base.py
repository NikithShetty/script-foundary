"""Base script generator class."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from app.services.llm_service import get_llm_client
import os
import logging

logger = logging.getLogger(__name__)


class BaseScriptGenerator(ABC):
    """Base class for subject-specific script generators."""
    
    def __init__(self):
        self.client, self.provider = get_llm_client()
        self.model = self._get_model()
    
    def _get_model(self) -> str:
        """Get the appropriate model name based on provider."""
        if self.provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4")
        else:  # anthropic
            return os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this generator."""
        pass
    
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """Build the full prompt from context."""
        topic = context.get("topic", "")
        year_level = context.get("year_level", "")
        learning_objective = context.get("learning_objective", "")
        subject = context.get("subject", "")
        curriculum_outcomes = context.get("curriculum_outcomes", [])
        curriculum_codes = context.get("curriculum_codes", [])
        misconceptions = context.get("misconceptions", [])
        fact_check_issues = context.get("fact_check_issues", [])
        low_confidence_claims = context.get("low_confidence_claims", [])
        
        prompt = f"""Generate an educational video script with the following requirements:

Topic: {topic}
Year Level: {year_level}
Subject: {subject}
Learning Objective: {learning_objective}

"""
        
        if curriculum_outcomes:
            prompt += "Curriculum Outcomes:\n"
            for outcome in curriculum_outcomes:
                code = outcome.get("code", "")
                desc = outcome.get("description", "")
                prompt += f"- {code}: {desc}\n"
            prompt += "\n"
        
        if curriculum_codes:
            prompt += f"Curriculum Codes: {', '.join(curriculum_codes)}\n\n"
        
        if misconceptions:
            prompt += "Common Misconceptions to Address:\n"
            for misc in misconceptions:
                if isinstance(misc, dict):
                    prompt += f"- {misc.get('misconception', misc)}\n"
                else:
                    prompt += f"- {misc}\n"
            prompt += "\n"
        
        if fact_check_issues:
            prompt += "Fact-Check Issues to Address:\n"
            for issue in fact_check_issues:
                prompt += f"- {issue}\n"
            prompt += "\n"
        
        if low_confidence_claims:
            prompt += "Low Confidence Claims to Verify/Correct:\n"
            for claim in low_confidence_claims:
                if isinstance(claim, dict):
                    prompt += f"- {claim.get('claim', claim)}\n"
                else:
                    prompt += f"- {claim}\n"
            prompt += "\n"
        
        prompt += self.get_system_prompt()
        prompt += "\n\nGenerate a comprehensive educational script that is engaging, accurate, and aligned with the curriculum."
        
        return prompt
    
    async def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script using LLM."""
        try:
            prompt = self.build_prompt(context)
            system_prompt = self.get_system_prompt()
            
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000,
                )
                content = response.choices[0].message.content
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                )
                content = response.content[0].text
            
            # Parse scenes from script
            scenes = self._parse_scenes_from_script(content)
            
            return {
                "script": content,
                "scenes": scenes,
            }
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate script: {str(e)}")
    
    def _parse_scenes_from_script(self, script: str) -> list:
        """Parse scenes from generated script text."""
        scenes = []
        lines = script.split("\n")
        current_scene = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect scene headers
            if line.upper().startswith("SCENE") or line.upper().startswith("##"):
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {
                    "scene_number": len(scenes) + 1,
                    "title": line.replace("#", "").strip(),
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

