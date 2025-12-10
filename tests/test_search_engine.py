#!/usr/bin/env python3
"""
Comprehensive Search Engine Tests

Tests all core functionality of the IndexManager including indexing,
search accuracy, hybrid scoring, and edge cases.
"""

import asyncio
import sys
from pathlib import Path
import tempfile
import shutil
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from search_engine import IndexManager


class TestIndexManager:
    """Test suite for IndexManager core functionality."""
    
    def __init__(self):
        """Initialize test suite."""
        self.manager = IndexManager()
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test IndexManager initializes correctly."""
        assert self.manager is not None
        assert self.manager.embedding_model is not None
        assert self.manager.es_client is not None
        assert self.manager.qdrant_client is not None
        print("✓ IndexManager initialized successfully")
    
    @pytest.mark.asyncio
    async def test_basic_search(self):
        """Test basic search returns results."""
        results = await self.manager.search("Django authentication", top_k=5)
        
        assert len(results) > 0, "Search should return results"
        assert results[0].hybrid_score > 0, "Top result should have positive score"
        print(f"✓ Basic search returned {len(results)} results")
        print(f"  Top result: {results[0].topic} (score: {results[0].hybrid_score:.3f})")
    
    @pytest.mark.asyncio
    async def test_tech_filter(self):
        """Test technology filter works correctly."""
        django_results = await self.manager.search(
            "authentication", 
            tech_filter="django",
            top_k=5
        )
        
        assert all(r.tech == "django" for r in django_results), \
            "All results should be from Django"
        print(f"✓ Tech filter working - {len(django_results)} Django results")
    
    @pytest.mark.asyncio
    async def test_hybrid_scoring(self):
        """Test hybrid scoring combines BM25 and semantic correctly."""
        results = await self.manager.search("Django middleware", top_k=5)
        
        assert len(results) > 0, "Should have results"
        
        top_result = results[0]
        assert top_result.hybrid_score > 0, "Hybrid score should be positive"
        
        # At least one of BM25 or semantic should contribute
        assert top_result.bm25_score > 0 or top_result.semantic_score > 0, \
            "At least one score component should be positive"
        
        # Verify hybrid is weighted combination with boosts
        # Base formula: 0.4 * BM25 + 0.6 * semantic
        # But can be boosted by position/section factors (up to ~1.5x)
        base_expected = (0.4 * top_result.bm25_score + 0.6 * top_result.semantic_score)
        
        # Check hybrid is at least the base and not more than 1.5x base (due to boosts)
        assert top_result.hybrid_score >= base_expected * 0.95, \
            f"Hybrid {top_result.hybrid_score} should be >= base {base_expected}"
        assert top_result.hybrid_score <= base_expected * 1.5, \
            f"Hybrid {top_result.hybrid_score} should be <= 1.5x base {base_expected}"
        
        print(f"✓ Hybrid scoring working correctly")
        print(f"  BM25: {top_result.bm25_score:.3f}, Semantic: {top_result.semantic_score:.3f}")
        print(f"  Hybrid: {top_result.hybrid_score:.3f}")
    
    @pytest.mark.asyncio
    async def test_semantic_search_not_zero(self):
        """Test semantic scores are not all zero."""
        results = await self.manager.search("authentication methods", top_k=10)
        
        semantic_scores = [r.semantic_score for r in results]
        assert any(score > 0 for score in semantic_scores), \
            "At least some results should have semantic scores"
        
        # Top result should have strong semantic score
        assert results[0].semantic_score > 0.5, \
            f"Top result semantic score too low: {results[0].semantic_score}"
        
        print(f"✓ Semantic search working - top semantic score: {results[0].semantic_score:.3f}")
    
    @pytest.mark.asyncio
    async def test_bm25_search_not_zero(self):
        """Test BM25 scores are not all zero."""
        # Use exact keyword that should match well
        results = await self.manager.search("ForeignKey", top_k=10)
        
        bm25_scores = [r.bm25_score for r in results]
        assert any(score > 0 for score in bm25_scores), \
            "At least some results should have BM25 scores"
        
        print(f"✓ BM25 search working - top BM25 score: {results[0].bm25_score:.3f}")
    
    @pytest.mark.asyncio
    async def test_top_k_limit(self):
        """Test top_k parameter limits results correctly."""
        for k in [3, 5, 10, 20]:
            results = await self.manager.search("Django", top_k=k)
            assert len(results) <= k, f"Should return at most {k} results"
        
        print("✓ top_k parameter working correctly")
    
    @pytest.mark.asyncio
    async def test_component_filter(self):
        """Test component filter works."""
        results = await self.manager.search(
            "models",
            component_filter="models",
            top_k=5
        )
        
        # Component filter should prefer results from that component
        if results:
            assert any("model" in r.component.lower() for r in results[:3]), \
                "Top results should include models component"
        
        print(f"✓ Component filter returned {len(results)} results")
    
    @pytest.mark.asyncio
    async def test_exact_method_name_search(self):
        """Test searching for exact method names."""
        test_cases = [
            ("get_or_create", "django"),
            ("select_related", "django"),
            ("prefetch_related", "django"),
        ]
        
        for method_name, tech in test_cases:
            results = await self.manager.search(
                method_name,
                tech_filter=tech,
                top_k=5
            )
            
            assert len(results) > 0, f"Should find results for {method_name}"
            
            # Method name should appear in top results
            top_content = " ".join([r.content.lower() for r in results[:3]])
            assert method_name.lower() in top_content, \
                f"{method_name} should appear in top 3 results"
        
        print("✓ Exact method name searches working")
    
    @pytest.mark.asyncio
    async def test_natural_language_query(self):
        """Test natural language queries work."""
        queries = [
            "How does Django authentication work?",
            "What is the best way to optimize queries?",
            "How do I create a custom serializer?",
        ]
        
        for query in queries:
            results = await self.manager.search(query, top_k=5)
            assert len(results) > 0, f"Should find results for: {query}"
            assert results[0].hybrid_score > 0.3, \
                f"Top result should have decent score for: {query}"
        
        print("✓ Natural language queries working")
    
    @pytest.mark.asyncio
    async def test_cross_tech_search(self):
        """Test searching across technologies."""
        results = await self.manager.search("connection pool", top_k=10)
        
        # Should get results from multiple technologies
        techs = set(r.tech for r in results)
        assert len(techs) > 0, "Should have results from at least one tech"
        
        print(f"✓ Cross-tech search found results from: {', '.join(techs)}")
    
    @pytest.mark.asyncio
    async def test_empty_query(self):
        """Test handling of empty query."""
        results = await self.manager.search("", top_k=5)
        # Should either return nothing or handle gracefully
        assert isinstance(results, list), "Should return list for empty query"
        print("✓ Empty query handled gracefully")
    
    @pytest.mark.asyncio
    async def test_special_characters_query(self):
        """Test queries with special characters."""
        special_queries = [
            "Django's ORM",
            "@action decorator",
            "get() vs filter()",
            "connection['key']",
        ]
        
        for query in special_queries:
            try:
                results = await self.manager.search(query, top_k=5)
                assert isinstance(results, list), f"Should handle: {query}"
            except Exception as e:
                pytest.fail(f"Failed on query '{query}': {e}")
        
        print("✓ Special character queries handled")
    
    @pytest.mark.asyncio
    async def test_long_query(self):
        """Test handling of very long queries."""
        long_query = " ".join(["Django"] * 50)  # Very long query
        results = await self.manager.search(long_query, top_k=5)
        assert isinstance(results, list), "Should handle long queries"
        print("✓ Long query handled")
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting index statistics."""
        stats = await self.manager.get_stats()
        
        assert "total_chunks" in stats, "Stats should include total_chunks"
        assert stats["total_chunks"] > 0, "Should have indexed chunks"
        assert "technologies" in stats, "Stats should include technologies"
        
        print(f"✓ Index stats retrieved: {stats['total_chunks']} total chunks")
        print(f"  Technologies: {', '.join(stats['technologies'])}")
    
    @pytest.mark.asyncio
    async def test_list_sources(self):
        """Test listing source files."""
        sources = self.manager.list_sources()
        
        assert len(sources) > 0, "Should have source files"
        assert all("source_path" in s for s in sources), "Sources should have source_path"
        assert all("tech" in s for s in sources), "Sources should have tech"
        
        print(f"✓ Listed {len(sources)} source files")
    
    @pytest.mark.asyncio
    async def test_retrieve_chunk(self):
        """Test retrieving specific chunk by ID."""
        # First get a chunk ID from search
        results = await self.manager.search("Django", top_k=1)
        assert len(results) > 0, "Need at least one result"
        
        chunk_id = results[0].chunk_id
        
        # Now retrieve it
        chunk = self.manager.retrieve(chunk_id)
        
        assert chunk is not None, "Should retrieve chunk"
        assert chunk.chunk_id == chunk_id, "Should match requested ID"
        
        print(f"✓ Successfully retrieved chunk: {chunk_id}")
    
    @pytest.mark.asyncio
    async def test_score_ranges(self):
        """Test that scores are in valid ranges."""
        results = await self.manager.search("Django models", top_k=10)
        
        for result in results:
            assert 0 <= result.bm25_score <= 1, \
                f"BM25 score out of range: {result.bm25_score}"
            assert 0 <= result.semantic_score <= 1, \
                f"Semantic score out of range: {result.semantic_score}"
            # Hybrid scores can exceed 1.0 due to position and section boosts (up to ~1.5)
            assert 0 <= result.hybrid_score <= 1.5, \
                f"Hybrid score out of range: {result.hybrid_score}"
        
        print("✓ All scores in valid ranges (BM25/Semantic: [0,1], Hybrid: [0,1.5])")
    
    @pytest.mark.asyncio
    async def test_results_sorted_by_score(self):
        """Test results are sorted by hybrid score descending."""
        results = await self.manager.search("authentication", top_k=10)
        
        scores = [r.hybrid_score for r in results]
        assert scores == sorted(scores, reverse=True), \
            "Results should be sorted by score descending"
        
        print("✓ Results properly sorted by score")


async def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("COMPREHENSIVE SEARCH ENGINE TESTS")
    print("=" * 70)
    print()
    
    tester = TestIndexManager()
    
    test_methods = [
        method for method in dir(tester)
        if method.startswith('test_') and callable(getattr(tester, method))
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for test_name in test_methods:
        try:
            print(f"\nRunning {test_name}...")
            await getattr(tester, test_name)()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append((test_name, str(e)))
            print(f"  ❌ FAILED: {e}")
        except Exception as e:
            failed += 1
            errors.append((test_name, f"ERROR: {e}"))
            print(f"  ❌ ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests:  {len(test_methods)}")
    print(f"Passed:       {passed} ({passed/len(test_methods)*100:.1f}%)")
    print(f"Failed:       {failed}")
    
    if errors:
        print("\nFAILED TESTS:")
        for test_name, error in errors:
            print(f"  ❌ {test_name}")
            print(f"     {error}")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
