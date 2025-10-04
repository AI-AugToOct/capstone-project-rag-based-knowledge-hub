"""
Authentication and Authorization Service

This module handles:
- JWT token verification from Supabase
- Loading user project memberships from database
- Ensuring users can only access documents they have permission for
""" 
#Raghad


from typing import List
import os
from jose import jwt
from fastapi import HTTPException
from app.db.client import fetch_all


JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "change-me")
JWT_ALG = "HS256"


def verify_jwt(token: str) -> str:
    
    """
    Verify a Supabase JWT and extract user_id (sub).
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        decoded = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALG],
            options={"verify_signature": True, "verify_exp": True}
        )
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no sub")
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    """
    Verifies a Supabase JWT token and extracts the user ID.

    Args:
        token (str): JWT token from Authorization header
            Example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImlhdCI6MTY0MDk5NTIwMCwiZXhwIjoxNjQwOTk4ODAwfQ.abc123"

    Returns:
        str: User ID (employee_id) extracted from JWT
            Example: "550e8400-e29b-41d4-a716-446655440000"

    Raises:
        ValueError: If token is invalid, expired, or has wrong signature
        Exception: If SUPABASE_JWT_SECRET is not set in environment

    What This Does:
        1. Decodes the JWT token using Supabase's secret key
        2. Verifies the signature matches (ensures token wasn't tampered with)
        3. Checks token hasn't expired
        4. Extracts the 'sub' (subject) claim which contains the user_id
        5. Returns the user_id as a string

    Example Usage:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> user_id = verify_jwt(token)
        >>> print(user_id)
        "550e8400-e29b-41d4-a716-446655440000"

    Why We Need This:
        - Every API request must verify the user's identity
        - JWT tokens are signed by Supabase, so we can trust them if signature is valid
        - Without this, anyone could impersonate any user
        - This is the foundation of our access control system

    Dependencies:
        - python-jose[cryptography] library for JWT handling
        - Environment variable: SUPABASE_JWT_SECRET

    Security Notes:
        - NEVER log or print the actual token (contains sensitive data)
        - NEVER expose the JWT secret
        - Always check token expiration (reject expired tokens)
        - Validate the 'aud' (audience) claim if needed

    API Reference:
        https://supabase.com/docs/guides/auth/server-side-rendering#verify-jwt

    Implementation Hints:
        - Use jose.jwt.decode() with the secret
        - Set options={"verify_signature": True, "verify_exp": True}
        - Extract user_id from decoded['sub']
    """


    
    

async def get_user_projects(user_id: str) -> List[str]:
    """
    Retrieves all project IDs for a user.
    """
    query = """
        SELECT project_id
        FROM employee_projects
        WHERE employee_id = $1
    """
    rows = await fetch_all(query, user_id)
    return [row["project_id"] for row in rows]
    """
    Retrieves all project IDs that a user has access to.

    Args:
        user_id (str): The user's employee ID (UUID from Supabase Auth)
            Example: "550e8400-e29b-41d4-a716-446655440000"

    Returns:
        List[str]: List of project IDs the user belongs to
            Example: ["Atlas", "Phoenix", "Bolt"]
            Example (no projects): []

    Raises:
        Exception: If database query fails

    What This Does:
        1. Connects to the database
        2. Queries the employee_projects table
        3. Finds all rows where employee_id matches the input
        4. Returns a list of project_id values

    Example Usage:
        >>> user_id = "550e8400-e29b-41d4-a716-446655440000"
        >>> projects = get_user_projects(user_id)
        >>> print(projects)
        ["Atlas", "Phoenix"]

    SQL Query:
        SELECT project_id
        FROM employee_projects
        WHERE employee_id = %s

    Why We Need This:
        - Access control is based on project membership
        - Users can only see documents from:
          1. Projects they belong to (this function returns those)
          2. Public documents (visible to everyone)
        - This list is used to filter vector search results

    Example Scenario:
        - Sarah belongs to ["Atlas", "Phoenix"]
        - When Sarah searches, she sees:
          ✅ Atlas documents (she's in Atlas)
          ✅ Phoenix documents (she's in Phoenix)
          ✅ Public documents (everyone sees these)
          ❌ Bolt documents (she's NOT in Bolt)

    Database Schema:
        employee_projects table:
        - employee_id (UUID) → Foreign key to employees
        - project_id (TEXT) → Foreign key to projects
        - role (TEXT) → 'owner', 'editor', 'viewer' (optional for V1)

    Edge Cases:
        - User exists but has no projects → return []
        - User doesn't exist in employee_projects → return []
        - Don't fail the query, just return empty list

    Dependencies:
        - Database connection (from app.db.client)
        - asyncpg or psycopg2 for PostgreSQL queries

    Implementation Hints:
        - Use parameterized queries to prevent SQL injection
        - Return empty list if no rows found (not None)
        - Consider caching results for performance (optional)
    """
    raise NotImplementedError("TODO: Implement get_user_projects query")

