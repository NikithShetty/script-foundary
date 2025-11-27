"""Fact checking service using Brave Search API."""

import re
import requests
import logging
from typing import List, Dict, Any
from app.config import settings
from app.services.llm_service import get_llm_client

logger = logging.getLogger(__name__)

BRAVE_SEARCH_API_URL = "https://api.search.brave.com/res/v1/web/search"


def extract_factual_claims(text: str) -> List[Dict[str, Any]]:
    """
    Extract factual claims from text using LLM for better identification.
    Returns claims with importance scores for prioritization.

    Args:
        text: Text to extract claims from

    Returns:
        List of dictionaries with 'claim' and 'importance' (0.0-1.0) keys
    """
    try:
        # Use LLM to extract factual claims
        client, provider, model = get_llm_client()

        prompt = f"""Extract factual claims from the following educational script text and assign importance scores.
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

For each claim, assign an importance score (0.0-1.0) based on:
- Educational significance (core concepts = high importance)
- Potential for misinformation (critical facts = high importance)
- Relevance to learning objectives (central facts = high importance)
- Trivial facts (common knowledge, obvious statements = low importance)

Text to analyze:
{text[:3000] if len(text) > 3000 else text}

Return a JSON array of objects, each with "claim" (string) and "importance" (float 0.0-1.0).
Example format: [
  {{"claim": "The Earth orbits the Sun", "importance": 0.9}},
  {{"claim": "Water boils at 100 degrees Celsius", "importance": 0.8}},
  {{"claim": "The script is 5 minutes long", "importance": 0.2}}
]

Return only the JSON array, no other text."""

        messages = [
            {
                "role": "system",
                "content": "You are a fact extraction assistant. Extract verifiable factual claims from text and assign importance scores. Return only valid JSON arrays with 'claim' and 'importance' fields.",
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

        claims_data = json.loads(content)

        # Validate and normalize claims data
        normalized_claims = []
        for item in claims_data if isinstance(claims_data, list) else []:
            if isinstance(item, dict) and "claim" in item:
                # Ensure importance is a float between 0 and 1
                importance = float(item.get("importance", 0.5))
                importance = max(0.0, min(1.0, importance))
                normalized_claims.append(
                    {"claim": str(item["claim"]), "importance": importance}
                )
            elif isinstance(item, str):
                # Backward compatibility: if just a string, assign default importance
                normalized_claims.append({"claim": item, "importance": 0.5})

        # Sort by importance (highest first) and limit to max claims
        normalized_claims.sort(key=lambda x: x["importance"], reverse=True)
        max_claims = settings.fact_checker_max_claims
        return normalized_claims[:max_claims]

    except Exception as e:
        logger.warning(
            f"Error extracting claims with LLM, falling back to simple extraction: {str(e)}"
        )
        # Fallback to simple extraction with basic importance scoring
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
                    # Basic importance scoring: higher for numbers, dates, scientific terms
                    importance = 0.3  # Base importance
                    if re.search(r"\d{4}", sentence):  # Years/dates
                        importance = 0.7
                    elif re.search(r"\d+", sentence):  # Numbers
                        importance = 0.5
                    if any(
                        term in sentence.lower()
                        for term in ["definition", "means", "is defined", "consists"]
                    ):
                        importance = max(importance, 0.6)  # Definitions are important

                    claims.append({"claim": sentence, "importance": importance})

        # Sort by importance and limit
        claims.sort(key=lambda x: x["importance"], reverse=True)
        max_claims = settings.fact_checker_max_claims
        return claims[:max_claims]


def _validate_claim_with_llm(claim: str, evidence: str) -> Dict[str, Any]:
    """
    Use LLM to validate a claim against evidence from Brave Search.

    Args:
        claim: The factual claim to validate
        evidence: Evidence text from Brave Search results

    Returns:
        Dictionary with validation result including confidence score
    """
    try:
        client, provider, model = get_llm_client()

        prompt = f"""You are a fact-checking assistant. Analyze the following claim against the provided evidence from web search results.

CLAIM TO VERIFY: {claim}

EVIDENCE FROM WEB SEARCH:
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
    Check a factual claim against Brave Search using LLM validation.

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

        # Search Brave Search for relevant information
        # Try with the full claim first, then fall back to key terms
        search_query = claim
        search_result = _search_brave(search_query)

        if not search_result.get("found"):
            # Try searching with key terms
            for term in key_terms:
                search_result = _search_brave(term)
                if search_result.get("found"):
                    break

        if search_result.get("found"):
            # Use LLM to validate claim against Brave Search evidence
            evidence = search_result.get("evidence", "")

            if evidence:
                validation = _validate_claim_with_llm(claim, evidence)

                return {
                    "claim": claim,
                    "verified": validation["verified"],
                    "confidence": validation["confidence"],
                    "sources": search_result.get("sources", []),
                    "notes": validation.get("notes", "Verified via Brave Search"),
                    "evidence_summary": validation.get("evidence_summary", ""),
                }
            else:
                # Found results but no evidence text available
                return {
                    "claim": claim,
                    "verified": True,  # Results found, assume verified
                    "confidence": 0.6,  # Lower confidence without evidence text
                    "sources": search_result.get("sources", []),
                    "notes": "Search results found but content unavailable for detailed verification",
                    "evidence_summary": "",
                }
        else:
            # No search results found
            return {
                "claim": claim,
                "verified": False,
                "confidence": 0.3,
                "sources": [],
                "notes": "Could not find relevant search results for verification",
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


def _search_brave(query: str) -> Dict[str, Any]:
    """
    Search Brave Search API for a query.

    Args:
        query: Search query

    Returns:
        Dictionary with search results including evidence and sources
    """
    try:
        if not settings.brave_search_api_key:
            logger.warning("Brave Search API key not configured")
            return {"found": False, "evidence": "", "sources": []}

        url = BRAVE_SEARCH_API_URL
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": settings.brave_search_api_key,
        }
        params = {
            "q": query,
            "count": 5,  # Get top 5 results
        }
        timeout = settings.fact_checker_api_timeout

        response = requests.get(url, headers=headers, params=params, timeout=timeout)

        # Log request and truncated response
        if response.status_code == 200:
            data = response.json()
            web_results = data.get("web", {}).get("results", [])
            # Truncate response for logging (first 200 chars of JSON string)
            response_str = str(data)[:200]
            logger.info(
                f"Brave Search API - Request: query='{query}' | Response (truncated): {response_str}..."
            )
        else:
            logger.info(
                f"Brave Search API - Request: query='{query}' | Response: status={response.status_code}"
            )

        if response.status_code == 200:
            data = response.json()
            web_results = data.get("web", {}).get("results", [])

            if not web_results:
                return {"found": False, "evidence": "", "sources": []}

            # Combine evidence from top results
            evidence_parts = []
            sources = []

            for result in web_results[:3]:  # Use top 3 results
                title = result.get("title", "")
                description = result.get("description", "")
                url = result.get("url", "")

                if url:
                    sources.append(url)

                # Combine title and description as evidence
                if title or description:
                    evidence_text = f"{title}: {description}" if title else description
                    evidence_parts.append(evidence_text)

            evidence = "\n\n".join(evidence_parts)

            return {
                "found": True,
                "evidence": evidence,
                "sources": sources,
            }
        else:
            return {"found": False, "evidence": "", "sources": []}
    except Exception as e:
        logger.error(
            f"Error searching Brave Search for '{query}': {str(e)}", exc_info=True
        )
        return {"found": False, "evidence": "", "sources": []}
