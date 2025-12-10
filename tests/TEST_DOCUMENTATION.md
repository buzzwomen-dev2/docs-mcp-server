# Test Suite Documentation

## Overview

Comprehensive testing framework for the MCP Docs Server with focus on search accuracy, score validation, and system integration.

## Test Structure

```
tests/
├── smoke_test.py                    # Quick health check (7 tests, 30s)
├── test_search_engine.py            # Core functionality (20+ tests, 2-3min)
├── test_score_accuracy.py           # Score validation (15+ tests, 1-2min)
├── test_integration.py              # Workflows & integration (7+ tests, 1-2min)
├── test_mcp_accuracy.py             # Query accuracy (50+ queries, 2-3min)
├── run_comprehensive_tests.py       # Run all tests sequentially
├── test_cases.yaml                  # Test query definitions
└── README.md                        # Quick reference
```

## Quick Commands

```bash
# Fastest check (30 seconds)
uv run tests/smoke_test.py

# Comprehensive testing (8-10 minutes)
uv run tests/run_comprehensive_tests.py

# Individual suites
uv run tests/test_search_engine.py
uv run tests/test_score_accuracy.py
uv run tests/test_integration.py
uv run tests/test_mcp_accuracy.py
```

## Test Coverage

### 1. Smoke Test (`smoke_test.py`)

Fast sanity check covering essential functionality:

✅ **Index Status**: Verifies index has data
✅ **Basic Search**: Tests search returns results
✅ **BM25 Scores**: Validates BM25 scoring works
✅ **Semantic Scores**: Validates semantic scoring works
✅ **Hybrid Formula**: Verifies 0.4*BM25 + 0.6*Semantic
✅ **Tech Filter**: Tests technology filtering
✅ **Chunk Retrieval**: Tests retrieving specific chunks

**When to use**: Before every development session, after index rebuilds, in CI/CD

### 2. Core Functionality Tests (`test_search_engine.py`)

Comprehensive testing of IndexManager functionality:

**Search Tests:**
- Basic search returns results
- Tech filter (django/drf/psycopg)
- Component filter
- top_k parameter limiting
- Cross-tech searches
- Empty query handling
- Special characters in queries
- Very long queries

**Scoring Tests:**
- Hybrid scoring calculation
- BM25 scores not zero
- Semantic scores not zero
- Score ranges [0, 1]
- Results sorted by score descending

**Query Types:**
- Exact method names (get_or_create, select_related)
- Natural language queries
- Technical keywords
- Comparison queries (vs, versus)

**System Tests:**
- Index statistics
- Source file listing
- Chunk retrieval by ID

**Expected**: All tests pass, 100% success rate

### 3. Score Accuracy Tests (`test_score_accuracy.py`)

Validates search scores meet quality thresholds:

**Exact Match Tests:**
- ForeignKey, ModelSerializer, AsyncConnection
- BM25 score > 0.6
- Hybrid score > 0.5

**Semantic Similarity Tests:**
- Natural language queries
- Semantic score > 0.7
- Hybrid score > 0.6

**Hybrid Balance Tests:**
- Verifies formula: 0.4*BM25 + 0.6*Semantic
- Both scores contribute (> 0)

**Consistency Tests:**
- Same query returns same scores
- Difference < 0.001

**Ordering Tests:**
- Relevant queries score higher than irrelevant

**Output**: `score_accuracy_results.json`

**Expected**: >90% pass rate, some variation acceptable

### 4. Integration Tests (`test_integration.py`)

End-to-end workflow validation:

**Workflows:**
- Full indexing flow
- Cross-tech search workflows
- Filter combination testing
- Search → retrieve workflow
- Concurrent searches (5 simultaneous)
- Edge case handling

**Tech-Specific:**
- Tech filter isolation
- Component filtering
- Multi-technology results

**Expected**: All workflows complete successfully

### 5. Query Accuracy Tests (`test_mcp_accuracy.py`)

Real-world developer query validation:

**50+ Test Queries Covering:**

**Django (20+ queries):**
- ORM (transactions, relationships, querysets, fields)
- Authentication (middleware, permissions, passwords, sessions)
- Migrations (create, apply)
- Custom user models

**DRF (15+ queries):**
- Serializers (validation, nested, fields)
- ViewSets (routing, permissions, actions)
- Pagination and filtering

**Psycopg (10+ queries):**
- Connections (DSN, pooling, context managers)
- Async API (AsyncConnection, AsyncCursor)
- Transactions and cursors

**Cross-tech (5+ queries):**
- Connection pooling
- API authentication
- ORM optimization
- Middleware

**Validation Criteria:**
- Results exist
- Top score > min_score threshold
- Expected keywords in top 5 results
- Tech filter working
- No hybrid scoring errors

**Expected**: >80% pass rate

## Score Thresholds

### BM25 Scores (Keyword Matching)
- **Exact matches** (ForeignKey): > 0.6
- **Keywords** (middleware): > 0.5
- **Multi-word** (transaction commit): > 0.4

### Semantic Scores (Conceptual)
- **Natural language** (How to...): > 0.7
- **Technical concepts**: > 0.6
- **General queries**: > 0.5

### Hybrid Scores (Combined)
- **Exact + conceptual**: > 0.6
- **Good matches**: > 0.5
- **Acceptable**: > 0.4
- **Minimum**: > 0.3

## Test Data Requirements

**Before running tests:**

```bash
# Build complete index
uv run scripts/build_index.py

# Verify index stats
uv run python -c "
import asyncio
from search_engine import IndexManager

async def check():
    m = IndexManager()
    await m.initialize()
    stats = await m.get_stats()
    print(f'Chunks: {stats[\"total_chunks\"]}')
    print(f'Technologies: {stats[\"technologies\"]}')

asyncio.run(check())
"
```

**Expected Index Stats:**
- Total chunks: > 20,000
- Technologies: django, drf, psycopg
- Django chunks: > 15,000
- DRF chunks: > 3,000
- Psycopg chunks: > 2,000

## Interpreting Results

### Smoke Test

**All Pass**: System healthy, proceed with development
**1-2 Fail**: Minor issues, check specific failures
**3+ Fail**: Major problems, rebuild index or restart services

### Core Functionality

**100% Pass**: System working correctly
**90-99% Pass**: Check specific failures, may be acceptable
**<90% Pass**: Serious issues, investigate thoroughly

### Score Accuracy

**>95% Pass**: Excellent scoring accuracy
**85-95% Pass**: Good, minor tuning may help
**80-85% Pass**: Acceptable, consider weight adjustments
**<80% Pass**: Poor accuracy, check index quality

### Query Accuracy

**>85% Pass**: Excellent search quality
**75-85% Pass**: Good quality
**65-75% Pass**: Acceptable, some queries problematic
**<65% Pass**: Poor quality, investigate index or queries

## Troubleshooting

### No Results in Tests

```bash
# Check index exists
uv run scripts/build_index.py

# Verify services
docker ps | grep -E "elasticsearch|qdrant"

# Check Elasticsearch
curl http://localhost:9200/docs_index/_count

# Check Qdrant
curl http://localhost:6333/collections/docs_collection
```

### Semantic Scores All Zero

```bash
# Restart Qdrant
docker-compose restart qdrant

# Rebuild with vectors
uv run scripts/build_index.py --force

# Verify vectors exist
curl http://localhost:6333/collections/docs_collection | grep vectors_count
```

### Score Thresholds Too Strict

If tests fail due to score thresholds:

1. Check if it's consistent across similar queries
2. Review actual scores in test output
3. Adjust thresholds in test files if scores are close
4. Consider if hybrid weights need tuning

### Tests Hang or Timeout

```bash
# Check service health
docker-compose ps

# Check logs
docker-compose logs elasticsearch
docker-compose logs qdrant

# Restart services
docker-compose restart
```

## Continuous Integration

Recommended CI pipeline:

```yaml
test:
  script:
    - docker-compose up -d
    - uv sync
    - uv run scripts/build_index.py
    - uv run tests/smoke_test.py
    - uv run tests/run_comprehensive_tests.py
  artifacts:
    - tests/*_results.json
```

## Performance Expectations

**Test Runtimes:**
- Smoke test: 30 seconds
- Core functionality: 2-3 minutes
- Score accuracy: 1-2 minutes
- Integration: 1-2 minutes
- Query accuracy: 2-3 minutes
- Full suite: 8-10 minutes

**System Resources:**
- Memory: < 2GB during tests
- CPU: Moderate (embedding generation)
- Disk: Minimal I/O

## Adding New Tests

### To test_search_engine.py:
```python
@pytest.mark.asyncio
async def test_new_feature(self):
    """Test description."""
    results = await self.manager.search("query")
    assert len(results) > 0
    print("✓ Test passed")
```

### To test_score_accuracy.py:
```python
# Add to test_cases list
{
    "query": "test query",
    "tech": "django",
    "min_bm25": 0.6,
    "min_hybrid": 0.5,
    "description": "Test description"
}
```

### To test_cases.yaml:
```yaml
- query: "new test query"
  description: "Test description"
  expected_keywords: ["keyword1", "keyword2"]
  expected_tech: "django"
  min_score: 0.5
  top_k: 10
```

## Test Maintenance

**Regular Tasks:**
- Update test_cases.yaml with new query patterns
- Adjust score thresholds based on model changes
- Add regression tests for bugs
- Review and update expected keyword lists

**After Code Changes:**
- Run smoke test immediately
- Run affected test suites
- Update tests if behavior intentionally changed
- Document threshold changes

## Contact & Support

For test failures or questions:
1. Check test output for specific failures
2. Review this documentation
3. Check main README troubleshooting section
4. Open issue with test output and logs
