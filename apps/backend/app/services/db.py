"""
Database Helper Functions

it's good practice:
  -  DRY (Don't Repeat Yourself) - Write query once, use everywhere
  -  Testable - Easy to mock fetch_document()
  -  Maintainable - Change query in one place
  -  Readable - fetch_document(123) vs raw SQL

Wrapper functions for common database operations.
"""

from typing import Optional, Dict, Any
from app.db.client import fetch_one


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