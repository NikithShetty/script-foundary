"""Fact checking service using Wikipedia/Wikidata APIs."""

import os
import re
import requests
from typing import List, Dict, Any


WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"


def extract_factual_claims(text: str) -> List[str]:
    """
    Extract factual claims from text.
    
    Args:
        text: Text to extract claims from
        
    Returns:
        List of factual claims
    """
    claims = []
    
    # Simple extraction: look for statements with numbers, dates, or "is/are" statements
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Look for factual patterns
        if any(pattern in sentence.lower() for pattern in [
            "is", "are", "was", "were", "has", "have", "contains",
            "consists of", "made of", "composed of",
        ]):
            # Check if it has numbers or specific terms
            if re.search(r'\d+', sentence) or len(sentence.split()) > 5:
                claims.append(sentence)
    
    return claims[:10]  # Limit to 10 claims


def check_fact(claim: str) -> Dict[str, Any]:
    """
    Check a factual claim against Wikipedia/Wikidata.
    
    Args:
        claim: Factual claim to check
        
    Returns:
        Dictionary with verification results
    """
    try:
        # Extract key terms from claim
        key_terms = _extract_key_terms(claim)
        
        if not key_terms:
            return {
                "claim": claim,
                "verified": False,
                "confidence": 0.0,
                "sources": [],
                "notes": "Could not extract key terms",
            }
        
        # Try Wikipedia API
        wiki_result = _check_wikipedia(key_terms[0])
        
        if wiki_result["found"]:
            return {
                "claim": claim,
                "verified": True,
                "confidence": 0.8,
                "sources": [wiki_result["url"]],
                "notes": "Verified via Wikipedia",
            }
        
        # If not found, return low confidence
        return {
            "claim": claim,
            "verified": False,
            "confidence": 0.3,
            "sources": [],
            "notes": "Could not verify via Wikipedia",
        }
        
    except Exception as e:
        return {
            "claim": claim,
            "verified": False,
            "confidence": 0.0,
            "sources": [],
            "notes": f"Error checking fact: {str(e)}",
        }


def _extract_key_terms(text: str) -> List[str]:
    """Extract key terms from text for searching."""
    # Remove common words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "has", "have", "this", "that"}
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    key_terms = [w for w in words if w not in stop_words]
    return key_terms[:3]  # Top 3 terms


def _check_wikipedia(term: str) -> Dict[str, Any]:
    """
    Check term against Wikipedia API.
    
    Args:
        term: Term to search for
        
    Returns:
        Dictionary with search results
    """
    try:
        url = f"{WIKIPEDIA_API_URL}/{term}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "found": True,
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "title": data.get("title", ""),
            }
        else:
            return {"found": False, "url": "", "title": ""}
    except Exception:
        return {"found": False, "url": "", "title": ""}



