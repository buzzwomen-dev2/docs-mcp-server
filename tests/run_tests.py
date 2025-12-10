#!/usr/bin/env python3
"""
Test Suite Runner

Orchestrates all test suites: accuracy, performance, and quality analysis.
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


class TestRunner:
    """Run all test suites and generate comprehensive report."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "accuracy": None,
            "performance": None,
            "quality": None,
            "overall_status": "UNKNOWN"
        }
        self.tests_dir = Path(__file__).parent
    
    def run_command(self, script_name: str, args: Optional[list] = None) -> dict:
        """Run a test script and capture results."""
        cmd = ["python", str(self.tests_dir / script_name)]
        if args:
            cmd.extend(args)
        
        print(f"\n{'='*70}")
        print(f"Running: {' '.join(cmd)}")
        print(f"{'='*70}\n")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.tests_dir.parent
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            print(f"Error running {script_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def parse_accuracy_results(self, stdout: str) -> dict:
        """Parse accuracy test output."""
        lines = stdout.split('\n')
        for line in lines:
            if "Passed:" in line and "(" in line:
                # Extract: "Passed: 35 (87.5%)"
                parts = line.split()
                passed = int(parts[1])
                percent = float(parts[2].strip('()%'))
                total = int(passed / (percent / 100)) if percent > 0 else 0
                return {
                    "total": total,
                    "passed": passed,
                    "failed": total - passed,
                    "pass_rate": percent / 100
                }
        return {"error": "Could not parse results"}
    
    def run_all_tests(self):
        """Run all test suites."""
        print("=" * 70)
        print("MCP SERVER COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Started at: {self.results['timestamp']}\n")
        
        # 1. Core Functionality Tests
        print("\n🔧 RUNNING CORE FUNCTIONALITY TESTS...\n")
        core_result = self.run_command("test_search_engine.py")
        self.results["core"] = {
            "success": core_result["success"],
            "returncode": core_result["returncode"]
        }
        
        # 2. Score Accuracy Tests
        print("\n📊 RUNNING SCORE ACCURACY TESTS...\n")
        score_result = self.run_command("test_score_accuracy.py")
        self.results["scores"] = {
            "success": score_result["success"],
            "returncode": score_result["returncode"]
        }
        
        # 3. Integration Tests
        print("\n🔗 RUNNING INTEGRATION TESTS...\n")
        integration_result = self.run_command("test_integration.py")
        self.results["integration"] = {
            "success": integration_result["success"],
            "returncode": integration_result["returncode"]
        }
        
        # 4. Query Accuracy Tests
        print("\n📋 RUNNING QUERY ACCURACY TESTS...\n")
        accuracy_result = self.run_command("test_mcp_accuracy.py")
        self.results["accuracy"] = {
            "success": accuracy_result["success"],
            "details": self.parse_accuracy_results(accuracy_result.get("stdout", ""))
        }
        
        # 5. Performance Benchmark
        print("\n⚡ RUNNING PERFORMANCE BENCHMARK...\n")
        perf_output = self.tests_dir / "benchmark_results.json"
        perf_result = self.run_command(
            "benchmark_search.py",
            ["--queries", "30", "--output", str(perf_output)]
        )
        
        if perf_output.exists():
            with open(perf_output, 'r') as f:
                perf_data = json.load(f)
                self.results["performance"] = {
                    "success": True,
                    "mean_latency": perf_data.get("mean_latency"),
                    "queries_per_second": perf_data.get("queries_per_second"),
                    "p95_latency": perf_data.get("p95_latency")
                }
        else:
            self.results["performance"] = {
                "success": False,
                "error": "No benchmark output generated"
            }
        
        # 3. Quality Analysis
        print("\n📊 RUNNING QUALITY ANALYSIS...\n")
        quality_output = self.tests_dir / "quality_results.json"
        quality_result = self.run_command(
            "analyze_quality.py",
            ["--output", str(quality_output)]
        )
        
        if quality_output.exists():
            with open(quality_output, 'r') as f:
                quality_data = json.load(f)
                metrics = quality_data.get("metrics", {})
                self.results["quality"] = {
                    "success": True,
                    "precision_at_1": metrics.get("precision@1", {}).get("mean"),
                    "mrr": metrics.get("mrr", {}).get("mean"),
                    "ndcg": metrics.get("ndcg@10", {}).get("mean")
                }
        else:
            self.results["quality"] = {
                "success": False,
                "error": "No quality output generated"
            }
        
        # Determine overall status
        accuracy_ok = self.results["accuracy"]["success"]
        perf_ok = (self.results["performance"].get("mean_latency", 999) < 3.0)
        quality_ok = (self.results["quality"].get("precision_at_1", 0) > 0.3)
        
        if accuracy_ok and perf_ok and quality_ok:
            self.results["overall_status"] = "PASS"
        elif accuracy_ok:
            self.results["overall_status"] = "PARTIAL"
        else:
            self.results["overall_status"] = "FAIL"
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        # Accuracy
        print("\n📋 ACCURACY:")
        if self.results["accuracy"]["success"]:
            details = self.results["accuracy"]["details"]
            print(f"  Status: ✅ PASS")
            print(f"  Tests:  {details.get('passed', 0)}/{details.get('total', 0)} passed")
            print(f"  Rate:   {details.get('pass_rate', 0)*100:.1f}%")
        else:
            print(f"  Status: ❌ FAIL")
        
        # Performance
        print("\n⚡ PERFORMANCE:")
        if self.results["performance"]["success"]:
            mean_lat = self.results["performance"]["mean_latency"]
            qps = self.results["performance"]["queries_per_second"]
            p95 = self.results["performance"]["p95_latency"]
            
            status = "✅" if mean_lat < 2.0 else "⚠️"
            print(f"  Status:     {status}")
            print(f"  Avg Latency: {mean_lat*1000:.0f}ms")
            print(f"  P95 Latency: {p95*1000:.0f}ms")
            print(f"  QPS:        {qps:.1f}")
        else:
            print(f"  Status: ❌ FAIL")
        
        # Quality
        print("\n📊 QUALITY:")
        if self.results["quality"]["success"]:
            p1 = self.results["quality"]["precision_at_1"]
            mrr = self.results["quality"]["mrr"]
            ndcg = self.results["quality"]["ndcg"]
            
            status = "✅" if p1 > 0.5 else "⚠️"
            print(f"  Status:       {status}")
            print(f"  Precision@1:  {p1:.3f}")
            print(f"  MRR:          {mrr:.3f}")
            print(f"  NDCG@10:      {ndcg:.3f}")
        else:
            print(f"  Status: ❌ FAIL")
        
        # Overall
        print("\n" + "=" * 70)
        print("OVERALL STATUS:")
        if self.results["overall_status"] == "PASS":
            print("  ✅ ALL TESTS PASSED")
        elif self.results["overall_status"] == "PARTIAL":
            print("  ⚠️  SOME TESTS PASSED (Performance/Quality issues)")
        else:
            print("  ❌ TESTS FAILED")
        print("=" * 70)
    
    def save_report(self, output_file: str = "tests/test_report.json"):
        """Save test report to JSON."""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Full report saved to: {output_path}")


def main():
    """Main test runner."""
    runner = TestRunner()
    runner.run_all_tests()
    runner.print_summary()
    runner.save_report()
    
    # Exit with appropriate code
    sys.exit(0 if runner.results["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
