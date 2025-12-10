#!/usr/bin/env python3
"""
Hybrid Search Engine for Documentation MCP Server.

Combines:
- Semantic search using FastEmbed + Qdrant
- Keyword search using Elasticsearch BM25
- Weighted hybrid scoring (0.4 BM25 + 0.6 semantic by default)
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import psutil
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles

from elasticsearch import Elasticsearch, helpers
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from semantic_text_splitter import MarkdownSplitter, TextSplitter

logger = logging.getLogger(__name__)


# ==================== DATA MODELS ====================


@dataclass
class DocumentChunk:
    """Represents a chunk of a document with metadata."""
    chunk_id: str
    content: str
    source_path: str
    tech: str
    component: str
    topic: str
    version: str
    file_type: str
    chunk_index: int
    start_line: int
    end_line: int
    timestamp: datetime
    file_checksum: str = ""  # SHA256 hash for incremental updates


@dataclass
class SearchResult:
    """Search result with hybrid scoring."""
    chunk_id: str
    content: str
    source_path: str
    tech: str
    component: str
    topic: str
    version: str
    file_type: str
    chunk_index: int
    bm25_score: float
    semantic_score: float
    hybrid_score: float


# ==================== INDEX MANAGER ====================


class IndexManager:
    """
    Manages hybrid search indices for documentation.
    
    Combines:
    - Qdrant for semantic vector search (FastEmbed)
    - Elasticsearch for BM25 keyword search
    - Rich metadata tagging for filtering
    
    Redis-ready: Prepared for caching layer (not yet implemented)
    """
    
    def __init__(
        self,
        index_dir: str = ".index",
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        bm25_weight: float = 0.4,
        semantic_weight: float = 0.6,
        chunk_size_tokens: int = 100,
        chunk_overlap_words: int = 30,
        # Elasticsearch config
        es_host: str = "http://localhost:9200",
        es_index_name: str = "docs_index",
        # Qdrant config
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        qdrant_collection: str = "docs_collection",
        # Redis config (for future use)
        redis_host: Optional[str] = None,
        redis_port: int = 6379,
        redis_enabled: bool = False,
    ):
        """
        Initialize the IndexManager.
        
        Args:
            index_dir: Directory to store local metadata
            embedding_model: FastEmbed model name
            bm25_weight: Weight for BM25 scores (default 0.4)
            semantic_weight: Weight for semantic scores (default 0.6)
            chunk_size_tokens: Target chunk size in tokens (100 = ~75 words)
            chunk_overlap_words: Overlap between chunks in words
            es_host: Elasticsearch host URL
            es_index_name: Elasticsearch index name
            qdrant_host: Qdrant host
            qdrant_port: Qdrant port
            qdrant_collection: Qdrant collection name
            redis_host: Redis host (optional, for future caching)
            redis_port: Redis port
            redis_enabled: Enable Redis caching (not yet implemented)
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        
        # Validate weights
        if not (0 <= bm25_weight <= 1 and 0 <= semantic_weight <= 1):
            raise ValueError(
                f"Weights must be between 0 and 1: bm25={bm25_weight}, semantic={semantic_weight}"
            )
        if abs((bm25_weight + semantic_weight) - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0: bm25={bm25_weight} + semantic={semantic_weight} = "
                f"{bm25_weight + semantic_weight}"
            )
        
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_words = chunk_overlap_words
        
        # Separate locks for read/write to prevent blocking searches during indexing
        self._write_lock = asyncio.Lock()  # For indexing operations
        self._read_lock = asyncio.Lock()   # For search operations
        
        # Memory limit (80% of available RAM)
        self.max_memory_bytes = int(psutil.virtual_memory().total * 0.8)
        
        # Disk space check (warn if < 1GB free)
        self.min_disk_space_bytes = 1024 * 1024 * 1024
        
        # Metadata cache
        self.metadata_cache_path = self.index_dir / "chunks_metadata.pkl"
        self.checksum_cache_path = self.index_dir / "file_checksums.json"
        
        # Initialize semantic text splitters for better chunking
        self.markdown_splitter = MarkdownSplitter(capacity=chunk_size_tokens * 4)  # ~100 tokens = ~400 chars
        self.text_splitter = TextSplitter(capacity=chunk_size_tokens * 4)
        
        # Load file checksums for incremental updates
        self.file_checksums: Dict[str, str] = self._load_checksums()
        
        # Initialize FastEmbed (CPU-optimized, no GPU required)
        logger.info(f"Loading FastEmbed model: {embedding_model}")
        self.embedding_model = TextEmbedding(model_name=embedding_model)
        self.embedding_dimension = 384  # bge-small-en-v1.5 dimension
        logger.info(f"FastEmbed initialized: {self.embedding_dimension}D embeddings")
        
        # Initialize Elasticsearch
        logger.info(f"Connecting to Elasticsearch: {es_host}")
        try:
            self.es_client = Elasticsearch(
                [es_host],
                max_retries=5,
                retry_on_timeout=True,
                request_timeout=60  # Increased from 30s to 60s for large batches
            )
            if not self.es_client.ping():
                raise ConnectionError("Elasticsearch ping failed")
            logger.info("✓ Elasticsearch connected successfully")
        except Exception as e:
            logger.error(f"❌ Could not connect to Elasticsearch at {es_host}")
            logger.error(f"   Error: {e}")
            logger.error(f"   Make sure Elasticsearch is running: docker run -p 9200:9200 -e 'discovery.type=single-node' elasticsearch:8.11.0")
            raise ConnectionError(f"Elasticsearch connection failed: {e}")
        
        self.es_index_name = es_index_name
        self._create_elasticsearch_index()
        
        # Initialize Qdrant
        logger.info(f"Connecting to Qdrant: {qdrant_host}:{qdrant_port}")
        try:
            self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=5)
            # Test connection
            self.qdrant_client.get_collections()
            logger.info("✓ Qdrant connected successfully")
        except Exception as e:
            logger.error(f"❌ Could not connect to Qdrant at {qdrant_host}:{qdrant_port}")
            logger.error(f"   Error: {e}")
            logger.error(f"   Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
            raise ConnectionError(f"Qdrant connection failed: {e}")
        
        self.qdrant_collection = qdrant_collection
        self._create_qdrant_collection()
        
        # Redis setup (prepared but not implemented)
        self.redis_enabled = redis_enabled
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_client = None
        # TODO: Uncomment when adding Redis
        # if redis_enabled and redis_host:
        #     import redis
        #     self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        #     logger.info(f"Redis caching enabled: {redis_host}:{redis_port}")
        
        # Chunk metadata cache (load from disk if available)
        self.chunks_metadata: Dict[str, DocumentChunk] = {}
        self._load_metadata_cache()
        
        # Query log
        self.query_log_path = self.index_dir / "search_queries.log"
        
        logger.info("IndexManager initialized successfully")
    
    def _create_elasticsearch_index(self):
        """Create Elasticsearch index with optimized mappings for documentation."""
        if self.es_client.indices.exists(index=self.es_index_name):
            logger.info(f"Elasticsearch index '{self.es_index_name}' already exists")
            return
        
        mappings = {
            "properties": {
                "chunk_id": {"type": "keyword"},
                "content": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "source_path": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "tech": {"type": "keyword"},
                "component": {"type": "text", "analyzer": "standard", "fields": {"keyword": {"type": "keyword"}}},
                "topic": {"type": "text", "analyzer": "standard"},
                "version": {"type": "keyword"},
                "file_type": {"type": "keyword"},
                "chunk_index": {"type": "integer"},
                "timestamp": {"type": "date"}
            }
        }
        
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,  # Single-node setup
            "analysis": {
                "analyzer": {
                    "code_analyzer": {
                        "type": "standard",
                        "stopwords": "_none_"  # Preserve code terms
                    }
                }
            }
        }
        
        self.es_client.indices.create(
            index=self.es_index_name,
            mappings=mappings,
            settings=settings
        )
        logger.info(f"Created Elasticsearch index: {self.es_index_name}")
    
    def _create_qdrant_collection(self):
        """Create Qdrant collection for vector search."""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.qdrant_collection in collection_names:
            logger.info(f"Qdrant collection '{self.qdrant_collection}' already exists")
            return
        
        self.qdrant_client.create_collection(
            collection_name=self.qdrant_collection,
            vectors_config=VectorParams(
                size=self.embedding_dimension,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Created Qdrant collection: {self.qdrant_collection}")
    
    def _chunk_id_to_point_id(self, chunk_id: str) -> int:
        """Convert chunk_id to deterministic integer ID for Qdrant (collision-free)."""
        # Use first 8 bytes of SHA256 as positive int64
        hash_bytes = hashlib.sha256(chunk_id.encode('utf-8')).digest()
        return int.from_bytes(hash_bytes[:8], 'big') & 0x7FFFFFFFFFFFFFFF
    
    async def _retry_with_backoff(self, func, *args, max_retries=3, initial_delay=1.0, **kwargs):
        """Retry a function with exponential backoff on failure."""
        last_exception = Exception("No attempts were made")
        
        for attempt in range(max_retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {max_retries} attempts failed: {e}")
        
        raise last_exception
    
    def _check_memory_usage(self) -> bool:
        """Check if memory usage is within safe limits."""
        current_memory = psutil.Process().memory_info().rss
        usage_percent = (current_memory / psutil.virtual_memory().total) * 100
        
        if usage_percent > 70:
            logger.warning(f"High memory usage: {usage_percent:.1f}%")
            return False
        return True
    
    def _check_disk_space(self) -> bool:
        """Check if sufficient disk space is available."""
        try:
            disk_usage = psutil.disk_usage(str(self.index_dir))
            if disk_usage.free < self.min_disk_space_bytes:
                logger.error(f"Low disk space: {disk_usage.free / (1024**3):.2f}GB free")
                return False
            return True
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
            return True  # Assume OK if check fails
    
    def _compute_file_checksum(self, file_path: Path) -> str:
        """Compute SHA256 checksum of file content for change detection."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing checksum for {file_path}: {e}")
            return ""
    
    def _load_checksums(self) -> Dict[str, str]:
        """Load file checksums from disk."""
        if self.checksum_cache_path.exists():
            try:
                with open(self.checksum_cache_path, 'r') as f:
                    checksums = json.load(f)
                logger.info(f"Loaded checksums for {len(checksums)} files")
                return checksums
            except Exception as e:
                logger.warning(f"Could not load checksums: {e}")
        return {}
    
    def _save_checksums(self):
        """Save file checksums to disk."""
        if not self._check_disk_space():
            logger.error("Insufficient disk space to save checksums")
            return
        
        try:
            # Write to temp file first, then atomic rename
            temp_path = self.checksum_cache_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(self.file_checksums, f, indent=2)
            temp_path.replace(self.checksum_cache_path)
            logger.debug(f"Saved checksums for {len(self.file_checksums)} files")
        except Exception as e:
            logger.error(f"Could not save checksums: {e}")
    
    def _has_file_changed(self, file_path: Path) -> bool:
        """Check if file has changed since last index."""
        current_checksum = self._compute_file_checksum(file_path)
        if not current_checksum:
            return True  # Treat errors as changed
        
        file_key = str(file_path)
        old_checksum = self.file_checksums.get(file_key)
        
        if old_checksum is None:
            return True  # New file
        
        return current_checksum != old_checksum
    
    def _remove_file_from_index(self, file_path: Path):
        """Remove all chunks for a file from indices."""
        file_key = str(file_path)
        
        # Find chunks for this file
        chunks_to_remove = [
            chunk_id for chunk_id, chunk in self.chunks_metadata.items()
            if chunk.source_path == file_key
        ]
        
        if not chunks_to_remove:
            return
        
        logger.info(f"Removing {len(chunks_to_remove)} chunks for {file_path.name}")
        
        # Remove from Elasticsearch
        try:
            actions = [
                {"_op_type": "delete", "_index": self.es_index_name, "_id": chunk_id}
                for chunk_id in chunks_to_remove
            ]
            helpers.bulk(self.es_client, actions, refresh=True)
        except Exception as e:
            logger.error(f"Error removing from Elasticsearch: {e}")
        
        # Remove from Qdrant
        try:
            from qdrant_client.models import PointIdsList
            point_ids = [self._chunk_id_to_point_id(cid) for cid in chunks_to_remove]
            self.qdrant_client.delete(
                collection_name=self.qdrant_collection,
                points_selector=PointIdsList(points=point_ids)  # type: ignore
            )
        except Exception as e:
            logger.error(f"Error removing from Qdrant: {e}")
        
        # Remove from metadata
        for chunk_id in chunks_to_remove:
            del self.chunks_metadata[chunk_id]
    
    def _load_metadata_cache(self):
        """Load metadata from disk cache."""
        if self.metadata_cache_path.exists():
            try:
                with open(self.metadata_cache_path, 'rb') as f:
                    self.chunks_metadata = pickle.load(f)
                logger.info(f"Loaded {len(self.chunks_metadata)} chunks from metadata cache")
            except Exception as e:
                logger.warning(f"Could not load metadata cache: {e}")
                self.chunks_metadata = {}
        else:
            self.chunks_metadata = {}
    
    def _save_metadata_cache(self):
        """Save metadata to disk cache."""
        if not self._check_disk_space():
            logger.error("Insufficient disk space to save metadata cache")
            return
        
        try:
            # Write to temp file first, then atomic rename
            temp_path = self.metadata_cache_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                pickle.dump(self.chunks_metadata, f)
            temp_path.replace(self.metadata_cache_path)
            logger.debug(f"Saved {len(self.chunks_metadata)} chunks to metadata cache")
        except Exception as e:
            logger.error(f"Could not save metadata cache: {e}")
    
    def _log_query(self, query: str, filters: Optional[Dict] = None, result_count: int = 0):
        """Log search queries for debugging and tuning."""
        timestamp = datetime.now().isoformat()
        filters_str = str(filters) if filters else "none"
        log_entry = f"{timestamp} | query='{query}' | filters={filters_str} | results={result_count}\n"
        
        with open(self.query_log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def _extract_metadata_from_path(self, file_path: Path) -> Tuple[str, str, str]:
        """
        Extract tech, component, version from file path.
        
        Examples:
            docs/django-6.0/ref/models/fields.md -> (django, models, 6.0)
            docs/drf-3.16.1/api-guide/serializers.md -> (drf, serializers, 3.16.1)
        """
        parts = file_path.parts
        
        # Extract tech and version from directory name
        tech = "unknown"
        version = "unknown"
        
        for part in parts:
            if "django-" in part and "drf" not in part:
                tech = "django"
                version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', part)
                version = version_match.group(1) if version_match else "unknown"
                break
            elif "drf-" in part:
                tech = "drf"
                version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', part)
                version = version_match.group(1) if version_match else "unknown"
                break
            elif "psycopg-" in part:
                tech = "psycopg"
                version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', part)
                version = version_match.group(1) if version_match else "unknown"
                break
            elif part in ["nuxt", "redis", "architecture"]:
                tech = part
                break
        
        # Extract component from path
        component = "general"
        if len(parts) >= 3:
            for part in reversed(parts[:-1]):
                if part not in ["docs", tech] and not any(char.isdigit() for char in part):
                    component = part
                    break
        
        return tech, component, version
    
    def _extract_topic_from_content(self, content: str, file_path: Path) -> str:
        """Extract topic from content (first heading or filename)."""
        lines = content.strip().split('\n')
        
        # Try to find first markdown heading
        for line in lines[:20]:
            if line.strip().startswith('#'):
                topic = line.strip('#').strip()
                if topic:
                    return topic[:100]
        
        # Fall back to filename
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()
    
    def _chunk_content(self, content: str, file_type: str) -> List[Tuple[str, int, int]]:
        """
        Chunk content using semantic splitting based on file type.
        
        Uses semantic-text-splitter to respect document structure:
        - Markdown: Splits on headings, paragraphs, code blocks
        - Code files: Splits on functions, classes, logical blocks
        - Plain text: Splits on paragraphs and sentences
        
        Returns:
            List of (chunk_content, start_line, end_line) tuples
        """
        if not content.strip():
            return []
        
        lines = content.split('\n')
        
        try:
            # Choose splitter based on file type
            if file_type in ['.md', '.markdown']:
                # Markdown-aware splitting (respects headings, code blocks, lists)
                chunk_texts = self.markdown_splitter.chunks(content)
            elif file_type in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs']:
                # For code, use text splitter but with larger chunks
                text_splitter = TextSplitter(capacity=self.chunk_size_tokens * 6)  # Larger for code
                chunk_texts = text_splitter.chunks(content)
            else:
                # Generic text splitting (respects sentences and paragraphs)
                chunk_texts = self.text_splitter.chunks(content)
            
            # Map chunks back to line numbers
            chunks = []
            content_pos = 0
            
            for chunk_text in chunk_texts:
                if not chunk_text.strip():
                    continue
                
                # Find chunk in original content
                chunk_start = content.find(chunk_text, content_pos)
                if chunk_start == -1:
                    # Fallback if exact match fails
                    chunk_start = content_pos
                
                # Count lines up to chunk start
                start_line = content[:chunk_start].count('\n')
                
                # Count lines in chunk
                end_line = start_line + chunk_text.count('\n')
                
                chunks.append((chunk_text, start_line, end_line))
                content_pos = chunk_start + len(chunk_text)
            
            return chunks if chunks else [(content, 0, len(lines))]
            
        except Exception as e:
            logger.warning(f"Semantic splitting failed, falling back to simple split: {e}")
            # Fallback to simple chunking
            max_chars = self.chunk_size_tokens * 4  # ~4 chars per token
            chunks = []
            for i in range(0, len(content), max_chars):
                chunk_text = content[i:i + max_chars]
                start_line = content[:i].count('\n')
                end_line = content[:i + len(chunk_text)].count('\n')
                chunks.append((chunk_text, start_line, end_line))
            return chunks if chunks else [(content, 0, len(lines))]
    
    async def index_documents(
        self,
        paths: List[Path],
        progress_callback=None,
        force_reindex: bool = False
    ) -> Dict[str, int]:
        """
        Index documents from given paths with incremental update support.
        
        Args:
            paths: List of file or directory paths to index
            progress_callback: Optional async callback(current, total, message)
            force_reindex: If True, reindex all files regardless of checksums
        
        Returns:
            Statistics dict with counts
        """
        stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "files_updated": 0,
            "chunks_created": 0,
            "chunks_removed": 0,
            "errors": 0
        }
        
        # Track chunks added in this session for rollback if needed
        chunks_added_this_session = []
        
        # Collect all files to process
        all_files = []
        supported_extensions = {'.md', '.txt', '.rst', '.py', '.json', '.yaml', '.yml', '.html'}
        exclude_dirs = {'.index', '.git', 'node_modules', 'venv', '.venv', '__pycache__', '.pytest_cache'}
        
        def should_skip_dir(dir_path: Path) -> bool:
            return any(part in exclude_dirs for part in dir_path.parts)
        
        for path in paths:
            if path.is_file() and path.suffix in supported_extensions:
                all_files.append(path)
            elif path.is_dir():
                for ext in supported_extensions:
                    for file_path in path.rglob(f"*{ext}"):
                        if not should_skip_dir(file_path):
                            all_files.append(file_path)
        
        # Filter to only changed files (incremental update)
        files_to_process = []
        for file_path in all_files:
            if force_reindex or self._has_file_changed(file_path):
                files_to_process.append(file_path)
            else:
                stats["files_skipped"] += 1
        
        total_files = len(all_files)
        files_to_index = len(files_to_process)
        
        if not force_reindex:
            logger.info(f"Found {total_files} files, {files_to_index} changed, {stats['files_skipped']} unchanged")
        else:
            logger.info(f"Found {total_files} files to index (force reindex)")
        
        if progress_callback:
            await progress_callback(0, files_to_index, "Starting indexing...")
        
        # Process files in batches with dynamic sizing based on memory
        file_batch_size = 10
        initial_chunk_batch_size = 100
        chunk_batch_size = initial_chunk_batch_size
        all_chunks = []
        
        try:
            for batch_idx in range(0, files_to_index, file_batch_size):
                batch_files = files_to_process[batch_idx:batch_idx + file_batch_size]
                
                for file_idx, file_path in enumerate(batch_files):
                    try:
                        current_file = batch_idx + file_idx + 1
                        
                        if progress_callback:
                            await progress_callback(
                                current_file,
                                files_to_index,
                                f"Processing {file_path.name}..."
                            )
                        
                        # Remove old chunks for this file (if updating)
                        file_key = str(file_path)
                        if file_key in self.file_checksums:
                            old_chunk_count = sum(1 for c in self.chunks_metadata.values() if c.source_path == file_key)
                            if old_chunk_count > 0:
                                self._remove_file_from_index(file_path)
                                stats["chunks_removed"] += old_chunk_count
                                stats["files_updated"] += 1
                        
                        # Read file asynchronously
                        try:
                            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                                content = await f.read()
                            # Warn about encoding issues
                            if '\ufffd' in content:  # Unicode replacement character
                                logger.warning(f"Encoding issues detected in {file_path} - some characters were replaced")
                        except (IOError, OSError) as e:
                            logger.error(f"Error reading {file_path}: {e}")
                            stats["errors"] += 1
                            continue
                        
                        if not content.strip():
                            continue
                        
                        # Compute and store checksum for incremental updates
                        file_checksum = self._compute_file_checksum(file_path)
                        self.file_checksums[file_key] = file_checksum
                        
                        # Save checksums incrementally every 10 files
                        if stats["files_processed"] % 10 == 0:
                            self._save_checksums()
                        
                        # Extract metadata
                        tech, component, version = self._extract_metadata_from_path(file_path)
                        topic = self._extract_topic_from_content(content, file_path)
                        file_type = file_path.suffix
                        timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        # Chunk content
                        chunks = self._chunk_content(content, file_type)
                        
                        # Create chunk IDs
                        try:
                            path_parts = file_path.relative_to(Path.cwd()).parts
                        except ValueError:
                            path_parts = file_path.parts
                        
                        path_prefix = "_".join(str(p) for p in path_parts).replace("/", "_").replace(".", "_")[:100]
                        
                        for chunk_idx, (chunk_content, start_line, end_line) in enumerate(chunks):
                            # Use deterministic hash for stable chunk IDs across sessions
                            content_hash = hashlib.sha256(
                                (chunk_content + str(start_line) + str(end_line)).encode('utf-8')
                            ).hexdigest()[:12]
                            chunk_id = f"{path_prefix}_{chunk_idx}_{content_hash}"
                            
                            chunk = DocumentChunk(
                                chunk_id=chunk_id,
                                content=chunk_content,
                                source_path=str(file_path),
                                tech=tech,
                                component=component,
                                topic=topic,
                                version=version,
                                file_type=file_type,
                                chunk_index=chunk_idx,
                                start_line=start_line,
                                end_line=end_line,
                                timestamp=timestamp,
                                file_checksum=file_checksum
                            )
                            
                            all_chunks.append(chunk)
                            self.chunks_metadata[chunk_id] = chunk
                            chunks_added_this_session.append(chunk_id)
                        
                        stats["files_processed"] += 1
                        stats["chunks_created"] += len(chunks)
                        
                        # Check memory and adjust batch size dynamically
                        if not self._check_memory_usage():
                            # Reduce batch size if memory is high
                            chunk_batch_size = max(10, chunk_batch_size // 2)
                            logger.warning(f"Reduced batch size to {chunk_batch_size} due to memory pressure")
                            
                            # Force indexing current batch if any
                            if all_chunks:
                                logger.info(f"Indexing batch of {len(all_chunks)} chunks (memory pressure)...")
                                await self._index_chunks(all_chunks)
                                all_chunks = []
                        
                        # Index in batches
                        if len(all_chunks) >= chunk_batch_size:
                            logger.info(f"Indexing batch of {len(all_chunks)} chunks...")
                            await self._index_chunks(all_chunks)
                            all_chunks = []
                            
                            # Restore batch size if memory is ok
                            if self._check_memory_usage() and chunk_batch_size < initial_chunk_batch_size:
                                chunk_batch_size = min(initial_chunk_batch_size, chunk_batch_size * 2)
                                logger.info(f"Increased batch size to {chunk_batch_size}")
                    
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        stats["errors"] += 1
        
            # Index remaining chunks
            if all_chunks:
                if progress_callback:
                    await progress_callback(
                        files_to_index,
                        files_to_index,
                        f"Indexing final batch of {len(all_chunks)} chunks..."
                    )
                await self._index_chunks(all_chunks)
            
            # Save checksums for incremental updates
            self._save_checksums()
            
            # Save metadata cache after successful indexing
            self._save_metadata_cache()
            
            logger.info(f"Indexing complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            logger.error(f"Rolling back {len(chunks_added_this_session)} chunks added in this session")
            
            # Rollback: remove chunks from metadata and indices
            try:
                await self._rollback_chunks(chunks_added_this_session)
                stats["errors"] += 1
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
            
            raise
    
    async def _rollback_chunks(self, chunk_ids: List[str]):
        """Rollback chunks added in current session on failure."""
        if not chunk_ids:
            return
        
        logger.info(f"Rolling back {len(chunk_ids)} chunks...")
        
        # Remove from Elasticsearch
        try:
            actions = [
                {"_op_type": "delete", "_index": self.es_index_name, "_id": chunk_id}
                for chunk_id in chunk_ids
            ]
            helpers.bulk(self.es_client, actions, refresh=True, raise_on_error=False)
        except Exception as e:
            logger.error(f"Error removing from Elasticsearch during rollback: {e}")
        
        # Remove from Qdrant
        try:
            from qdrant_client.models import PointIdsList
            point_ids = [self._chunk_id_to_point_id(cid) for cid in chunk_ids]
            self.qdrant_client.delete(
                collection_name=self.qdrant_collection,
                points_selector=PointIdsList(points=point_ids)  # type: ignore
            )
        except Exception as e:
            logger.error(f"Error removing from Qdrant during rollback: {e}")
        
        # Remove from metadata
        for chunk_id in chunk_ids:
            if chunk_id in self.chunks_metadata:
                del self.chunks_metadata[chunk_id]
        
        logger.info(f"Rollback complete for {len(chunk_ids)} chunks")
    
    async def _index_chunks(self, chunks: List[DocumentChunk]):
        """Index chunks into both Elasticsearch and Qdrant with retry logic."""
        async with self._write_lock:
            # Index into Elasticsearch (BM25) with retry
            logger.info(f"Indexing {len(chunks)} chunks into Elasticsearch...")
            try:
                actions = []
                for chunk in chunks:
                    action = {
                        "_index": self.es_index_name,
                        "_id": chunk.chunk_id,
                        "_source": {
                            "chunk_id": chunk.chunk_id,
                            "content": chunk.content,
                            "source_path": chunk.source_path,
                            "tech": chunk.tech,
                            "component": chunk.component,
                            "topic": chunk.topic,
                            "version": chunk.version,
                            "file_type": chunk.file_type,
                            "chunk_index": chunk.chunk_index,
                            "timestamp": chunk.timestamp.isoformat()
                        }
                    }
                    actions.append(action)
                
                # Retry bulk operation with exponential backoff
                # Process in batches to avoid overwhelming Elasticsearch
                es_batch_size = 500
                for i in range(0, len(actions), es_batch_size):
                    batch_actions = actions[i:i + es_batch_size]
                    
                    success, failed = await self._retry_with_backoff(
                        helpers.bulk,
                        self.es_client,
                        batch_actions,
                        refresh=False,  # Don't refresh on each batch
                        raise_on_error=False,  # Get detailed error info
                        max_retries=3
                    )
                    
                    if failed:
                        logger.error(f"Elasticsearch batch had {len(failed)} failures")
                        for item in failed[:5]:  # Log first 5 failures
                            logger.error(f"Failed item: {item}")
                    
                    # Rate limiting: small delay between batches
                    if i + es_batch_size < len(actions):
                        await asyncio.sleep(0.1)
                
                # Refresh index after all batches
                self.es_client.indices.refresh(index=self.es_index_name)
                logger.info("Elasticsearch indexing complete")
            except Exception as e:
                logger.error(f"Error indexing to Elasticsearch: {e}")
                # Rollback: attempt to remove from Elasticsearch
                try:
                    delete_actions = [
                        {"_op_type": "delete", "_index": self.es_index_name, "_id": chunk.chunk_id}
                        for chunk in chunks
                    ]
                    helpers.bulk(self.es_client, delete_actions, raise_on_error=False)
                    logger.info("Rolled back Elasticsearch documents after error")
                except Exception as rollback_error:
                    logger.error(f"Elasticsearch rollback failed: {rollback_error}")
                raise
            
            # Generate embeddings with FastEmbed and index into Qdrant
            # Process in smaller batches to prevent memory exhaustion
            try:
                contents = [chunk.content for chunk in chunks]
                logger.info(f"Generating embeddings for {len(contents)} chunks with FastEmbed...")
                
                # Process embeddings in batches of 50 to avoid OOM
                embedding_batch_size = 50
                all_points = []
                
                for batch_start in range(0, len(chunks), embedding_batch_size):
                    batch_end = min(batch_start + embedding_batch_size, len(chunks))
                    batch_contents = contents[batch_start:batch_end]
                    batch_chunks = chunks[batch_start:batch_end]
                    
                    # Generate embeddings for this batch
                    embeddings_generator = self.embedding_model.embed(batch_contents)
                    batch_embeddings = list(embeddings_generator)
                    
                    # Prepare Qdrant points for this batch
                    for idx, chunk in enumerate(batch_chunks):
                        point = PointStruct(
                            id=self._chunk_id_to_point_id(chunk.chunk_id),
                            vector=batch_embeddings[idx].tolist(),
                            payload={
                                "chunk_id": chunk.chunk_id,
                                "source_path": chunk.source_path,
                                "tech": chunk.tech,
                                "component": chunk.component,
                                "topic": chunk.topic,
                                "version": chunk.version,
                                "file_type": chunk.file_type,
                                "chunk_index": chunk.chunk_index
                            }
                        )
                        all_points.append(point)
                    
                    logger.debug(f"Generated embeddings for batch {batch_start}-{batch_end}")
                
                logger.info("Embedding generation complete")
                
                # Upsert to Qdrant with retry and rate limiting
                # Split into smaller batches for Qdrant (max 100 points per request)
                qdrant_batch_size = 100
                for i in range(0, len(all_points), qdrant_batch_size):
                    batch_points = all_points[i:i + qdrant_batch_size]
                    
                    await self._retry_with_backoff(
                        self.qdrant_client.upsert,
                        collection_name=self.qdrant_collection,
                        points=batch_points,
                        max_retries=3
                    )
                    
                    # Rate limiting: small delay between batches
                    if i + qdrant_batch_size < len(all_points):
                        await asyncio.sleep(0.1)
                
                logger.info(f"Successfully indexed {len(chunks)} chunks to Qdrant")
                
            except Exception as e:
                logger.error(f"Error indexing to Qdrant: {e}")
                # Rollback: attempt to remove from Qdrant
                try:
                    from qdrant_client.models import PointIdsList
                    point_ids = [self._chunk_id_to_point_id(c.chunk_id) for c in chunks]
                    self.qdrant_client.delete(
                        collection_name=self.qdrant_collection,
                        points_selector=PointIdsList(points=point_ids)  # type: ignore
                    )
                    logger.info("Rolled back Qdrant points after error")
                except Exception as rollback_error:
                    logger.error(f"Qdrant rollback failed: {rollback_error}")
                raise
    
    def _is_code_heavy(self, content: str) -> bool:
        """Detect if chunk is >70% code."""
        lines = content.split('\n')
        if not lines:
            return False
        
        code_lines = 0
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('```') or stripped.startswith('~~~'):
                in_code_block = not in_code_block
                code_lines += 1
                continue
            
            if in_code_block:
                code_lines += 1
                continue
            
            if line.startswith('    ') or line.startswith('\t'):
                code_lines += 1
                continue
            
            if any(pattern in stripped for pattern in ['":',  '": {', '": [', '"BACKEND"', '"OPTIONS"', '"DIRS"']):
                code_lines += 1
        
        if len(lines) == 0:
            return False
        
        code_ratio = code_lines / len(lines)
        return code_ratio > 0.7
    
    def _get_section_boost(self, source_path: str, component: str) -> float:
        """Calculate boost based on document section."""
        path_lower = source_path.lower()
        component_lower = component.lower()
        
        if any(keyword in path_lower for keyword in ['intro/', 'overview', 'getting-started']):
            return 1.3
        
        if 'topics/' in path_lower or component_lower in ['topics', 'guides']:
            return 1.2
        
        if 'howto/' in path_lower or 'how-to' in path_lower:
            return 1.1
        
        if 'ref/' in path_lower or component_lower == 'reference':
            return 1.0
        
        return 1.05
    
    def _get_position_boost(self, chunk_index: int) -> float:
        """Calculate boost based on chunk position."""
        if chunk_index == 0:
            return 1.25
        elif chunk_index == 1:
            return 1.15
        elif chunk_index == 2:
            return 1.1
        else:
            return 1.0
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to  range."""[1]
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == 0.0:
            return [0.0] * len(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [(s - min_score) / (max_score - min_score) for s in scores]
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        tech_filter: Optional[str] = None,
        component_filter: Optional[str] = None,
        version_filter: Optional[str] = None,
        file_type_filter: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining BM25 and semantic search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            tech_filter: Filter by technology
            component_filter: Filter by component
            version_filter: Filter by version
            file_type_filter: Filter by file type
        
        Returns:
            List of SearchResult objects sorted by hybrid score
        """
        # TODO: Check Redis cache here when implemented
        # if self.redis_enabled and self.redis_client:
        #     cache_key = f"search:{query}:{tech_filter}:{top_k}"
        #     cached = self.redis_client.get(cache_key)
        #     if cached:
        #         return json.loads(cached)
        
        async with self._read_lock:
            # Calculate fetch size dynamically to maintain good overlap
            # Use aggressive multipliers to ensure 100% semantic coverage
            if top_k <= 5:
                fetch_multiplier = 20  # 20x for very small queries (fetch 100 for top 5)
            elif top_k <= 10:
                fetch_multiplier = 15  # 15x for small queries (fetch 150 for top 10)
            elif top_k <= 20:
                fetch_multiplier = 12  # 12x for medium queries (fetch 240 for top 20)
            elif top_k <= 50:
                fetch_multiplier = 10  # 10x for large queries (fetch 500 for top 50)
            else:
                fetch_multiplier = 8   # 8x for very large queries
            
            fetch_size = top_k * fetch_multiplier
            logger.debug(f"Using fetch_size={fetch_size} (top_k={top_k} * {fetch_multiplier}x)")
            
            # BM25 search with Elasticsearch
            bm25_results = {}
            try:
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["content^2", "topic^1.5", "component"],
                                        "type": "best_fields"
                                    }
                                }
                            ],
                            "filter": []
                        }
                    },
                    "size": fetch_size
                }
                
                # Add filters
                if tech_filter:
                    es_query["query"]["bool"]["filter"].append({"term": {"tech": tech_filter}})
                if version_filter:
                    es_query["query"]["bool"]["filter"].append({"term": {"version": version_filter}})
                if file_type_filter:
                    es_query["query"]["bool"]["filter"].append({"term": {"file_type": file_type_filter}})
                if component_filter:
                    es_query["query"]["bool"]["filter"].append({"match": {"component": component_filter}})
                
                response = self.es_client.search(index=self.es_index_name, **es_query)
                
                for hit in response["hits"]["hits"]:
                    chunk_id = hit["_source"]["chunk_id"]
                    bm25_results[chunk_id] = hit["_score"]
                    
            except Exception as e:
                logger.error(f"Elasticsearch search error: {e}")
            
            # Semantic search with Qdrant
            semantic_results = {}
            try:
                # Build Qdrant filter
                qdrant_filter = None
                must_conditions = []
                
                if tech_filter:
                    must_conditions.append(
                        FieldCondition(key="tech", match=MatchValue(value=tech_filter))
                    )
                if version_filter:
                    must_conditions.append(
                        FieldCondition(key="version", match=MatchValue(value=version_filter))
                    )
                if file_type_filter:
                    must_conditions.append(
                        FieldCondition(key="file_type", match=MatchValue(value=file_type_filter))
                    )
                
                if must_conditions:
                    qdrant_filter = Filter(must=must_conditions)
                
                # Generate query embedding (FastEmbed returns generator of numpy arrays)
                query_embedding_gen = self.embedding_model.embed([query])
                query_embedding = list(query_embedding_gen)[0].tolist()
                
                logger.debug(f"Query embedding dimension: {len(query_embedding)}")
                
                # Search Qdrant - fetch more to ensure overlap with BM25
                search_result = self.qdrant_client.query_points(
                    collection_name=self.qdrant_collection,
                    query=query_embedding,
                    limit=fetch_size,
                    query_filter=qdrant_filter,
                    with_payload=True
                )
                
                logger.debug(f"Qdrant returned {len(search_result.points)} results")
                
                for scored_point in search_result.points:
                    if scored_point.payload:
                        chunk_id = scored_point.payload["chunk_id"]
                        semantic_results[chunk_id] = scored_point.score
                        logger.debug(f"Qdrant result: {chunk_id} score={scored_point.score:.4f}")
                
            except Exception as e:
                logger.error(f"Qdrant search error: {e}", exc_info=True)
            
            # Combine results
            all_chunk_ids = set(bm25_results.keys()) | set(semantic_results.keys())
            
            if not all_chunk_ids:
                self._log_query(query, {
                    "tech": tech_filter,
                    "component": component_filter,
                    "version": version_filter,
                    "file_type": file_type_filter
                }, 0)
                return []
            
            # Normalize scores
            bm25_scores_list = [bm25_results.get(cid, 0.0) for cid in all_chunk_ids]
            semantic_scores_list = [semantic_results.get(cid, 0.0) for cid in all_chunk_ids]
            
            # Debug: Log score statistics
            bm25_nonzero = sum(1 for s in bm25_scores_list if s > 0)
            semantic_nonzero = sum(1 for s in semantic_scores_list if s > 0)
            logger.debug(f"Score distribution: BM25 {bm25_nonzero}/{len(all_chunk_ids)} non-zero, "
                        f"Semantic {semantic_nonzero}/{len(all_chunk_ids)} non-zero")
            
            normalized_bm25 = self._normalize_scores(bm25_scores_list)
            normalized_semantic = self._normalize_scores(semantic_scores_list)
            
            # Calculate hybrid scores with boosting
            results = []
            for idx, chunk_id in enumerate(all_chunk_ids):
                bm25_score = normalized_bm25[idx]
                semantic_score = normalized_semantic[idx]
                base_hybrid_score = (
                    self.bm25_weight * bm25_score +
                    self.semantic_weight * semantic_score
                )
                
                chunk = self.chunks_metadata.get(chunk_id)
                if chunk:
                    position_boost = self._get_position_boost(chunk.chunk_index)
                    section_boost = self._get_section_boost(chunk.source_path, chunk.component)
                    code_penalty = 0.7 if self._is_code_heavy(chunk.content) else 1.0
                    
                    hybrid_score = base_hybrid_score * position_boost * section_boost * code_penalty
                    
                    results.append(SearchResult(
                        chunk_id=chunk_id,
                        content=chunk.content,
                        source_path=chunk.source_path,
                        tech=chunk.tech,
                        component=chunk.component,
                        topic=chunk.topic,
                        version=chunk.version,
                        file_type=chunk.file_type,
                        chunk_index=chunk.chunk_index,
                        bm25_score=bm25_score,
                        semantic_score=semantic_score,
                        hybrid_score=hybrid_score
                    ))
            
            # Sort and limit
            results.sort(key=lambda r: r.hybrid_score, reverse=True)
            results = results[:top_k]
            
            # Log query
            self._log_query(query, {
                "tech": tech_filter,
                "component": component_filter,
                "version": version_filter,
                "file_type": file_type_filter
            }, len(results))
            
            # TODO: Cache results in Redis when implemented
            # if self.redis_enabled and self.redis_client:
            #     cache_key = f"search:{query}:{tech_filter}:{top_k}"
            #     self.redis_client.setex(cache_key, 300, json.dumps([r.__dict__ for r in results]))
            
            return results
    
    def retrieve(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Retrieve a specific chunk by ID."""
        return self.chunks_metadata.get(chunk_id)
    
    async def get_stats(self) -> Dict:
        """Get index statistics."""
        async with self._read_lock:
            es_count = self.es_client.count(index=self.es_index_name)["count"]
            qdrant_count = self.qdrant_client.count(collection_name=self.qdrant_collection).count
            
            return {
                "total_chunks": len(self.chunks_metadata),
                "whoosh_documents": es_count,  # Keep key name for compatibility
                "chroma_documents": qdrant_count,  # Keep key name for compatibility
                "embedding_model": self.embedding_dimension,
                "embedding_dimension": self.embedding_dimension,
                "bm25_weight": self.bm25_weight,
                "semantic_weight": self.semantic_weight,
                "index_directory": str(self.index_dir),
                "technologies": list(set(chunk.tech for chunk in self.chunks_metadata.values())),
                "file_types": list(set(chunk.file_type for chunk in self.chunks_metadata.values()))
            }
    
    def list_sources(self) -> List[Dict]:
        """List all indexed source files with metadata."""
        sources: Dict[str, Dict] = {}
        
        for chunk in self.chunks_metadata.values():
            if chunk.source_path not in sources:
                sources[chunk.source_path] = {
                    "chunk_count": 0,
                    "tech": chunk.tech,
                    "component": chunk.component,
                    "version": chunk.version,
                    "file_type": chunk.file_type
                }
            sources[chunk.source_path]["chunk_count"] += 1
        
        return [
            {"source_path": path, **data}
            for path, data in sorted(sources.items())
        ]
    
    async def clear_tech(self, tech: str):
        """Clear indices for a specific technology only."""
        async with self._write_lock:
            logger.info(f"Clearing {tech} documentation...")
            
            # Find all chunks for this tech
            chunks_to_remove = [
                chunk_id for chunk_id, chunk in self.chunks_metadata.items()
                if chunk.tech == tech.lower()
            ]
            
            if not chunks_to_remove:
                logger.warning(f"No chunks found for tech: {tech}")
                return
            
            logger.info(f"Removing {len(chunks_to_remove)} chunks for {tech}")
            
            # Remove from Elasticsearch
            try:
                actions = [
                    {"_op_type": "delete", "_index": self.es_index_name, "_id": chunk_id}
                    for chunk_id in chunks_to_remove
                ]
                helpers.bulk(self.es_client, actions, refresh=True, raise_on_error=False)
                logger.info(f"Removed {len(chunks_to_remove)} documents from Elasticsearch")
            except Exception as e:
                logger.error(f"Error removing from Elasticsearch: {e}")
            
            # Remove from Qdrant
            try:
                from qdrant_client.models import PointIdsList
                point_ids = [self._chunk_id_to_point_id(cid) for cid in chunks_to_remove]
                self.qdrant_client.delete(
                    collection_name=self.qdrant_collection,
                    points_selector=PointIdsList(points=point_ids)  # type: ignore
                )
                logger.info(f"Removed {len(chunks_to_remove)} points from Qdrant")
            except Exception as e:
                logger.error(f"Error removing from Qdrant: {e}")
            
            # Remove from metadata
            for chunk_id in chunks_to_remove:
                if chunk_id in self.chunks_metadata:
                    del self.chunks_metadata[chunk_id]
            
            # Remove checksums for files of this tech
            files_to_remove = set(
                chunk.source_path for chunk in self.chunks_metadata.values()
                if chunk.tech == tech.lower()
            )
            for file_path in files_to_remove:
                if file_path in self.file_checksums:
                    del self.file_checksums[file_path]
            
            # Save updated caches
            self._save_metadata_cache()
            self._save_checksums()
            
            logger.info(f"Cleared {tech} documentation successfully")
    
    async def clear_index(self):
        """Clear all indices completely."""
        async with self._write_lock:
            # Clear Elasticsearch
            try:
                self.es_client.indices.delete(index=self.es_index_name)
                self._create_elasticsearch_index()
            except Exception as e:
                logger.warning(f"Error clearing Elasticsearch: {e}")
            
            # Clear Qdrant
            try:
                self.qdrant_client.delete_collection(collection_name=self.qdrant_collection)
                self._create_qdrant_collection()
            except Exception as e:
                logger.warning(f"Error clearing Qdrant: {e}")
            
            # Clear metadata
            self.chunks_metadata.clear()
            self.file_checksums.clear()
            
            # Remove metadata cache files
            try:
                if self.metadata_cache_path.exists():
                    self.metadata_cache_path.unlink()
                    logger.info("Removed metadata cache file")
                if self.checksum_cache_path.exists():
                    self.checksum_cache_path.unlink()
                    logger.info("Removed checksum cache file")
            except Exception as e:
                logger.warning(f"Error removing cache files: {e}")
            
            logger.info("Index cleared successfully")
