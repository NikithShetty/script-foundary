"""Module 4: Fact Checker - Verifies factual claims and prevents hallucinations."""

import re
from typing import List, Dict, Any
from app.models.pipeline import PipelineContext, PipelineConfig
from app.pipeline.base import PipelineModule
from app.services.fact_check_service import check_fact, extract_factual_claims


class FactChecker(PipelineModule):
    """Verifies factual claims in generated script."""
    
    def __init__(self):
        super().__init__("FactChecker")
    
    def process(self, context: PipelineContext, config: PipelineConfig) -> PipelineContext:
        """
        Extract and verify factual claims from generated script.
        
        Args:
            context: Pipeline context
            config: Pipeline configuration
            
        Returns:
            Updated context with fact-check results
        """
        try:
            if not context.generated_script:
                context.warnings.append("No script to fact-check")
                return context
            
            # Extract factual claims
            claims = extract_factual_claims(context.generated_script)
            
            # Check each claim
            fact_check_results = []
            verified_count = 0
            total_confidence = 0.0
            
            for claim in claims:
                result = check_fact(claim)
                fact_check_results.append(result)
                
                if result.get("verified", False):
                    verified_count += 1
                
                confidence = result.get("confidence", 0.0)
                total_confidence += confidence
                
                # Add citations
                if result.get("sources"):
                    context.citations.extend(result["sources"])
            
            context.fact_check_results = fact_check_results
            
            # Calculate overall confidence score
            if len(claims) > 0:
                context.confidence_score = (verified_count / len(claims)) * 100
                context.metadata["average_confidence"] = total_confidence / len(claims)
            else:
                context.confidence_score = 100.0  # No claims to check
            
        except Exception as e:
            context = self.handle_error(context, e, f"Failed to fact-check script: {str(e)}")
        
        return context



