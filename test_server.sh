#!/bin/bash
# Test script for MCP server

echo "🧪 Testing docs-mcp-server..."
echo ""

# Test 1: List technologies
echo "📋 Test 1: List technologies"
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_technologies", "arguments": {}}}' | uv run server.py | jq '.result.content[0].text'
echo ""

# Test 2: Search Django docs
echo "🔍 Test 2: Search for 'models' in Django"
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "search_docs", "arguments": {"query": "models", "tech": "django"}}}' | uv run server.py | jq '.result.content[0].text'
echo ""

echo "✅ Tests complete!"
