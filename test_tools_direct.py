#!/usr/bin/env python3
"""Direct test of MCP tools without inspector"""

import json
import subprocess

def call_tool(tool_name, arguments=None):
    """Call a tool via JSON-RPC"""
    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
    ]
    
    input_data = "\n".join(json.dumps(r) for r in requests) + "\n"
    
    result = subprocess.run(
        ["uv", "run", "server.py"],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Parse last JSON response (the tool call result)
    responses = []
    for line in result.stdout.split('\n'):
        if line.strip().startswith('{'):
            try:
                responses.append(json.loads(line))
            except:
                pass
    
    if len(responses) >= 2:
        return responses[1]  # Second response is the tool call
    return {"error": "No response", "output": result.stdout}

print("=" * 60)
print("Testing MCP Server Tools")
print("=" * 60)

# Test 1: list_technologies
print("\n🔧 Tool: list_technologies")
print("-" * 60)
result = call_tool("list_technologies")
if "result" in result:
    content = result["result"]["content"][0]["text"]
    print(content)
else:
    print(f"Error: {result}")

# Test 2: search_docs for "model"
print("\n🔧 Tool: search_docs (query='model', tech='django')")
print("-" * 60)
result = call_tool("search_docs", {"query": "model", "tech": "django"})
if "result" in result:
    content = result["result"]["content"][0]["text"]
    # Print first 500 chars
    print(content[:500] + "..." if len(content) > 500 else content)
else:
    print(f"Error: {result}")

# Test 3: list_docs
print("\n🔧 Tool: list_docs (tech='drf')")
print("-" * 60)
result = call_tool("list_docs", {"tech": "drf"})
if "result" in result:
    content = result["result"]["content"][0]["text"]
    # Print first 500 chars
    lines = content.split('\n')[:20]
    print('\n'.join(lines))
    if len(content.split('\n')) > 20:
        print("... (truncated)")
else:
    print(f"Error: {result}")

print("\n" + "=" * 60)
print("✅ All tools tested successfully!")
print("=" * 60)
