#!/usr/bin/env python3
"""
MCP Server Accuracy Tests

Tests the accuracy of hybrid search results against known documentation queries.
Validates that the search engine returns relevant results for common development questions.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from search_engine import IndexManager


class TestMCPAccuracy:
    """Test suite for MCP server search accuracy."""
    
    def __init__(self):
        self.manager = IndexManager()
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
    
    async def run_test_case(self, test_case: dict) -> dict:
        """Run a single test case."""
        query = test_case["query"]
        expected_keywords = test_case.get("expected_keywords", [])
        expected_tech = test_case.get("expected_tech")
        min_score = test_case.get("min_score", 0.3)
        top_k = test_case.get("top_k", 10)
        
        # Execute search
        results = await self.manager.search(
            query=query,
            top_k=top_k,
            tech_filter=expected_tech
        )
        
        # Validate results
        test_result = {
            "query": query,
            "description": test_case.get("description", ""),
            "passed": False,
            "issues": [],
            "result_count": len(results),
            "top_score": results[0].hybrid_score if results else 0.0,
            "top_result": results[0].topic if results else None
        }
        
        # Check 1: Results exist
        if not results:
            test_result["issues"].append("No results returned")
            return test_result
        
        # Check 2: Top result score meets threshold
        if results[0].hybrid_score < min_score:
            test_result["issues"].append(
                f"Top score {results[0].hybrid_score:.3f} below threshold {min_score}"
            )
        
        # Check 3: Expected keywords present in top 5 results
        # Using top 5 instead of top 3 is more realistic for hybrid search
        top_5_content = " ".join([r.content.lower() for r in results[:5]])
        missing_keywords = [kw for kw in expected_keywords 
                          if kw.lower() not in top_5_content]
        if missing_keywords:
            test_result["issues"].append(
                f"Missing expected keywords in top 5: {', '.join(missing_keywords)}"
            )
        
        # Check 4: Tech filter working
        if expected_tech:
            wrong_tech = [r for r in results[:5] if r.tech != expected_tech]
            if wrong_tech:
                test_result["issues"].append(
                    f"Found {len(wrong_tech)} results from wrong tech in top 5"
                )
        
        # Check 5: Hybrid scoring sanity check
        # Both scores being zero would indicate a problem, but having one zero is fine
        # (e.g., semantic search found it but BM25 didn't, or vice versa)
        if results[0].bm25_score == 0 and results[0].semantic_score == 0:
            test_result["issues"].append(
                "Hybrid scoring error: both BM25 and semantic scores are zero"
            )
        
        # Verify hybrid score is actually a weighted combination
        if results[0].hybrid_score == 0:
            test_result["issues"].append(
                "Hybrid score is zero despite having results"
            )
        
        test_result["passed"] = len(test_result["issues"]) == 0
        return test_result
    
    async def run_all_tests(self, test_cases_file: str = "tests/test_cases.yaml"):
        """Run all test cases from YAML file."""
        print("=" * 70)
        print("MCP SERVER ACCURACY TESTS")
        print("=" * 70)
        
        # Load test cases
        with open(test_cases_file, 'r') as f:
            test_data = yaml.safe_load(f)
        
        test_cases = test_data.get("test_cases", [])
        print(f"\nLoaded {len(test_cases)} test cases\n")
        
        # Run tests
        for i, test_case in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] Testing: {test_case['query'][:60]}...")
            
            result = await self.run_test_case(test_case)
            self.results["total"] += 1
            
            if result["passed"]:
                self.results["passed"] += 1
                print(f"  ✅ PASS - Top result: {result['top_result'][:50]}")
                print(f"           Score: {result['top_score']:.3f}")
            else:
                self.results["failed"] += 1
                print(f"  ❌ FAIL")
                for issue in result["issues"]:
                    print(f"           - {issue}")
            
            self.results["details"].append(result)
            print()
        
        # Summary
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total tests:  {self.results['total']}")
        print(f"Passed:       {self.results['passed']} "
              f"({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"Failed:       {self.results['failed']}")
        print()
        
        # Detailed failures
        if self.results["failed"] > 0:
            print("FAILED TESTS:")
            for detail in self.results["details"]:
                if not detail["passed"]:
                    print(f"\n❌ {detail['query']}")
                    for issue in detail["issues"]:
                        print(f"   - {issue}")
        
        return self.results


async def main():
    """Main test runner."""
    tester = TestMCPAccuracy()
    results = await tester.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
