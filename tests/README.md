# Testing Framework

Comprehensive test suite for validating MCP server accuracy, performance, and quality.

## Quick Start

```bash
# Install dependencies (if not already done)
uv sync

# Build index (required before testing)
uv run scripts/build_index.py

# Quick sanity check (30 seconds)
uv run tests/smoke_test.py

# Run comprehensive test suite
uv run tests/run_comprehensive_tests.py

# Or run specific test suites
uv run tests/test_search_engine.py      # Core functionality tests
uv run tests/test_score_accuracy.py     # Score threshold validation
uv run tests/test_integration.py        # Integration tests
uv run tests/test_mcp_accuracy.py       # Query accuracy tests (40+ queries)
```

## Test Files

| File | Purpose | Runtime |
|------|---------|---------|
| `smoke_test.py` | ✨ **NEW** Quick sanity check (7 tests) | ~30 sec |
| `test_search_engine.py` | ✨ **NEW** Core functionality tests (20+ tests) | ~2-3 min |
| `test_score_accuracy.py` | ✨ **NEW** Score threshold validation | ~1-2 min |
| `test_integration.py` | ✨ **NEW** Integration & workflow tests | ~1-2 min |
| `test_mcp_accuracy.py` | Query accuracy tests (40+ queries) | ~2-3 min |
| `benchmark_search.py` | Performance benchmarks | ~1-2 min |
| `analyze_quality.py` | Quality metrics | ~3-5 min |
| `run_comprehensive_tests.py` | ✨ **NEW** Run all suites sequentially | ~8-10 min |
| `run_tests.py` | Legacy test runner | ~8-10 min |
| `test_cases.yaml` | Test case definitions (50+ queries) | - |
| `TESTING_GUIDE.md` | Full documentation | - |

## Individual Test Suites

### Core Functionality Tests (NEW)
```bash
uv run tests/test_search_engine.py
```
Comprehensive tests for:
- Basic search functionality
- Tech and component filters
- Hybrid scoring calculation
- BM25 and semantic search
- Edge cases (empty queries, special characters, long queries)
- Index statistics and chunk retrieval
- Score ranges and sorting

### Score Accuracy Tests (NEW)
```bash
uv run tests/test_score_accuracy.py
```
Validates score thresholds:
- Exact keyword match scores (BM25 > 0.6)
- Semantic similarity scores (Semantic > 0.7)
- Hybrid balance (0.4 BM25 + 0.6 Semantic)
- Score consistency across runs
- Relevance ordering

**Generates:** `score_accuracy_results.json`

### Query Accuracy Tests
```bash
uv run tests/test_mcp_accuracy.py
```
Validates that search returns relevant results for 40+ common queries across Django, DRF, and Psycopg.

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

**Core Functionality:**
- All tests should pass
- Hybrid scoring formula verified
- Both BM25 and semantic contributing

**Score Accuracy:**
- Exact matches: BM25 > 0.6, Hybrid > 0.5
- Semantic queries: Semantic > 0.7, Hybrid > 0.6
- Score consistency: < 0.001 difference
- Pass rate: > 90%

**Query Accuracy:**
- Pass rate: > 80%
- Top results contain expected keywords
- Tech filters working correctly

**Performance:**
- Mean latency: < 150ms
- P95 latency: < 300ms
- QPS: > 5

**Quality:**
- Precision@1: > 0.7
- MRR: > 0.8
- NDCG@10: > 0.6

## Test Output Files

Tests generate the following output files:

- `score_accuracy_results.json` - Detailed score validation results
- `comprehensive_test_results.json` - Overall test suite summary
- `benchmark_results.json` - Performance metrics

## Running Full Test Suite

```bash
# Run comprehensive tests (all test suites)
uv run tests/run_comprehensive_tests.py

# This runs in sequence:
# 1. Core functionality tests
# 2. Score accuracy tests  
# 3. Integration tests
# 4. Query accuracy tests (40+ queries)
```

## Customization

Edit `test_cases.yaml` to add your own test queries:

```yaml
- query: "Your custom query"
  expected_keywords: ["keyword1", "keyword2"]
  expected_tech: "django"
  min_score: 0.5
  top_k: 10
```

## Test Coverage

### Core Functionality (test_search_engine.py)
- ✅ Basic search
- ✅ Tech and component filters
- ✅ Hybrid scoring calculation (0.4 BM25 + 0.6 semantic)
- ✅ BM25 and semantic search independently
- ✅ top_k parameter
- ✅ Exact method name searches
- ✅ Natural language queries
- ✅ Cross-tech searches
- ✅ Empty and special character queries
- ✅ Index statistics
- ✅ Chunk retrieval
- ✅ Score ranges [0, 1]
- ✅ Result sorting by score

### Score Accuracy (test_score_accuracy.py)
- ✅ Exact keyword matches (BM25 > 0.6)
- ✅ Semantic similarity (Semantic > 0.7)
- ✅ Hybrid balance verification
- ✅ Score consistency across runs
- ✅ Relevance ordering

### Integration (test_integration.py)
- ✅ Full indexing flow
- ✅ Cross-tech workflows
- ✅ Filter combinations
- ✅ Search → retrieve workflow
- ✅ Tech-specific operations
- ✅ Concurrent searches
- ✅ Edge case handling

### Query Accuracy (test_mcp_accuracy.py)
- ✅ 40+ real-world developer queries
- ✅ Django ORM, auth, migrations
- ✅ DRF serializers, viewsets, permissions
- ✅ Psycopg connections, async, pooling
- ✅ Cross-tech queries
- ✅ Edge cases and comparisons

## Troubleshooting Tests

### Tests fail with "No results"
```bash
# Rebuild the index first
uv run scripts/build_index.py

# Then run tests
uv run tests/test_search_engine.py
```

### Score threshold failures
- Check if index is fully built
- Verify Elasticsearch and Qdrant are running
- Review score thresholds in test files (may need adjustment)

### Semantic scores are 0
- Restart Qdrant: `docker-compose restart qdrant`
- Rebuild index: `uv run scripts/build_index.py --force`
- Check Qdrant has vectors: `curl http://localhost:6333/collections/docs_collection`

## Full Documentation

See [`TESTING_GUIDE.md`](TESTING_GUIDE.md) for complete documentation.
