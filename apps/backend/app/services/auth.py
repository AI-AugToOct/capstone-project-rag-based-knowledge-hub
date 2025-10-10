"""
Authentication and Authorization Service

This module handles:
- JWT token verification from Supabase
- Loading user project memberships from database
- Ensuring users can only access documents they have permission for
""" 
#Raghad


from typing import List, Optional
import os
import jwt
from fastapi import HTTPException
from app.db.client import fetch_all, fetch_one


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
            audience="authenticated",  # Supabase uses "authenticated" for logged-in users
            options={"verify_signature": True, "verify_exp": True}
        )

        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no sub")
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
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


async def get_user_role(user_id: str, project_id: str) -> Optional[str]:
    """
    Get user's role for a specific project.

    Args:
        user_id: Employee ID
        project_id: Project ID

    Returns:
        'member' or 'manager' if user is in project, None otherwise
    """
    query = """
        SELECT role
        FROM employee_projects
        WHERE employee_id = $1 AND project_id = $2
    """
    row = await fetch_one(query, user_id, project_id)
    return row["role"] if row else None


async def check_user_is_manager(user_id: str, project_id: Optional[str] = None) -> bool:
    """
    Check if user is a manager (in any project or specific project).

    Args:
        user_id: Employee ID
        project_id: Optional project ID. If None, checks if user is manager in ANY project

    Returns:
        True if user is a manager, False otherwise
    """
    if project_id:
        role = await get_user_role(user_id, project_id)
        return role == "manager"
    else:
        # Check if user is manager in ANY project
        query = """
            SELECT EXISTS(
                SELECT 1 FROM employee_projects
                WHERE employee_id = $1 AND role = 'manager'
            )
        """
        row = await fetch_one(query, user_id)
        return row["exists"] if row else False

