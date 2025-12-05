# How to Use Your MCP Documentation Server

Your server is running and ready! Here are the ways to use it:

---

## 🔍 **Option 1: MCP Inspector (Best for Testing)**

**Currently Running:** http://localhost:6274

### How to use:
1. Look for the **"Tools"** section in the left sidebar
2. Click on any tool to see its parameters
3. Fill in the parameters and click "Run" or "Execute"

### Example searches to try:
- Tool: `list_technologies` → Shows all available docs
- Tool: `search_docs` with `query="ORM"`, `tech="django"` → Find ORM docs
- Tool: `search_docs` with `query="serializer"`, `tech="drf"` → Find serializer docs
- Tool: `list_docs` with `tech="psycopg"` → Browse psycopg docs structure

---

## 💬 **Option 2: Use with Claude Desktop (Production)**

Add this to your Claude config file:

**Location:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "docs-server": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/home/prabuddh/projects/docs-mcp-server"
    }
  }
}
```

Then restart Claude Desktop. You'll be able to ask Claude:
- "Search the Django docs for model relationships"
- "Show me DRF serializer documentation"
- "What does the psycopg docs say about connection pooling?"

---

## 🧪 **Option 3: Test via Command Line**

Run the test script:
```bash
cd /home/prabuddh/projects/docs-mcp-server
uv run test_tools_direct.py
```

Or use the bash test:
```bash
./test_server.sh
```

---

## 🐛 **Option 4: Debug in VS Code**

1. Press **F5** in VS Code
2. Select "Debug MCP Server with uv"
3. Set breakpoints in `server.py`
4. Step through the code

---

## 📝 Available Tools

### 1. `list_technologies`
Lists all available documentation sets
- No parameters needed
- Returns: django, drf, psycopg with file counts

### 2. `search_docs`
Search for content in documentation
- `query` (string): What to search for
- `tech` (string): "django", "drf", or "psycopg"
- Returns: Top 3 matching docs with context

### 3. `list_docs`
Show directory structure of docs
- `tech` (string): Which docs to browse
- Returns: Tree view of documentation files

---

## 🎯 Next Steps

1. **Try the inspector** (already open at localhost:6274)
2. **Add to Claude Desktop** if you want to use it with Claude
3. **Customize** the search logic in `server.py` if needed

The server is working perfectly! 🚀
