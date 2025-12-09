#!/usr/bin/env python3
"""
Search Quality Analysis

Analyzes search quality metrics including precision, recall, MRR, and NDCG.
"""

import asyncio
import sys
from pathlib import Path
from collections import defaultdict
import argparse
import json
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from search_engine import IndexManager


class QualityAnalyzer:
    """Analyze search result quality."""
    
    def __init__(self):
        self.manager = IndexManager()
        self.metrics = defaultdict(list)
    
    async def calculate_precision_at_k(
        self,
        query: str,
        expected_keywords: list,
        tech: str = None,
        k: int = 5
    ) -> float:
        """Calculate Precision@K."""
        results = await self.manager.search(
            query=query,
            top_k=k,
            tech_filter=tech
        )
        
        if not results:
            return 0.0
        
        # Check how many of top K results contain expected keywords
        relevant = 0
        for result in results[:k]:
            content_lower = result.content.lower()
            topic_lower = result.topic.lower()
            combined = content_lower + " " + topic_lower
            
            if any(kw.lower() in combined for kw in expected_keywords):
                relevant += 1
        
        return relevant / k
    
    async def calculate_mrr(
        self,
        query: str,
        expected_keywords: list,
        tech: str = None,
        top_k: int = 10
    ) -> float:
        """Calculate Mean Reciprocal Rank."""
        results = await self.manager.search(
            query=query,
            top_k=top_k,
            tech_filter=tech
        )
        
        if not results:
            return 0.0
        
        # Find rank of first relevant result
        for i, result in enumerate(results, 1):
            content_lower = result.content.lower()
            topic_lower = result.topic.lower()
            combined = content_lower + " " + topic_lower
            
            if any(kw.lower() in combined for kw in expected_keywords):
                return 1.0 / i
        
        return 0.0
    
    async def calculate_ndcg(
        self,
        query: str,
        expected_keywords: list,
        tech: str = None,
        k: int = 10
    ) -> float:
        """Calculate Normalized Discounted Cumulative Gain@K."""
        results = await self.manager.search(
            query=query,
            top_k=k,
            tech_filter=tech
        )
        
        if not results:
            return 0.0
        
        # Calculate DCG
        dcg = 0.0
        for i, result in enumerate(results[:k], 1):
            content_lower = result.content.lower()
            topic_lower = result.topic.lower()
            combined = content_lower + " " + topic_lower
            
            # Relevance score: count of matching keywords
            relevance = sum(1 for kw in expected_keywords 
                          if kw.lower() in combined)
            
            dcg += relevance / math.log2(i + 1)
        
        # Calculate ideal DCG (all relevant at top)
        ideal_relevance = [len(expected_keywords)] * min(k, len(expected_keywords))
        ideal_relevance.extend([0] * (k - len(ideal_relevance)))
        
        idcg = sum(rel / math.log2(i + 2) 
                  for i, rel in enumerate(ideal_relevance))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    async def analyze_test_cases(
        self,
        test_cases_file: str = "tests/test_cases.yaml"
    ) -> dict:
        """Analyze all test cases."""
        print("=" * 70)
        print("SEARCH QUALITY ANALYSIS")
        print("=" * 70)
        
        # Load test cases
        with open(test_cases_file, 'r') as f:
            test_data = yaml.safe_load(f)
        
        test_cases = test_data.get("test_cases", [])
        print(f"\nAnalyzing {len(test_cases)} test cases...\n")
        
        # Analyze each test case
        for i, test_case in enumerate(test_cases, 1):
            query = test_case["query"]
            keywords = test_case.get("expected_keywords", [])
            tech = test_case.get("expected_tech")
            
            if not keywords:
                continue
            
            print(f"[{i}/{len(test_cases)}] {query[:50]}...")
            
            # Calculate metrics
            p1 = await self.calculate_precision_at_k(query, keywords, tech, k=1)
            p3 = await self.calculate_precision_at_k(query, keywords, tech, k=3)
            p5 = await self.calculate_precision_at_k(query, keywords, tech, k=5)
            p10 = await self.calculate_precision_at_k(query, keywords, tech, k=10)
            mrr = await self.calculate_mrr(query, keywords, tech)
            ndcg = await self.calculate_ndcg(query, keywords, tech)
            
            self.metrics["precision@1"].append(p1)
            self.metrics["precision@3"].append(p3)
            self.metrics["precision@5"].append(p5)
            self.metrics["precision@10"].append(p10)
            self.metrics["mrr"].append(mrr)
            self.metrics["ndcg@10"].append(ndcg)
            
            print(f"  P@1: {p1:.2f} | P@3: {p3:.2f} | P@5: {p5:.2f} | "
                  f"MRR: {mrr:.2f} | NDCG: {ndcg:.2f}")
        
        # Calculate averages
        results = {
            "test_cases": len(test_cases),
            "metrics": {}
        }
        
        for metric_name, values in self.metrics.items():
            if values:
                results["metrics"][metric_name] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "samples": len(values)
                }
        
        return results
    
    def print_results(self, results: dict):
        """Print analysis results."""
        print("\n" + "=" * 70)
        print("QUALITY METRICS SUMMARY")
        print("=" * 70)
        
        for metric_name, stats in results["metrics"].items():
            print(f"\n{metric_name.upper()}:")
            print(f"  Mean: {stats['mean']:.3f}")
            print(f"  Min:  {stats['min']:.3f}")
            print(f"  Max:  {stats['max']:.3f}")
        
        print("\n" + "=" * 70)
        print("QUALITY RATING")
        print("=" * 70)
        
        mean_p1 = results["metrics"]["precision@1"]["mean"]
        mean_mrr = results["metrics"]["mrr"]["mean"]
        
        if mean_p1 > 0.7 and mean_mrr > 0.8:
            print("  ⭐⭐⭐ Excellent Quality")
        elif mean_p1 > 0.5 and mean_mrr > 0.6:
            print("  ⭐⭐ Good Quality")
        elif mean_p1 > 0.3 and mean_mrr > 0.4:
            print("  ⭐ Acceptable Quality")
        else:
            print("  ⚠️  Needs Improvement")
        
        print("\nRecommendations:")
        if mean_p1 < 0.5:
            print("  • Consider adjusting hybrid weights (BM25 vs semantic)")
            print("  • Review chunk size and overlap settings")
        if mean_mrr < 0.6:
            print("  • Improve keyword matching in BM25")
            print("  • Consider using a different embedding model")
        print()


async def main():
    """Main analysis runner."""
    parser = argparse.ArgumentParser(
        description="Analyze MCP search quality metrics"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    analyzer = QualityAnalyzer()
    results = await analyzer.analyze_test_cases()
    analyzer.print_results(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
