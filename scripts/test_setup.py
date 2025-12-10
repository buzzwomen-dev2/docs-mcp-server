#!/usr/bin/env python3
"""
Test setup and validation script for the docs MCP server.

Validates installation, index status, and performs sample searches.

Usage:
    python test_setup.py
"""

import asyncio
import logging
import sys
from pathlib import Path

try:
    from search_engine import IndexManager
    from server import DOCS_ROOT, TECH_DIRS
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease install dependencies first:")
    print("  uv sync")
    print("  # or")
    print("  pip install -e .")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_documentation_files():
    """Check if documentation files exist."""
    print("\n" + "=" * 60)
    print("📁 Checking Documentation Files")
    print("=" * 60)
    
    all_exist = True
    for tech, dir_name in TECH_DIRS.items():
        tech_path = DOCS_ROOT / dir_name
        if tech_path.exists():
            file_count = sum(1 for _ in tech_path.rglob("*.md"))
            print(f"✅ {tech}: {dir_name} ({file_count} files)")
        else:
            print(f"❌ {tech}: {dir_name} (NOT FOUND)")
            all_exist = False
    
    return all_exist


async def check_index_status():
    """Check if search index exists and is populated."""
    print("\n" + "=" * 60)
    print("🔍 Checking Search Index")
    print("=" * 60)
    
    try:
        manager = IndexManager()
        stats = manager.get_stats()
        
        if stats["total_chunks"] == 0:
            print("⚠️  Index is empty (needs to be built)")
            print("\nTo build the index, run:")
            print("  python build_index.py")
            return False
        else:
            print(f"✅ Index loaded successfully")
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   Elasticsearch documents: {stats['whoosh_documents']}")
            print(f"   Qdrant documents: {stats['chroma_documents']}")
            print(f"   Technologies: {', '.join(stats['technologies'])}")
            print(f"   Embedding dimension: {stats['embedding_model']}D (FastEmbed)")
            print(f"   Weights: BM25={stats['bm25_weight']}, Semantic={stats['semantic_weight']}")
            return True
            
    except Exception as e:
        print(f"❌ Error checking index: {e}")
        logger.exception("Index check failed")
        return False


async def test_sample_searches(manager: IndexManager):
    """Perform sample searches to validate functionality."""
    print("\n" + "=" * 60)
    print("🔎 Testing Sample Searches")
    print("=" * 60)
    
    test_queries = [
        ("Django authentication", "django", "Testing Django-specific search"),
        ("serializer validation", "drf", "Testing DRF-specific search"),
        ("database connection", None, "Testing cross-technology search"),
    ]
    
    all_passed = True
    
    for query, tech, description in test_queries:
        print(f"\n{description}:")
        print(f"  Query: '{query}'")
        if tech:
            print(f"  Filter: tech={tech}")
        
        try:
            results = await manager.search(
                query=query,
                top_k=3,
                tech_filter=tech
            )
            
            if results:
                print(f"  ✅ Found {len(results)} results")
                for i, result in enumerate(results[:2], 1):
                    print(f"     {i}. {result.topic[:50]}... (score: {result.hybrid_score:.3f})")
                    print(f"        {result.source_path}")
            else:
                print(f"  ⚠️  No results found")
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ Search failed: {e}")
            logger.exception("Search test failed")
            all_passed = False
    
    return all_passed


async def test_index_manager_initialization():
    """Test that IndexManager can be initialized."""
    print("\n" + "=" * 60)
    print("⚙️  Testing IndexManager Initialization")
    print("=" * 60)
    
    try:
        manager = IndexManager()
        print("✅ IndexManager initialized successfully")
        print(f"   Index directory: {manager.index_dir}")
        print(f"   Embedding model: FastEmbed ({manager.embedding_dimension}D)")
        print(f"   BM25 weight: {manager.bm25_weight}")
        print(f"   Semantic weight: {manager.semantic_weight}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize IndexManager: {e}")
        logger.exception("IndexManager initialization failed")
        return False


async def main():
    """Run all validation checks."""
    print("\n" + "=" * 60)
    print("🚀 Docs MCP Server - Setup Validation")
    print("=" * 60)
    
    # Check 1: IndexManager initialization
    init_ok = await test_index_manager_initialization()
    
    if not init_ok:
        print("\n❌ Cannot proceed - IndexManager failed to initialize")
        print("\nPlease check:")
        print("  • Dependencies are installed: uv sync")
        print("  • Python version is 3.13+")
        return 1
    
    # Check 2: Documentation files
    docs_exist = check_documentation_files()
    
    # Check 3: Index status
    index_exists = await check_index_status()
    
    # Check 4: Sample searches (only if index exists)
    if index_exists:
        try:
            manager = IndexManager()
            search_works = await test_sample_searches(manager)
        except Exception as e:
            print(f"\n❌ Error during search tests: {e}")
            logger.exception("Search tests failed")
            search_works = False
    else:
        search_works = False
        print("\n⚠️  Skipping search tests (index not built)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    
    checks = {
        "IndexManager initialization": init_ok,
        "Documentation files": docs_exist,
        "Search index": index_exists,
        "Sample searches": search_works if index_exists else None
    }
    
    for check_name, status in checks.items():
        if status is True:
            print(f"✅ {check_name}: PASS")
        elif status is False:
            print(f"❌ {check_name}: FAIL")
        else:
            print(f"⊘  {check_name}: SKIPPED")
    
    # Final verdict
    print("\n" + "=" * 60)
    
    if all(v is True for v in checks.values() if v is not None):
        print("✅ All checks passed! Server is ready to use.")
        print("\nNext steps:")
        print("  • Run MCP server: python server.py")
        print("  • Run HTTP API: python server.py --http")
        print("  • Test with inspector: npx @modelcontextprotocol/inspector python server.py")
        return 0
    elif not index_exists:
        print("⚠️  Setup incomplete: Index needs to be built")
        print("\nNext steps:")
        print("  1. Build index: python build_index.py")
        print("  2. Run validation again: python test_setup.py")
        return 1
    else:
        print("❌ Some checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
