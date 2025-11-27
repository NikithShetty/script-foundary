"""Base script generator class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.services.llm_service import get_llm_client, get_llm_client_for_node
import logging
import re

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

    def _get_script_structure_instructions(self) -> str:
        """Get detailed script structure instructions based on requirements."""
        return """## SCRIPT STRUCTURE

Generate the educational script following this structure:

### INTRO BLOCK

Begin with these elements in sequence:

1. **Orientation** (1 sentence)
   - Introduce the topic simply and clearly

2. **Misconception Prevention** (1-2 sentences)
   - Address common misconceptions early using LNA data and curriculum misconceptions
   - Prevent misconceptions before they form

3. **Teaser/Hook** (1 short story, real-life example, or question)
   - Use Kolb's Concrete Experience approach
   - Engage learners with relatable, concrete content

4. **Lesson Plan** (3-4 bullet points)
   - Clearly state what learners will learn
   - Set expectations for the lesson

5. **Core Message Seed** (1 key idea)
   - Introduce the central "big idea" early
   - This is the main concept learners should understand

6. **I DO Start** (first teacher-led explanation)
   - Begin Gradual Release of Responsibility
   - Teacher models the concept fully

---

### SUBTOPIC BLOCKS

For each curriculum concept, include this pattern:

1. **Concept Naming** - Define the micro-concept clearly
2. **Explanation** - Simple, clear, age-appropriate explanation
3. **Dual-Coding Description** - Specify what visuals should show (visual and verbal work together, not redundantly)
4. **Worked Example (I DO)** - Teacher demonstrates the concept fully
5. **Guided Example (WE DO)** - Teacher and student work together
6. **Reflective Question** - Ask "Why do you think...?" to promote deeper thinking
7. **Micro to Macro Connection** - Connect this concept to the bigger picture
8. **Retrieval Questions** - Check understanding with recall questions
9. **Misconception Alert** (only if relevant) - Address specific misconceptions if they arise

Repeat this block for each curriculum concept.

---

### MIDPOINT SUMMARY

Include a brief summary section with:
- Short recap (3 bullet points summarizing key points covered)
- One reflective question to encourage deeper thinking
- One misconception check to verify understanding
- Simple transition sentence to the next concept

---

### FINAL BLOCK

Conclude with these elements in order:

1. **Return to Intro Promise**
   - Reference what was promised at the start
   - Close the learning loop

2. **Key Idea Highlights** (2-3 bullet points)
   - Reinforce the most important concepts

3. **Core Message Repeat**
   - Restate the central "big idea" from the intro

4. **Take-Home Message**
   - One clear, memorable statement

5. **Final Retrieval Questions**
   - Comprehensive check of understanding

6. **YOU DO Task**
   - Learner applies the idea independently (Kolb's Active Experimentation)
   - Full transfer of responsibility

7. **Transfer Confirmation**
   - Confirm learner is ready to apply knowledge independently

---

### SCENE OUTPUT FORMAT

Each scene in the script must include all of these elements, formatted EXACTLY as shown:

**Scene X: [Scene Title]**

Narration:
[What the teacher/narrator says]

Visual Description:
[Detailed description of what should be shown visually]

On-Screen Text:
[Any text overlays, labels, or captions]

Accessibility Note:
[Considerations for accessibility - alt text, captions, etc.]

Teacher Notes:
[Misconceptions to watch for, retrieval cues, pedagogical reminders]

Important: Use plain text labels with colons (Narration:, Visual Description:, etc.), NOT bold markdown. Each section should be on its own line with the label followed by a colon, then the content on the following line(s)."""

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
            prompt += "\n\n"
            prompt += self._get_script_structure_instructions()
            prompt += "\n\nINSTRUCTIONS FOR MODIFICATION:\n"
            prompt += "1. Carefully review the existing script above\n"
            prompt += "2. Understand the user's modification request\n"
            prompt += "3. Modify the script according to the request, preserving what should remain unchanged\n"
            prompt += "4. Ensure the modified script still meets all original requirements (topic, year level, learning objective, curriculum alignment)\n"
            prompt += "5. Maintain the structure defined above (Intro Block, Subtopic Blocks, Midpoint Summary, Final Block) unless the modification request specifically asks to change it\n"
            prompt += "6. Ensure each scene includes all required elements: Narration, Visual description, On-screen text, Accessibility note, Teacher notes\n"
            prompt += (
                "7. Generate the complete modified script (not just the changes)\n\n"
            )
            prompt += "Generate the modified educational script that addresses the user's request while maintaining quality, accuracy, curriculum alignment, and the required structure."

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
        prompt += "\n\n"
        prompt += self._get_script_structure_instructions()
        prompt += "\n\nGenerate a comprehensive educational script that follows the structure above and is engaging, accurate, and aligned with the curriculum."

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
            logger.info("Temperature: 0.7")
            logger.info("Max Tokens: 4000")
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
        current_section = None
        collecting_content = False

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                collecting_content = False
                continue

            # Detect scene headers (Scene 1:, **Scene 1:**, ## Scene 1, etc.)
            scene_match = (
                line_stripped.upper().startswith("SCENE")
                or line_stripped.startswith("##")
                or (
                    line_stripped.startswith("**")
                    and "Scene" in line_stripped
                    and ":" in line_stripped
                )
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
                    content = (
                        line_stripped.split(":", 1)[1].replace("**", "").strip()
                        if ":" in line_stripped
                        else ""
                    )
                else:
                    label = line_stripped.replace("**", "").split(":")[0].strip()
                    content = ""
            # Handle regular colon labels
            elif (
                ":" in line_stripped
                and not line_stripped.startswith("-")
                and not line_stripped.startswith("*")
            ):
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
                elif "on-screen" in label_lower or (
                    "text" in label_lower and "overlay" in label_lower
                ):
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
