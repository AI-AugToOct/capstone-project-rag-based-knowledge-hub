"""
Database Client

This module provides a connection pool to PostgreSQL using asyncpg.
All database queries go through this client.
"""

import asyncpg
import os
from typing import List, Dict, Any, Optional


# Global connection pool (initialized on startup)
pool: Optional[asyncpg.Pool] = None


async def init_db_pool():
    """
    Initializes the database connection pool.

    What This Does:
        1. Gets DATABASE_URL from environment
        2. Creates a connection pool with asyncpg
        3. Stores pool in global variable
        4. Pool is shared across all requests (efficient!)

    Why Connection Pooling:
        - Opening a new connection for each request is slow (~50-100ms)
        - Connection pool maintains 10-20 open connections
        - Requests reuse existing connections (~1ms)
        - Much better performance under load

    When This Runs:
        - Called once during app startup (in main.py)
        - Pool stays alive for the entire application lifecycle

    Pool Configuration:
        - min_size: Minimum connections to keep open (default: 10)
        - max_size: Maximum connections allowed (default: 20)
        - command_timeout: Query timeout in seconds (default: 60)

    Example:
        # In main.py (startup event)
        from app.db.client import init_db_pool

        @app.on_event("startup")
        async def startup():
            await init_db_pool()

    Raises:
        Exception: If DATABASE_URL is not set or connection fails

    Dependencies:
        - asyncpg library: pip install asyncpg
        - Environment variable: DATABASE_URL

    Implementation Hints:
        - global pool
        - database_url = os.getenv("DATABASE_URL")
        - pool = await asyncpg.create_pool(database_url, min_size=10, max_size=20)
    """
    global pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable is not set")

    pool = await asyncpg.create_pool(
        database_url,
        min_size=10,
        max_size=20,
        command_timeout=60
    )

    print(f"✅ Database connection pool initialized (min_size=10, max_size=20)")


async def close_db_pool():
    """
    Closes the database connection pool.

    What This Does:
        - Closes all connections in the pool
        - Frees up resources

    When This Runs:
        - Called during app shutdown (in main.py)

    Example:
        # In main.py (shutdown event)
        from app.db.client import close_db_pool

        @app.on_event("shutdown")
        async def shutdown():
            await close_db_pool()

    Implementation Hints:
        - global pool
        - if pool:
        -     await pool.close()
    """
    global pool

    if pool:
        await pool.close()
        print("✅ Database connection pool closed")


async def fetch_one(query: str, *args) -> Optional[Dict[str, Any]]:
    """
    Executes a SELECT query and returns a single row.

    Args:
        query (str): SQL query with $1, $2, ... placeholders
            Example: "SELECT * FROM employees WHERE employee_id = $1"

        *args: Values for query parameters
            Example: ("550e8400-e29b-41d4-a716-446655440000",)

    Returns:
        Optional[Dict[str, Any]]: Single row as dictionary, or None if no results
            Example: {
                "employee_id": "550e8400-...",
                "email": "sarah@company.com",
                "display_name": "Sarah Chen"
            }

    Example Usage:
        >>> query = "SELECT * FROM employees WHERE employee_id = $1"
        >>> user_id = "550e8400-e29b-41d4-a716-446655440000"
        >>> row = await fetch_one(query, user_id)
        >>> print(row["email"])
        "sarah@company.com"

    Why We Need This:
        - Common pattern: fetch one employee, one document, etc.
        - Cleaner than fetch_all() when you expect 1 result
        - Returns None if not found (easy to check)

    Implementation Hints:
        - async with pool.acquire() as connection:
        -     row = await connection.fetchrow(query, *args)
        -     return dict(row) if row else None
    """
    if pool is None:
        raise Exception("Database pool not initialized. Call init_db_pool() first.")

    async with pool.acquire() as connection:
        row = await connection.fetchrow(query, *args)
        return dict(row) if row else None


async def fetch_all(query: str, *args) -> List[Dict[str, Any]]:
    """
    Executes a SELECT query and returns all rows.

    Args:
        query (str): SQL query with $1, $2, ... placeholders
            Example: "SELECT project_id FROM employee_projects WHERE employee_id = $1"

        *args: Values for query parameters
            Example: ("550e8400-e29b-41d4-a716-446655440000",)

    Returns:
        List[Dict[str, Any]]: List of rows as dictionaries
            Example: [
                {"project_id": "Atlas"},
                {"project_id": "Phoenix"}
            ]
            Empty list if no results

    Example Usage:
        >>> query = "SELECT project_id FROM employee_projects WHERE employee_id = $1"
        >>> user_id = "550e8400-..."
        >>> rows = await fetch_all(query, user_id)
        >>> project_ids = [row["project_id"] for row in rows]
        >>> print(project_ids)
        ["Atlas", "Phoenix"]

    Why We Need This:
        - Most common database operation
        - Fetching multiple projects, chunks, etc.
        - Always returns a list (empty if no results)

    PostgreSQL Placeholders:
        - Use $1, $2, $3 for parameters (not ?)
        - asyncpg uses PostgreSQL's native format
        - Prevents SQL injection

    Implementation Hints:
        - async with pool.acquire() as connection:
        -     rows = await connection.fetch(query, *args)
        -     return [dict(row) for row in rows]
    """
    if pool is None:
        raise Exception("Database pool not initialized. Call init_db_pool() first.")

    async with pool.acquire() as connection:
        rows = await connection.fetch(query, *args)
        return [dict(row) for row in rows]


async def execute(query: str, *args) -> str:
    """
    Executes an INSERT, UPDATE, or DELETE query.

    Args:
        query (str): SQL query with $1, $2, ... placeholders
            Example: "INSERT INTO audit_queries (user_id, query, used_doc_ids) VALUES ($1, $2, $3)"

        *args: Values for query parameters
            Example: ("550e8400-...", "How do I deploy?", [1, 5, 12])

    Returns:
        str: Status message from database
            Example: "INSERT 0 1" (1 row inserted)
            Example: "UPDATE 3" (3 rows updated)

    Example Usage:
        >>> query = "INSERT INTO audit_queries (user_id, query, used_doc_ids) VALUES ($1, $2, $3)"
        >>> await execute(query, user_id, query_text, doc_ids)

    Why We Need This:
        - For INSERT, UPDATE, DELETE operations
        - Doesn't return rows, just status
        - Used in audit logging, updates, etc.

    Implementation Hints:
        - async with pool.acquire() as connection:
        -     status = await connection.execute(query, *args)
        -     return status
    """
    if pool is None:
        raise Exception("Database pool not initialized. Call init_db_pool() first.")

    async with pool.acquire() as connection:
        status = await connection.execute(query, *args)
        return status


# Example Usage in Services:
#
# from app.db.client import fetch_one, fetch_all, execute
#
# # Get user's projects
# async def get_user_projects(user_id: str) -> List[str]:
#     query = "SELECT project_id FROM employee_projects WHERE employee_id = $1"
#     rows = await fetch_all(query, user_id)
#     return [row["project_id"] for row in rows]
#
# # Log audit entry
# async def audit_log(user_id: str, query: str, doc_ids: List[int]):
#     sql = "INSERT INTO audit_queries (user_id, query, used_doc_ids) VALUES ($1, $2, $3)"
#     await execute(sql, user_id, query, doc_ids)
#
# # Vector search
# async def run_vector_search(qvec: List[float], projects: List[str], top_k: int):
#     query = """
#         SELECT c.chunk_id, c.text, d.title, d.uri,
#                1 - (c.embedding <=> $1::vector) AS score
#         FROM chunks c
#         JOIN documents d ON d.doc_id = c.doc_id
#         WHERE d.deleted_at IS NULL
#           AND (d.visibility = 'Public' OR d.project_id = ANY($2))
#         ORDER BY c.embedding <=> $1::vector
#         LIMIT $3
#     """
#     return await fetch_all(query, qvec, projects, top_k)


# Connection Pool Best Practices:
#
# 1. Initialize once on startup
#    - Don't create new pool for each request
#    - Reuse the global pool
#
# 2. Use connection context managers
#    - async with pool.acquire() as conn: ...
#    - Automatically returns connection to pool
#
# 3. Set reasonable pool sizes
#    - min_size=10: Always keep 10 connections ready
#    - max_size=20: Don't exceed 20 connections
#    - Adjust based on traffic
#
# 4. Handle connection errors
#    - Retry transient errors
#    - Log persistent errors
#    - Don't crash the app
#
# 5. Close pool on shutdown
#    - Free resources cleanly
#    - Important for graceful shutdown