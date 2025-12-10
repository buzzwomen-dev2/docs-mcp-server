#!/usr/bin/env python3
"""
Test Semantic Score Distribution

Verifies that semantic scores are properly distributed across results
and not all zero.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from search_engine import IndexManager


async def test_semantic_scores():
    """Test that semantic scores are working correctly."""
    print("=" * 70)
    print("SEMANTIC SCORE DISTRIBUTION TEST")
    print("=" * 70)
    
    manager = IndexManager()
    
    test_queries = [
        {
            "query": "Django context template rendering",
            "tech": "django",
            "description": "Django conceptual query",
            "top_k": 5
        },
        {
            "query": "DRF serializer validation",
            "tech": "drf",
            "description": "DRF conceptual query",
            "top_k": 5
        },
        {
            "query": "psycopg async connection pool",
            "tech": "psycopg",
            "description": "Psycopg conceptual query",
            "top_k": 5
        },
        {
            "query": "authentication middleware permissions",
            "tech": None,
            "description": "Cross-tech query",
            "top_k": 5
        },
        {
            "query": "How to pass data from view to template",
            "tech": "django",
            "description": "Natural language query",
            "top_k": 5
        },
        {
            "query": "Django templates render HttpResponse template views context",
            "tech": "django",
            "description": "Complex multi-keyword query",
            "top_k": 10
        },
        {
            "query": "serializer fields nested writable representation",
            "tech": "drf",
            "description": "DRF multi-keyword query",
            "top_k": 10
        },
        {
            "query": "connection pool async cursor execute batch",
            "tech": "psycopg",
            "description": "Psycopg multi-keyword query",
            "top_k": 10
        },
    ]
    
    total_tests = len(test_queries)
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{total_tests}: {test['description']}")
        print(f"Query: '{test['query']}'")
        print(f"Tech: {test['tech'] or 'All'}")
        print("=" * 70)
        
        results = await manager.search(
            test["query"],
            tech_filter=test["tech"],
            top_k=test["top_k"]
        )
        
        if not results:
            print("❌ FAIL: No results returned")
            failed += 1
            continue
        
        # Analyze scores
        semantic_scores = [r.semantic_score for r in results]
        bm25_scores = [r.bm25_score for r in results]
        
        semantic_nonzero = sum(1 for s in semantic_scores if s > 0)
        bm25_nonzero = sum(1 for s in bm25_scores if s > 0)
        
        print(f"\n📊 Score Statistics:")
        print(f"   Total results: {len(results)}")
        print(f"   BM25 non-zero: {bm25_nonzero}/{len(results)} ({bm25_nonzero/len(results)*100:.1f}%)")
        print(f"   Semantic non-zero: {semantic_nonzero}/{len(results)} ({semantic_nonzero/len(results)*100:.1f}%)")
        
        print(f"\n🔝 Top 5 Results:")
        for j, r in enumerate(results[:5], 1):
            print(f"   {j}. {r.topic[:50]}")
            print(f"      BM25: {r.bm25_score:.4f} | Semantic: {r.semantic_score:.4f} | Hybrid: {r.hybrid_score:.4f}")
        
        # Test criteria - updated to expect 100% semantic coverage
        issues = []
        
        # ALL results should have semantic scores (100% coverage)
        if semantic_nonzero < len(results):
            missing = len(results) - semantic_nonzero
            issues.append(f"{missing}/{len(results)} results have semantic_score = 0 (expected 100% coverage)")
        
        # Top result should have semantic score
        if results[0].semantic_score == 0:
            issues.append("Top result has semantic_score = 0")
        
        # All top 3 should have semantic scores
        top3_semantic = sum(1 for r in results[:3] if r.semantic_score > 0)
        if top3_semantic < 3:
            issues.append(f"Only {top3_semantic}/3 top results have semantic scores (expected 3/3)")
        
        # Both BM25 and semantic should contribute to top result
        top = results[0]
        if top.bm25_score == 0 and top.semantic_score == 0:
            issues.append("Top result has both scores = 0")
        
        if issues:
            print(f"\n❌ FAIL:")
            for issue in issues:
                print(f"   - {issue}")
            failed += 1
        else:
            print(f"\n✅ PASS: Semantic scores properly distributed")
            passed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Semantic scoring is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("\nPossible issues:")
        print("  1. Qdrant not returning enough results")
        print("  2. Query embeddings not matching well")
        print("  3. Index needs rebuilding")
        print("\nTroubleshooting:")
        print("  1. Check Qdrant: curl http://localhost:6333/collections/docs_collection")
        print("  2. Rebuild index: uv run scripts/build_index.py --force")
        print("  3. Restart services: docker-compose restart")
        return False


async def test_semantic_score_consistency():
    """Test that semantic scores are consistent across runs."""
    print("\n" + "=" * 70)
    print("SEMANTIC SCORE CONSISTENCY TEST")
    print("=" * 70)
    
    manager = IndexManager()
    
    query = "Django authentication middleware"
    tech = "django"
    
    print(f"\nRunning same query 3 times to check consistency...")
    print(f"Query: '{query}'")
    print(f"Tech: {tech}")
    
    runs = []
    for i in range(3):
        results = await manager.search(query, tech_filter=tech, top_k=5)
        runs.append(results)
        print(f"\nRun {i+1}: {len(results)} results")
        if results:
            print(f"  Top result semantic score: {results[0].semantic_score:.6f}")
    
    # Check consistency
    if not all(runs):
        print("\n❌ FAIL: Some runs returned no results")
        return False
    
    # Compare top result semantic scores
    top_semantic_scores = [run[0].semantic_score for run in runs]
    max_diff = max(top_semantic_scores) - min(top_semantic_scores)
    
    print(f"\n📊 Consistency Analysis:")
    print(f"   Top result semantic scores: {[f'{s:.6f}' for s in top_semantic_scores]}")
    print(f"   Max difference: {max_diff:.6f}")
    
    if max_diff < 0.001:
        print(f"\n✅ PASS: Semantic scores are consistent (diff < 0.001)")
        return True
    else:
        print(f"\n❌ FAIL: Semantic scores vary too much (diff = {max_diff:.6f})")
        return False


async def main():
    """Run all semantic score tests."""
    try:
        # Test 1: Score distribution
        test1_passed = await test_semantic_scores()
        
        # Test 2: Consistency
        test2_passed = await test_semantic_score_consistency()
        
        # Overall result
        if test1_passed and test2_passed:
            print("\n" + "=" * 70)
            print("✅ ALL SEMANTIC SCORE TESTS PASSED")
            print("=" * 70)
            sys.exit(0)
        else:
            print("\n" + "=" * 70)
            print("❌ SOME TESTS FAILED")
            print("=" * 70)
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        print("\nCheck that services are running:")
        print("  docker-compose ps")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
