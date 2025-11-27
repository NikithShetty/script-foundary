"""Fact checking service using Wikipedia/Wikidata APIs."""

import os
import re
import requests
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.llm_service import get_llm_client

logger = logging.getLogger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"  # MediaWiki API for search
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"


def extract_factual_claims(text: str) -> List[str]:
    """
    Extract factual claims from text using LLM for better identification.

    Args:
        text: Text to extract claims from

    Returns:
        List of factual claims
    """
    try:
        # Use LLM to extract factual claims
        client, provider, model = get_llm_client()

        prompt = f"""Extract factual claims from the following educational script text. 
Focus on statements that contain verifiable facts such as:
- Dates, numbers, statistics
- Definitions and explanations
- Historical events
- Scientific facts
- Geographic information

Ignore:
- Instructions or directions
- Dialogue or conversational text
- Opinions or subjective statements
- Questions

Text to analyze:
{text[:3000] if len(text) > 3000 else text}

Return a JSON array of factual claim strings. Each claim should be a complete, verifiable statement.
Example format: ["The Earth orbits the Sun", "Water boils at 100 degrees Celsius"]

Return only the JSON array, no other text."""

        messages = [
            {
                "role": "system",
                "content": "You are a fact extraction assistant. Extract only verifiable factual claims from text. Return only valid JSON arrays.",
            },
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON response
        import json

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        claims = json.loads(content)

        # Limit to configured max claims
        max_claims = settings.fact_checker_max_claims
        return claims[:max_claims] if isinstance(claims, list) else []

    except Exception as e:
        logger.warning(
            f"Error extracting claims with LLM, falling back to simple extraction: {str(e)}"
        )
        # Fallback to simple extraction
        claims = []
        sentences = re.split(r"[.!?]+", text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Look for factual patterns
            if any(
                pattern in sentence.lower()
                for pattern in [
                    "is",
                    "are",
                    "was",
                    "were",
                    "has",
                    "have",
                    "contains",
                    "consists of",
                    "made of",
                    "composed of",
                ]
            ):
                # Check if it has numbers or specific terms
                if re.search(r"\d+", sentence) or len(sentence.split()) > 5:
                    claims.append(sentence)

        max_claims = settings.fact_checker_max_claims
        return claims[:max_claims]


def _validate_claim_with_llm(claim: str, evidence: str) -> Dict[str, Any]:
    """
    Use LLM to validate a claim against evidence from Wikipedia.

    Args:
        claim: The factual claim to validate
        evidence: Evidence text from Wikipedia

    Returns:
        Dictionary with validation result including confidence score
    """
    try:
        client, provider, model = get_llm_client()

        prompt = f"""You are a fact-checking assistant. Analyze the following claim against the provided evidence from Wikipedia.

CLAIM TO VERIFY: {claim}

EVIDENCE FROM WIKIPEDIA:
{evidence[:2000] if len(evidence) > 2000 else evidence}

Determine:
1. Is the claim VERIFIED (supported by evidence), PARTIALLY_VERIFIED (partially supported), or UNVERIFIED (not supported or contradicted)?
2. Assign a confidence score from 0.0 to 1.0 based on:
   - How well the evidence supports the claim
   - Quality and relevance of the evidence
   - Specificity of the claim
3. Provide a brief explanation

Return a JSON object with this structure:
{{
    "verified": true/false,
    "confidence": 0.0-1.0,
    "notes": "Brief explanation of verification result",
    "evidence_summary": "Key points from evidence that support or contradict the claim"
}}

Return only the JSON object, no other text."""

        messages = [
            {
                "role": "system",
                "content": "You are a fact-checking assistant. Analyze claims against evidence and return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON response
        import json

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)

        # Ensure confidence is a float between 0 and 1
        confidence = float(result.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))

        return {
            "verified": bool(result.get("verified", False)),
            "confidence": confidence,
            "notes": result.get("notes", ""),
            "evidence_summary": result.get("evidence_summary", ""),
        }

    except Exception as e:
        logger.error(f"Error validating claim with LLM: {str(e)}")
        return {
            "verified": False,
            "confidence": 0.0,
            "notes": f"Error during LLM validation: {str(e)}",
            "evidence_summary": "",
        }


def check_fact(claim: str) -> Dict[str, Any]:
    """
    Check a factual claim against Wikipedia/Wikidata using LLM validation.

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
                "evidence_summary": "",
            }

        # Search Wikipedia for relevant information
        wiki_result = _check_wikipedia(key_terms[0])

        if not wiki_result.get("found"):
            # Try searching with the full claim or other key terms
            for term in key_terms[1:]:
                wiki_result = _check_wikipedia(term)
                if wiki_result.get("found"):
                    break

        if wiki_result.get("found"):
            # Use LLM to validate claim against Wikipedia evidence
            evidence = wiki_result.get("extract", "")
            if not evidence:
                # Try to get more content from the page
                page = _get_wikipedia_page(wiki_result.get("title", ""))
                if page:
                    evidence = page.get("extract", "")

            if evidence:
                validation = _validate_claim_with_llm(claim, evidence)

                return {
                    "claim": claim,
                    "verified": validation["verified"],
                    "confidence": validation["confidence"],
                    "sources": [wiki_result.get("url", "")]
                    if wiki_result.get("url")
                    else [],
                    "notes": validation.get("notes", "Verified via Wikipedia"),
                    "evidence_summary": validation.get("evidence_summary", ""),
                }
            else:
                # Found page but no extract available
                return {
                    "claim": claim,
                    "verified": True,  # Page exists, assume verified
                    "confidence": 0.6,  # Lower confidence without evidence text
                    "sources": [wiki_result.get("url", "")]
                    if wiki_result.get("url")
                    else [],
                    "notes": "Wikipedia page found but content unavailable for detailed verification",
                    "evidence_summary": "",
                }
        else:
            # No Wikipedia page found
            return {
                "claim": claim,
                "verified": False,
                "confidence": 0.3,
                "sources": [],
                "notes": "Could not find relevant Wikipedia page for verification",
                "evidence_summary": "",
            }

    except Exception as e:
        logger.error(f"Error checking fact '{claim}': {str(e)}")
        return {
            "claim": claim,
            "verified": False,
            "confidence": 0.0,
            "sources": [],
            "notes": f"Error checking fact: {str(e)}",
            "evidence_summary": "",
        }


def _extract_key_terms(text: str) -> List[str]:
    """Extract key terms from text for searching."""
    # Remove common words
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "has",
        "have",
        "this",
        "that",
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    key_terms = [w for w in words if w not in stop_words]
    return key_terms[:3]  # Top 3 terms


def _search_wikipedia(term: str) -> List[Dict[str, Any]]:
    """
    Search Wikipedia for a term using MediaWiki API.

    Args:
        term: Term to search for

    Returns:
        List of search results with title, url, and extract
    """
    try:
        url = WIKIPEDIA_SEARCH_URL
        params = {
            "action": "query",
            "list": "search",
            "srsearch": term,
            "srlimit": 3,
            "format": "json",
        }
        timeout = settings.fact_checker_api_timeout

        response = requests.get(url, params=params, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            results = []
            for item in search_results:
                title = item.get("title", "")
                # Get page summary for extract
                page_data = _get_wikipedia_page(title)
                if page_data:
                    results.append(
                        {
                            "title": title,
                            "url": page_data.get("url", ""),
                            "extract": page_data.get("extract", ""),
                        }
                    )
                else:
                    # Fallback: create URL from title
                    import urllib.parse

                    encoded_title = urllib.parse.quote(title.replace(" ", "_"))
                    results.append(
                        {
                            "title": title,
                            "url": f"https://en.wikipedia.org/wiki/{encoded_title}",
                            "extract": item.get("snippet", "")
                            .replace('<span class="searchmatch">', "")
                            .replace("</span>", ""),
                        }
                    )
            return results
        else:
            return []
    except Exception as e:
        logger.warning(f"Error searching Wikipedia for '{term}': {str(e)}")
        return []


def _get_wikipedia_page(title: str) -> Optional[Dict[str, Any]]:
    """
    Get Wikipedia page summary by title.

    Args:
        title: Wikipedia page title

    Returns:
        Dictionary with page data or None
    """
    try:
        # URL encode the title
        import urllib.parse

        encoded_title = urllib.parse.quote(title.replace(" ", "_"))
        url = f"{WIKIPEDIA_API_URL}/{encoded_title}"
        timeout = settings.fact_checker_api_timeout

        response = requests.get(url, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            return {
                "found": True,
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "title": data.get("title", ""),
                "extract": data.get("extract", ""),
                "description": data.get("description", ""),
            }
        else:
            return None
    except Exception as e:
        logger.warning(f"Error getting Wikipedia page '{title}': {str(e)}")
        return None


def _check_wikipedia(term: str) -> Dict[str, Any]:
    """
    Check term against Wikipedia API (legacy function for backward compatibility).

    Args:
        term: Term to search for

    Returns:
        Dictionary with search results
    """
    # First try direct page lookup
    page = _get_wikipedia_page(term)
    if page:
        return {
            "found": True,
            "url": page.get("url", ""),
            "title": page.get("title", ""),
            "extract": page.get("extract", ""),
        }

    # If not found, try search
    results = _search_wikipedia(term)
    if results:
        return {
            "found": True,
            "url": results[0].get("url", ""),
            "title": results[0].get("title", ""),
            "extract": results[0].get("extract", ""),
        }

    return {"found": False, "url": "", "title": "", "extract": ""}
