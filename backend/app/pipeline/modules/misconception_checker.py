"""Module 2: Misconception Checker - Detects and addresses common misconceptions."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.base import PipelineModule


class MisconceptionChecker(PipelineModule):
    """Checks for and addresses common student misconceptions."""
    
    def __init__(self):
        super().__init__("MisconceptionChecker")
        self.misconception_db: Dict[str, List[Dict[str, Any]]] = {}
        self._load_misconceptions()
    
    def _load_misconceptions(self):
        """Load misconception database from JSON files."""
        misconceptions_dir = Path(__file__).parent.parent.parent.parent / "data" / "misconceptions"
        
        if misconceptions_dir.exists():
            for file_path in misconceptions_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        topic = data.get("topic", file_path.stem)
                        self.misconception_db[topic.lower()] = data.get("misconceptions", [])
                except Exception:
                    continue
    
    def _find_misconceptions(self, topic: str) -> List[Dict[str, Any]]:
        """
        Find relevant misconceptions for a topic.
        
        Args:
            topic: Topic to search for
            
        Returns:
            List of relevant misconceptions
        """
        topic_lower = topic.lower()
        misconceptions = []
        
        # Exact match
        if topic_lower in self.misconception_db:
            misconceptions.extend(self.misconception_db[topic_lower])
        
        # Partial match
        for key, values in self.misconception_db.items():
            if key in topic_lower or topic_lower in key:
                misconceptions.extend(values)
        
        return misconceptions
    
    def process(self, context: PipelineContext, config: PipelineConfig) -> PipelineContext:
        """
        Check for misconceptions and add warnings.
        
        Args:
            context: Pipeline context
            config: Pipeline configuration
            
        Returns:
            Updated context with misconception data
        """
        try:
            misconceptions = self._find_misconceptions(context.topic)
            context.misconceptions = misconceptions
            
            # Generate warnings
            for misconception in misconceptions:
                warning = f"Common mistake: Students think {misconception.get('misconception', 'X')}, "
                warning += f"but actually {misconception.get('correction', 'Y')}"
                context.misconception_warnings.append(warning)
            
        except Exception as e:
            context = self.handle_error(context, e, f"Failed to check misconceptions: {str(e)}")
        
        return context



