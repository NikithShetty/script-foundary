"""Input validation utilities."""

from typing import Any


def validate_year_level(year_level: Any) -> bool:
    """
    Validate year level is a non-empty string.
    
    Args:
        year_level: Year level to validate (can be any string)
        
    Returns:
        True if valid (non-empty string), False otherwise
    """
    return isinstance(year_level, str) and len(year_level.strip()) > 0


def validate_topic(topic: Any) -> bool:
    """
    Validate topic is a non-empty string.
    
    Args:
        topic: Topic to validate
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(topic, str) and len(topic.strip()) > 0


def validate_learning_objective(objective: Any) -> bool:
    """
    Validate learning objective is a non-empty string.
    
    Args:
        objective: Learning objective to validate
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(objective, str) and len(objective.strip()) > 0



