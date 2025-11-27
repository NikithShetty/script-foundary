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
{misconception_text}

## SCRIPT STRUCTURE

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

Important: Use plain text labels with colons (Narration:, Visual Description:, etc.), NOT bold markdown. Each section should be on its own line with the label followed by a colon, then the content on the following line(s).

## QUALITY GUIDELINES

Avoid:
- Oversimplification that creates false mental models
- Culturally insensitive examples
- Unsourced factual claims
- Jargon not defined at this year level

Generate the complete script now:"""

    return prompt
