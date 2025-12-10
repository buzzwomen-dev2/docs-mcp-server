#!/usr/bin/env python3
"""
File watcher for automatic incremental indexing.

Monitors the docs/ directory and automatically reindexes changed files.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from search_engine import IndexManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocsChangeHandler(FileSystemEventHandler):
    """Handle file system changes in docs directory."""
    
    def __init__(self, index_manager: IndexManager, debounce_seconds: float = 2.0):
        super().__init__()
        self.index_manager = index_manager
        self.debounce_seconds = debounce_seconds
        self.pending_changes = set()
        self.last_change_time = 0
        self.reindex_task = None
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(str(event.src_path))
        if file_path.suffix in {'.md', '.txt', '.rst', '.py', '.json', '.yaml', '.yml', '.html'}:
            logger.info(f"Detected change: {file_path.name}")
            self.pending_changes.add(file_path)
            self.last_change_time = time.time()
            self._schedule_reindex()
    
    def on_created(self, event):
        """Handle file creation events."""
        from watchdog.events import FileModifiedEvent
        modified_event = FileModifiedEvent(event.src_path)
        self.on_modified(modified_event)
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if event.is_directory:
            return
        
        file_path = Path(str(event.src_path))
        if file_path.suffix in {'.md', '.txt', '.rst', '.py', '.json', '.yaml', '.yml', '.html'}:
            logger.info(f"Detected deletion: {file_path.name}")
            # Remove from index
            self.index_manager._remove_file_from_index(file_path)
            # Remove from checksums
            file_key = str(file_path)
            if file_key in self.index_manager.file_checksums:
                del self.index_manager.file_checksums[file_key]
                self.index_manager._save_checksums()
    
    def _schedule_reindex(self):
        """Schedule a debounced reindex operation."""
        if self.reindex_task and not self.reindex_task.done():
            return  # Already scheduled
        
        self.reindex_task = asyncio.create_task(self._debounced_reindex())
    
    async def _debounced_reindex(self):
        """Wait for changes to settle, then reindex."""
        while True:
            await asyncio.sleep(0.5)
            
            # Check if changes have settled
            if time.time() - self.last_change_time >= self.debounce_seconds:
                break
        
        if not self.pending_changes:
            return
        
        logger.info(f"Reindexing {len(self.pending_changes)} changed files...")
        
        try:
            files_to_index = list(self.pending_changes)
            self.pending_changes.clear()
            
            stats = await self.index_manager.index_documents(
                paths=files_to_index,
                force_reindex=False  # Incremental update
            )
            
            logger.info(f"Incremental index complete: {stats}")
            
        except Exception as e:
            logger.error(f"Error during incremental indexing: {e}", exc_info=True)


async def main():
    """Main watcher loop."""
    logger.info("Initializing IndexManager...")
    index_manager = IndexManager()
    
    logger.info(f"Starting file watcher on docs/")
    logger.info("Press Ctrl+C to stop")
    
    # Set up file system observer
    event_handler = DocsChangeHandler(index_manager, debounce_seconds=2.0)
    observer = Observer()
    observer.schedule(event_handler, "docs", recursive=True)
    observer.start()
    
    try:
        # Keep the script running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
    
    observer.join()
    logger.info("Watcher stopped")


if __name__ == "__main__":
    asyncio.run(main())
