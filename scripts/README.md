# Utility Scripts

Helper scripts for managing the documentation search server:

## Management Scripts

- **build_index.py** - Index builder for documentation files
  ```bash
  uv run scripts/build_index.py              # Index all docs
  uv run scripts/build_index.py --tech django # Index specific tech
  uv run scripts/build_index.py --clear       # Clear and rebuild
  ```

- **test_setup.py** - Validation script to verify installation and setup
  ```bash
  uv run scripts/test_setup.py
  ```

## Testing Framework

See `tests/` directory for comprehensive testing tools:

- **tests/test_mcp_accuracy.py** - Accuracy tests (40 test cases)
- **tests/benchmark_search.py** - Performance benchmarks
- **tests/analyze_quality.py** - Quality metrics (precision, MRR, NDCG)
- **tests/run_tests.py** - Run all test suites

Quick test:
```bash
# Run all tests
uv run tests/run_tests.py

# Run specific suite
uv run tests/test_mcp_accuracy.py
```
