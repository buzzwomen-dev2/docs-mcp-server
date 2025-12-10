# Docs MCP Server - Hybrid Search for Technical Documentation

A high-performance **Model Context Protocol (MCP) server** that provides hybrid search capabilities combining:
- **Semantic search** using FastEmbed (BAAI/bge-small-en-v1.5) + Qdrant vector database
- **Keyword search** using Elasticsearch BM25 with inverted index
- **Weighted fusion** (0.4 BM25 + 0.6 semantic by default)

Designed for local developer documentation search across Django, Django REST Framework, Psycopg, and other technical docs.

## Prerequisites

This server requires **Elasticsearch** and **Qdrant** to be running. The easiest way is using Docker:

### Option 1: Using Docker Compose (Recommended)

```bash
# Start services (Elasticsearch + Qdrant)
./start-services.sh

# Stop services
./stop-services.sh
```

The script will:
- Start Elasticsearch on port 9200
- Start Qdrant on port 6333
- Wait for both services to be healthy
- Persist data in Docker volumes

### Option 2: Manual Docker Commands

```bash
# Elasticsearch
docker run -d \
  --name docs-elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.11.0

# Qdrant
docker run -d \
  --name docs-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant
```

### Option 3: Native Installation

- **Elasticsearch**: https://www.elastic.co/downloads/elasticsearch
- **Qdrant**: https://qdrant.tech/documentation/quick-start/

## Features

- 🔍 **Hybrid Search**: Combines semantic understanding with keyword precision
- 🏷️ **Rich Metadata**: Auto-tags documents by tech, component, topic, version
- 📊 **Structured Results**: Pydantic models with individual and combined scores
- 🚀 **Dual Interface**: MCP tools + REST API
- 💾 **Persistent Index**: Elasticsearch + Qdrant with disk-based metadata cache
- 📝 **Smart Chunking**: Semantic for prose (~100 tokens), structural for code (80-150 lines)
- 🔒 **Localhost-only**: Secure by default, no external access
- ⚡ **Fast Embeddings**: CPU-optimized FastEmbed (no GPU required)

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Build the Search Index

First time setup - index your documentation:

```bash
# Use the build script (recommended)
uv run scripts/build_index.py

# Or index programmatically
uv run python -c "
import asyncio
from pathlib import Path
from search_engine import IndexManager

async def main():
    manager = IndexManager()
    stats = await manager.index_documents([Path('docs')])
    print(f'Indexed {stats["chunks_created"]} chunks from {stats["files_processed"]} files')

asyncio.run(main())
"
```

Or use the MCP tool after starting the server (see below).

### 3. Run the Server

#### As MCP Server (stdio)

```bash
uv run server.py
```

Then configure in your MCP client (Claude Desktop, VSCode, etc):

```json
{
  "mcpServers": {
    "docs-server": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/path/to/docs-mcp-server"
    }
  }
}
```

#### As HTTP API Server

```bash
uv run server.py --http
```

Access at:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### 4. Validate Setup

```bash
# Run validation script
uv run scripts/test_setup.py
```

### 5. Test with MCP Inspector

```bash
# In one terminal: start server
uv run server.py

# In another terminal: start inspector
npx @modelcontextprotocol/inspector uv run server.py
```

Navigate to `http://localhost:5173` and test the tools.

## MCP Features

This server implements the full MCP specification with **Tools**, **Resources**, and **Prompts**.

### Tools

#### `search`
Hybrid search with semantic + keyword matching.

**Parameters:**
- `query` (required): Search query text
- `tech` (optional): Filter by technology (django/drf/psycopg)
- `component` (optional): Filter by component/module
- `top_k` (default 10): Number of results

**Example:**
```python
search(
    query="How does Django auth middleware work?",
    tech="django",
    top_k=5
)
```

**Returns:** List of `SearchResultModel` with:
- `chunk_id`: Unique identifier
- `content`: Chunk text (truncated to 500 chars)
- `source_path`: Original file path
- `tech`, `component`, `topic`, `version`, `file_type`: Metadata
- `bm25_score`, `semantic_score`, `hybrid_score`: Individual and combined scores

### `retrieve`
Fetch a specific chunk by ID.

**Parameters:**
- `chunk_id` (required): From search results

**Returns:** Full `SearchResultModel` with complete content.

### `reindex_docs`
Build or rebuild the search index. Uses checksums to skip unchanged files.

**Parameters:**
- `paths` (optional): Specific file/directory paths to index
- `tech` (optional): Index specific technology (django/drf/psycopg)

**Examples:**
```python
# Reindex all docs (incremental - skips unchanged)
reindex_docs()

# Index only Django docs
reindex_docs(tech="django")

# Index specific paths
reindex_docs(paths=["docs/django-6.0/ref"])
```

**Returns:** Statistics with `files_processed`, `chunks_created`, `errors`.

**Note:** This performs incremental updates by default. To force a complete rebuild, use the build script with `--force` flag.

### `get_index_stats`
Get index statistics and health.

**Returns:** `IndexStats` with chunk counts, model info, technologies, etc.

### `list_sources`
List all indexed source files.

**Parameters:**
- `tech` (optional): Filter by technology

**Returns:** List of `SourceInfo` with file metadata and chunk counts.

### `search_docs` (deprecated)
Legacy keyword-only search. Use `search` instead for better results.

### `list_docs`
Show directory structure for a technology.

### `list_technologies`
List available documentation sets.

### Resources

MCP resources provide direct access to documentation for use as context:

#### `doc://{tech}/{path}`
Access raw documentation files:
```
doc://django/ref/models/fields.md
doc://drf/api-guide/serializers.md
```

#### `chunk://{chunk_id}`
Access indexed chunks from search results:
```
chunk://middleware_3_1234
```

**Usage in VS Code**: Select **Add Context** > **MCP Resources** in Chat view.

### Prompts

Preconfigured search prompts available as slash commands:

- `/mcp.docsSearch.find_authentication_docs` - Authentication & authorization docs
- `/mcp.docsSearch.find_database_docs` - Database & ORM documentation  
- `/mcp.docsSearch.find_api_docs` - API & serialization docs

Each prompt accepts a `tech` parameter (django/drf/psycopg).

**Usage in VS Code**: Type `/` in chat input to see available MCP prompts.

## REST API Endpoints

All endpoints bind to `127.0.0.1:8000` (localhost only).

### `POST /search`
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Django middleware authentication",
    "tech": "django",
    "top_k": 10
  }'
```

### `GET /retrieve/{chunk_id}`
```bash
curl http://localhost:8000/retrieve/middleware_3_1234
```

### `GET /status`
```bash
curl http://localhost:8000/status
```

### `GET /sources?tech=django`
```bash
curl http://localhost:8000/sources?tech=django
```

### `POST /reindex`
```bash
curl -X POST http://localhost:8000/reindex \
  -H "Content-Type: application/json" \
  -d '{"tech": "django"}'
```

## Configuration

### Environment Variables

All configuration is managed via environment variables. Set these before running the server or build script.

#### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `INDEX_DIR` | `.index` | Directory for metadata cache (checksums, pickled data) |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | FastEmbed model for semantic embeddings |
| `CHUNK_SIZE_TOKENS` | `100` | Target chunk size in tokens for semantic splitting |

#### Search Weights

| Variable | Default | Description |
|----------|---------|-------------|
| `BM25_WEIGHT` | `0.4` | Weight for BM25 keyword scores (0.0-1.0) |
| `SEMANTIC_WEIGHT` | `0.6` | Weight for semantic similarity scores (0.0-1.0) |

> **Note:** Weights should sum to 1.0. Increase BM25 for keyword-heavy queries, increase semantic for concept matching.

#### Elasticsearch Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ES_HOST` | `http://localhost:9200` | Elasticsearch server URL |
| `ES_INDEX_NAME` | `docs_index` | Index name for BM25 documents |

#### Qdrant Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant gRPC port |
| `QDRANT_COLLECTION` | `docs_collection` | Collection name for vector embeddings |

#### Redis Configuration (Prepared, Not Yet Used)

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis server host (for future caching) |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_ENABLED` | `false` | Enable Redis caching (currently unused) |

### Build Script Flags

The `scripts/build_index.py` script supports the following command-line flags:

#### Index Building

```bash
# Index all documentation
uv run scripts/build_index.py

# Index specific technology
uv run scripts/build_index.py --tech django
uv run scripts/build_index.py --tech drf
uv run scripts/build_index.py --tech psycopg

# Force reindex (ignore checksums, rebuild everything)
uv run scripts/build_index.py --force

# Index specific paths
uv run scripts/build_index.py --paths docs/django-6.0/ref docs/django-6.0/topics
```

#### Clear Index

```bash
# Clear ALL documentation from index
uv run scripts/build_index.py --clear

# Clear specific technology only (keeps others intact)
uv run scripts/build_index.py --tech django --clear
uv run scripts/build_index.py --tech drf --clear
```

> **Warning:** `--clear` without `--tech` will delete ALL indexed documentation. Use `--tech` flag to selectively clear.

#### Combined Operations

```bash
# Clear Django docs and reindex them
uv run scripts/build_index.py --tech django --clear
uv run scripts/build_index.py --tech django

# Force rebuild specific technology
uv run scripts/build_index.py --tech drf --force
```

### Configuration Examples

**High semantic weight for conceptual queries:**
```bash
export BM25_WEIGHT=0.3
export SEMANTIC_WEIGHT=0.7
uv run server.py
```

**High BM25 weight for exact keyword matching:**
```bash
export BM25_WEIGHT=0.7
export SEMANTIC_WEIGHT=0.3
uv run server.py
```

**Custom embedding model:**
```bash
export EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2"
uv run server.py
```

**Larger chunks for more context:**
```bash
export CHUNK_SIZE_TOKENS=200
uv run scripts/build_index.py --force  # Rebuild with new chunk size
```

**Custom Elasticsearch instance:**
```bash
export ES_HOST="http://192.168.1.100:9200"
export ES_INDEX_NAME="my_docs"
python server.py
```

## Example Queries

Tune your hybrid weights based on these common developer queries:

```
"How does Django auth middleware work?"
"What is the DRF request lifecycle?"
"Configure Nuxt SSR"
"Redis cache invalidation flow"
"psycopg transaction patterns"
"Django model field options"
"DRF serializer validation"
```

## Architecture

```
┌─────────────────┐
│   MCP Client    │  (Claude, VSCode, etc)
│  or HTTP Client │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   server.py     │  FastMCP + FastAPI
│   (Tools/API)   │  • Lifespan context manager
│                 │  • Context[ServerSession, AppContext]
│                 │  • Structured Pydantic outputs
└────────┬────────┘
         │
         v
┌────────────────────────────────────────┐
│         search_engine.py                 │
│         (IndexManager)                   │
│  ┌──────────────┐   ┌───────────────┐ │
│  │ Elasticsearch │   │    Qdrant     │ │
│  │  BM25 Index  │   │ Vector Index │ │
│  │  (Inverted)  │   │    (HNSW)    │ │
│  └──────────────┘   └───────────────┘ │
│           │                  │          │
│           v                  v          │
│      ┌────────────────────────┐   │
│      │   FastEmbed (CPU)      │   │
│      │ bge-small-en-v1.5    │   │
│      │    384-dim vectors    │   │
│      └────────────────────────┘   │
└────────────────────────────────────────┘
         │
         v
    ┌─────────┐
    │ .index/ │  (Metadata cache)
    └─────────┘
```

**Implementation Notes:**
- **Lifespan Management**: IndexManager initialized once via `@asynccontextmanager` and injected into tool context
- **Context Pattern**: Tools receive `Context[ServerSession, AppContext]` for accessing shared state
- **Structured Output**: All results returned as validated Pydantic models
- **Security**: Localhost-only binding, query logging for monitoring

## Document Sources

Current documentation sets in `docs/`:

- **Django 6.0** (~300 files): Models, views, ORM, middleware, admin
- **Django REST Framework 3.16.1** (~30 files): Serializers, views, authentication
- **Psycopg 3.3.1** (~20 files): PostgreSQL adapter, connection pooling

Supports: `.md`, `.txt`, `.rst`, `.py`, `.json`, `.yaml`, `.yml`, `.html`

## Performance

### Initial Indexing

- **350-400 files → 2-5 minutes**
- Generates embeddings (384-dim FastEmbed with CPU optimization)
- Builds Elasticsearch BM25 inverted index + Qdrant HNSW vector index
- **Memory usage:** ~500MB-1GB peak during embedding generation
- **Disk usage:** ~50-100MB for `.index/` cache + Qdrant vectors

### Incremental Updates

The system uses checksums to detect file changes and skip reindexing unchanged files:

```bash
# First run: indexes all files
uv run scripts/build_index.py
# Processing 350 files...

# Second run: skips unchanged files
uv run scripts/build_index.py
# Skipped 350 files (unchanged)

# After modifying one file
uv run scripts/build_index.py
# Skipped 349 files (unchanged)
# Processing 1 file...
```

**Checksum behavior:**
- Saved incrementally every 10 files to prevent loss on crashes
- Stored in `.index/checksums.json`
- Use `--force` flag to bypass checksum validation and rebuild everything

### Search Latency

- **Semantic search (Qdrant):** ~50-100ms (HNSW index lookup)
- **BM25 search (Elasticsearch):** ~10-20ms (inverted index)
- **Hybrid fusion:** ~5ms (score normalization and combination)
- **Total per query:** ~100-150ms

### Optimizations Implemented

1. **Batched Processing:**
   - Embeddings: 50 chunks per batch (prevents OOM)
   - Qdrant uploads: 100 points per batch
   - Elasticsearch indexing: 500 documents per batch

2. **Concurrent Operations:**
   - Separate read/write locks allow searches during indexing
   - Async I/O for all network operations

3. **Resource Management:**
   - Disk space check before cache writes (1GB minimum)
   - Rate limiting between batches (0.1s delays)
   - Incremental checkpoint saving

4. **Memory Efficiency:**
   - Streaming file processing
   - Batch cleanup after processing
   - No GPU required (FastEmbed CPU-optimized)

### System Requirements

- **CPU:** Modern multi-core (4+ cores recommended)
- **RAM:** 2GB minimum, 4GB recommended
- **Disk:** 500MB free for indices and cache
- **Services:**
  - Elasticsearch 8.x+ on localhost:9200
  - Qdrant 1.x+ on localhost:6333
- **GPU:** Not required (FastEmbed uses CPU)

## Troubleshooting

### Docker Services Not Running

**Symptom:** Connection errors to Elasticsearch or Qdrant

**Solution:**
```bash
# Check service status
docker ps

# Start services if not running
docker-compose up -d

# Check logs
docker-compose logs elasticsearch
docker-compose logs qdrant
```

### Index is Empty

**Symptom:** `get_index_stats` shows 0 chunks

**Solutions:**
```bash
# Check status via REST API
curl http://localhost:8000/status

# Rebuild index manually
uv run scripts/build_index.py

# Or via Python
uv run python -c "
import asyncio
from pathlib import Path
from search_engine import IndexManager

asyncio.run(IndexManager().index_documents([Path('docs')]))
"
```

### Build Script Crashes (Exit 143 / SIGTERM)

**Symptom:** Indexing process terminates with `Exit Code 143` or runs out of memory

**Causes:**
- System OOM (Out Of Memory) killer terminating process
- Insufficient RAM for large batch processing

**Solutions:**
1. **Reduce batch sizes** (already optimized in current version):
   - Embeddings: 50 chunks per batch
   - Qdrant: 100 points per batch  
   - Elasticsearch: 500 documents per batch

2. **Close memory-intensive applications** during indexing

3. **Monitor memory usage:**
   ```bash
   # Watch memory in real-time
   watch -n 1 free -h
   
   # Monitor indexing process
   ps aux | grep build_index
   ```

4. **Index in smaller batches:**
   ```bash
   # Index one technology at a time
   uv run scripts/build_index.py --tech django
   uv run scripts/build_index.py --tech drf
   uv run scripts/build_index.py --tech psycopg
   ```

### Semantic Search Returns All Scores = 0

**Symptom:** Search results show `semantic_score: 0.0` for all results

**Causes:**
- Qdrant vectors not properly indexed
- Stale MCP client cache
- Server not restarted after reindexing

**Solutions:**
1. **Restart the server:**
   ```bash
   # Stop server (Ctrl+C)
   # Restart
   uv run server.py
   ```

2. **Verify Qdrant has vectors:**
   ```bash
   curl http://localhost:6333/collections/docs_collection
   # Check "points_count" > 0 and "vectors_count" > 0
   ```

3. **Test semantic search directly:**
   ```bash
   uv run python -c "
import asyncio
from search_engine import IndexManager

async def test():
    manager = IndexManager()
    await manager.initialize()
    results = await manager.search('Django authentication', top_k=5)
    for r in results:
        print(f'Semantic: {r.semantic_score}, BM25: {r.bm25_score}')

asyncio.run(test())
   "
   ```

4. **Rebuild Qdrant collection:**
   ```bash
   uv run scripts/build_index.py --clear
   uv run scripts/build_index.py
   ```

### Accidentally Cleared All Documentation

**Symptom:** Used `--tech X --clear` expecting to clear only technology X, but all docs were deleted

**Cause:** Older versions of the script had incorrect clear logic

**Current Behavior (Fixed):**
- `--clear` alone: Clears ALL documentation
- `--tech django --clear`: Clears ONLY Django docs, keeps DRF and Psycopg
- `--tech drf --clear`: Clears ONLY DRF docs

**Recovery:**
```bash
# Reindex everything
uv run scripts/build_index.py

# Or reindex specific techs
uv run scripts/build_index.py --tech django
uv run scripts/build_index.py --tech drf
uv run scripts/build_index.py --tech psycopg
```

### Poor Search Quality

**Symptom:** Results don't match expectations or miss relevant documents

**Solutions:**

1. **Check query log** at `.index/search_queries.log` to see how queries are being processed

2. **Tune hybrid search weights:**
   - **Keyword-heavy queries** (exact terms, function names): Increase `BM25_WEIGHT`
     ```bash
     export BM25_WEIGHT=0.7
     export SEMANTIC_WEIGHT=0.3
     ```
   - **Conceptual queries** (how to, best practices): Increase `SEMANTIC_WEIGHT`
     ```bash
     export BM25_WEIGHT=0.3
     export SEMANTIC_WEIGHT=0.7
     ```

3. **Try different embedding models:**
   ```bash
   # Larger, more accurate (slower)
   export EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2"
   
   # Smaller, faster (less accurate)
   export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
   
   # Rebuild with new model
   uv run scripts/build_index.py --force
   ```

4. **Increase result count:**
   ```python
   search(query="...", top_k=20)  # Default is 10
   ```

### Disk Space Issues

**Symptom:** Index building fails with disk write errors

**Cause:** Insufficient disk space for metadata cache writes

**Solution:**
- The system checks for minimum 1GB free space before writing caches
- Free up disk space if needed:
  ```bash
  df -h  # Check available space
  docker system prune  # Clean Docker artifacts
  ```

### Embeddings Taking Too Long

**Solutions:**
- FastEmbed is already CPU-optimized and batched (50 chunks at a time)
- Try smaller model: `export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"`
- Verify Elasticsearch and Qdrant are running: `docker ps`
- Check CPU usage isn't bottlenecked: `top` or `htop`

### Missing Await Errors

**Symptom:** `RuntimeWarning: coroutine 'get_stats' was never awaited`

**Cause:** Async functions called without `await`

**Solution:** Already fixed in current version. All async calls properly awaited:
```python
# Correct (current version)
stats = await manager.get_stats()

# Incorrect (would cause warning)
stats = manager.get_stats()
```

## Development

### Local Cache Directory (`.index/`)

The `.index/` directory contains local metadata cache and should **NOT** be committed to Git:

```
.index/
├── checksums.json          # File checksums for incremental indexing
├── metadata_cache.pkl      # Pickled chunk metadata
└── search_queries.log      # Query history for debugging
```

**Git Configuration:**
```bash
# Already in .gitignore
echo ".index/" >> .gitignore
```

**Why not commit?**
- Contains machine-specific paths
- Large binary pickle files
- Rebuilt automatically on first run
- Elasticsearch and Qdrant hold the actual indices

**Rebuilding on new machine:**
```bash
# Clone repo
git clone <repo-url>
cd docs-mcp-server

# Start services
docker-compose up -d

# Build index (will create .index/ automatically)
uv run scripts/build_index.py
```

### Run Tests

```bash
# Quick sanity check (30 seconds)
uv run tests/smoke_test.py

# Comprehensive test suite (8-10 minutes)
uv run tests/run_comprehensive_tests.py

# Individual test suites
uv run tests/test_search_engine.py      # Core functionality
uv run tests/test_score_accuracy.py     # Score validation
uv run tests/test_integration.py        # Integration tests
uv run tests/test_mcp_accuracy.py       # 50+ query tests

# See tests/README.md for full documentation
```

**Test Coverage:**
- ✅ Core search functionality (20+ tests)
- ✅ Score accuracy & thresholds (15+ tests)
- ✅ Integration workflows (7+ tests)
- ✅ Real-world queries (50+ queries)
- ✅ Hybrid scoring validation
- ✅ Tech/component filters
- ✅ Edge cases & error handling

### Debug Logging

**Enable debug output:**
```bash
# Set environment variable
export PYTHONVERBOSE=1

# Or add to Python code
uv run python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

**Debug semantic search:**
```python
# Already enabled in search_engine.py
# Check logs for:
# - "Semantic search returned X results"
# - "Normalized semantic scores: [...]"
# - "Final hybrid scores: [...]"
```

### Inspect Query Log
```bash
# Watch queries in real-time
tail -f .index/search_queries.log

# Analyze query patterns
grep "query=" .index/search_queries.log | head -20
```

### Testing Changes

**After modifying search weights:**
```bash
# Update environment
export BM25_WEIGHT=0.7
export SEMANTIC_WEIGHT=0.3

# Restart server (no reindex needed)
uv run server.py
```

**After modifying chunk size:**
```bash
# Update environment
export CHUNK_SIZE_TOKENS=200

# Must rebuild index with new chunks
uv run scripts/build_index.py --force
```

**After modifying embedding model:**
```bash
# Update environment
export EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2"

# Must rebuild with new embeddings
uv run scripts/build_index.py --force
```

## Future Enhancements

Post-MVP improvements:

- [ ] Local reranker (BAAI/bge-reranker) for top-k refinement
- [ ] Document diffing for incremental updates
- [ ] File watcher for auto-reindex
- [ ] Version-aware filtering (Django 4 vs 5)
- [ ] Query expansion with synonyms
- [ ] Usage analytics dashboard


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with MCP Inspector
5. Submit a pull request

## Support

- GitHub Issues: [Report bugs or request features]
- MCP Docs: https://modelcontextprotocol.io/
- SentenceTransformers: https://www.sbert.net/

---

**Built with:**
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
- [FastEmbed](https://qdrant.github.io/fastembed/)
- [Qdrant](https://qdrant.tech/)
- [Elasticsearch](https://www.elastic.co/elasticsearch/)
