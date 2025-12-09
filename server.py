#!/usr/bin/env python3
"""
Hybrid Search MCP Documentation Server for Django/DRF/Psycopg stack.

Combines semantic search (sentence-transformers + ChromaDB) with
keyword search (Whoosh BM25) for optimal retrieval of technical documentation.
"""

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

from search_engine import IndexManager, SearchResult as EngineSearchResult

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
DOCS_ROOT = Path("docs")
INDEX_DIR = os.getenv("INDEX_DIR", ".index")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en")
BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", "0.6"))
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", "0.4"))
CHUNK_SIZE_TOKENS = int(os.getenv("CHUNK_SIZE_TOKENS", "400"))

TECH_DIRS = {
    "django": "django-6.0",
    "drf": "drf-3.16.1", 
    "psycopg": "psycopg-3.3.1"
}


# Pydantic models for structured output
class SearchResultModel(BaseModel):
    """Structured search result."""
    chunk_id: str = Field(description="Unique chunk identifier")
    content: str = Field(description="Chunk content/excerpt")
    source_path: str = Field(description="Source file path")
    tech: str = Field(description="Technology (django/drf/psycopg/etc)")
    component: str = Field(description="Component or module")
    topic: str = Field(description="Topic or heading")
    version: str = Field(description="Version string")
    file_type: str = Field(description="File extension")
    chunk_index: int = Field(description="Chunk position in document")
    bm25_score: float = Field(description="BM25 keyword score (0-1)")
    semantic_score: float = Field(description="Semantic similarity score (0-1)")
    hybrid_score: float = Field(description="Combined hybrid score (0-1)")


class IndexStats(BaseModel):
    """Index statistics and health information."""
    total_chunks: int
    whoosh_documents: int
    chroma_documents: int
    embedding_model: int
    embedding_dimension: int
    bm25_weight: float
    semantic_weight: float
    index_directory: str
    technologies: List[str]
    file_types: List[str]


class SourceInfo(BaseModel):
    """Information about an indexed source file."""
    source_path: str
    chunk_count: int
    tech: str
    component: str
    version: str
    file_type: str


@dataclass
class AppContext:
    """Application context with IndexManager."""
    index_manager: IndexManager


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with IndexManager initialization."""
    logger.info("Initializing IndexManager...")
    
    index_manager = IndexManager(
        index_dir=INDEX_DIR,
        embedding_model=EMBEDDING_MODEL,
        bm25_weight=BM25_WEIGHT,
        semantic_weight=SEMANTIC_WEIGHT,
        chunk_size_tokens=CHUNK_SIZE_TOKENS
    )
    
    # Check if index exists and has content
    stats = index_manager.get_stats()
    if stats["total_chunks"] == 0:
        logger.warning("Index is empty. Use reindex_docs tool to build the index.")
    else:
        logger.info(f"Index loaded: {stats['total_chunks']} chunks across {len(stats['technologies'])} technologies")
    
    yield AppContext(index_manager=index_manager)
    
    logger.info("Shutting down IndexManager...")


# Initialize FastMCP server with lifespan
# Server name uses camelCase per VS Code MCP naming conventions
mcp = FastMCP("docsSearch", lifespan=app_lifespan)

# ==================== HYBRID SEARCH TOOLS ====================

def expand_query(query: str) -> str:
    """
    Expand comparison queries to improve search results.
    
    Transforms 'X vs Y' queries into OR queries that search for both terms.
    Also handles 'versus', 'compared to', 'difference between' patterns.
    
    Examples:
        'Serializer vs ModelSerializer' -> 'Serializer OR ModelSerializer'
        'difference between X and Y' -> 'X OR Y'
    """
    import re
    
    # Pattern 1: "X vs Y" or "X versus Y"
    vs_pattern = r'(.+?)\s+(?:vs\.?|versus)\s+(.+?)(?:\s+|$)'
    match = re.search(vs_pattern, query, re.IGNORECASE)
    if match:
        term1 = match.group(1).strip()
        term2 = match.group(2).strip()
        # Remove trailing words like "difference", "when to use", etc.
        term2 = re.sub(r'\s+(difference|when|how|why).*$', '', term2, flags=re.IGNORECASE)
        return f"{term1} OR {term2}"
    
    # Pattern 2: "difference between X and Y"
    diff_pattern = r'difference\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+|$)'
    match = re.search(diff_pattern, query, re.IGNORECASE)
    if match:
        term1 = match.group(1).strip()
        term2 = match.group(2).strip()
        return f"{term1} OR {term2}"
    
    # Pattern 3: "compared to" or "comparison"
    comp_pattern = r'(.+?)\s+compared\s+to\s+(.+?)(?:\s+|$)'
    match = re.search(comp_pattern, query, re.IGNORECASE)
    if match:
        term1 = match.group(1).strip()
        term2 = match.group(2).strip()
        return f"{term1} OR {term2}"
    
    # No pattern matched, return original query
    return query


@mcp.tool()
async def search(
    query: str,
    ctx: Context[ServerSession, AppContext],
    tech: Optional[str] = None,
    component: Optional[str] = None,
    top_k: int = 15
) -> List[SearchResultModel]:
    """
    Search documentation using hybrid semantic + keyword search.
    
    Combines BM25 keyword matching with semantic embeddings for optimal results.
    Returns ranked results with individual and hybrid scores.
    
    Args:
        query: Search query text
        tech: Filter by technology (django/drf/psycopg)
        component: Filter by component/module
        top_k: Number of results to return (default 10)
    
    Returns:
        List of search results with scores and metadata
    """
    # Expand comparison queries for better results
    expanded_query = expand_query(query)
    if expanded_query != query:
        await ctx.info(f"Query expanded: '{query}' -> '{expanded_query}'")
    
    await ctx.info(f"Searching: '{expanded_query}' (tech={tech}, component={component}, top_k={top_k})")
    
    index_manager = ctx.request_context.lifespan_context.index_manager
    
    try:
        results = await index_manager.search(
            query=expanded_query,
            top_k=top_k,
            tech_filter=tech,
            component_filter=component
        )
        
        await ctx.info(f"Found {len(results)} results")
        
        return [
            SearchResultModel(
                chunk_id=r.chunk_id,
                content=r.content[:500] + "..." if len(r.content) > 500 else r.content,
                source_path=r.source_path,
                tech=r.tech,
                component=r.component,
                topic=r.topic,
                version=r.version,
                file_type=r.file_type,
                chunk_index=r.chunk_index,
                bm25_score=round(r.bm25_score, 4),
                semantic_score=round(r.semantic_score, 4),
                hybrid_score=round(r.hybrid_score, 4)
            )
            for r in results
        ]
    except Exception as e:
        await ctx.error(f"Search error: {e}")
        raise


@mcp.tool()
async def retrieve(
    chunk_id: str,
    ctx: Context[ServerSession, AppContext]
) -> Optional[SearchResultModel]:
    """
    Retrieve a specific document chunk by ID.
    
    Args:
        chunk_id: Unique chunk identifier from search results
    
    Returns:
        Full chunk content and metadata, or None if not found
    """
    index_manager = ctx.request_context.lifespan_context.index_manager
    
    chunk = index_manager.retrieve(chunk_id)
    
    if not chunk:
        await ctx.warning(f"Chunk not found: {chunk_id}")
        return None
    
    return SearchResultModel(
        chunk_id=chunk.chunk_id,
        content=chunk.content,
        source_path=chunk.source_path,
        tech=chunk.tech,
        component=chunk.component,
        topic=chunk.topic,
        version=chunk.version,
        file_type=chunk.file_type,
        chunk_index=chunk.chunk_index,
        bm25_score=0.0,
        semantic_score=0.0,
        hybrid_score=0.0
    )


@mcp.tool()
async def reindex_docs(
    ctx: Context[ServerSession, AppContext],
    paths: Optional[List[str]] = None,
    tech: Optional[str] = None
) -> Dict[str, int]:
    """
    Reindex documentation files.
    
    Builds or rebuilds the search index. This may take several minutes for large doc sets.
    Progress is reported during indexing.
    
    Args:
        paths: Specific file/directory paths to index (optional)
        tech: Index specific technology docs (django/drf/psycopg) (optional)
    
    Returns:
        Statistics: files_processed, chunks_created, errors
    """
    await ctx.info("Starting reindex operation...")
    
    index_manager = ctx.request_context.lifespan_context.index_manager
    
    # Determine paths to index
    paths_to_index = []
    
    if paths:
        paths_to_index = [Path(p) for p in paths]
    elif tech:
        tech_key = tech.lower()
        if tech_key in TECH_DIRS:
            tech_path = DOCS_ROOT / TECH_DIRS[tech_key]
            if tech_path.exists():
                paths_to_index = [tech_path]
            else:
                await ctx.error(f"Technology docs not found: {tech_path}")
                return {"files_processed": 0, "chunks_created": 0, "errors": 1}
        else:
            await ctx.error(f"Unknown technology: {tech}. Available: {', '.join(TECH_DIRS.keys())}")
            return {"files_processed": 0, "chunks_created": 0, "errors": 1}
    else:
        # Index all docs
        paths_to_index = [DOCS_ROOT]
    
    # Progress callback
    async def progress_callback(current: int, total: int, message: str):
        await ctx.report_progress(current, total, message)
    
    try:
        stats = await index_manager.index_documents(
            paths=paths_to_index,
            progress_callback=progress_callback
        )
        
        await ctx.info(f"Indexing complete: {stats}")
        return stats
        
    except Exception as e:
        await ctx.error(f"Indexing error: {e}")
        raise


@mcp.tool()
async def get_index_stats(
    ctx: Context[ServerSession, AppContext]
) -> IndexStats:
    """
    Get index statistics and health information.
    
    Returns:
        Index statistics including chunk counts, model info, and indexed technologies
    """
    index_manager = ctx.request_context.lifespan_context.index_manager
    
    stats = index_manager.get_stats()
    
    return IndexStats(**stats)


@mcp.tool()
async def list_sources(
    ctx: Context[ServerSession, AppContext],
    tech: Optional[str] = None
) -> List[SourceInfo]:
    """
    List all indexed source files with metadata.
    
    Args:
        tech: Filter by technology (optional)
    
    Returns:
        List of source files with chunk counts and metadata
    """
    index_manager = ctx.request_context.lifespan_context.index_manager
    
    sources = index_manager.list_sources()
    
    if tech:
        sources = [s for s in sources if s.get("tech") == tech.lower()]
    
    return [SourceInfo(**source) for source in sources]


# ==================== MCP RESOURCES ====================
# Provide direct access to documentation as context

@mcp.resource("doc://{tech}/{path}")
async def get_doc_resource(
    tech: str,
    path: str,
    ctx: Context[ServerSession, AppContext]
) -> str:
    """
    Access documentation files as MCP resources.
    
    URI format: doc://django/ref/models/fields.md
    
    Returns the raw file content for use as context in chat.
    """
    file_path = path
    
    if tech not in TECH_DIRS:
        raise ValueError(f"Unknown technology: {tech}. Available: {', '.join(TECH_DIRS.keys())}")
    
    full_path = DOCS_ROOT / TECH_DIRS[tech] / file_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"Documentation file not found: {file_path}")
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        await ctx.info(f"Loaded resource: doc://{tech}/{path}")
        return content
    except Exception as e:
        await ctx.error(f"Error reading file: {e}")
        raise


@mcp.resource("chunk://{chunk_id}")
async def get_chunk_resource(
    chunk_id: str,
    ctx: Context[ServerSession, AppContext]
) -> str:
    """
    Access indexed documentation chunks as MCP resources.
    
    URI format: chunk://middleware_3_1234
    
    Returns the chunk content from the search index.
    """
    
    index_manager = ctx.request_context.lifespan_context.index_manager
    chunk = index_manager.retrieve(chunk_id)
    
    if not chunk:
        raise ValueError(f"Chunk not found: {chunk_id}")
    
    await ctx.info(f"Loaded chunk: {chunk_id}")
    
    # Format chunk with metadata
    return f"""# {chunk.topic}
Source: {chunk.source_path}
Tech: {chunk.tech} | Component: {chunk.component} | Version: {chunk.version}

{chunk.content}"""


# ==================== MCP PROMPTS ====================
# Preconfigured prompts for common documentation searches

@mcp.prompt()
async def find_authentication_docs(
    tech: str = "django"
) -> str:
    """
    Search for authentication and authorization documentation.
    
    Args:
        tech: Technology to search (django/drf/psycopg)
    """
    return f"""Search the {tech} documentation for authentication, authorization, permissions, and user management.

Focus on:
- Setting up authentication
- Permission classes and decorators
- User models and authentication backends
- Session management
- Security best practices

Use the search tool with: query="authentication authorization permissions" tech="{tech}" """


@mcp.prompt()
async def find_database_docs(
    tech: str = "django"
) -> str:
    """
    Search for database and ORM documentation.
    
    Args:
        tech: Technology to search (django/drf/psycopg)
    """
    return f"""Search the {tech} documentation for database operations, queries, and ORM usage.

Focus on:
- Database connections and configuration
- Query syntax and optimization
- Model relationships and fields
- Migrations and schema management
- Transaction handling

Use the search tool with: query="database queries ORM models" tech="{tech}" """


@mcp.prompt()
async def find_api_docs(
    tech: str = "drf"
) -> str:
    """
    Search for API and serialization documentation.
    
    Args:
        tech: Technology to search (typically drf)
    """
    return f"""Search the {tech} documentation for REST API development and serialization.

Focus on:
- Serializers and validation
- ViewSets and routers
- API endpoints and URL routing
- Request/response handling
- API authentication and permissions

Use the search tool with: query="serializers viewsets API endpoints" tech="{tech}" """


# ==================== FASTAPI REST ENDPOINTS ====================
# For non-MCP HTTP access (localhost only)

app = FastAPI(
    title="Docs Search API",
    description="Hybrid search API for technical documentation",
    version="0.1.0"
)


class SearchRequest(BaseModel):
    """HTTP search request."""
    query: str
    tech: Optional[str] = None
    component: Optional[str] = None
    top_k: int = 10


class ReindexRequest(BaseModel):
    """HTTP reindex request."""
    paths: Optional[List[str]] = None
    tech: Optional[str] = None


# Global index manager for HTTP endpoints
_http_index_manager: Optional[IndexManager] = None


def get_http_index_manager() -> IndexManager:
    """Get or create HTTP index manager."""
    global _http_index_manager
    if _http_index_manager is None:
        _http_index_manager = IndexManager(
            index_dir=INDEX_DIR,
            embedding_model=EMBEDDING_MODEL,
            bm25_weight=BM25_WEIGHT,
            semantic_weight=SEMANTIC_WEIGHT,
            chunk_size_tokens=CHUNK_SIZE_TOKENS
        )
    return _http_index_manager


@app.post("/search", response_model=List[SearchResultModel])
async def http_search(request: SearchRequest):
    """HTTP endpoint for search."""
    index_manager = get_http_index_manager()
    
    try:
        results = await index_manager.search(
            query=request.query,
            top_k=request.top_k,
            tech_filter=request.tech,
            component_filter=request.component
        )
        
        return [
            SearchResultModel(
                chunk_id=r.chunk_id,
                content=r.content[:500] + "..." if len(r.content) > 500 else r.content,
                source_path=r.source_path,
                tech=r.tech,
                component=r.component,
                topic=r.topic,
                version=r.version,
                file_type=r.file_type,
                chunk_index=r.chunk_index,
                bm25_score=round(r.bm25_score, 4),
                semantic_score=round(r.semantic_score, 4),
                hybrid_score=round(r.hybrid_score, 4)
            )
            for r in results
        ]
    except Exception as e:
        logger.error(f"HTTP search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retrieve/{chunk_id}", response_model=Optional[SearchResultModel])
async def http_retrieve(chunk_id: str):
    """HTTP endpoint for chunk retrieval."""
    index_manager = get_http_index_manager()
    
    chunk = index_manager.retrieve(chunk_id)
    
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    return SearchResultModel(
        chunk_id=chunk.chunk_id,
        content=chunk.content,
        source_path=chunk.source_path,
        tech=chunk.tech,
        component=chunk.component,
        topic=chunk.topic,
        version=chunk.version,
        file_type=chunk.file_type,
        chunk_index=chunk.chunk_index,
        bm25_score=0.0,
        semantic_score=0.0,
        hybrid_score=0.0
    )


@app.get("/status", response_model=IndexStats)
async def http_status():
    """HTTP endpoint for index statistics."""
    index_manager = get_http_index_manager()
    stats = index_manager.get_stats()
    return IndexStats(**stats)


@app.get("/sources", response_model=List[SourceInfo])
async def http_sources(tech: Optional[str] = None):
    """HTTP endpoint for listing sources."""
    index_manager = get_http_index_manager()
    sources = index_manager.list_sources()
    
    if tech:
        sources = [s for s in sources if s.get("tech") == tech.lower()]
    
    return [SourceInfo(**source) for source in sources]


@app.post("/reindex")
async def http_reindex(request: ReindexRequest):
    """HTTP endpoint for reindexing (admin only - localhost)."""
    index_manager = get_http_index_manager()
    
    paths_to_index = []
    
    if request.paths:
        paths_to_index = [Path(p) for p in request.paths]
    elif request.tech:
        tech_key = request.tech.lower()
        if tech_key in TECH_DIRS:
            tech_path = DOCS_ROOT / TECH_DIRS[tech_key]
            if tech_path.exists():
                paths_to_index = [tech_path]
            else:
                raise HTTPException(status_code=404, detail=f"Technology docs not found: {tech_path}")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown technology: {request.tech}")
    else:
        paths_to_index = [DOCS_ROOT]
    
    try:
        stats = await index_manager.index_documents(paths=paths_to_index)
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"HTTP reindex error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MAIN ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run HTTP server
        import uvicorn
        logger.info("Starting HTTP server on http://localhost:8000")
        logger.info("API docs: http://localhost:8000/docs")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        # Run MCP server (stdio)
        try:
            logger.info("Starting docs MCP server (stdio)...")
            mcp.run(transport="stdio")
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

