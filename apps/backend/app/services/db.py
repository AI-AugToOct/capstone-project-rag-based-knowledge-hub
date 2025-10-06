from typing import Optional, Dict, Any, List
from app.db.client import fetch_one, fetch_all


async def fetch_document(doc_id: int, is_manager: bool, user_token: str) -> Optional[Dict[str, Any]]:
    if is_manager:
        query = """
            SELECT doc_id, title, uri, visibility, project_id
            FROM documents
            WHERE doc_id = $1 AND deleted_at IS NULL
        """
        return await fetch_one(query, doc_id)
    
    query = """
        SELECT d.doc_id, d.title, d.uri, d.visibility, d.project_id
        FROM documents d
        LEFT JOIN employee_projects ep ON ep.project_id = d.project_id
        LEFT JOIN employees e ON e.employee_id = ep.employee_id
        WHERE d.doc_id = $1
          AND d.deleted_at IS NULL
          AND (d.visibility='Public' OR e.token=$2)
    """
    return await fetch_one(query, doc_id, user_token)

async def fetch_documents_for_user(is_manager: bool, user_token: str) -> List[Dict[str, Any]]:
    if is_manager:
        query = """
            SELECT doc_id, title, uri, visibility, project_id
            FROM documents
            WHERE deleted_at IS NULL
            ORDER BY doc_id DESC
        """
        return await fetch_all(query)
    
    query = """
        SELECT DISTINCT d.doc_id, d.title, d.uri, d.visibility, d.project_id
        FROM documents d
        LEFT JOIN employee_projects ep ON ep.project_id = d.project_id
        LEFT JOIN employees e ON e.employee_id = ep.employee_id
        WHERE d.deleted_at IS NULL
          AND (d.visibility='Public' OR e.token=$1)
        ORDER BY d.doc_id DESC
    """
    return await fetch_all(query, user_token)
