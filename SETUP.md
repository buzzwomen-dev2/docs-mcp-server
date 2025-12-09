# Quick Setup Guide

## Prerequisites

- Python 3.13+
- 4GB+ RAM (for embedding model)
- 2GB+ disk space (for indices)

## Installation

### 1. Clone and Install

```bash
cd /path/to/docs-mcp-server

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Build Search Index

This will take 2-5 minutes on first run:

```bash
# Option A: Using helper script (recommended)
python scripts/build_index.py

# Option B: Using Python directly
python -c "
import asyncio
from pathlib import Path
from search_engine import IndexManager

async def main():
    manager = IndexManager()
    stats = await manager.index_documents([Path('docs')])
    print(f'Indexed {stats[\"chunks_created\"]} chunks')

asyncio.run(main())
"
```

**Expected output:**
```
Initializing IndexManager...
Loading embedding model: BAAI/bge-small-en
Initializing ChromaDB...
Initializing Whoosh BM25 index...
Found 350 files to index
[10.0%] Processing models.md...
[20.0%] Processing views.md...
...
[100.0%] Indexing 2847 chunks...
Indexing Complete!
  Files processed: 350
  Chunks created:  2847
```

### 3. Test the Setup

#### Test with MCP Inspector

```bash
# Terminal 1: Start inspector
npx @modelcontextprotocol/inspector python server.py

# Opens browser at http://localhost:5173
```

In the inspector UI:
1. Click "Connect"
2. Try the `get_index_stats` tool
3. Try searching: `search(query="Django authentication", top_k=5)`

#### Test with HTTP API

```bash
# Terminal 1: Start HTTP server
python server.py --http

# Terminal 2: Test endpoints
curl http://localhost:8000/status | jq
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Django models", "top_k":3}' | jq
```

### 4. Configure MCP Client

#### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "docs-server": {
      "command": "python",
      "args": ["/absolute/path/to/docs-mcp-server/server.py"],
      "env": {
        "EMBEDDING_MODEL": "BAAI/bge-small-en",
        "BM25_WEIGHT": "0.6",
        "SEMANTIC_WEIGHT": "0.4"
      }
    }
  }
}
```

Restart Claude Desktop and look for the tools icon.

#### VS Code with Copilot

Create `.vscode/mcp.json`:

```json
{
  "servers": {
    "docs-server": {
      "type": "stdio",
      "command": "python",
      "args": ["server.py"],
      "env": {
        "EMBEDDING_MODEL": "BAAI/bge-small-en"
      }
    }
  }
}
```

## Verification Checklist

- [ ] Dependencies installed (`uv sync` or `pip install -e .`)
- [ ] Index built successfully (`.index/` directory exists)
- [ ] MCP Inspector shows tools and connects
- [ ] HTTP API responds to `/status` endpoint
- [ ] Sample search returns results
- [ ] MCP client configured and connected

## Example Queries to Test

Try these in your MCP client or via HTTP:

```python
# 1. Search Django auth
search(query="How does Django authentication work?", tech="django", top_k=5)

# 2. Search DRF serializers
search(query="DRF serializer validation", tech="drf", top_k=3)

# 3. Get index stats
get_index_stats()

# 4. List sources
list_sources(tech="django")
```

## Troubleshooting

### "No module named 'sentence_transformers'"

```bash
uv sync
# or
pip install sentence-transformers
```

### "Index is empty"

```bash
python build_index.py --clear
```

### "Embedding model download failed"

The model downloads automatically on first run (~130MB). If it fails:
- Check internet connection
- Try manual download:
  ```python
  from sentence_transformers import SentenceTransformer
  SentenceTransformer("BAAI/bge-small-en")
  ```

### "MCP client can't connect"

1. Check server is running: `python server.py` (should not exit)
2. Check absolute paths in config
3. Check Python path: `which python`
4. Try MCP Inspector first to verify

### "Search returns no results"

1. Run validation: `python scripts/test_setup.py`
2. Check index stats: `curl http://localhost:8000/status`
3. If `total_chunks: 0`, rebuild: `python scripts/build_index.py --clear`
4. Check query log: `tail .index/search_queries.log`

## Performance Tuning

### Faster Indexing

Use smaller embedding model:
```bash
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
python scripts/build_index.py --clear
```

### Better Semantic Search

Use larger model:
```bash
export EMBEDDING_MODEL="sentence-transformers/all-mpnet-base-v2"
```

### Tune Hybrid Weights

Based on your query patterns:
- More keyword-focused: `BM25_WEIGHT=0.7`, `SEMANTIC_WEIGHT=0.3`
- More semantic: `BM25_WEIGHT=0.5`, `SEMANTIC_WEIGHT=0.5`

Test with query log analysis.

## VS Code Configuration

### Using GitHub Copilot with MCP

1. **Copy the example config:**
   ```bash
   cp .vscode/mcp.json.example .vscode/mcp.json
   ```

2. **Edit `.vscode/mcp.json`** and update the `cwd` path:
   ```json
   {
     "servers": {
       "docsSearch": {
         "type": "stdio",
         "command": "python",
         "args": ["server.py"],
         "cwd": "/absolute/path/to/docs-mcp-server"
       }
     }
   }
   ```

   **Note**: The format changed in VS Code 1.102+. Use `"servers"` (not `"mcpServers"`) and include `"type": "stdio"`.

3. **Reload VS Code** or restart GitHub Copilot Chat

4. **Verify connection:**
   - Open GitHub Copilot Chat
   - Check that `docsSearch` appears in the MCP server list
   - Try a search: "search for Django authentication"
   - Try a resource: Add Context > MCP Resources > `doc://django/...`
   - Try a prompt: `/mcp.docsSearch.find_authentication_docs`

**Features Available:**
- **Tools**: 8 search and management tools
- **Resources**: Direct file access via `doc://` and `chunk://` URIs
- **Prompts**: 3 preconfigured search prompts as slash commands

**Requirements:** VS Code 1.102+ with GitHub Copilot Chat extension.

## Next Steps

1. Add more documentation to `docs/` directory
2. Reindex: `python scripts/build_index.py`
3. Validate: `python scripts/test_setup.py`
4. Configure in your preferred MCP client
5. Check query logs for improvement opportunities

## Support

- README.md - Full documentation
- GitHub Issues - Bug reports
- MCP Docs: https://modelcontextprotocol.io/
