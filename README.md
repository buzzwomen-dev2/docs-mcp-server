# Docs MCP Server - Hybrid Search for Technical Documentation

A high-performance **Model Context Protocol (MCP) server** that provides hybrid search capabilities combining:
- **Semantic search** using sentence-transformers (BGE-small-en) + ChromaDB
- **Keyword search** using Whoosh BM25
- **Weighted fusion** (0.6 BM25 + 0.4 semantic by default)

Designed for local developer documentation search across Django, Django REST Framework, Psycopg, and other technical docs.

## Features

- 🔍 **Hybrid Search**: Combines semantic understanding with keyword precision
- 🏷️ **Rich Metadata**: Auto-tags documents by tech, component, topic, version
- 📊 **Structured Results**: Pydantic models with individual and combined scores
- 🚀 **Dual Interface**: MCP tools + REST API
- 💾 **Persistent Index**: ChromaDB + Whoosh on disk
- 📝 **Smart Chunking**: Semantic for prose (300-500 tokens), structural for code (80-150 lines)
- 🔒 **Localhost-only**: Secure by default, no external access

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
python scripts/build_index.py

# Or index programmatically
python -c "
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
python server.py
```

Then configure in your MCP client (Claude Desktop, VSCode, etc):

```json
{
  "mcpServers": {
    "docs-server": {
      "command": "python",
      "args": ["/path/to/docs-mcp-server/server.py"]
    }
  }
}
```

#### As HTTP API Server

```bash
python server.py --http
```

Access at:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### 4. Validate Setup

```bash
# Run validation script
python scripts/test_setup.py
```

### 5. Test with MCP Inspector

```bash
# In one terminal: start server
python server.py

# In another terminal: start inspector
npx @modelcontextprotocol/inspector python server.py
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
Build or rebuild the search index.

**Parameters:**
- `paths` (optional): Specific file/directory paths
- `tech` (optional): Index specific technology (django/drf/psycopg)

**Example:**
```python
# Reindex all docs
reindex_docs()

# Index only Django docs
reindex_docs(tech="django")

# Index specific paths
reindex_docs(paths=["docs/django-6.0/ref"])
```

**Returns:** Statistics with `files_processed`, `chunks_created`, `errors`.

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

Set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `INDEX_DIR` | `.index` | Directory for indices |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en` | SentenceTransformer model |
| `BM25_WEIGHT` | `0.6` | Weight for BM25 scores |
| `SEMANTIC_WEIGHT` | `0.4` | Weight for semantic scores |
| `CHUNK_SIZE_TOKENS` | `400` | Target chunk size (tokens) |

**Example:**
```bash
export EMBEDDING_MODEL="nomic-embed-text"  # If using Ollama
export BM25_WEIGHT=0.7
export SEMANTIC_WEIGHT=0.3
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
┌─────────────────────────────────┐
│      search_engine.py           │
│      (IndexManager)             │
│  ┌──────────┐   ┌────────────┐ │
│  │ Whoosh   │   │  ChromaDB  │ │
│  │  BM25    │   │ Embeddings │ │
│  └──────────┘   └────────────┘ │
└─────────────────────────────────┘
         │
         v
    ┌─────────┐
    │ .index/ │  (Persistent storage)
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

**Initial Indexing:**
- 350-400 files → 2-5 minutes
- Generates embeddings (768-dim for bge-small-en)
- Builds BM25 inverted index

**Search Latency:**
- Semantic search: ~50-100ms (HNSW index)
- BM25 search: ~10-20ms (inverted index)
- Hybrid fusion: ~5ms
- **Total:** ~100-150ms per query

## Troubleshooting

### Index is empty
```bash
# Check stats
curl http://localhost:8000/status

# Rebuild index
python -c "
import asyncio
from pathlib import Path
from search_engine import IndexManager

asyncio.run(IndexManager().index_documents([Path('docs')]))
"
```

### Poor search quality

1. **Check query log** at `.index/search_queries.log`
2. **Tune weights** for your query patterns:
   - More keyword-focused: Increase `BM25_WEIGHT`
   - More semantic: Increase `SEMANTIC_WEIGHT`
3. **Try different models**:
   ```bash
   export EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2"
   ```

### Embeddings taking too long

- Switch to smaller model: `all-MiniLM-L6-v2` (384-dim, faster)
- Or use Ollama: `nomic-embed-text` (768-dim, local)

### Memory issues

- Reduce `CHUNK_SIZE_TOKENS` to 300
- Process docs in batches (already implemented)
- Use FAISS instead of ChromaDB (requires code change)

## Development

### Run Tests
```bash
# Test search engine
python -m pytest tests/

# Test with example queries
python examples/test_queries.py
```

### Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Query Log
```bash
tail -f .index/search_queries.log
```

## Future Enhancements

Post-MVP improvements:

- [ ] Local reranker (BAAI/bge-reranker) for top-k refinement
- [ ] Document diffing for incremental updates
- [ ] File watcher for auto-reindex
- [ ] Version-aware filtering (Django 4 vs 5)
- [ ] Query expansion with synonyms
- [ ] Usage analytics dashboard

## License

MIT

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
- [sentence-transformers](https://www.sbert.net/)
- [ChromaDB](https://www.trychroma.com/)
- [Whoosh](https://whoosh.readthedocs.io/)
