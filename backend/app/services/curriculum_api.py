"""CurricuLLM-AU API client for curriculum alignment."""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

CURRICULLM_API_URL = os.getenv("CURRICULLM_API_URL", "https://api.curricullm.com")


def get_curriculum_outcomes(
    topic: str, year_level: str, subject: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get curriculum outcomes for a topic and year level.

    Args:
        topic: Topic name
        year_level: Year level (can be string like "1", "2", "university level", etc.)
        subject: Optional subject area

    Returns:
        List of curriculum outcomes
    """
    api_key = os.getenv("CURRICULLM_API_KEY")

    if not api_key:
        # Return mock data if API key not available
        return _get_mock_outcomes(topic, year_level, subject)

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        params = {
            "topic": topic,
            "year_level": year_level,
        }

        if subject:
            params["subject"] = subject

        response = requests.get(
            f"{CURRICULLM_API_URL}/outcomes",
            headers=headers,
            params=params,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("outcomes", [])
        else:
            # Fallback to mock data on API error
            return _get_mock_outcomes(topic, year_level, subject)

    except Exception:
        # Fallback to mock data on exception
        return _get_mock_outcomes(topic, year_level, subject)


def _get_mock_outcomes(
    topic: str, year_level: str, subject: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Return mock curriculum outcomes when API is unavailable."""
    subject_code = (subject or "SCI")[:3].upper()

    return [
        {
            "code": f"AC{year_level}.{subject_code}.01",
            "description": f"Year {year_level} {subject or 'Science'} outcome related to {topic}",
            "year_level": year_level,
            "subject": subject or "Science",
            "strand": "Understanding",
            "content_descriptor": f"Students explore {topic} and its applications",
        }
    ]


def get_prerequisites(topic: str, year_level: str) -> List[str]:
    """
    Get prerequisite knowledge for a topic.

    Args:
        topic: Topic name
        year_level: Year level (can be string)

    Returns:
        List of prerequisite topics
    """
    # Mock implementation - can be enhanced with actual API call
    return []


def get_learning_needs_analysis(
    topic: str, year_level: str, subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get prerequisites and misconceptions in a single prompt from curriculum API.
    This follows the Learning Needs Analysis methodology.

    Args:
        topic: Topic name
        year_level: Year level (can be string)
        subject: Optional subject area

    Returns:
        Dictionary with 'prerequisites' (List[str]) and 'misconceptions' (List[Dict[str, Any]])
    """
    api_key = os.getenv("CURRICULLM_API_KEY")

    if not api_key:
        # Return mock data if API key not available
        return _get_mock_learning_needs(topic, year_level, subject)

    try:
        # Use OpenAI-compatible client for curriculum API
        client = OpenAI(api_key=api_key, base_url=CURRICULLM_API_URL)

        prompt = f"""You are an expert educational curriculum analyst. For the following topic, provide a comprehensive Learning Needs Analysis.

Topic: {topic}
Year Level: {year_level}
{f"Subject: {subject}" if subject else ""}

Please provide:
1. Prerequisites: List the key prerequisite knowledge, concepts, and skills that students should have before learning this topic. These are foundational concepts that students need to understand first.

2. Expected Misconceptions: List common misconceptions that students typically have about this topic. For each misconception, provide:
   - The misconception itself (what students incorrectly believe)
   - Why this misconception is common
   - The correct understanding

Return your response as a JSON object with the following structure:
{{
    "prerequisites": ["prerequisite 1", "prerequisite 2", ...],
    "misconceptions": [
        {{
            "misconception": "description of the misconception",
            "why_common": "explanation of why students have this misconception",
            "correct_understanding": "the correct concept or understanding"
        }},
        ...
    ]
}}

Be thorough and specific. Focus on the most important prerequisites and the most common misconceptions for this topic at this year level."""

        # Call curriculum API using OpenAI-compatible schema
        response = client.chat.completions.create(
            model=os.getenv("CURRICULLM_MODEL", "gpt-4"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational curriculum analyst specializing in Learning Needs Analysis. Always return valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        content = response.choices[0].message.content

        # Log the API call
        logger.info("=" * 80)
        logger.info("[CURRICULUM API] Learning Needs Analysis")
        logger.info("=" * 80)
        logger.info(f"Topic: {topic}, Year Level: {year_level}, Subject: {subject}")
        logger.info(f"\n--- RESPONSE ---\n{content[:500]}")
        if len(content) > 500:
            logger.info(f"... (truncated, total length: {len(content)} chars)")
        logger.info("=" * 80)

        # Parse JSON response
        content = content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)

        # Ensure proper structure
        prerequisites = result.get("prerequisites", [])
        misconceptions = result.get("misconceptions", [])

        # Validate misconceptions structure and filter out generic/placeholder ones
        validated_misconceptions = []
        generic_patterns = [
            "common misunderstanding about",
            "correct understanding of",
            "correct concept",
        ]

        for misc in misconceptions:
            if isinstance(misc, dict):
                misconception_text = misc.get("misconception", "").lower()
                # Skip if it's a generic placeholder
                if any(pattern in misconception_text for pattern in generic_patterns):
                    continue
                # Ensure it has meaningful content
                if (
                    misc.get("misconception")
                    and len(misc.get("misconception", "").strip()) > 10
                ):
                    validated_misconceptions.append(misc)
            elif isinstance(misc, str):
                # Only add if it's a meaningful string (not generic)
                misc_lower = misc.lower()
                if len(misc.strip()) > 10 and not any(
                    pattern in misc_lower for pattern in generic_patterns
                ):
                    validated_misconceptions.append(
                        {
                            "misconception": misc,
                            "why_common": "Common student misunderstanding",
                            "correct_understanding": "See curriculum resources for correct understanding",
                        }
                    )

        return {
            "prerequisites": prerequisites if isinstance(prerequisites, list) else [],
            "misconceptions": validated_misconceptions,
        }

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from curriculum API: {str(e)}", exc_info=True)
        return _get_mock_learning_needs(topic, year_level, subject)
    except Exception as e:
        logger.error(
            f"Error calling curriculum API for learning needs: {str(e)}", exc_info=True
        )
        # Fallback to mock data on exception
        return _get_mock_learning_needs(topic, year_level, subject)


def _get_mock_learning_needs(
    topic: str, year_level: str, subject: Optional[str] = None
) -> Dict[str, Any]:
    """Return mock learning needs analysis when API is unavailable."""
    return {
        "prerequisites": [
            f"Basic understanding of {topic}",
            f"Year {year_level} foundational concepts",
        ],
        "misconceptions": [],  # Return empty list instead of generic placeholder
    }
