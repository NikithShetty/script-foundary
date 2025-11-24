"""Module 6: Accessibility Generator - Generates accessibility features."""

import re
from typing import List, Dict, Any
from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.base import PipelineModule


class AccessibilityGenerator(PipelineModule):
    """Generates accessibility features for the script."""
    
    def __init__(self):
        super().__init__("AccessibilityGenerator")
    
    def _generate_alt_text(self, visual_description: str) -> str:
        """
        Generate ALT text from visual description.
        
        Args:
            visual_description: Visual description from script
            
        Returns:
            ALT text
        """
        # Clean up and format for ALT text
        alt_text = visual_description.strip()
        # Ensure it's descriptive
        if not alt_text.startswith(("A", "An", "The", "Image", "Diagram", "Chart")):
            alt_text = f"Image showing {alt_text}"
        return alt_text
    
    def _generate_caption(self, narration: str) -> str:
        """
        Generate caption from narration.
        
        Args:
            narration: Narration text
            
        Returns:
            Caption text
        """
        # Captions are typically the same as narration, but formatted
        return narration.strip()
    
    def _format_dyslexia_friendly(self, text: str) -> str:
        """
        Format text for dyslexia-friendly reading.
        
        Args:
            text: Text to format
            
        Returns:
            Formatted text
        """
        # Basic formatting: ensure proper spacing, avoid all caps
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        # Avoid all caps
        if text.isupper() and len(text) > 3:
            text = text.capitalize()
        return text
    
    def process(self, context: PipelineContext, config: PipelineConfig) -> PipelineContext:
        """
        Generate accessibility features for the script.
        
        Args:
            context: Pipeline context
            config: Pipeline configuration
            
        Returns:
            Updated context with accessibility data
        """
        try:
            # Generate ALT texts and captions from scenes
            for scene in context.script_scenes:
                visual_desc = scene.get("visual_description", "")
                narration = scene.get("narration", "")
                
                if visual_desc:
                    alt_text = self._generate_alt_text(visual_desc)
                    context.alt_texts.append(alt_text)
                
                if narration:
                    caption = self._generate_caption(narration)
                    context.captions.append(caption)
            
            # Format script for dyslexia-friendly reading
            if context.generated_script:
                formatted_script = self._format_dyslexia_friendly(context.generated_script)
                context.accessibility_metadata["dyslexia_friendly_script"] = formatted_script
            
            # Add accessibility metadata
            context.accessibility_metadata.update({
                "alt_text_count": len(context.alt_texts),
                "caption_count": len(context.captions),
                "has_accessibility_features": True,
            })
            
        except Exception as e:
            context = self.handle_error(context, e, f"Failed to generate accessibility features: {str(e)}")
        
        return context



