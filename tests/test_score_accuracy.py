#!/usr/bin/env python3
"""
Score Accuracy Tests

Tests that verify search scores are accurate and meet expected thresholds
for different query types.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from search_engine import IndexManager


class ScoreAccuracyTests:
    """Test suite for validating search score accuracy."""
    
    def __init__(self):
        self.manager = IndexManager()
        self.results: List[Dict] = []
    
    async def test_exact_match_scores(self):
        """Test that exact keyword matches get high BM25 scores."""
        test_cases = [
            {
                "query": "ForeignKey",
                "tech": "django",
                "min_bm25": 0.6,
                "min_hybrid": 0.5,
                "description": "Exact class name match"
            },
            {
                "query": "ModelSerializer",
                "tech": "drf",
                "min_bm25": 0.6,
                "min_hybrid": 0.5,
                "description": "Exact DRF class name"
            },
            {
                "query": "AsyncConnection",
                "tech": "psycopg",
                "min_bm25": 0.5,
                "min_hybrid": 0.5,
                "description": "Exact psycopg class name"
            },
        ]
        
        print("\n" + "=" * 70)
        print("EXACT MATCH SCORE TESTS")
        print("=" * 70)
        
        for case in test_cases:
            results = await self.manager.search(
                case["query"],
                tech_filter=case["tech"],
                top_k=5
            )
            
            test_result = {
                "test": "exact_match",
                "query": case["query"],
                "description": case["description"],
                "passed": False,
                "details": {}
            }
            
            if not results:
                test_result["details"]["error"] = "No results returned"
                print(f"\n❌ {case['description']}: No results")
                self.results.append(test_result)
                continue
            
            top = results[0]
            test_result["details"] = {
                "top_result": top.topic,
                "bm25_score": top.bm25_score,
                "semantic_score": top.semantic_score,
                "hybrid_score": top.hybrid_score,
                "min_bm25_required": case["min_bm25"],
                "min_hybrid_required": case["min_hybrid"]
            }
            
            # Check if scores meet thresholds
            bm25_pass = top.bm25_score >= case["min_bm25"]
            hybrid_pass = top.hybrid_score >= case["min_hybrid"]
            
            test_result["passed"] = bm25_pass and hybrid_pass
            
            if test_result["passed"]:
                print(f"\n✅ {case['description']}")
                print(f"   Query: '{case['query']}'")
                print(f"   BM25: {top.bm25_score:.3f} (min: {case['min_bm25']})")
                print(f"   Hybrid: {top.hybrid_score:.3f} (min: {case['min_hybrid']})")
            else:
                print(f"\n❌ {case['description']}")
                print(f"   Query: '{case['query']}'")
                if not bm25_pass:
                    print(f"   BM25: {top.bm25_score:.3f} < {case['min_bm25']} (FAIL)")
                if not hybrid_pass:
                    print(f"   Hybrid: {top.hybrid_score:.3f} < {case['min_hybrid']} (FAIL)")
            
            self.results.append(test_result)
    
    async def test_semantic_similarity_scores(self):
        """Test that semantically similar queries get high semantic scores."""
        test_cases = [
            {
                "query": "How to authenticate users in Django",
                "tech": "django",
                "min_semantic": 0.7,
                "min_hybrid": 0.6,
                "description": "Natural language auth query"
            },
            {
                "query": "What is the best way to serialize data in REST API",
                "tech": "drf",
                "min_semantic": 0.6,
                "min_hybrid": 0.5,
                "description": "Natural language serialization query"
            },
            {
                "query": "How to manage database connections efficiently",
                "tech": "psycopg",
                "min_semantic": 0.6,
                "min_hybrid": 0.5,
                "description": "Natural language connection query"
            },
        ]
        
        print("\n" + "=" * 70)
        print("SEMANTIC SIMILARITY SCORE TESTS")
        print("=" * 70)
        
        for case in test_cases:
            results = await self.manager.search(
                case["query"],
                tech_filter=case["tech"],
                top_k=5
            )
            
            test_result = {
                "test": "semantic_similarity",
                "query": case["query"],
                "description": case["description"],
                "passed": False,
                "details": {}
            }
            
            if not results:
                test_result["details"]["error"] = "No results returned"
                print(f"\n❌ {case['description']}: No results")
                self.results.append(test_result)
                continue
            
            top = results[0]
            test_result["details"] = {
                "top_result": top.topic,
                "bm25_score": top.bm25_score,
                "semantic_score": top.semantic_score,
                "hybrid_score": top.hybrid_score,
                "min_semantic_required": case["min_semantic"],
                "min_hybrid_required": case["min_hybrid"]
            }
            
            semantic_pass = top.semantic_score >= case["min_semantic"]
            hybrid_pass = top.hybrid_score >= case["min_hybrid"]
            
            test_result["passed"] = semantic_pass and hybrid_pass
            
            if test_result["passed"]:
                print(f"\n✅ {case['description']}")
                print(f"   Query: '{case['query'][:60]}...'")
                print(f"   Semantic: {top.semantic_score:.3f} (min: {case['min_semantic']})")
                print(f"   Hybrid: {top.hybrid_score:.3f} (min: {case['min_hybrid']})")
            else:
                print(f"\n❌ {case['description']}")
                print(f"   Query: '{case['query'][:60]}...'")
                if not semantic_pass:
                    print(f"   Semantic: {top.semantic_score:.3f} < {case['min_semantic']} (FAIL)")
                if not hybrid_pass:
                    print(f"   Hybrid: {top.hybrid_score:.3f} < {case['min_hybrid']} (FAIL)")
            
            self.results.append(test_result)
    
    async def test_hybrid_balance(self):
        """Test that hybrid scoring properly balances BM25 and semantic."""
        test_cases = [
            {
                "query": "Django ORM query optimization",
                "tech": "django",
                "description": "Mixed keyword and semantic query"
            },
            {
                "query": "DRF viewset permissions configuration",
                "tech": "drf",
                "description": "DRF mixed query"
            },
            {
                "query": "psycopg async connection pooling",
                "tech": "psycopg",
                "description": "Psycopg mixed query"
            },
        ]
        
        print("\n" + "=" * 70)
        print("HYBRID BALANCE TESTS")
        print("=" * 70)
        
        for case in test_cases:
            results = await self.manager.search(
                case["query"],
                tech_filter=case["tech"],
                top_k=5
            )
            
            test_result = {
                "test": "hybrid_balance",
                "query": case["query"],
                "description": case["description"],
                "passed": False,
                "details": {}
            }
            
            if not results:
                test_result["details"]["error"] = "No results returned"
                print(f"\n❌ {case['description']}: No results")
                self.results.append(test_result)
                continue
            
            top = results[0]
            
            # Check that hybrid is weighted combination with boosts
            # Base: 0.4 BM25 + 0.6 semantic, but can be boosted up to ~1.5x
            base_hybrid = 0.4 * top.bm25_score + 0.6 * top.semantic_score
            
            # Hybrid should be at least the base and not more than 1.5x (due to boosts)
            hybrid_reasonable = (top.hybrid_score >= base_hybrid * 0.95 and 
                               top.hybrid_score <= base_hybrid * 1.5)
            
            # Check that both BM25 and semantic contribute
            both_contribute = top.bm25_score > 0 and top.semantic_score > 0
            
            test_result["details"] = {
                "top_result": top.topic,
                "bm25_score": top.bm25_score,
                "semantic_score": top.semantic_score,
                "hybrid_score": top.hybrid_score,
                "base_hybrid": base_hybrid,
                "hybrid_reasonable": hybrid_reasonable,
                "both_contribute": both_contribute
            }
            
            test_result["passed"] = hybrid_reasonable and both_contribute
            
            if test_result["passed"]:
                print(f"\n✅ {case['description']}")
                print(f"   BM25: {top.bm25_score:.3f}")
                print(f"   Semantic: {top.semantic_score:.3f}")
                print(f"   Hybrid: {top.hybrid_score:.3f} (base: {base_hybrid:.3f})")
            else:
                print(f"\n❌ {case['description']}")
                print(f"   BM25: {top.bm25_score:.3f}")
                print(f"   Semantic: {top.semantic_score:.3f}")
                print(f"   Hybrid: {top.hybrid_score:.3f} (base: {base_hybrid:.3f})")
                if not hybrid_reasonable:
                    print(f"   ⚠️  Hybrid score unreasonable")
                if not both_contribute:
                    print(f"   ⚠️  Not both scores contributing")
            
            self.results.append(test_result)
    
    async def test_score_consistency(self):
        """Test that same query returns consistent scores."""
        test_queries = [
            ("Django models", "django"),
            ("DRF serializers", "drf"),
            ("psycopg connection", "psycopg"),
        ]
        
        print("\n" + "=" * 70)
        print("SCORE CONSISTENCY TESTS")
        print("=" * 70)
        
        for query, tech in test_queries:
            # Run same query twice
            results1 = await self.manager.search(query, tech_filter=tech, top_k=5)
            await asyncio.sleep(0.1)  # Small delay
            results2 = await self.manager.search(query, tech_filter=tech, top_k=5)
            
            test_result = {
                "test": "score_consistency",
                "query": query,
                "description": f"Consistency for '{query}'",
                "passed": False,
                "details": {}
            }
            
            if not results1 or not results2:
                test_result["details"]["error"] = "Missing results in one run"
                print(f"\n❌ {query}: Missing results")
                self.results.append(test_result)
                continue
            
            # Compare top result scores
            score_diff = abs(results1[0].hybrid_score - results2[0].hybrid_score)
            consistent = score_diff < 0.001  # Allow tiny floating point differences
            
            test_result["details"] = {
                "run1_score": results1[0].hybrid_score,
                "run2_score": results2[0].hybrid_score,
                "difference": score_diff,
                "consistent": consistent
            }
            
            test_result["passed"] = consistent
            
            if test_result["passed"]:
                print(f"\n✅ {query}")
                print(f"   Scores: {results1[0].hybrid_score:.4f} vs {results2[0].hybrid_score:.4f}")
                print(f"   Difference: {score_diff:.6f}")
            else:
                print(f"\n❌ {query}")
                print(f"   Scores: {results1[0].hybrid_score:.4f} vs {results2[0].hybrid_score:.4f}")
                print(f"   Difference: {score_diff:.6f} (too large)")
            
            self.results.append(test_result)
    
    async def test_score_ordering(self):
        """Test that higher scores indicate better relevance."""
        test_cases = [
            {
                "relevant_query": "Django authentication middleware",
                "irrelevant_query": "random unrelated words xyz",
                "tech": "django",
                "description": "Relevant vs irrelevant query scores"
            }
        ]
        
        print("\n" + "=" * 70)
        print("SCORE ORDERING TESTS")
        print("=" * 70)
        
        for case in test_cases:
            relevant = await self.manager.search(
                case["relevant_query"],
                tech_filter=case["tech"],
                top_k=5
            )
            irrelevant = await self.manager.search(
                case["irrelevant_query"],
                tech_filter=case["tech"],
                top_k=5
            )
            
            test_result = {
                "test": "score_ordering",
                "description": case["description"],
                "passed": False,
                "details": {}
            }
            
            if not relevant:
                test_result["details"]["error"] = "No relevant results"
                print(f"\n❌ {case['description']}: No relevant results")
                self.results.append(test_result)
                continue
            
            relevant_score = relevant[0].hybrid_score if relevant else 0.0
            irrelevant_score = irrelevant[0].hybrid_score if irrelevant else 0.0
            
            # Relevant query should score higher
            score_diff = relevant_score - irrelevant_score
            
            test_result["details"] = {
                "relevant_query": case["relevant_query"],
                "irrelevant_query": case["irrelevant_query"],
                "relevant_score": relevant_score,
                "irrelevant_score": irrelevant_score,
                "difference": score_diff
            }
            
            test_result["passed"] = relevant_score > irrelevant_score
            
            if test_result["passed"]:
                print(f"\n✅ {case['description']}")
                print(f"   Relevant: {relevant_score:.3f}")
                print(f"   Irrelevant: {irrelevant_score:.3f}")
                print(f"   Difference: +{score_diff:.3f}")
            else:
                print(f"\n❌ {case['description']}")
                print(f"   Relevant: {relevant_score:.3f}")
                print(f"   Irrelevant: {irrelevant_score:.3f}")
                print(f"   ⚠️  Irrelevant scored higher!")
            
            self.results.append(test_result)
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("SCORE ACCURACY TEST SUMMARY")
        print("=" * 70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        
        print(f"\nTotal tests:  {total}")
        print(f"Passed:       {passed} ({passed/total*100:.1f}%)")
        print(f"Failed:       {failed}")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.results:
                if not result["passed"]:
                    print(f"\n  ❌ {result['test']}: {result['description']}")
                    if "details" in result and "error" in result["details"]:
                        print(f"     Error: {result['details']['error']}")
        
        # Export results to JSON
        output_file = Path(__file__).parent / "score_accuracy_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": passed / total if total > 0 else 0
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n📊 Detailed results saved to: {output_file}")
        
        return failed == 0


async def main():
    """Run all score accuracy tests."""
    print("=" * 70)
    print("SCORE ACCURACY TESTS")
    print("=" * 70)
    print("\nValidating search score accuracy and thresholds...\n")
    
    tester = ScoreAccuracyTests()
    
    # Run all test suites
    await tester.test_exact_match_scores()
    await tester.test_semantic_similarity_scores()
    await tester.test_hybrid_balance()
    await tester.test_score_consistency()
    await tester.test_score_ordering()
    
    # Print summary and exit
    success = tester.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
