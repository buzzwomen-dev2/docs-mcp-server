# MCP Server Testing Guide

## Overview

Comprehensive testing framework for validating MCP server accuracy, performance, and quality.

## Test Suites

### 1. Accuracy Tests (`test_mcp_accuracy.py`)

Tests that search returns relevant results for 40 common development queries.

```bash
# Run accuracy tests
uv run tests/test_mcp_accuracy.py
```

**What it tests:**
- ✓ Results are returned for each query
- ✓ Expected keywords appear in top 3 results
- ✓ Tech filtering works correctly
- ✓ Hybrid scoring (BM25 + semantic) is functioning
- ✓ Score thresholds are met

**Expected results:**
- Pass rate: > 80%
- Issues indicate indexing or scoring problems

### 2. Performance Benchmark (`benchmark_search.py`)

Measures search latency and throughput.

```bash
# Run 30 queries with 3 warmup
uv run tests/benchmark_search.py --queries 30

# Filter by tech
uv run tests/benchmark_search.py --tech django --queries 20

# Save results
uv run tests/benchmark_search.py --output benchmark.json
```

**Metrics measured:**
- Mean/median/P95/P99 latency
- Queries per second
- Cold start time
- Memory usage patterns

**Good performance:**
- Mean latency: < 2 seconds
- P95 latency: < 3 seconds
- QPS: > 0.5

### 3. Quality Analysis (`analyze_quality.py`)

Calculates precision, recall, and ranking metrics.

```bash
# Analyze all test cases
uv run tests/analyze_quality.py

# Save detailed results
uv run tests/analyze_quality.py --output quality.json
```

**Metrics calculated:**
- **Precision@K** (K=1,3,5,10) - Relevance of top K results
- **MRR** (Mean Reciprocal Rank) - Position of first relevant result
- **NDCG** (Normalized DCG) - Quality of ranking

**Good quality:**
- Precision@1: > 0.7
- MRR: > 0.8
- NDCG@10: > 0.6

### 4. Full Test Suite (`run_tests.py`)

Runs all tests and generates comprehensive report.

```bash
# Run everything
uv run tests/run_tests.py
```

**Output:**
- Accuracy summary
- Performance metrics
- Quality scores
- Overall PASS/FAIL status
- JSON report saved to `tests/test_report.json`

## Test Cases

Test cases are defined in `tests/test_cases.yaml`. Each case includes:

```yaml
- query: "Django ORM transactions"
  description: "Test transaction docs"
  expected_keywords: ["transaction", "atomic", "database"]
  expected_tech: "django"
  min_score: 0.5
  top_k: 10
```

**Categories covered:**
- Django ORM (5 tests)
- Django Auth (5 tests)
- DRF Serializers (5 tests)
- DRF ViewSets (5 tests)
- Psycopg Connections (5 tests)
- Psycopg Async (5 tests)
- Cross-tech queries (5 tests)
- Edge cases (5 tests)

## Adding New Tests

1. Edit `tests/test_cases.yaml`:
```yaml
- query: "Your new query"
  description: "What you're testing"
  expected_keywords: ["keyword1", "keyword2"]
  expected_tech: "django"  # or null for cross-tech
  min_score: 0.4
  top_k: 10
```

2. Run tests:
```bash
uv run tests/test_mcp_accuracy.py
```

## Interpreting Results

### Accuracy Tests

```
✅ PASS - Top result matches expected keywords
❌ FAIL - Missing keywords/low score/wrong tech
```

**Common failures:**
- Missing keywords → Improve chunking or indexing
- Low scores → Adjust hybrid weights
- Wrong tech → Check metadata extraction

### Performance Benchmark

```
⭐⭐⭐ Excellent (< 1s average)
⭐⭐   Good (< 2s average)
⭐     Acceptable (< 3s average)
⚠️    Needs optimization (> 3s average)
```

**Optimization tips:**
- Use GPU: Set `CUDA_VISIBLE_DEVICES=0`
- Reduce chunk size: `CHUNK_SIZE_TOKENS=200`
- Smaller model: `EMBEDDING_MODEL=all-MiniLM-L6-v2`

### Quality Analysis

```
⭐⭐⭐ Excellent (P@1 > 0.7, MRR > 0.8)
⭐⭐   Good (P@1 > 0.5, MRR > 0.6)
⭐     Acceptable (P@1 > 0.3, MRR > 0.4)
⚠️    Needs Improvement
```

**Improvement tips:**
- Low Precision@1 → Adjust `BM25_WEIGHT` and `SEMANTIC_WEIGHT`
- Low MRR → Improve BM25 keyword matching
- Low NDCG → Better chunk boundaries

## Continuous Testing

### Pre-deployment checks:
```bash
# 1. Rebuild index
uv run scripts/build_index.py --clear

# 2. Run full test suite
uv run tests/run_tests.py

# 3. Check report
cat tests/test_report.json
```

### After configuration changes:
```bash
# Test specific impact
uv run tests/benchmark_search.py --queries 50
uv run tests/analyze_quality.py
```

### Adding new documentation:
```bash
# 1. Add docs to docs/ directory
# 2. Reindex
uv run scripts/build_index.py

# 3. Verify with targeted test
# Edit test_cases.yaml with new query
uv run tests/test_mcp_accuracy.py
```

## Troubleshooting

### Tests fail to import modules
```bash
# Install dependencies
uv sync

# Ensure pyproject.toml includes pyyaml
```

### "Index is empty" error
```bash
# Build index first
uv run scripts/build_index.py
```

### Slow test execution
```bash
# Reduce query count
uv run tests/benchmark_search.py --queries 10

# Skip quality analysis (slowest)
uv run tests/test_mcp_accuracy.py
```

### Inconsistent results
```bash
# Clear and rebuild index
uv run scripts/build_index.py --clear

# Run tests again
uv run tests/run_tests.py
```

## CI/CD Integration

Example GitHub Actions:

```yaml
- name: Run MCP Tests
  run: |
    uv sync
    uv run scripts/build_index.py
    uv run tests/run_tests.py
```

Exit codes:
- `0` - All tests pass
- `1` - Tests failed

## Performance Baselines

**Typical results** (15K chunks, CPU):
- Initialization: 5-10s
- First query: 1-2s (cold start)
- Subsequent queries: 0.5-1.5s
- Precision@1: 0.6-0.8
- MRR: 0.7-0.9

**With GPU** (CUDA):
- First query: 0.5-1s
- Subsequent: 0.1-0.5s

## Related Files

- `tests/test_mcp_accuracy.py` - Accuracy test suite
- `tests/benchmark_search.py` - Performance benchmark
- `tests/analyze_quality.py` - Quality metrics
- `tests/run_tests.py` - Test orchestrator
- `tests/test_cases.yaml` - Test case definitions
- `tests/test_report.json` - Latest test results (generated)
