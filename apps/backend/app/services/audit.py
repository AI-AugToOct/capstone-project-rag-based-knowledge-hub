#LULUH

"""
Audit Service

This module handles logging all search queries for:
- Compliance and security audits
- Debugging (what did user search for?)
- Analytics (which docs are most useful?)
"""

from typing import List
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
        INSERT INTO audit_queries (user_id, query, used_doc_ids, created_at)
        VALUES (%s, %s, %s, NOW())

    Parameters:
        - %s (1st): user_id
        - %s (2nd): query
        - %s (3rd): used_doc_ids (array of integers)

    Example Usage:
        >>> user_id = "550e8400-e29b-41d4-a716-446655440000"
        >>> query = "How do I deploy Atlas?"
        >>> doc_ids = [1, 5, 12]
        >>> audit_log(user_id, query, doc_ids)
        # Row inserted into audit_queries table

    Why We Need This:
        - **Compliance**: Track who accessed what information
        - **Security**: Detect suspicious search patterns
        - **Analytics**: Which documents are most useful?
        - **Debugging**: Reproduce user issues

    Use Cases for Audit Logs:

    1. Compliance Audit:
       "Show me all queries by user X in the last 30 days"
       SELECT query, created_at
       FROM audit_queries
       WHERE user_id = 'xxx'
         AND created_at > NOW() - INTERVAL '30 days'

    2. Popular Documents:
       "Which documents are used most often?"
       SELECT doc_id, COUNT(*) as usage_count
       FROM audit_queries, unnest(used_doc_ids) AS doc_id
       GROUP BY doc_id
       ORDER BY usage_count DESC

    3. Search Analytics:
       "What are the most common questions?"
       SELECT query, COUNT(*) as frequency
       FROM audit_queries
       GROUP BY query
       ORDER BY frequency DESC

    4. Debugging:
       "User reported wrong answer, what did they search?"
       SELECT query, used_doc_ids, created_at
       FROM audit_queries
       WHERE user_id = 'xxx'
       ORDER BY created_at DESC
       LIMIT 10

    Database Schema:
        audit_queries table:
        - id: BIGSERIAL PRIMARY KEY (auto-increment)
        - user_id: UUID (references employees.employee_id)
        - query: TEXT (the question)
        - used_doc_ids: BIGINT[] (array of document IDs)
        - created_at: TIMESTAMPTZ DEFAULT now()

    Example Row:
        {
          "id": 42,
          "user_id": "550e8400-e29b-41d4-a716-446655440000",
          "query": "How do I deploy Atlas?",
          "used_doc_ids": [1, 5, 12],
          "created_at": "2025-01-15T14:32:18Z"
        }

    Error Handling:
        - If audit fails, log the error but DON'T fail the API request
        - User should still get their answer even if logging fails
        - Wrap in try/except and log errors

    Privacy Considerations:
        - Audit logs contain sensitive data (user queries)
        - Restrict access to audit_queries table (only admins)
        - Consider retention policy (delete logs after 90 days?)
        - Comply with GDPR/privacy laws

    Dependencies:
        - Database connection (from app.db.client)
        - PostgreSQL with support for array types

    Implementation Hints:
        - Use parameterized query (prevent SQL injection)
        - Convert used_doc_ids to PostgreSQL array format
        - Don't wait for insert to complete (fire and forget)
        - Consider async insert for better performance

    Edge Cases:
        - Empty used_doc_ids → insert empty array []
        - Very long query → might need to truncate
        - Database unavailable → catch exception, don't crash

    Performance:
        - This is a simple INSERT, very fast (~1-5ms)
        - Don't block the API response waiting for this
        - Consider batching logs for high-traffic scenarios

    Testing:
        - Verify row is inserted correctly
        - Verify all fields are populated
        - Verify array format is correct
        - Test with empty used_doc_ids
    """
    sql = """
        INSERT INTO audit_queries (user_id, query, used_doc_ids, created_at)
        VALUES ($1, $2, $3, NOW())
    """
    try:
        await execute(sql, user_id, query, used_doc_ids)
    except Exception as e:
        logging.error(f"Failed to insert audit log: {e}")