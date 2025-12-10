#!/usr/bin/env python3
"""
Test Variable top_k Values

Verifies that semantic score coverage works for any value of top_k.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from search_engine import IndexManager


async def test_variable_topk():
    """Test semantic score coverage with various top_k values."""
    print("=" * 70)
    print("VARIABLE top_k SEMANTIC COVERAGE TEST")
    print("=" * 70)
    print("\nTesting semantic score coverage with different top_k values...")
    
    manager = IndexManager()
    
    test_cases = [
        ("Django templates render HttpResponse", "django"),
        ("DRF serializer validation", "drf"),
        ("psycopg connection pool", "psycopg"),
        ("authentication permissions", None),
    ]
    
    # Test with various top_k values
    top_k_values = [1, 3, 5, 10, 15, 20, 30, 50]
    
    all_passed = True
    results_summary = []
    
    for query, tech in test_cases:
        print(f"\n{'='*70}")
        print(f"Query: '{query}'")
        print(f"Tech: {tech or 'All'}")
        print("=" * 70)
        
        query_results = []
        for top_k in top_k_values:
            results = await manager.search(query, tech_filter=tech, top_k=top_k)
            
            if not results:
                print(f"  top_k={top_k:2d}: ⚠️  No results")
                continue
            
            zero_semantic = sum(1 for r in results if r.semantic_score == 0)
            coverage = (len(results) - zero_semantic) / len(results) * 100 if results else 0
            
            # Check if all results have semantic scores
            passed = zero_semantic == 0
            status = "✅" if passed else "❌"
            
            query_results.append({
                "top_k": top_k,
                "total": len(results),
                "zero_semantic": zero_semantic,
                "coverage": coverage,
                "passed": passed
            })
            
            if not passed:
                all_passed = False
            
            print(f"  top_k={top_k:2d}: {status} {len(results):2d} results, "
                  f"{zero_semantic:2d} with semantic=0, coverage={coverage:5.1f}%")
        
        results_summary.append({
            "query": query,
            "tech": tech,
            "results": query_results
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_tests = sum(len(r["results"]) for r in results_summary)
    passed_tests = sum(sum(1 for test in r["results"] if test["passed"]) 
                      for r in results_summary)
    
    print(f"\nTotal configurations tested: {total_tests}")
    print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Failed: {total_tests - passed_tests}")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Semantic score coverage is 100% for all top_k values tested")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("⚠️  Semantic score coverage is not 100% for some top_k values")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_variable_topk())
    sys.exit(exit_code)
