#!/usr/bin/env python3
"""
Comprehensive Test Runner

Runs all test suites in sequence and generates a comprehensive report.
"""

import asyncio
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json


class ComprehensiveTestRunner:
    """Run all test suites and generate report."""
    
    def __init__(self):
        self.tests_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "suites": {}
        }
    
    def run_test_suite(self, script_name: str, suite_name: str) -> dict:
        """Run a single test suite."""
        print(f"\n{'='*70}")
        print(f"RUNNING: {suite_name}")
        print(f"{'='*70}\n")
        
        cmd = ["uv", "run", str(self.tests_dir / script_name)]
        
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
            print(f"❌ Error running {script_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Run all test suites."""
        print("=" * 70)
        print("COMPREHENSIVE MCP SERVER TEST SUITE")
        print("=" * 70)
        print(f"Started at: {self.results['timestamp']}")
        print("=" * 70)
        
        test_suites = [
            ("test_search_engine.py", "Core Functionality Tests"),
            ("test_score_accuracy.py", "Score Accuracy Tests"),
            ("test_integration.py", "Integration Tests"),
            ("test_mcp_accuracy.py", "Query Accuracy Tests (40+ queries)"),
        ]
        
        for script, name in test_suites:
            result = self.run_test_suite(script, name)
            self.results["suites"][name] = {
                "success": result["success"],
                "returncode": result.get("returncode", -1)
            }
        
        # Generate summary
        self.print_summary()
        
        # Save results
        self.save_results()
    
    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        total_suites = len(self.results["suites"])
        passed_suites = sum(1 for s in self.results["suites"].values() if s["success"])
        failed_suites = total_suites - passed_suites
        
        print(f"\nTest Suites Run: {total_suites}")
        print(f"Passed: {passed_suites}")
        print(f"Failed: {failed_suites}")
        
        print("\nDetailed Results:")
        for suite_name, result in self.results["suites"].items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"  {status} - {suite_name}")
        
        # Overall status
        if failed_suites == 0:
            print("\n🎉 ALL TEST SUITES PASSED!")
            self.results["overall_status"] = "PASS"
        else:
            print(f"\n⚠️  {failed_suites} TEST SUITE(S) FAILED")
            self.results["overall_status"] = "FAIL"
    
    def save_results(self):
        """Save results to JSON."""
        output_file = self.tests_dir / "comprehensive_test_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📊 Results saved to: {output_file}")


def main():
    """Main entry point."""
    runner = ComprehensiveTestRunner()
    runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if runner.results["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
