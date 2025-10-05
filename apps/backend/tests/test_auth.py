"""
Test auth service

Run with: pytest apps/backend/tests/test_auth.py -v
"""

import pytest
from app.services.auth import verify_jwt, get_user_projects
import os


def test_verify_jwt_with_test_token():
    """Test verify_jwt() with a test JWT token"""

    # Create a test JWT (you need to generate this from Supabase or create one)
    # For now, we'll show the structure
    test_jwt = os.getenv("TEST_JWT_TOKEN")

    if not test_jwt:
        pytest.skip("Set TEST_JWT_TOKEN environment variable to test JWT verification")

    # When
    user_id = verify_jwt(test_jwt)

    # Then - Verify requirements from table:
    # Returns user_id string
    assert isinstance(user_id, str), f"Expected string, got {type(user_id)}"
    assert len(user_id) > 0, "user_id is empty"

    print(f"✅ verify_jwt() works! User ID: {user_id}")


def test_verify_jwt_invalid_token():
    """Test that invalid JWT raises error"""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt("invalid.token.here")

    assert exc_info.value.status_code == 401


def test_verify_jwt_missing_token():
    """Test that missing JWT raises error"""
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        verify_jwt("")


@pytest.mark.asyncio
async def test_get_user_projects():
    """Test get_user_projects() with test DB"""

    # You need a test user in your database
    test_user_id = os.getenv("TEST_USER_ID")

    if not test_user_id:
        pytest.skip("Set TEST_USER_ID environment variable to test user projects")

    # When
    projects = await get_user_projects(test_user_id)

    # Then - Verify requirements from table:
    # Returns list of strings
    assert isinstance(projects, list), f"Expected list, got {type(projects)}"
    assert all(isinstance(p, str) for p in projects), "Not all projects are strings"

    print(f"✅ get_user_projects() works! Projects: {projects}")


@pytest.mark.asyncio
async def test_get_user_projects_no_projects():
    """Test user with no projects returns empty list"""

    # Use a UUID that doesn't exist in employee_projects
    fake_user_id = "00000000-0000-0000-0000-000000000000"

    # When
    projects = await get_user_projects(fake_user_id)

    # Then
    assert projects == [], f"Expected empty list, got {projects}"

    print("✅ get_user_projects() handles users with no projects")


if __name__ == "__main__":
    import asyncio

    # Run sync tests
    test_verify_jwt_invalid_token()
    test_verify_jwt_missing_token()

    # Run async tests
    asyncio.run(test_get_user_projects())
    asyncio.run(test_get_user_projects_no_projects())

    print("All auth tests passed!")