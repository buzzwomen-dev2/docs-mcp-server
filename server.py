#!/usr/bin/env python3
"""Local MCP Documentation Server for Django/DRF/Psycopg stack."""

import logging
import sys
from pathlib import Path
from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

# Enable debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("docs-server")
DOCS_ROOT = Path("docs")

TECH_DIRS = {
    "django": "django-6.0",
    "drf": "drf-3.16.1", 
    "psycopg": "psycopg-3.3.1"
}

@mcp.tool()
def search_docs(query: str, tech: str = "django") -> str:
    logger.info(f"Searching {tech} for '{query}'")
    tech_key = tech.lower()
    if tech_key not in TECH_DIRS:
        return f"Available technologies: {', '.join(TECH_DIRS.keys())}"

    tech_path = DOCS_ROOT / TECH_DIRS[tech_key]
    if not tech_path.exists():
        return f"{tech} docs not found at {tech_path}"

    results = []
    query_lower = query.lower()
    md_files = list(tech_path.rglob("*.md"))

    logger.info(f"Found {len(md_files)} .md files in {tech}")

    for md_file in md_files[:20]:  # Limit for performance
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if query_lower in content.lower():
                lines = content.split('\n')
                title = next((line.strip('# ').strip()
                             for line in lines[:10]
                             if line.strip().startswith('#')),
                            md_file.name)

                # Find first match context
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        context_start = max(0, i-2)
                        context_end = min(len(lines), i+3)
                        context = '\n'.join(lines[context_start:context_end])
                        break
                else:
                    context = '\n'.join(lines[:5])

                rel_path = md_file.relative_to(DOCS_ROOT)
                results.append(f"**{title}**\n``````\n📁 `{rel_path}`")

                if len(results) >= 3:
                    break

        except Exception as e:
            logger.warning(f"Error reading {md_file}: {e}")
            continue

    if results:
        return "\n\n---\n\n".join(results)
    return f"No matches found for '{query}' in {tech} ({len(md_files)} files scanned)"


@mcp.tool()
def list_docs(tech: str) -> str:
    tech_key = tech.lower()
    if tech_key not in TECH_DIRS:
        return f"Available: {', '.join(TECH_DIRS.keys())}"

    tech_path = DOCS_ROOT / TECH_DIRS[tech_key]
    if not tech_path.exists():
        return f"{tech} docs not found"

    structure = []

    def walk_dir(path, prefix=""):
        items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        pointers = ["├── "] * len(items)
        if items:
            pointers[-1] = "└── "

        for i, item in enumerate(items):
            connector = pointers[i]
            item_str = f"{item.name}/" if item.is_dir() else item.name
            structure.append(f"{prefix}{connector}{item_str}")

            if item.is_dir():
                new_prefix = prefix + ("    " if i == len(items) - 1 else "│   ")
                walk_dir(item, new_prefix)

    walk_dir(tech_path)
    return "``````"

@mcp.tool()
def list_technologies() -> str:
    """List all available documentation sets."""
    info = []
    for tech, dir_name in TECH_DIRS.items():
        tech_path = DOCS_ROOT / dir_name
        if tech_path.exists():
            md_count = sum(1 for _ in tech_path.rglob("*.md"))
            info.append(f"{tech}: {dir_name} ({md_count} files)")
        else:
            info.append(f"{tech}: {dir_name} (missing)")
    return "\n".join(info)
if __name__ == "__main__":
    try:
        logger.info("Starting docs MCP server...")
        mcp.run(transport="stdio")
        logger.info("Server ready")  # <-- log ready right after run
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

