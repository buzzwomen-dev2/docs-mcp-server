# Local Documentation MCP Server

MCP server providing local documentation for Django, DRF, and Psycopg.

## Setup

```bash
# Install dependencies
uv sync

# Run the server
uv run server.py
```

## Development

### Running with uv
```bash
uv run server.py
```

### Debugging

**Option 1: VS Code Debugger**
- Press `F5` or go to Run → Start Debugging
- Select "Debug MCP Server with uv"

**Option 2: MCP Inspector (Recommended)**
```bash
# Install MCP inspector globally
uv tool install mcp-inspector

# Run inspector (provides web UI for testing)
npx @modelcontextprotocol/inspector uv run server.py
```

**Option 3: Manual Testing**
```bash
./test_server.sh
```

### Available Tools

1. **list_technologies** - List all available documentation sets
2. **search_docs** - Search for content in documentation
3. **list_docs** - Show directory structure of docs

## Troubleshooting

- Make sure dependencies are installed: `uv sync`
- Check that docs are in `docs/` directory
- Use `uv run server.py` instead of `python server.py`
