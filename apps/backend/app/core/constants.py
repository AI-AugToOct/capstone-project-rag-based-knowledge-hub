"""
Shared constants for backend API

These values must be kept in sync with worker constants and database schema.
"""

# Embedding configuration (must match workers!)
EMBEDDING_MODEL = "embed-english-v3.0"
EMBEDDING_DIM = 1024  # Must match database VECTOR(1024) dimension

# Chunking configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval configuration
RERANK_MODEL = "rerank-english-v3.0"
MAX_INITIAL_CANDIDATES = 200
DEFAULT_TOP_K = 12

# Document visibility options
VALID_VISIBILITIES = ["Public", "Private"]