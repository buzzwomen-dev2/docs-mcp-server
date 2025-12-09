#!/usr/bin/env python3
"""
Test script to demonstrate query expansion functionality.
"""

import re

def expand_query(query: str) -> str:
    """
    Expand comparison queries to improve search results.
    
    Transforms 'X vs Y' queries into OR queries that search for both terms.
    Also handles 'versus', 'compared to', 'difference between' patterns.
    """
    # Pattern 1: "X vs Y" or "X versus Y"
    vs_pattern = r'(.+?)\s+(?:vs\.?|versus)\s+(.+?)(?:\s+|$)'
    match = re.search(vs_pattern, query, re.IGNORECASE)
    if match:
        term1 = match.group(1).strip()
        term2 = match.group(2).strip()
        # Remove trailing words like "difference", "when to use", etc.
        term2 = re.sub(r'\s+(difference|when|how|why).*$', '', term2, flags=re.IGNORECASE)
        return f"{term1} OR {term2}"
    
    # Pattern 2: "difference between X and Y"
    diff_pattern = r'difference\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+|$)'
    match = re.search(diff_pattern, query, re.IGNORECASE)
    if match:
        term1 = match.group(1).strip()
        term2 = match.group(2).strip()
        return f"{term1} OR {term2}"
    
    # Pattern 3: "compared to" or "comparison"
    comp_pattern = r'(.+?)\s+compared\s+to\s+(.+?)(?:\s+|$)'
    match = re.search(comp_pattern, query, re.IGNORECASE)
    if match:
        term1 = match.group(1).strip()
        term2 = match.group(2).strip()
        return f"{term1} OR {term2}"
    
    # No pattern matched, return original query
    return query


# Test cases
test_queries = [
    "DRF Serializer vs ModelSerializer difference when to use",
    "Serializer versus ModelSerializer",
    "difference between select_related and prefetch_related",
    "APIView compared to ViewSet",
    "AsyncConnection vs Connection in psycopg",
    "what is ModelSerializer",  # Should NOT expand
    "how to use select_related",  # Should NOT expand
]

print("=" * 70)
print("QUERY EXPANSION TEST")
print("=" * 70)
print()

for query in test_queries:
    expanded = expand_query(query)
    changed = " ✓ EXPANDED" if expanded != query else ""
    print(f"Original:  {query}")
    print(f"Expanded:  {expanded}{changed}")
    print()
