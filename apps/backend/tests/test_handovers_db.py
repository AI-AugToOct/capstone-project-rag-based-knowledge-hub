"""
Tests for handovers database functions

Tests the database layer for handovers:
- create_handover()
- get_user_handovers()
- get_handover_by_id()
- update_handover_status()
- delete_handover()
"""

import pytest
from app.services.db import (
    create_handover,
    get_user_handovers,
    get_handover_by_id,
    update_handover_status,
    delete_handover
)

# Test employee IDs (from seed_test_data.sql)
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
RECIPIENT_USER_ID = "660e8400-e29b-41d4-a716-446655440001"


@pytest.mark.asyncio
async def test_create_handover():
    """Test creating a new handover"""
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Test Handover - Database Layer",
        project_id="Atlas",
        context="Testing handover creation",
        current_status="In progress",
        next_steps=[{"task": "Test task 1", "done": False}],
        resources=[{"type": "link", "url": "https://test.com", "title": "Test Resource"}],
        contacts=[{"name": "Test Contact", "email": "test@test.com", "role": "Tester"}],
        additional_notes="This is a test handover",
        cc_employee_ids=None
    )

    assert handover_id is not None
    assert isinstance(handover_id, int)
    assert handover_id > 0


@pytest.mark.asyncio
async def test_get_user_handovers():
    """Test fetching handovers for a user (sent + received)"""
    handovers = await get_user_handovers(TEST_USER_ID)

    assert "received" in handovers
    assert "sent" in handovers
    assert isinstance(handovers["received"], list)
    assert isinstance(handovers["sent"], list)

    # Test user should have at least 1 received and 1 sent handover from seed data
    assert len(handovers["received"]) >= 1
    assert len(handovers["sent"]) >= 1

    # Verify structure of returned handovers
    if handovers["sent"]:
        sent = handovers["sent"][0]
        assert "handover_id" in sent
        assert "title" in sent
        assert "status" in sent
        assert "to_name" in sent  # Should have recipient name


@pytest.mark.asyncio
async def test_get_handover_by_id_authorized():
    """Test fetching a single handover when user has access"""
    # User 1 sent handover ID 1 to User 2
    handover = await get_handover_by_id(handover_id=1, user_id=TEST_USER_ID)

    assert handover is not None
    assert handover["handover_id"] == 1
    assert handover["title"] == "Atlas Project Handover"
    assert handover["from_employee_id"] == TEST_USER_ID
    assert handover["to_employee_id"] == RECIPIENT_USER_ID


@pytest.mark.asyncio
async def test_get_handover_by_id_unauthorized():
    """Test that unauthorized users cannot access handovers"""
    # Create a fake user ID that shouldn't have access
    unauthorized_user = "999e8400-e29b-41d4-a716-446655440999"

    handover = await get_handover_by_id(handover_id=1, user_id=unauthorized_user)

    # Should return None for unauthorized access
    assert handover is None


@pytest.mark.asyncio
async def test_get_handover_by_id_recipient_access():
    """Test that recipient can access handover"""
    # Recipient User 2 should be able to access handover 1
    handover = await get_handover_by_id(handover_id=1, user_id=RECIPIENT_USER_ID)

    assert handover is not None
    assert handover["handover_id"] == 1
    assert handover["to_employee_id"] == RECIPIENT_USER_ID


@pytest.mark.asyncio
async def test_update_handover_status_acknowledge():
    """Test acknowledging a handover (recipient only)"""
    # Create a new handover for testing status update
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Status Test Handover",
        project_id="Phoenix",
        context="Testing status updates"
    )

    # Recipient acknowledges the handover
    success = await update_handover_status(
        handover_id=handover_id,
        user_id=RECIPIENT_USER_ID,
        status="acknowledged"
    )

    assert success is True

    # Verify status was updated
    handover = await get_handover_by_id(handover_id, RECIPIENT_USER_ID)
    assert handover["status"] == "acknowledged"
    assert handover["acknowledged_at"] is not None


@pytest.mark.asyncio
async def test_update_handover_status_complete():
    """Test completing a handover"""
    # Create a new handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Complete Test Handover",
        project_id="Phoenix"
    )

    # Recipient completes the handover
    success = await update_handover_status(
        handover_id=handover_id,
        user_id=RECIPIENT_USER_ID,
        status="completed"
    )

    assert success is True

    # Verify status was updated
    handover = await get_handover_by_id(handover_id, RECIPIENT_USER_ID)
    assert handover["status"] == "completed"
    assert handover["completed_at"] is not None


@pytest.mark.asyncio
async def test_update_handover_status_unauthorized():
    """Test that sender cannot acknowledge/complete (only recipient can)"""
    # Create a new handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Unauthorized Status Test",
        project_id="Atlas"
    )

    # Sender tries to acknowledge (should fail)
    success = await update_handover_status(
        handover_id=handover_id,
        user_id=TEST_USER_ID,  # Sender, not recipient
        status="acknowledged"
    )

    assert success is False


@pytest.mark.asyncio
async def test_delete_handover_by_sender():
    """Test that sender can delete their handover"""
    # Create a new handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Delete Test Handover",
        project_id="Atlas"
    )

    # Sender deletes the handover
    success = await delete_handover(handover_id, TEST_USER_ID)

    assert success is True

    # Verify it's deleted
    handover = await get_handover_by_id(handover_id, TEST_USER_ID)
    assert handover is None


@pytest.mark.asyncio
async def test_delete_handover_unauthorized():
    """Test that recipient cannot delete handover (only sender can)"""
    # Create a new handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Unauthorized Delete Test",
        project_id="Phoenix"
    )

    # Recipient tries to delete (should fail)
    success = await delete_handover(handover_id, RECIPIENT_USER_ID)

    assert success is False

    # Verify it still exists
    handover = await get_handover_by_id(handover_id, TEST_USER_ID)
    assert handover is not None


@pytest.mark.asyncio
async def test_handover_with_cc():
    """Test creating handover with CC'd users and verify they can access it"""
    cc_user_id = RECIPIENT_USER_ID

    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id="660e8400-e29b-41d4-a716-446655440001",  # Different recipient
        title="CC Test Handover",
        project_id="Atlas",
        cc_employee_ids=[cc_user_id]
    )

    # CC'd user should be able to access the handover
    handover = await get_handover_by_id(handover_id, cc_user_id)

    assert handover is not None
    assert handover["handover_id"] == handover_id
    assert cc_user_id in (handover.get("cc_employee_ids") or [])


@pytest.mark.asyncio
async def test_handover_full_fields():
    """Test creating handover with all optional fields populated"""
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Full Fields Handover",
        project_id="Phoenix",
        context="Complete test with all fields",
        current_status="All systems operational",
        next_steps=[
            {"task": "Task 1", "done": True},
            {"task": "Task 2", "done": False}
        ],
        resources=[
            {"type": "doc", "doc_id": 1, "title": "Atlas Guide"},
            {"type": "link", "url": "https://example.com", "title": "External Resource"}
        ],
        contacts=[
            {"name": "Alice", "email": "alice@example.com", "role": "Manager"},
            {"name": "Bob", "email": "bob@example.com", "role": "Developer"}
        ],
        additional_notes="These are comprehensive notes for the handover",
        cc_employee_ids=None
    )

    # Fetch and verify all fields
    handover = await get_handover_by_id(handover_id, TEST_USER_ID)

    assert handover["title"] == "Full Fields Handover"
    assert handover["context"] == "Complete test with all fields"
    assert handover["current_status"] == "All systems operational"
    assert len(handover["next_steps"]) == 2
    assert len(handover["resources"]) == 2
    assert len(handover["contacts"]) == 2
    assert handover["additional_notes"] == "These are comprehensive notes for the handover"