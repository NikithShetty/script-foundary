"""Base module interface for pipeline modules."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pipeline import PipelineContext, PipelineConfig


class PipelineModule(ABC):
    """Base class for all pipeline modules."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, context: "PipelineContext", config: "PipelineConfig") -> "PipelineContext":
        """
        Process the pipeline context and return updated context.
        
        Args:
            context: Current pipeline context
            config: Pipeline configuration
            
        Returns:
            Updated pipeline context
        """
        pass
    
    def is_enabled(self, config: "PipelineConfig") -> bool:
        """
        Check if this module should run based on configuration.
        
        Args:
            config: Pipeline configuration
            
        Returns:
            True if module should run, False otherwise
        """
        # Default implementation checks for enable_<module_name> flag
        flag_name = f"enable_{self.name.lower().replace(' ', '_')}"
        return getattr(config, flag_name, True)
    
    def handle_error(self, context: "PipelineContext", error: Exception, message: str = None):
        """
        Handle errors gracefully by adding to context errors list.
        
        Args:
            context: Pipeline context
            error: Exception that occurred
            message: Optional custom error message
        """
        error_msg = message or f"Error in {self.name}: {str(error)}"
        context.errors.append(error_msg)
        return context



