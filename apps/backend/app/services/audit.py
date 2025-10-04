# LULUH

"""
Audit Service
Handles logging of user search queries for compliance, debugging, and analytics.
"""

from typing import List
import logging
from app.db.client import execute


async def audit_log(user_id: str, query: str, used_doc_ids: List[int]) -> None:
    """Insert a new audit log entry into the database."""
    sql = """
        INSERT INTO audit_queries (user_id, query, used_doc_ids, created_at)
        VALUES ($1, $2, $3, NOW())
    """
    try:
        await execute(sql, user_id, query, used_doc_ids)
    except Exception as e:
        logging.error(f"Failed to insert audit log: {e}")
    # Knowing that we log errors but do not raise
    # its better to avoid impacting user experience