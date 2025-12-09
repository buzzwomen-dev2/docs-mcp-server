#!/usr/bin/env python3
"""
MCP Server Performance Benchmark

Measures search performance metrics including latency, throughput, and resource usage.
"""

import asyncio
import sys
import time
from pathlib import Path
from statistics import mean, median, stdev
from typing import List
import argparse
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from search_engine import IndexManager


class SearchBenchmark:
    """Benchmark search engine performance."""
    
    def __init__(self):
        self.manager = None
        self.init_time = 0.0
        self.query_times: List[float] = []
    
    async def initialize(self):
        """Initialize the search engine and measure startup time."""
        print("Initializing IndexManager...")
        start = time.time()
        self.manager = IndexManager()
        self.init_time = time.time() - start
        print(f"✓ Initialization completed in {self.init_time:.2f}s\n")
    
    async def benchmark_single_query(
        self,
        query: str,
        tech: str = None,
        top_k: int = 10
    ) -> dict:
        """Benchmark a single query and return timing info."""
        start = time.time()
        results = await self.manager.search(
            query=query,
            top_k=top_k,
            tech_filter=tech
        )
        elapsed = time.time() - start
        
        return {
            "query": query,
            "elapsed": elapsed,
            "result_count": len(results),
            "top_score": results[0].hybrid_score if results else 0.0
        }
    
    async def run_benchmark(
        self,
        queries: List[str],
        warmup_queries: int = 3,
        tech_filter: str = None
    ) -> dict:
        """Run benchmark with multiple queries."""
        print("=" * 70)
        print("SEARCH PERFORMANCE BENCHMARK")
        print("=" * 70)
        print(f"Queries to run: {len(queries)}")
        print(f"Warmup queries: {warmup_queries}")
        print(f"Tech filter: {tech_filter or 'None'}\n")
        
        all_results = []
        
        # Warmup phase
        print("Warming up...")
        for i in range(min(warmup_queries, len(queries))):
            await self.benchmark_single_query(queries[i], tech_filter)
        print("✓ Warmup complete\n")
        
        # Benchmark phase
        print("Running benchmark...")
        for i, query in enumerate(queries, 1):
            result = await self.benchmark_single_query(query, tech_filter)
            all_results.append(result)
            self.query_times.append(result["elapsed"])
            
            if i % 10 == 0 or i == len(queries):
                print(f"  [{i}/{len(queries)}] {query[:50]}... "
                      f"{result['elapsed']*1000:.0f}ms")
        
        print()
        
        # Calculate statistics
        sorted_times = sorted(self.query_times)
        stats = {
            "initialization_time": self.init_time,
            "total_queries": len(queries),
            "total_time": sum(self.query_times),
            "mean_latency": mean(self.query_times),
            "median_latency": median(self.query_times),
            "stddev_latency": stdev(self.query_times) if len(self.query_times) > 1 else 0,
            "min_latency": min(self.query_times),
            "max_latency": max(self.query_times),
            "p50_latency": sorted_times[len(sorted_times) // 2],
            "p95_latency": sorted_times[int(len(sorted_times) * 0.95)],
            "p99_latency": sorted_times[int(len(sorted_times) * 0.99)],
            "queries_per_second": len(queries) / sum(self.query_times),
            "results": all_results
        }
        
        return stats
    
    def print_results(self, stats: dict):
        """Print benchmark results."""
        print("=" * 70)
        print("BENCHMARK RESULTS")
        print("=" * 70)
        print(f"\nInitialization:")
        print(f"  Time: {stats['initialization_time']:.2f}s")
        
        print(f"\nQuery Performance:")
        print(f"  Total queries: {stats['total_queries']}")
        print(f"  Total time: {stats['total_time']:.2f}s")
        print(f"  Queries/sec: {stats['queries_per_second']:.2f}")
        
        print(f"\nLatency (milliseconds):")
        print(f"  Mean:   {stats['mean_latency']*1000:.1f}ms")
        print(f"  Median: {stats['median_latency']*1000:.1f}ms")
        print(f"  StdDev: {stats['stddev_latency']*1000:.1f}ms")
        print(f"  Min:    {stats['min_latency']*1000:.1f}ms")
        print(f"  Max:    {stats['max_latency']*1000:.1f}ms")
        
        print(f"\nPercentiles:")
        print(f"  P50: {stats['p50_latency']*1000:.1f}ms")
        print(f"  P95: {stats['p95_latency']*1000:.1f}ms")
        print(f"  P99: {stats['p99_latency']*1000:.1f}ms")
        
        print(f"\nPerformance Rating:")
        if stats['mean_latency'] < 1.0:
            print("  ⭐⭐⭐ Excellent (< 1s average)")
        elif stats['mean_latency'] < 2.0:
            print("  ⭐⭐ Good (< 2s average)")
        elif stats['mean_latency'] < 3.0:
            print("  ⭐ Acceptable (< 3s average)")
        else:
            print("  ⚠️  Needs optimization (> 3s average)")
        print()


async def main():
    """Main benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Benchmark MCP search engine performance"
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=20,
        help="Number of queries to run (default: 20)"
    )
    parser.add_argument(
        "--tech",
        choices=["django", "drf", "psycopg"],
        help="Filter by technology"
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=3,
        help="Number of warmup queries (default: 3)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    # Standard benchmark queries
    benchmark_queries = [
        "Django ORM transactions",
        "DRF serializer validation",
        "psycopg connection pooling",
        "Django authentication middleware",
        "DRF ViewSet permissions",
        "psycopg async operations",
        "Django model relationships",
        "DRF nested serializers",
        "psycopg cursor usage",
        "Django queryset optimization",
        "DRF pagination",
        "psycopg transaction management",
        "Django migrations",
        "DRF filtering",
        "psycopg prepared statements",
        "Django signals",
        "DRF routers",
        "psycopg copy operations",
        "Django caching",
        "DRF throttling",
        "psycopg connection context",
        "Django forms validation",
        "DRF authentication",
        "psycopg server cursors",
        "Django admin customization",
        "DRF versioning",
        "psycopg type adapters",
        "Django testing",
        "DRF content negotiation",
        "psycopg connection strings",
        "Django URL routing",
        "DRF request parsing",
        "psycopg async pool",
        "Django templates",
        "DRF response rendering",
        "psycopg error handling",
        "Django middleware",
        "DRF metadata",
        "psycopg notifications",
        "Django sessions",
        "DRF schemas",
        "psycopg binary data",
        "Django security",
        "DRF testing",
        "psycopg SQL composition",
        "Django email",
        "DRF custom fields",
        "psycopg pipeline",
        "Django logging",
        "DRF renderers",
        "psycopg JSONB"
    ]
    
    # Select subset of queries
    queries = benchmark_queries[:args.queries]
    
    # Run benchmark
    benchmark = SearchBenchmark()
    await benchmark.initialize()
    stats = await benchmark.run_benchmark(
        queries=queries,
        warmup_queries=args.warmup,
        tech_filter=args.tech
    )
    
    # Print results
    benchmark.print_results(stats)
    
    # Save to file if requested
    if args.output:
        # Remove detailed results for cleaner JSON
        output_stats = {k: v for k, v in stats.items() if k != "results"}
        with open(args.output, 'w') as f:
            json.dump(output_stats, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
