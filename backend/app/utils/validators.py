"""Input validation utilities."""

from typing import Any


def validate_year_level(year_level: Any) -> bool:
    """
    Validate year level is between 1 and 12.
    
    Args:
        year_level: Year level to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        level = int(year_level)
        return 1 <= level <= 12
    except (ValueError, TypeError):
        return False


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



