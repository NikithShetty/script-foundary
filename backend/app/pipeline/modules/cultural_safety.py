"""Module 5: Cultural Safety Checker - Ensures inclusive and culturally sensitive content."""

import re
from typing import List
from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.base import PipelineModule


class CulturalSafetyChecker(PipelineModule):
    """Checks script for cultural sensitivity and inclusivity."""
    
    def __init__(self):
        super().__init__("CulturalSafetyChecker")
        # Patterns to detect potentially problematic content
        self.stereotype_patterns = [
            r"\b(all|every|always|never)\s+\w+\s+(are|is)\s+",
            r"\b(typical|normal|usual)\s+\w+\s+(person|people|group)",
        ]
        self.insensitive_terms = [
            "primitive", "backward", "uncivilized", "exotic",
        ]
    
    def _scan_for_issues(self, text: str) -> tuple[List[str], List[str]]:
        """
        Scan text for cultural safety issues.
        
        Args:
            text: Text to scan
            
        Returns:
            Tuple of (flags, suggestions)
        """
        flags = []
        suggestions = []
        text_lower = text.lower()
        
        # Check for stereotype patterns
        for pattern in self.stereotype_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                flags.append(f"Potential stereotype detected: {pattern}")
                suggestions.append("Consider using more specific, inclusive language")
        
        # Check for insensitive terms
        for term in self.insensitive_terms:
            if term in text_lower:
                flags.append(f"Potentially insensitive term detected: {term}")
                suggestions.append(f"Replace '{term}' with more respectful language")
        
        # Check for diversity
        if not any(word in text_lower for word in ["diverse", "various", "different", "inclusive"]):
            suggestions.append("Consider adding examples that reflect diverse perspectives")
        
        return flags, suggestions
    
    def process(self, context: PipelineContext, config: PipelineConfig) -> PipelineContext:
        """
        Check script for cultural safety issues.
        
        Args:
            context: Pipeline context
            config: Pipeline configuration
            
        Returns:
            Updated context with cultural safety data
        """
        try:
            if not context.generated_script:
                return context
            
            # Scan script text
            flags, suggestions = self._scan_for_issues(context.generated_script)
            
            context.cultural_safety_flags = flags
            context.cultural_suggestions = suggestions
            
            # Add Aboriginal perspectives suggestion for history/science topics
            if context.subject and context.subject.lower() in ["history", "science"]:
                context.cultural_suggestions.append(
                    "Consider including Australian Aboriginal perspectives and knowledge"
                )
            
        except Exception as e:
            context = self.handle_error(context, e, f"Failed to check cultural safety: {str(e)}")
        
        return context



