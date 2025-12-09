# Performance Fixes Applied

## Issue
Indexing was getting stuck at "Generating embeddings for 3833 chunks" with no visible progress.

## Root Causes Identified

### 1. ❌ Whoosh Writer Without Context Manager (Line 383)
**Problem:** Writer was opened manually and committed, risking locks if errors occurred.
```python
# Before (BAD)
writer = self.whoosh_index.writer()
try:
    for chunk in chunks:
        writer.add_document(...)
    writer.commit()
except Exception as e:
    writer.cancel()
```

**Fix:** Use context manager for automatic cleanup
```python
# After (GOOD)
with self.whoosh_index.writer() as writer:
    for chunk in chunks:
        writer.add_document(...)
# Automatic commit on exit
```

### 2. ❌ Hidden Embedding Progress (Line 413)
**Problem:** `show_progress_bar=False` made it appear stuck when actually processing.
```python
# Before (BAD)
batch_embeddings = self.embedding_model.encode(
    batch,
    normalize_embeddings=True,
    show_progress_bar=False  # No progress visible!
)
```

**Fix:** Enable progress bar and add batch logging
```python
# After (GOOD)
logger.info(f"Processing batch {batch_idx}/{total_batches} ({len(batch)} chunks)...")
batch_embeddings = self.embedding_model.encode(
    batch,
    batch_size=batch_size,
    normalize_embeddings=True,
    show_progress_bar=True,  # Show progress!
    convert_to_numpy=True
)
```

### 3. ⚠️ Small Batch Size (32)
**Problem:** Processing 3833 chunks in batches of 32 = 120 batches (slow)
**Fix:** Increased to batch_size=64 → ~60 batches (faster)

### 4. ✅ Model Loading (Already Correct)
Model is loaded **once** in `__init__` - no issues here.

### 5. ❌ Missing Directory Exclusions
**Problem:** File discovery was indexing ALL directories including `.index/`, `.git/`, `node_modules/`, etc.
```python
# Before (BAD)
for ext in supported_extensions:
    files_to_process.extend(path.rglob(f"*{ext}"))
# This includes .index/, .git/, etc!
```

**Fix:** Exclude common directories that shouldn't be indexed
```python
# After (GOOD)
exclude_dirs = {'.index', '.git', 'node_modules', 'venv', '.venv', '__pycache__', '.pytest_cache'}

def should_skip_dir(dir_path: Path) -> bool:
    return any(part in exclude_dirs for part in dir_path.parts)

for ext in supported_extensions:
    for file_path in path.rglob(f"*{ext}"):
        if not should_skip_dir(file_path):
            files_to_process.append(file_path)
```

### 6. ✅ GPU Detection Enhancement
**Enhancement:** Added device detection to use GPU if available
```python
try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    device = "cpu"
logger.info(f"Using device: {device}")
self.embedding_model = SentenceTransformer(embedding_model, device=device)
```

## Changes Made

### `search_engine.py`

1. **Lines 107-118**: Added device detection (GPU/CPU)
2. **Lines 295-310**: Added directory exclusions (`.index/`, `.git/`, `node_modules/`, etc.)
3. **Lines 381-400**: Whoosh writer now uses context manager
4. **Lines 403-426**: 
   - Increased batch_size from 32 to 64
   - Added batch progress logging
   - Enabled `show_progress_bar=True`
   - Added `convert_to_numpy=True` for efficiency
5. **Lines 649-660**: Fixed type error in `list_sources()`

## Expected Performance

### Before
- **3833 chunks**: ~5-8 minutes (appeared stuck)
- No progress indicators
- Risk of writer locks

### After
- **3833 chunks**: ~2-5 minutes with visible progress
- Batch progress: "Processing batch 45/60 (64 chunks)..."
- Embedding progress bars
- Safe writer cleanup

## Testing

Run the indexing again:
```bash
python scripts/build_index.py
```

You should now see:
1. Device detection: `Using device: cpu` or `Using device: cuda`
2. Batch progress: `Processing batch X/Y (64 chunks)...`
3. Progress bars for embedding generation
4. Faster overall completion time

## Additional Optimizations Available

If still too slow, consider:

1. **Smaller embedding model** (faster, slightly lower quality):
   ```bash
   export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
   ```

2. **Reduce chunk size** (fewer chunks to index):
   ```bash
   export CHUNK_SIZE_TOKENS="200"
   ```

3. **Use GPU** if available (10-20x faster):
   - Install PyTorch with CUDA support
   - Model will auto-detect and use GPU

4. **Incremental indexing** (index one tech at a time):
   ```bash
   python scripts/build_index.py --tech django
   python scripts/build_index.py --tech drf
   python scripts/build_index.py --tech psycopg
   ```
