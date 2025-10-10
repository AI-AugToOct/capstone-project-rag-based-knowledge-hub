"""
Shared constants for ingestion pipeline

These values must be kept in sync with backend constants and database schema.
"""

# Embedding configuration
EMBEDDING_MODEL = "embed-english-v3.0"
EMBEDDING_DIM = 1024  # Must match database VECTOR(1024) dimension

# Chunking configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Document visibility options
VALID_VISIBILITIES = ["Public", "Private"]