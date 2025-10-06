"""
Database Helper Functions

it's good practice:
  -  DRY (Don't Repeat Yourself) - Write query once, use everywhere
  -  Testable - Easy to mock fetch_document()
  -  Maintainable - Change query in one place
  -  Readable - fetch_document(123) vs raw SQL

Wrapper functions for common database operations.
"""

from typing import Optional, Dict, Any, List
from app.db.client import fetch_one, get_db_pool


async def fetch_document(doc_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a document by its ID.

    Args:
        doc_id (int): The document ID

    Returns:
        Optional[Dict[str, Any]]: Document metadata dict, or None if not found

    Example:
        >>> doc = await fetch_document(123)
        >>> print(doc["title"])
        "Atlas Deploy Guide"
    """
    query = """
        SELECT
            doc_id,
            title,
            project_id,
            visibility,
            uri,
            updated_at,
            language
        FROM documents
        WHERE doc_id = $1 AND deleted_at IS NULL
    """
    return await fetch_one(query, doc_id)


async def insert_document(
    title: str,
    project_id: Optional[str],
    visibility: str,
    uri: str,
    language: str = "en"
) -> int:
    """
    Inserts a new document into the database.

    Args:
        title: Document title (e.g., filename)
        project_id: Optional project ID
        visibility: "Public" or "Private"
        uri: Document URI (for uploads: "upload://uuid/filename")
        language: Document language (default: "en")

    Returns:
        doc_id: The ID of the newly created document

    Example:
        >>> doc_id = await insert_document(
        ...     title="report.pdf",
        ...     project_id=None,
        ...     visibility="Public",
        ...     uri="upload://abc-123/report.pdf"
        ... )
        >>> print(doc_id)
        456
    """
    pool = get_db_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO documents (title, project_id, visibility, uri, language)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING doc_id
        """, title, project_id, visibility, uri, language)

    return row["doc_id"]


async def insert_chunk(
    doc_id: int,
    text: str,
    heading_path: List[str],
    embedding: List[float]
) -> int:
    """
    Inserts a chunk into the database.

    Args:
        doc_id: Document ID this chunk belongs to
        text: Chunk text content
        heading_path: List of heading hierarchy (e.g., ["Deployment", "Steps"])
        embedding: 1024-dimensional embedding vector

    Returns:
        chunk_id: The ID of the newly created chunk

    Example:
        >>> chunk_id = await insert_chunk(
        ...     doc_id=123,
        ...     text="To deploy the API...",
        ...     heading_path=["Deployment", "Steps"],
        ...     embedding=[0.1, 0.2, ...]
        ... )
    """
    pool = get_db_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO chunks (doc_id, text, heading_path, embedding)
            VALUES ($1, $2, $3, $4::vector)
            RETURNING chunk_id
        """, doc_id, text, heading_path, embedding)

    return row["chunk_id"]