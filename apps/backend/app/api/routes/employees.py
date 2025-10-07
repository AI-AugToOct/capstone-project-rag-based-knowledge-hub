from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List
from app.services import auth
from app.db.client import get_db_pool

router = APIRouter()


@router.get("/employees/search")
async def search_employees(
    q: str = Query(..., min_length=1, description="Search query (name or email)"),
    authorization: Optional[str] = Header(None)
):
    """Search employees by name or email."""

    # Auth check
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        user_id = auth.verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Search employees in database
    pool = get_db_pool()

    query = """
        SELECT
            employee_id::text,
            email,
            display_name
        FROM employees
        WHERE
            LOWER(display_name) LIKE LOWER($1)
            OR LOWER(email) LIKE LOWER($1)
        ORDER BY display_name
        LIMIT 10
    """

    search_pattern = f"%{q}%"

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, search_pattern)

    results = [
        {
            "employee_id": row["employee_id"],
            "email": row["email"],
            "display_name": row["display_name"]
        }
        for row in rows
    ]

    return {"employees": results}