#!/usr/bin/env python3
"""
Hybrid Search Engine for Documentation MCP Server.

Combines:
- Semantic search using sentence-transformers + ChromaDB
- Keyword search using Whoosh BM25
- Weighted hybrid scoring (0.6 BM25 + 0.4 semantic by default)
"""

import asyncio
import logging
import os
import re
import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from whoosh import index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, TEXT, DATETIME, KEYWORD, Schema
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh.scoring import BM25F

logger = logging.getLogger(__name__)


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
    

class IndexManager:
    """
    Manages hybrid search indices for documentation.
    
    Combines:
    - ChromaDB for semantic vector search
    - Whoosh for BM25 keyword search
    - Rich metadata tagging for filtering
    """
    
    def __init__(
        self,
        index_dir: str = ".index",
        embedding_model: str = "BAAI/bge-small-en",
        bm25_weight: float = 0.6,
        semantic_weight: float = 0.4,
        chunk_size_tokens: int = 400,
        chunk_overlap_words: int = 100,
    ):
        """
        Initialize the IndexManager.
        
        Args:
            index_dir: Directory to store indices
            embedding_model: SentenceTransformer model name
            bm25_weight: Weight for BM25 scores (default 0.6)
            semantic_weight: Weight for semantic scores (default 0.4)
            chunk_size_tokens: Target chunk size in tokens
            chunk_overlap_words: Overlap between chunks in words
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_words = chunk_overlap_words
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        # Detect device (GPU if available, otherwise CPU)
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
        logger.info(f"Using device: {device}")
        self.embedding_model = SentenceTransformer(embedding_model, device=device)
        logger.info(f"Embedding dimension: {self.embedding_model.get_sentence_embedding_dimension()}")
        
        # Initialize ChromaDB
        logger.info("Initializing ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.index_dir / "chroma"),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="docs_collection",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize Whoosh
        logger.info("Initializing Whoosh BM25 index...")
        self.whoosh_dir = self.index_dir / "whoosh"
        self.whoosh_dir.mkdir(exist_ok=True)
        
        # Create analyzer that preserves code identifiers (min 2 chars to catch field names)
        # StemmingAnalyzer applies Porter stemming but preserves structure
        code_analyzer = StemmingAnalyzer(minsize=2, stoplist=None)
        
        self.schema = Schema(
            chunk_id=ID(stored=True, unique=True),
            content=TEXT(stored=True, analyzer=code_analyzer),
            source_path=TEXT(stored=True),
            tech=KEYWORD(stored=True, commas=True),
            component=TEXT(stored=True, analyzer=code_analyzer),
            topic=TEXT(stored=True, analyzer=code_analyzer),
            version=KEYWORD(stored=True),
            file_type=KEYWORD(stored=True),
            timestamp=DATETIME(stored=True)
        )
        
        if index.exists_in(str(self.whoosh_dir)):
            self.whoosh_index = index.open_dir(str(self.whoosh_dir))
        else:
            self.whoosh_index = index.create_in(str(self.whoosh_dir), self.schema)
        
        # Chunk metadata cache
        self.chunks_metadata: Dict[str, DocumentChunk] = {}
        
        # Load existing metadata from index
        self._load_metadata_from_index()
        
        # Query log
        self.query_log_path = self.index_dir / "search_queries.log"
        
        logger.info("IndexManager initialized successfully")
    
    def _load_metadata_from_index(self):
        """Load chunk metadata from existing Whoosh index."""
        try:
            with self.whoosh_index.searcher() as searcher:
                doc_count = searcher.doc_count_all()
                if doc_count == 0:
                    logger.info("No existing index data found")
                    return
                
                logger.info(f"Loading metadata for {doc_count} chunks from index...")
                
                for docnum in range(doc_count):
                    try:
                        doc = searcher.stored_fields(docnum)
                        if not doc:
                            continue
                        
                        chunk = DocumentChunk(
                            chunk_id=doc.get("chunk_id", ""),
                            content=doc.get("content", ""),
                            source_path=doc.get("source_path", ""),
                            tech=doc.get("tech", "unknown"),
                            component=doc.get("component", "unknown"),
                            topic=doc.get("topic", ""),
                            version=doc.get("version", "unknown"),
                            file_type=doc.get("file_type", "unknown"),
                            chunk_index=0,  # Not stored in Whoosh
                            start_line=0,    # Not stored in Whoosh
                            end_line=0,      # Not stored in Whoosh
                            timestamp=doc.get("timestamp", datetime.now())
                        )
                        self.chunks_metadata[chunk.chunk_id] = chunk
                    except Exception as e:
                        logger.warning(f"Error loading doc {docnum}: {e}")
                        continue
                
                logger.info(f"Loaded metadata for {len(self.chunks_metadata)} chunks")
        except Exception as e:
            logger.warning(f"Could not load existing metadata: {e}")
    
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
            # Try to get meaningful component from path
            for part in reversed(parts[:-1]):  # Exclude filename
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
                    return topic[:100]  # Limit length
        
        # Fall back to filename
        return file_path.stem.replace('-', ' ').replace('_', ' ').title()
    
    def _chunk_content(self, content: str, file_type: str) -> List[Tuple[str, int, int]]:
        """
        Chunk content based on file type.
        
        Returns:
            List of (chunk_content, start_line, end_line) tuples
        """
        lines = content.split('\n')
        chunks = []
        
        if file_type in ['.py', '.json', '.yaml', '.yml']:
            # Structural chunking for code (80-150 lines)
            chunk_size = 100
            for i in range(0, len(lines), chunk_size):
                chunk_lines = lines[i:i + chunk_size + 20]  # Some overlap
                chunk_text = '\n'.join(chunk_lines)
                if chunk_text.strip():
                    chunks.append((chunk_text, i, i + len(chunk_lines)))
        else:
            # Semantic chunking for prose (300-500 tokens ≈ 400-650 words)
            # Approximate: 1 token ≈ 0.75 words, so 400 tokens ≈ 300 words
            words_per_chunk = int(self.chunk_size_tokens * 0.75)
            words = []
            line_map = []  # Track which line each word came from
            
            for line_idx, line in enumerate(lines):
                line_words = line.split()
                words.extend(line_words)
                line_map.extend([line_idx] * len(line_words))
            
            overlap_words = self.chunk_overlap_words
            
            for i in range(0, len(words), words_per_chunk - overlap_words):
                chunk_words = words[i:i + words_per_chunk]
                if chunk_words:
                    chunk_text = ' '.join(chunk_words)
                    start_line = line_map[i] if i < len(line_map) else 0
                    end_idx = min(i + len(chunk_words) - 1, len(line_map) - 1)
                    end_line = line_map[end_idx] if end_idx >= 0 else len(lines)
                    chunks.append((chunk_text, start_line, end_line))
        
        return chunks if chunks else [(content, 0, len(lines))]
    
    async def index_documents(
        self,
        paths: List[Path],
        progress_callback=None
    ) -> Dict[str, int]:
        """
        Index documents from given paths.
        
        Args:
            paths: List of file or directory paths to index
            progress_callback: Optional async callback(current, total, message)
        
        Returns:
            Statistics dict with counts
        """
        stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "errors": 0
        }
        
        # Collect all files to process
        files_to_process = []
        supported_extensions = {'.md', '.txt', '.rst', '.py', '.json', '.yaml', '.yml', '.html'}
        exclude_dirs = {'.index', '.git', 'node_modules', 'venv', '.venv', '__pycache__', '.pytest_cache'}
        
        def should_skip_dir(dir_path: Path) -> bool:
            """Check if directory should be skipped."""
            return any(part in exclude_dirs for part in dir_path.parts)
        
        for path in paths:
            if path.is_file() and path.suffix in supported_extensions:
                files_to_process.append(path)
            elif path.is_dir():
                for ext in supported_extensions:
                    for file_path in path.rglob(f"*{ext}"):
                        if not should_skip_dir(file_path):
                            files_to_process.append(file_path)
        
        total_files = len(files_to_process)
        logger.info(f"Found {total_files} files to index")
        
        if progress_callback:
            await progress_callback(0, total_files, "Starting indexing...")
        
        # Process files in batches
        batch_size = 10
        all_chunks = []
        
        for batch_idx in range(0, total_files, batch_size):
            batch_files = files_to_process[batch_idx:batch_idx + batch_size]
            
            for file_idx, file_path in enumerate(batch_files):
                try:
                    current_file = batch_idx + file_idx + 1
                    
                    if progress_callback:
                        await progress_callback(
                            current_file,
                            total_files,
                            f"Processing {file_path.name}..."
                        )
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if not content.strip():
                        continue
                    
                    # Extract metadata
                    tech, component, version = self._extract_metadata_from_path(file_path)
                    topic = self._extract_topic_from_content(content, file_path)
                    file_type = file_path.suffix
                    timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    # Chunk content
                    chunks = self._chunk_content(content, file_type)
                    
                    for chunk_idx, (chunk_content, start_line, end_line) in enumerate(chunks):
                        chunk_id = f"{file_path.stem}_{chunk_idx}_{hash(chunk_content) % 10000}"
                        
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
                            timestamp=timestamp
                        )
                        
                        all_chunks.append(chunk)
                        self.chunks_metadata[chunk_id] = chunk
                    
                    stats["files_processed"] += 1
                    stats["chunks_created"] += len(chunks)
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    stats["errors"] += 1
        
        # Index all chunks
        if all_chunks:
            if progress_callback:
                await progress_callback(
                    total_files,
                    total_files,
                    f"Indexing {len(all_chunks)} chunks..."
                )
            
            await self._index_chunks(all_chunks)
        
        logger.info(f"Indexing complete: {stats}")
        return stats
    
    async def _index_chunks(self, chunks: List[DocumentChunk]):
        """Index chunks into both Whoosh and ChromaDB."""
        with self._lock:
            # Index into Whoosh using context manager
            logger.info(f"Indexing {len(chunks)} chunks into Whoosh...")
            try:
                with self.whoosh_index.writer() as writer:
                    for chunk in chunks:
                        writer.add_document(
                            chunk_id=chunk.chunk_id,
                            content=chunk.content,
                            source_path=chunk.source_path,
                            tech=chunk.tech,
                            component=chunk.component,
                            topic=chunk.topic,
                            version=chunk.version,
                            file_type=chunk.file_type,
                            timestamp=chunk.timestamp
                        )
                logger.info("Whoosh indexing complete")
            except Exception as e:
                logger.error(f"Error indexing to Whoosh: {e}")
                raise
            
            # Generate embeddings and index into ChromaDB
            try:
                contents = [chunk.content for chunk in chunks]
                logger.info(f"Generating embeddings for {len(contents)} chunks (this may take 2-5 minutes)...")
                
                # Generate embeddings in larger batches for better performance
                # Use batch_size=64 for CPU, model will handle efficiently
                batch_size = 64
                embeddings = []
                total_batches = (len(contents) + batch_size - 1) // batch_size
                
                for batch_idx, i in enumerate(range(0, len(contents), batch_size), 1):
                    batch = contents[i:i + batch_size]
                    logger.info(f"  Processing batch {batch_idx}/{total_batches} ({len(batch)} chunks)...")
                    batch_embeddings = self.embedding_model.encode(
                        batch,
                        batch_size=batch_size,
                        normalize_embeddings=True,
                        show_progress_bar=True,
                        convert_to_numpy=True
                    )
                    embeddings.extend(batch_embeddings.tolist())
                
                logger.info("Embedding generation complete")
                
                # Add to ChromaDB
                self.collection.add(
                    ids=[chunk.chunk_id for chunk in chunks],
                    embeddings=embeddings,
                    documents=contents,
                    metadatas=[{
                        "source_path": chunk.source_path,
                        "tech": chunk.tech,
                        "component": chunk.component,
                        "topic": chunk.topic,
                        "version": chunk.version,
                        "file_type": chunk.file_type,
                        "chunk_index": str(chunk.chunk_index)
                    } for chunk in chunks]
                )
                
                logger.info(f"Successfully indexed {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error indexing to ChromaDB: {e}")
                raise
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """
        Normalize scores to [0, 1] range using min-max normalization.
        Handles edge cases where all scores are zero or identical.
        """
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        # If all scores are zero, keep them as zero (don't normalize to 1.0)
        if max_score == 0.0:
            return [0.0] * len(scores)
        
        # If all scores are identical but non-zero, normalize to 1.0
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [(s - min_score) / (max_score - min_score) for s in scores]
    
    def _boost_query_keywords(self, query: str, tech_filter: Optional[str] = None) -> str:
        """
        Apply keyword boosting to prioritize tech-specific terms.
        
        Args:
            query: Original query string
            tech_filter: Technology context for boosting
        
        Returns:
            Query with boosted terms
        """
        # Define tech-specific boost terms (boost factor: ^1.5)
        boost_terms = {
            "django": ["Model", "Field", "IntegerField", "CharField", "ForeignKey", 
                      "QuerySet", "Manager", "migrate", "makemigrations"],
            "drf": ["Serializer", "ModelSerializer", "ViewSet", "ModelViewSet", 
                   "APIView", "Response", "Request", "permission", "authentication"],
            "psycopg": ["Connection", "Pool", "AsyncConnection", "AsyncPool", 
                       "cursor", "execute", "fetch", "fetchone", "fetchall", "commit"]
        }
        
        # Don't boost if query is very short or already has boost syntax
        if len(query) < 3 or '^' in query:
            return query
        
        boosted_query = query
        replacements_made = set()
        
        # If tech_filter is specified, boost those specific terms
        if tech_filter and tech_filter.lower() in boost_terms:
            for term in boost_terms[tech_filter.lower()]:
                # Case-insensitive search for the term
                pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                matches = pattern.findall(boosted_query)
                if matches and term.lower() not in replacements_made:
                    # Only boost once per term
                    boosted_query = pattern.sub(f"{term}^1.5", boosted_query, count=1)
                    replacements_made.add(term.lower())
        else:
            # Boost all tech terms if no filter specified (lighter touch)
            for tech_terms in boost_terms.values():
                for term in tech_terms:
                    pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                    matches = pattern.findall(boosted_query)
                    if matches and term.lower() not in replacements_made:
                        boosted_query = pattern.sub(f"{term}^1.5", boosted_query, count=1)
                        replacements_made.add(term.lower())
        
        return boosted_query
    
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
            tech_filter: Filter by technology (e.g., "django")
            component_filter: Filter by component
            version_filter: Filter by version
            file_type_filter: Filter by file type (e.g., ".md")
        
        Returns:
            List of SearchResult objects sorted by hybrid score
        """
        with self._lock:
            # Build Whoosh filter query
            filter_parts = []
            if tech_filter:
                filter_parts.append(f"tech:{tech_filter}")
            if component_filter:
                filter_parts.append(f"component:{component_filter}")
            if version_filter:
                filter_parts.append(f"version:{version_filter}")
            if file_type_filter:
                filter_parts.append(f"file_type:{file_type_filter}")
            
            # BM25 search with Whoosh
            bm25_results = {}
            try:
                with self.whoosh_index.searcher(weighting=BM25F()) as searcher:
                    parser = MultifieldParser(["content", "topic", "component"], schema=self.schema)
                    # Apply keyword boosting to the query
                    boosted_query = self._boost_query_keywords(query, tech_filter)
                    whoosh_query = parser.parse(boosted_query)
                    
                    results = searcher.search(whoosh_query, limit=top_k * 2)
                    
                    for hit in results:
                        chunk_id = hit["chunk_id"]
                        # Apply manual filters if Whoosh doesn't support them well
                        if tech_filter and hit.get("tech") != tech_filter:
                            continue
                        if component_filter and component_filter.lower() not in hit.get("component", "").lower():
                            continue
                        if version_filter and hit.get("version") != version_filter:
                            continue
                        if file_type_filter and hit.get("file_type") != file_type_filter:
                            continue
                        
                        bm25_results[chunk_id] = hit.score
            except Exception as e:
                logger.error(f"BM25 search error: {e}")
            
            # Semantic search with ChromaDB
            semantic_results = {}
            try:
                # Build ChromaDB where filter
                where_filter = {}
                if tech_filter:
                    where_filter["tech"] = tech_filter
                if version_filter:
                    where_filter["version"] = version_filter
                if file_type_filter:
                    where_filter["file_type"] = file_type_filter
                
                # Generate query embedding
                query_embedding = self.embedding_model.encode(
                    query,
                    normalize_embeddings=True
                ).tolist()
                
                # Query ChromaDB
                chroma_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k * 2,
                    where=where_filter if where_filter else None
                )
                
                if chroma_results and chroma_results["ids"]:
                    for idx, chunk_id in enumerate(chroma_results["ids"][0]):
                        # Cosine similarity is already in [0, 1] range
                        # ChromaDB returns distance, convert to similarity
                        distance = chroma_results["distances"][0][idx]
                        similarity = 1 - distance  # Convert distance to similarity
                        semantic_results[chunk_id] = max(0.0, similarity)
                        
            except Exception as e:
                logger.error(f"Semantic search error: {e}")
            
            # Combine results using weighted scoring
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
            
            normalized_bm25 = self._normalize_scores(bm25_scores_list)
            normalized_semantic = self._normalize_scores(semantic_scores_list)
            
            # Calculate hybrid scores
            results = []
            for idx, chunk_id in enumerate(all_chunk_ids):
                bm25_score = normalized_bm25[idx]
                semantic_score = normalized_semantic[idx]
                hybrid_score = (
                    self.bm25_weight * bm25_score +
                    self.semantic_weight * semantic_score
                )
                
                chunk = self.chunks_metadata.get(chunk_id)
                if chunk:
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
            
            # Sort by hybrid score and limit
            results.sort(key=lambda r: r.hybrid_score, reverse=True)
            results = results[:top_k]
            
            # Log query
            self._log_query(query, {
                "tech": tech_filter,
                "component": component_filter,
                "version": version_filter,
                "file_type": file_type_filter
            }, len(results))
            
            return results
    
    def retrieve(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Retrieve a specific chunk by ID."""
        return self.chunks_metadata.get(chunk_id)
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        with self._lock:
            whoosh_doc_count = self.whoosh_index.doc_count_all()
            chroma_count = self.collection.count()
            
            return {
                "total_chunks": len(self.chunks_metadata),
                "whoosh_documents": whoosh_doc_count,
                "chroma_documents": chroma_count,
                "embedding_model": self.embedding_model.get_sentence_embedding_dimension(),
                "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension(),
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
    
    async def clear_index(self):
        """Clear all indices."""
        with self._lock:
            # Clear Whoosh by recreating the index
            import shutil
            if self.whoosh_dir.exists():
                shutil.rmtree(self.whoosh_dir)
            self.whoosh_dir.mkdir(exist_ok=True)
            self.whoosh_index = index.create_in(str(self.whoosh_dir), self.schema)
            
            # Clear ChromaDB
            try:
                self.chroma_client.delete_collection("docs_collection")
            except Exception:
                pass  # Collection might not exist
            self.collection = self.chroma_client.get_or_create_collection(
                name="docs_collection",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Clear metadata
            self.chunks_metadata.clear()
            
            logger.info("Index cleared successfully")
