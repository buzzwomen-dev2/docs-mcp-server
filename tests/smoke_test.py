#!/usr/bin/env python3
"""
Quick Smoke Test

Fast sanity check to verify the system is working correctly.
Runs a few essential tests to catch major issues.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from search_engine import IndexManager


async def smoke_test():
    """Run quick smoke tests."""
    print("=" * 70)
    print("QUICK SMOKE TEST")
    print("=" * 70)
    print("\nRunning essential checks...\n")
    
    manager = IndexManager()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Index has data
    print("1️⃣  Checking index has data...")
    stats = await manager.get_stats()
    if stats["total_chunks"] > 0:
        print(f"   ✅ Index has {stats['total_chunks']} chunks")
        tests_passed += 1
    else:
        print(f"   ❌ Index is empty!")
        tests_failed += 1
    
    # Test 2: Basic search works
    print("\n2️⃣  Testing basic search...")
    results = await manager.search("Django authentication", top_k=5)
    if len(results) > 0 and results[0].hybrid_score > 0:
        print(f"   ✅ Search returned {len(results)} results")
        print(f"      Top score: {results[0].hybrid_score:.3f}")
        tests_passed += 1
    else:
        print(f"   ❌ Search failed or returned no results")
        tests_failed += 1
    
    # Test 3: BM25 scores work
    print("\n3️⃣  Testing BM25 scores...")
    if results and results[0].bm25_score > 0:
        print(f"   ✅ BM25 score: {results[0].bm25_score:.3f}")
        tests_passed += 1
    else:
        print(f"   ❌ BM25 scores not working")
        tests_failed += 1
    
    # Test 4: Semantic scores work
    print("\n4️⃣  Testing semantic scores...")
    if results and results[0].semantic_score > 0:
        print(f"   ✅ Semantic score: {results[0].semantic_score:.3f}")
        tests_passed += 1
    else:
        print(f"   ❌ Semantic scores not working")
        tests_failed += 1
    
    # Test 5: Hybrid formula correct (with position/section boosts)
    print("\n5️⃣  Testing hybrid scoring formula...")
    if results:
        top = results[0]
        base_expected = 0.4 * top.bm25_score + 0.6 * top.semantic_score
        # Hybrid score can exceed base due to position/section boosts (max ~1.4x)
        # Check if hybrid is at least the base and not more than 1.5x base
        if top.hybrid_score >= base_expected * 0.95 and top.hybrid_score <= base_expected * 1.5:
            print(f"   ✅ Hybrid = 0.4*BM25 + 0.6*Semantic + boosts")
            print(f"      {top.hybrid_score:.3f} ≈ 0.4*{top.bm25_score:.3f} + 0.6*{top.semantic_score:.3f} = {base_expected:.3f} (with boosts)")
            tests_passed += 1
        else:
            print(f"   ❌ Hybrid formula incorrect")
            print(f"      Got: {top.hybrid_score:.3f}")
            print(f"      Base expected: {base_expected:.3f}")
            tests_failed += 1
    else:
        print(f"   ⚠️  Skipped (no results)")
        tests_failed += 1
    
    # Test 6: Tech filter works
    print("\n6️⃣  Testing tech filter...")
    django_results = await manager.search("models", tech_filter="django", top_k=5)
    if django_results and all(r.tech == "django" for r in django_results):
        print(f"   ✅ Tech filter working (found {len(django_results)} Django results)")
        tests_passed += 1
    else:
        print(f"   ❌ Tech filter not working correctly")
        tests_failed += 1
    
    # Test 7: Retrieve chunk works
    print("\n7️⃣  Testing chunk retrieval...")
    if results:
        chunk_id = results[0].chunk_id
        chunk = manager.retrieve(chunk_id)
        if chunk and chunk.chunk_id == chunk_id:
            print(f"   ✅ Retrieved chunk: {chunk_id}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed to retrieve chunk")
            tests_failed += 1
    else:
        print(f"   ⚠️  Skipped (no results)")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("SMOKE TEST SUMMARY")
    print("=" * 70)
    print(f"\nPassed: {tests_passed}/7")
    print(f"Failed: {tests_failed}/7")
    
    if tests_failed == 0:
        print("\n✅ ALL SMOKE TESTS PASSED - System is healthy!")
        return True
    elif tests_failed <= 2:
        print("\n⚠️  Some tests failed - System may have minor issues")
        return False
    else:
        print("\n❌ MULTIPLE FAILURES - System needs attention!")
        print("\nTroubleshooting:")
        print("  1. Check if index is built: uv run scripts/build_index.py")
        print("  2. Verify services running: docker ps")
        print("  3. Check Qdrant has vectors: curl http://localhost:6333/collections/docs_collection")
        return False


def main():
    """Main entry point."""
    try:
        success = asyncio.run(smoke_test())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        print("\nCheck that Elasticsearch and Qdrant are running:")
        print("  docker-compose up -d")
        sys.exit(2)


if __name__ == "__main__":
    main()
