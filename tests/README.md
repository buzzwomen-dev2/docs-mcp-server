# Testing Framework

Comprehensive test suite for validating MCP server accuracy, performance, and quality.

## Quick Start

```bash
# Install dependencies (if not already done)
uv sync

# Build index (required before testing)
uv run scripts/build_index.py

# Run all tests
uv run tests/run_tests.py
```

## Test Files

| File | Purpose | Runtime |
|------|---------|---------|
| `test_mcp_accuracy.py` | Accuracy tests (40 queries) | ~2-3 min |
| `benchmark_search.py` | Performance benchmarks | ~1-2 min |
| `analyze_quality.py` | Quality metrics | ~3-5 min |
| `run_tests.py` | Run all suites | ~8-10 min |
| `test_cases.yaml` | Test case definitions | - |
| `TESTING_GUIDE.md` | Full documentation | - |

## Individual Tests

### Accuracy Tests
```bash
uv run tests/test_mcp_accuracy.py
```
Validates that search returns relevant results for common queries.

### Performance Benchmark
```bash
uv run tests/benchmark_search.py --queries 30
```
Measures latency, throughput, and resource usage.

### Quality Analysis
```bash
uv run tests/analyze_quality.py
```
Calculates Precision@K, MRR, and NDCG metrics.

## Expected Results

**Accuracy:**
- Pass rate: > 80%
- Failed tests indicate indexing issues

**Performance:**
- Mean latency: < 2s
- P95 latency: < 3s
- QPS: > 0.5

**Quality:**
- Precision@1: > 0.7
- MRR: > 0.8
- NDCG@10: > 0.6

## Customization

Edit `test_cases.yaml` to add your own queries:

```yaml
- query: "Your custom query"
  expected_keywords: ["keyword1", "keyword2"]
  expected_tech: "django"
  min_score: 0.5
```

## Full Documentation

See [`TESTING_GUIDE.md`](TESTING_GUIDE.md) for complete documentation.
