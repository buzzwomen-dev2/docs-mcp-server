#!/usr/bin/env python3
"""
Helper script to build the search index for the documentation server.

Usage:
    python build_index.py                    # Index all docs
    python build_index.py --tech django      # Index only Django docs
    python build_index.py --clear            # Clear and rebuild
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from search_engine import IndexManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TECH_DIRS = {
    "django": "docs/django-6.0",
    "drf": "docs/drf-3.16.1",
    "psycopg": "docs/psycopg-3.3.1"
}


async def build_index(tech: str | None = None, clear: bool = False):
    """Build the search index."""
    logger.info("Initializing IndexManager...")
    manager = IndexManager()
    
    if clear:
        logger.info("Clearing existing index...")
        await manager.clear_index()
    
    # Determine paths to index
    if tech:
        if tech not in TECH_DIRS:
            logger.error(f"Unknown technology: {tech}")
            logger.info(f"Available: {', '.join(TECH_DIRS.keys())}")
            sys.exit(1)
        
        tech_path = Path(TECH_DIRS[tech])
        if not tech_path.exists():
            logger.error(f"Documentation not found: {tech_path}")
            sys.exit(1)
        
        paths = [tech_path]
        logger.info(f"Indexing {tech} documentation from {tech_path}")
    else:
        paths = [Path("docs")]
        logger.info("Indexing all documentation from docs/")
    
    # Index with progress
    async def progress_callback(current: int, total: int, message: str):
        pct = (current / total * 100) if total > 0 else 0
        logger.info(f"[{pct:5.1f}%] {message}")
    
    try:
        stats = await manager.index_documents(
            paths=paths,
            progress_callback=progress_callback
        )
        
        logger.info("=" * 60)
        logger.info("Indexing Complete!")
        logger.info(f"  Files processed: {stats['files_processed']}")
        logger.info(f"  Chunks created:  {stats['chunks_created']}")
        logger.info(f"  Errors:          {stats['errors']}")
        logger.info("=" * 60)
        
        # Show final stats
        final_stats = manager.get_stats()
        logger.info(f"Total chunks in index: {final_stats['total_chunks']}")
        logger.info(f"Technologies: {', '.join(final_stats['technologies'])}")
        logger.info(f"Index directory: {final_stats['index_directory']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}", exc_info=True)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Build search index for documentation server"
    )
    parser.add_argument(
        "--tech",
        choices=list(TECH_DIRS.keys()),
        help="Index specific technology docs only"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing index before rebuilding"
    )
    
    args = parser.parse_args()
    
    return asyncio.run(build_index(tech=args.tech, clear=args.clear))


if __name__ == "__main__":
    sys.exit(main())
