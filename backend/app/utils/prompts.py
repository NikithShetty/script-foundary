"""Prompt templates for LLM script generation."""

from typing import List, Dict, Any


def get_fame_prompt(
    topic: str,
    year_level: str,
    learning_objective: str,
    curriculum_codes: List[str] = None,
    misconceptions: List[Dict[str, Any]] = None,
) -> str:
    """
    Generate FAME framework prompt for script generation.
    
    Args:
        topic: Topic for the script
        year_level: Year level (can be string like "1", "2", "university level", etc.)
        learning_objective: Learning objective
        curriculum_codes: List of curriculum codes
        misconceptions: List of misconceptions to address
        
    Returns:
        Complete prompt string
    """
    curriculum_codes = curriculum_codes or []
    misconceptions = misconceptions or []
    
    misconception_text = ""
    if misconceptions:
        misconception_text = "\nCommon misconceptions to address:\n"
        for i, mc in enumerate(misconceptions[:3], 1):
            misconception_text += f"{i}. {mc.get('misconception', 'N/A')} - {mc.get('correction', 'N/A')}\n"
    
    curriculum_text = ""
    if curriculum_codes:
        curriculum_text = f"\nCurriculum Codes: {', '.join(curriculum_codes)}\n"
    
    prompt = f"""You are an expert educational script writer. Generate a script for:
Topic: {topic}
Year Level: {year_level}
Learning Objective: {learning_objective}
{curriculum_text}
Follow the FAME framework:
- Fading: Start with full worked example, gradually remove scaffolding
- Alternating: Alternate worked examples with student practice
- Mistakes: Include common errors (with corrections)
- Explanation: Include "think-aloud" narration explaining reasoning
{misconception_text}
Include:
1. Scene-by-scene breakdown with visual descriptions
2. Character/voice guidance
3. One "misconception warning" based on the misconceptions listed above
4. Spaced retrieval question
5. Accessibility captions for each visual
6. Curriculum alignment markers

Script Structure:
SCENE 1: Hook & Context
[Visual description]
[Narration]
[Text overlay]
[Accessibility cue]

SCENE 2: Worked Example (I DO)
[Problem setup]
[Step-by-step solution with thinking aloud]
[Visual metaphor reinforcement]

SCENE 3: Faded Example (WE DO)
[Similar problem, partially solved]
[Student prompts for completion]
[Reveal solution with explanation]

SCENE 4: Key Concept Summary
[Spaced retrieval question]
[Common misconception addressed]
[Reinforcement visual]

SCENE 5: Closure & Next Steps
[Summary of learning objective]
[Connection to curriculum outcome]

Avoid:
- Oversimplification that creates false mental models
- Culturally insensitive examples
- Unsourced factual claims
- Jargon not defined at this year level

Generate the complete script now:"""
    
    return prompt



