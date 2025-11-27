"""Base script generator class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.services.llm_service import get_llm_client, get_llm_client_for_node
import logging

logger = logging.getLogger(__name__)


class BaseScriptGenerator(ABC):
    """Base class for subject-specific script generators."""

    def __init__(self, node_name: Optional[str] = None):
        """
        Initialize the script generator.

        Args:
            node_name: Optional node name for node-specific LLM configuration (e.g., "script_generation")
        """
        if node_name:
            self.client, self.provider, self.model = get_llm_client_for_node(node_name)
        else:
            self.client, self.provider, self.model = get_llm_client()

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
        prerequisites = context.get("prerequisites", [])
        misconceptions = context.get("misconceptions", [])
        script_pace = context.get("script_pace", "slow")
        fact_check_issues = context.get("fact_check_issues", [])
        low_confidence_claims = context.get("low_confidence_claims", [])
        is_modification = context.get("is_modification", False)
        existing_script = context.get("existing_script", "")
        modification_request = context.get("modification_request", "")

        # Handle modification requests
        if is_modification and existing_script:
            prompt = f"""You are modifying an existing educational video script based on user feedback.

EXISTING SCRIPT:
{existing_script}

USER'S MODIFICATION REQUEST:
{modification_request}

Original Requirements:
- Topic: {topic}
- Year Level: {year_level}
- Subject: {subject}
- Learning Objective: {learning_objective}

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

            if prerequisites:
                prompt += "Prerequisites (students should already know):\n"
                for prereq in prerequisites:
                    prompt += f"- {prereq}\n"
                prompt += "\n"

            if misconceptions:
                prompt += "Common Misconceptions to Address:\n"
                for misc in misconceptions:
                    if isinstance(misc, dict):
                        prompt += f"- {misc.get('misconception', misc)}\n"
                    else:
                        prompt += f"- {misc}\n"
                prompt += "\n"

            # Add pace/tone instruction
            pace_instructions = {
                "slow": "The script should be slow-paced, assuming students are hearing this content for the first time. Use clear explanations, pause for understanding, and avoid rushing through concepts.",
                "normal": "The script should be at a normal pace, suitable for students who may have some prior exposure to the topic.",
                "fast": "The script can be faster-paced, suitable for students who are already familiar with the foundational concepts.",
            }
            pace_instruction = pace_instructions.get(
                script_pace, pace_instructions["slow"]
            )
            prompt += f"Script Pace: {pace_instruction}\n\n"

            prompt += self.get_system_prompt()
            prompt += "\n\nINSTRUCTIONS FOR MODIFICATION:\n"
            prompt += "1. Carefully review the existing script above\n"
            prompt += "2. Understand the user's modification request\n"
            prompt += "3. Modify the script according to the request, preserving what should remain unchanged\n"
            prompt += "4. Ensure the modified script still meets all original requirements (topic, year level, learning objective, curriculum alignment)\n"
            prompt += "5. Maintain the same format and structure unless the modification request specifically asks to change it\n"
            prompt += (
                "6. Generate the complete modified script (not just the changes)\n\n"
            )
            prompt += "Generate the modified educational script that addresses the user's request while maintaining quality, accuracy, and curriculum alignment."

            return prompt

        # Original generation prompt
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

        if prerequisites:
            prompt += "Prerequisites (students should already know):\n"
            for prereq in prerequisites:
                prompt += f"- {prereq}\n"
            prompt += "\n"

        if misconceptions:
            prompt += "Common Misconceptions to Address:\n"
            for misc in misconceptions:
                if isinstance(misc, dict):
                    prompt += f"- {misc.get('misconception', misc)}\n"
                else:
                    prompt += f"- {misc}\n"
            prompt += "\n"

        # Add pace/tone instruction
        pace_instructions = {
            "slow": "The script should be slow-paced, assuming students are hearing this content for the first time. Use clear explanations, pause for understanding, and avoid rushing through concepts.",
            "normal": "The script should be at a normal pace, suitable for students who may have some prior exposure to the topic.",
            "fast": "The script can be faster-paced, suitable for students who are already familiar with the foundational concepts.",
        }
        pace_instruction = pace_instructions.get(script_pace, pace_instructions["slow"])
        prompt += f"Script Pace: {pace_instruction}\n\n"

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

            # Log before call
            logger.info("=" * 80)
            logger.info(f"[LLM CALL] Script Generation - {self.__class__.__name__}")
            logger.info("=" * 80)
            logger.info(f"Model: {self.model}")
            logger.info(f"Temperature: 0.7")
            logger.info(f"Max Tokens: 4000")
            logger.info("\n--- SYSTEM PROMPT ---")
            system_preview = (
                system_prompt[:500] if len(system_prompt) > 500 else system_prompt
            )
            logger.info(f"{system_preview}")
            if len(system_prompt) > 500:
                logger.info(
                    f"... (truncated, total length: {len(system_prompt)} chars)"
                )
            logger.info("\n--- USER PROMPT ---")
            prompt_preview = prompt[:1000] if len(prompt) > 1000 else prompt
            logger.info(f"{prompt_preview}")
            if len(prompt) > 1000:
                logger.info(f"... (truncated, total length: {len(prompt)} chars)")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            content = response.choices[0].message.content

            # Log response
            logger.info("\n--- RESPONSE ---")
            response_preview = content[:2000] if len(content) > 2000 else content
            logger.info(f"{response_preview}")
            if len(content) > 2000:
                logger.info(f"... (truncated, total length: {len(content)} chars)")
            logger.info("=" * 80)

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
            scenes.append(
                {
                    "scene_number": 1,
                    "title": "Main Content",
                    "visual_description": "Educational content visualization",
                    "narration": script,
                    "text_overlay": "",
                }
            )

        return scenes
