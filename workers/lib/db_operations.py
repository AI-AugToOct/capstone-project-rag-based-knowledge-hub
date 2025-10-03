"""
Database Operations for Workers

Handles upserting documents and chunks to the database.
"""

from typing import List, Optional
import psycopg2
import os


def upsert_document(
    source_external_id: str,
    title: str,
    project_id: str,
    visibility: str,
    uri: str,
    content_hash: str,
    language: Optional[str] = "en"
) -> int:
    """
    Inserts or updates a document in the documents table.

    Args:
        source_external_id (str): Unique ID from source system (Notion page ID)
            Example: "notion_abc123def456"

        title (str): Document title
            Example: "Atlas Deploy Guide"

        project_id (str): Which project this document belongs to
            Example: "Atlas"

        visibility (str): "Public" or "Private"
            Example: "Private"

        uri (str): Deep link to source document
            Example: "https://notion.so/Atlas-Deploy-abc123"

        content_hash (str): MD5 hash of document content
            Example: "d8e8fca2dc0f896fd7cb4cb0031ba249"
            Why: Skip re-embedding if content hasn't changed

        language (Optional[str]): Document language code (default: "en")
            Example: "en", "ar", "fr"

    Returns:
        int: The doc_id of the inserted/updated document
            Example: 42

    What This Does:
        1. Connects to database
        2. Attempts INSERT with ON CONFLICT UPDATE (upsert)
        3. If source_external_id exists, updates the row
        4. If new, inserts new row
        5. Returns the doc_id

    Example Usage:
        >>> doc_id = upsert_document(
        ...     source_external_id="notion_abc123",
        ...     title="Atlas Deploy Guide",
        ...     project_id="Atlas",
        ...     visibility="Private",
        ...     uri="https://notion.so/abc123",
        ...     content_hash="d8e8fca2..."
        ... )
        >>> print(doc_id)
        42

    Why "Upsert":
        - First time: INSERT new document
        - Second time (re-ingestion): UPDATE existing document
        - Prevents duplicates
        - Updates metadata (title, updated_at) if page changed

    SQL Query (PostgreSQL UPSERT):
        INSERT INTO documents (
            source_external_id,
            title,
            project_id,
            visibility,
            uri,
            content_hash,
            language,
            updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, NOW()
        )
        ON CONFLICT (source_external_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            project_id = EXCLUDED.project_id,
            visibility = EXCLUDED.visibility,
            uri = EXCLUDED.uri,
            content_hash = EXCLUDED.content_hash,
            updated_at = NOW()
        RETURNING doc_id

    ON CONFLICT Explained:
        - Unique index on source_external_id prevents duplicates
        - If INSERT would violate unique constraint → DO UPDATE instead
        - EXCLUDED.* refers to the values we tried to INSERT

    Detecting Content Changes:
        - Compare content_hash with existing row
        - If different → content changed → re-embed
        - If same → content unchanged → skip re-embedding
        - Saves API costs and time!

    Example Workflow:
        # First ingestion
        upsert_document(..., content_hash="abc123")
        → INSERT new row, doc_id=42

        # Re-ingestion (same page, no changes)
        upsert_document(..., content_hash="abc123")  # Same hash
        → UPDATE row (title, updated_at), doc_id=42
        → Skip embedding (hash unchanged)

        # Re-ingestion (page edited)
        upsert_document(..., content_hash="def456")  # Different hash
        → UPDATE row, doc_id=42
        → Re-embed chunks (content changed)

    Database Connection:
        - Use connection string from DATABASE_URL
        - Example: postgresql://user:pass@host:5432/db

    Dependencies:
        - psycopg2 library: pip install psycopg2-binary
        - Environment variable: DATABASE_URL

    Implementation Hints:
        - conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        - cursor = conn.cursor()
        - cursor.execute(upsert_query, (params...))
        - doc_id = cursor.fetchone()[0]
        - conn.commit()
        - cursor.close()
        - conn.close()
        - return doc_id

    Error Handling:
        - Check if source_external_id is unique
        - Handle database connection errors
        - Rollback on failure

    Testing:
        - Insert new document → verify returns doc_id
        - Upsert same document → verify returns same doc_id
        - Verify updated_at is updated on upsert
    """
    raise NotImplementedError("TODO: Implement document upsert with conflict handling")


def insert_chunk(
    doc_id: int,
    text: str,
    embedding: List[float],
    heading_path: List[str],
    order_in_doc: int,
    page: Optional[int] = None
) -> None:
    """
    Inserts a chunk into the chunks table.

    Args:
        doc_id (int): Foreign key to documents table
            Example: 42

        text (str): The chunk content
            Example: "To deploy Atlas API, follow these steps: 1. Configure..."

        embedding (List[float]): 1024-dimensional vector
            Example: [0.12, -0.08, 0.34, ..., -0.15]

        heading_path (List[str]): Breadcrumb trail of headings
            Example: ["Deployment", "Prerequisites"]

        order_in_doc (int): Position of chunk in document (0, 1, 2, ...)
            Example: 0 (first chunk)

        page (Optional[int]): Page number for PDFs (null for Notion)
            Example: None

    Returns:
        None

    What This Does:
        1. Connects to database
        2. Inserts row into chunks table
        3. Stores text + embedding + metadata

    Example Usage:
        >>> insert_chunk(
        ...     doc_id=42,
        ...     text="To deploy...",
        ...     embedding=[0.1, 0.2, ...],  # 1024 floats
        ...     heading_path=["Deployment", "Steps"],
        ...     order_in_doc=0
        ... )

    SQL Query:
        INSERT INTO chunks (
            doc_id,
            text,
            embedding,
            heading_path,
            order_in_doc,
            page,
            updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, NOW()
        )

    Vector Format:
        - PostgreSQL pgvector expects array format
        - Convert list to string: str(embedding)
        - Or use psycopg2 array adapter

    Example Vector Storage:
        embedding = [0.1, 0.2, 0.3]
        → Stored as: VECTOR(1024) = '[0.1, 0.2, 0.3, ...]'

    heading_path Format:
        - PostgreSQL array type: TEXT[]
        - Example: ["Deployment", "Steps"]
        - Stored as: '{Deployment,Steps}'

    order_in_doc Purpose:
        - Allows reconstructing full document
        - Chunks can be stitched back together
        - Useful for "show full document" feature

    Unique Constraint:
        - (doc_id, order_in_doc) must be unique
        - Prevents duplicate chunks
        - If re-ingesting: DELETE old chunks first, then INSERT new

    Re-Ingestion Strategy:
        1. Upsert document (get doc_id)
        2. If content_hash changed:
           a. DELETE FROM chunks WHERE doc_id = %s
           b. Insert new chunks
        3. If content_hash unchanged:
           → Skip (chunks already exist)

    Dependencies:
        - psycopg2
        - DATABASE_URL environment variable

    Implementation Hints:
        - Convert embedding list to pgvector format
        - Convert heading_path to PostgreSQL array
        - Use parameterized query
        - Commit transaction

    Error Handling:
        - Check embedding has exactly 1024 dimensions
        - Handle unique constraint violations
        - Rollback on error

    Testing:
        - Insert chunk → verify row exists
        - Query chunk → verify embedding matches
        - Verify heading_path is stored correctly
        - Test with different order_in_doc values
    """
    raise NotImplementedError("TODO: Implement chunk insertion with vector storage")


def check_content_changed(source_external_id: str, new_content_hash: str) -> bool:
    """
    Checks if document content has changed since last ingestion.

    Args:
        source_external_id (str): Notion page ID
            Example: "notion_abc123"

        new_content_hash (str): MD5 hash of new content
            Example: "d8e8fca2dc0f896fd7cb4cb0031ba249"

    Returns:
        bool: True if content changed (need to re-embed), False otherwise

    What This Does:
        1. Query database for existing content_hash
        2. Compare with new_content_hash
        3. Return True if different (or document doesn't exist)

    Example Usage:
        >>> if check_content_changed("notion_abc123", "new_hash"):
        ...     print("Content changed, re-embedding...")
        ...     # Delete old chunks, insert new ones
        ... else:
        ...     print("Content unchanged, skipping...")

    SQL Query:
        SELECT content_hash
        FROM documents
        WHERE source_external_id = %s

    Why This Matters:
        - Embedding is expensive (API costs, time)
        - If content unchanged, don't re-embed
        - Saves money and time!

    Example Scenario:
        - First ingestion: content_hash = "abc123"
          → Embed all chunks

        - Re-ingestion (no changes): content_hash still "abc123"
          → Skip embedding (hash matches)

        - Re-ingestion (page edited): content_hash = "def456"
          → Re-embed chunks (hash changed)
    """
    raise NotImplementedError("TODO: Implement content change detection")