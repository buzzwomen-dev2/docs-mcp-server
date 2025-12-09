# Project Structure

```
docs-mcp-server/
├── 📂 docs/                    # Documentation to be indexed
│   ├── django-6.0/            # Django 6.0 documentation
│   ├── drf-3.16.1/            # Django REST Framework docs
│   └── psycopg-3.3.1/         # Psycopg PostgreSQL adapter docs
│
├── 📂 scripts/                 # Utility scripts
│   ├── build_index.py         # Index builder for documentation
│   ├── test_setup.py          # Validation script
│   └── README.md              # Scripts documentation
│
├── 📂 reference/               # Reference materials (kept for historical context)
│   ├── mcp-llms.txt           # MCP specification docs
│   ├── mcp-python-sdk-readme.md  # Python SDK docs
│   ├── vscode-mcp-setup.md    # VS Code integration guide
│   └── README.md              # Reference documentation
│
├── 📂 .vscode/                 # VS Code configuration
│   └── mcp.json.example       # MCP server config template
│
├── 📂 .index/                  # Search indices (generated)
│   ├── chroma/                # ChromaDB vector store
│   ├── whoosh/                # Whoosh BM25 index
│   └── search_queries.log     # Query log for analysis
│
├── 🐍 server.py                # Main MCP server (FastMCP + FastAPI)
├── 🔍 search_engine.py         # Hybrid search implementation
│
├── 📋 pyproject.toml           # Project dependencies (uv/pip)
├── 🔒 uv.lock                  # Locked dependencies
├── ⚙️  .env.template            # Environment variables template
│
├── 📖 README.md                # Main documentation
├── 📖 SETUP.md                 # Quick setup guide
├── 📖 IMPLEMENTATION.md        # Technical implementation details
└── 📖 PERFORMANCE_FIXES.md     # Performance optimization guide
```

## Quick Navigation

### Getting Started
1. Read **README.md** for overview and features
2. Follow **SETUP.md** for installation
3. Run `python scripts/test_setup.py` to validate

### Development
- **server.py** - MCP tools and FastAPI endpoints
- **search_engine.py** - IndexManager with hybrid search
- **scripts/** - Helper utilities for indexing and testing

### Documentation
- **IMPLEMENTATION.md** - Architecture and design decisions
- **PERFORMANCE_FIXES.md** - Debugging guide for indexing issues
- **reference/** - Original MCP/SDK documentation (historical)

### Configuration
- **.env.template** - Copy to `.env` and customize
- **.vscode/mcp.json.example** - VS Code MCP integration template

## File Roles

| File | Purpose | When to Modify |
|------|---------|----------------|
| `server.py` | MCP server with tools | Add new tools or API endpoints |
| `search_engine.py` | Hybrid search logic | Adjust chunking, scoring, or indexing |
| `scripts/build_index.py` | Index builder | Change indexing behavior |
| `scripts/test_setup.py` | Validation tests | Add new validation checks |
| `pyproject.toml` | Dependencies | Add/update packages |
| `.env.template` | Config template | Document new environment variables |

## Directory Purposes

- **docs/** - Documentation files to be indexed (add more here)
- **scripts/** - Standalone utilities that don't need to be imported
- **reference/** - Historical reference materials (rarely modified)
- **.index/** - Generated files (gitignored, rebuilt as needed)
- **.vscode/** - Editor-specific configuration

## Development Workflow

1. **Add docs**: Place files in `docs/<tech-name>/`
2. **Index**: `python scripts/build_index.py`
3. **Validate**: `python scripts/test_setup.py`
4. **Test**: `python server.py` → use MCP Inspector or HTTP API
5. **Deploy**: Configure in MCP client (Claude Desktop, VS Code, etc.)
