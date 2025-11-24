"""CurricuLLM-AU API client for curriculum alignment."""

import os
import requests
from typing import Dict, Any, List, Optional


CURRICULLM_API_URL = os.getenv("CURRICULLM_API_URL", "https://api.curricullm.com")


def get_curriculum_outcomes(topic: str, year_level: int, subject: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get curriculum outcomes for a topic and year level.
    
    Args:
        topic: Topic name
        year_level: Year level (1-12)
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


def _get_mock_outcomes(topic: str, year_level: int, subject: Optional[str] = None) -> List[Dict[str, Any]]:
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


def get_prerequisites(topic: str, year_level: int) -> List[str]:
    """
    Get prerequisite knowledge for a topic.
    
    Args:
        topic: Topic name
        year_level: Year level
        
    Returns:
        List of prerequisite topics
    """
    # Mock implementation - can be enhanced with actual API call
    return []



