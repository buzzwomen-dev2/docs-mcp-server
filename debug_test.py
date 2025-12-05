#!/usr/bin/env python3
"""Quick debug script to test MCP server functionality"""

import json
import subprocess
import sys
from pathlib import Path

def test_server_basic():
    """Test the server can start and respond"""
    # First send initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "debug-test", "version": "1.0"}
        }
    }
    
    # Then list tools
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    # Combine requests
    input_data = json.dumps(init_request) + "\n" + json.dumps(tools_request) + "\n"
    
    try:
        result = subprocess.run(
            ["uv", "run", "server.py"],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(Path(__file__).parent)
        )
        
        # Parse responses
        responses = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.startswith('{'):
                    try:
                        responses.append(json.loads(line))
                    except:
                        pass
        
        return responses, result.stderr
    
    except Exception as e:
        return [], str(e)

print("🧪 Testing MCP Server\n")

# Check docs directory exists
docs_path = Path("docs")
if not docs_path.exists():
    print("❌ Error: docs/ directory not found!")
    sys.exit(1)

print("📁 Docs directory found")
print(f"   Contents: {[d.name for d in docs_path.iterdir() if d.is_dir()]}\n")

# Test server
print("🔌 Testing server connection...")
responses, stderr = test_server_basic()

if stderr:
    print(f"⚠️  Stderr output:\n{stderr}\n")

if not responses:
    print("❌ No responses received from server")
    sys.exit(1)

print(f"✅ Received {len(responses)} responses\n")

# Check initialization
if len(responses) > 0:
    init_response = responses[0]
    if "result" in init_response:
        print("✅ Server initialized successfully")
        print(f"   Server: {init_response['result'].get('serverInfo', {}).get('name', 'unknown')}")
    else:
        print(f"❌ Initialization failed: {init_response}")

# Check tools list
if len(responses) > 1:
    tools_response = responses[1]
    if "result" in tools_response:
        tools = tools_response["result"].get("tools", [])
        print(f"\n📋 Available tools ({len(tools)}):")
        for tool in tools:
            print(f"   • {tool.get('name', 'unknown')}")
            if 'description' in tool:
                desc = tool['description'][:80] + "..." if len(tool['description']) > 80 else tool['description']
                print(f"     {desc}")
    else:
        print(f"❌ Tools list failed: {tools_response}")

print("\n✨ Basic testing complete!")
print("\n💡 Next steps:")
print("   1. Use MCP Inspector (already running at localhost:6274)")
print("   2. Or press F5 in VS Code to debug")
print("   3. Or run: uv run server.py")
