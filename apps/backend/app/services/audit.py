<<<<<<< HEAD
# LULUH
=======
#LULUH
>>>>>>> 4ab9f07 (add)

"""
Audit Service
Handles logging of user search queries for compliance, debugging, and analytics.
"""

from typing import List
<<<<<<< HEAD
import logging
from app.db.client import execute


async def audit_log(user_id: str, query: str, used_doc_ids: List[int]) -> None:
    """Insert a new audit log entry into the database."""
    sql = """
=======
import os # ماله داعي غالبا
from app.db.client import execute #اضفته
import logging #اضفته


# raise NotImplementedError("TODO: Implement audit logging to database") تمت المهمة

async def audit_log(user_id: str, query: str, used_doc_ids: List[int]) -> None:
    """
    Logs a search query to the audit_queries table.

    Args:
        user_id (str): The employee ID who made the query
            Example: "550e8400-e29b-41d4-a716-446655440000"

        query (str): The user's search question
            Example: "How do I deploy the Atlas API?"

        used_doc_ids (List[int]): IDs of documents that contributed to the answer
            Example: [1, 5, 12]
            Example (no docs used): []

    Returns:
        None

    Raises:
        Exception: If database insert fails (should NOT fail the API request)

    What This Does:
        1. Connects to the database
        2. Inserts a row into audit_queries table with:
           - user_id: who asked
           - query: what they asked
           - used_doc_ids: which docs were used (PostgreSQL array)
           - created_at: timestamp (auto-set by database)
        3. Returns (no need to return anything)

    SQL Insert:
>>>>>>> 4ab9f07 (add)
        INSERT INTO audit_queries (user_id, query, used_doc_ids, created_at)
        VALUES ($1, $2, $3, NOW())
    """
<<<<<<< HEAD
    try:
        await execute(sql, user_id, query, used_doc_ids)
    except Exception as e:
        logging.error(f"Failed to insert audit log: {e}")
    # Knowing that we log errors but do not raise
    # its better to avoid impacting user experience
=======
    sql = """
        INSERT INTO audit_queries (user_id, query, used_doc_ids, created_at)
        VALUES ($1, $2, $3, NOW())
    """
    try:
        await execute(sql, user_id, query, used_doc_ids)
    except Exception as e:
        logging.error(f"Failed to insert audit log: {e}")
>>>>>>> 4ab9f07 (add)
