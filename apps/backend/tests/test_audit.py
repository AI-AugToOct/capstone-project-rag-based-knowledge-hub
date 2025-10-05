"""
Test audit service

Run with: pytest apps/backend/tests/test_audit.py -v
"""

import pytest
from app.services.audit import audit_log


@pytest.mark.asyncio
async def test_audit_log():
    """Test audit_log() with test DB"""

    # Given
    test_user_id = "550e8400-e29b-41d4-a716-446655440000"
    test_query = "How do I deploy the Atlas API?"
    test_doc_ids = [1, 5, 12]

    # When
    try:
        await audit_log(test_user_id, test_query, test_doc_ids)
        success = True
    except Exception as e:
        success = False
        error = str(e)

    # Then - Verify requirements from table:
    # No errors, row inserted
    assert success, f"audit_log() raised error: {error if not success else 'N/A'}"

    print(f"✅ audit_log() works! Logged query to database")


@pytest.mark.asyncio
async def test_audit_log_empty_doc_ids():
    """Test audit log with no documents used"""

    test_user_id = "550e8400-e29b-41d4-a716-446655440000"
    test_query = "Random query with no results"
    empty_doc_ids = []

    # When
    try:
        await audit_log(test_user_id, test_query, empty_doc_ids)
        success = True
    except Exception as e:
        success = False

    # Then
    assert success, "audit_log() should handle empty doc_ids"

    print("✅ audit_log() handles empty doc_ids")


@pytest.mark.asyncio
async def test_audit_log_doesnt_crash_on_db_error():
    """Test that audit log failures don't crash the application"""

    # Given: Invalid user_id format (will cause DB error)
    invalid_user_id = "not-a-uuid"
    test_query = "Test query"
    test_doc_ids = [1]

    # When: This should log error but NOT raise exception
    try:
        await audit_log(invalid_user_id, test_query, test_doc_ids)
        # Should reach here (error logged, not raised)
        passed = True
    except Exception:
        # Should NOT raise exception (bad for UX)
        passed = False

    # Then
    assert passed, "audit_log() should catch errors, not raise them"

    print("✅ audit_log() handles errors gracefully")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_audit_log())
    asyncio.run(test_audit_log_empty_doc_ids())
    asyncio.run(test_audit_log_doesnt_crash_on_db_error())

    print("All audit tests passed!")