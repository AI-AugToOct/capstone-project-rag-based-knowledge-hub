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
    embedding: List[float],
    order_in_doc: int
) -> int:
    """
    Inserts a chunk into the database.

    Args:
        doc_id: Document ID this chunk belongs to
        text: Chunk text content
        heading_path: List of heading hierarchy (e.g., ["Deployment", "Steps"])
        embedding: 1024-dimensional embedding vector
        order_in_doc: Order of this chunk in the document (0-based index)

    Returns:
        chunk_id: The ID of the newly created chunk

    Example:
        >>> chunk_id = await insert_chunk(
        ...     doc_id=123,
        ...     text="To deploy the API...",
        ...     heading_path=["Deployment", "Steps"],
        ...     embedding=[0.1, 0.2, ...],
        ...     order_in_doc=0
        ... )
    """
    pool = get_db_pool()

    # Convert embedding list to PostgreSQL vector format
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO chunks (doc_id, text, heading_path, embedding, order_in_doc)
            VALUES ($1, $2, $3, $4::vector, $5)
            RETURNING chunk_id
        """, doc_id, text, heading_path, embedding_str, order_in_doc)

    return row["chunk_id"]


# ============================================================================
# Handover Database Operations
# ============================================================================

async def create_handover(
    from_employee_id: str,
    to_employee_id: str,
    title: str,
    project_id: Optional[str] = None,
    context: Optional[str] = None,
    current_status: Optional[str] = None,
    next_steps: Optional[List[Dict[str, Any]]] = None,
    resources: Optional[List[Dict[str, Any]]] = None,
    contacts: Optional[List[Dict[str, Any]]] = None,
    additional_notes: Optional[str] = None,
    cc_employee_ids: Optional[List[str]] = None
) -> int:
    """
    Creates a new handover.

    Args:
        from_employee_id: Sender's employee ID (UUID)
        to_employee_id: Recipient's employee ID (UUID)
        title: Handover title
        project_id: Optional project ID
        context: Why this handover exists
        current_status: What's been done
        next_steps: List of tasks [{"task": "...", "done": false}]
        resources: List of resources [{"type": "doc", "doc_id": 123, "title": "..."}]
        contacts: List of contacts [{"name": "...", "email": "...", "role": "..."}]
        additional_notes: Free-form notes
        cc_employee_ids: List of employee IDs to CC

    Returns:
        handover_id: The ID of the newly created handover
    """
    import json
    pool = get_db_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO handovers (
                from_employee_id, to_employee_id, title, project_id,
                context, current_status, next_steps, resources, contacts,
                additional_notes, cc_employee_ids, status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb, $9::jsonb, $10, $11, 'pending')
            RETURNING handover_id
        """,
            from_employee_id, to_employee_id, title, project_id,
            context, current_status,
            json.dumps(next_steps) if next_steps else None,
            json.dumps(resources) if resources else None,
            json.dumps(contacts) if contacts else None,
            additional_notes, cc_employee_ids
        )

    return row["handover_id"]


async def get_user_handovers(user_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Gets all handovers for a user (received + sent).

    Args:
        user_id: Employee ID (UUID)

    Returns:
        {
            "received": [...],
            "sent": [...]
        }
    """
    pool = get_db_pool()

    async with pool.acquire() as conn:
        # Received handovers (where user is recipient or CC'd)
        received_rows = await conn.fetch("""
            SELECT
                h.handover_id,
                h.title,
                h.project_id,
                h.context,
                h.current_status,
                h.next_steps,
                h.resources,
                h.contacts,
                h.additional_notes,
                h.status,
                h.created_at,
                h.acknowledged_at,
                h.completed_at,
                h.from_employee_id::text as from_employee_id,
                h.to_employee_id::text as to_employee_id,
                from_emp.display_name as from_name,
                from_emp.email as from_email,
                p.name as project_name
            FROM handovers h
            LEFT JOIN employees from_emp ON h.from_employee_id = from_emp.employee_id
            LEFT JOIN projects p ON h.project_id = p.project_id
            WHERE h.to_employee_id = $1 OR $1 = ANY(h.cc_employee_ids)
            ORDER BY h.created_at DESC
        """, user_id)

        # Sent handovers (where user is sender)
        sent_rows = await conn.fetch("""
            SELECT
                h.handover_id,
                h.title,
                h.project_id,
                h.context,
                h.current_status,
                h.next_steps,
                h.resources,
                h.contacts,
                h.additional_notes,
                h.status,
                h.created_at,
                h.acknowledged_at,
                h.completed_at,
                h.from_employee_id::text as from_employee_id,
                h.to_employee_id::text as to_employee_id,
                to_emp.display_name as to_name,
                to_emp.email as to_email,
                p.name as project_name
            FROM handovers h
            LEFT JOIN employees to_emp ON h.to_employee_id = to_emp.employee_id
            LEFT JOIN projects p ON h.project_id = p.project_id
            WHERE h.from_employee_id = $1
            ORDER BY h.created_at DESC
        """, user_id)

    import json

    def parse_handover_row(row):
        """Parse JSONB fields from database row"""
        d = dict(row)
        # Parse JSONB fields if they're strings
        for field in ['next_steps', 'resources', 'contacts']:
            if d.get(field) and isinstance(d[field], str):
                d[field] = json.loads(d[field])
        return d

    return {
        "received": [parse_handover_row(row) for row in received_rows],
        "sent": [parse_handover_row(row) for row in sent_rows]
    }


async def get_handover_by_id(handover_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Gets a single handover by ID (with ACL check).

    Args:
        handover_id: Handover ID
        user_id: Employee ID (for ACL check)

    Returns:
        Handover dict or None if not found or user doesn't have access
    """
    pool = get_db_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT
                h.handover_id,
                h.title,
                h.project_id,
                h.context,
                h.current_status,
                h.next_steps,
                h.resources,
                h.contacts,
                h.additional_notes,
                h.status,
                h.created_at,
                h.acknowledged_at,
                h.completed_at,
                h.from_employee_id::text as from_employee_id,
                h.to_employee_id::text as to_employee_id,
                ARRAY(SELECT unnest(h.cc_employee_ids)::text) as cc_employee_ids,
                from_emp.display_name as from_name,
                from_emp.email as from_email,
                to_emp.display_name as to_name,
                to_emp.email as to_email,
                p.name as project_name
            FROM handovers h
            LEFT JOIN employees from_emp ON h.from_employee_id = from_emp.employee_id
            LEFT JOIN employees to_emp ON h.to_employee_id = to_emp.employee_id
            LEFT JOIN projects p ON h.project_id = p.project_id
            WHERE h.handover_id = $1
              AND (
                h.from_employee_id = $2
                OR h.to_employee_id = $2
                OR $2 = ANY(h.cc_employee_ids)
              )
        """, handover_id, user_id)

    if not row:
        return None

    import json
    d = dict(row)

    # Parse JSONB fields if they're strings
    for field in ['next_steps', 'resources', 'contacts']:
        if d.get(field) and isinstance(d[field], str):
            d[field] = json.loads(d[field])

    return d


async def update_handover_status(
    handover_id: int,
    user_id: str,
    status: str
) -> bool:
    """
    Updates handover status (acknowledge or complete).

    Args:
        handover_id: Handover ID
        user_id: Employee ID (must be recipient to update)
        status: "acknowledged" or "completed"

    Returns:
        True if updated, False if not found or unauthorized
    """
    pool = get_db_pool()

    async with pool.acquire() as conn:
        # Only recipient can acknowledge/complete
        if status == "acknowledged":
            result = await conn.execute("""
                UPDATE handovers
                SET status = 'acknowledged', acknowledged_at = NOW()
                WHERE handover_id = $1 AND to_employee_id = $2 AND status = 'pending'
            """, handover_id, user_id)
        elif status == "completed":
            result = await conn.execute("""
                UPDATE handovers
                SET status = 'completed', completed_at = NOW()
                WHERE handover_id = $1 AND to_employee_id = $2 AND status IN ('pending', 'acknowledged')
            """, handover_id, user_id)
        else:
            return False

    return result != "UPDATE 0"


async def delete_handover(handover_id: int, user_id: str) -> bool:
    """
    Deletes a handover (only sender can delete).

    Args:
        handover_id: Handover ID
        user_id: Employee ID (must be sender)

    Returns:
        True if deleted, False if not found or unauthorized
    """
    pool = get_db_pool()

    async with pool.acquire() as conn:
        result = await conn.execute("""
            DELETE FROM handovers
            WHERE handover_id = $1 AND from_employee_id = $2
        """, handover_id, user_id)

    return result != "DELETE 0"