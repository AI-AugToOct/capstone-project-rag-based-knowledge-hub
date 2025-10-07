"""
Tests for handovers API endpoints

Tests all handover REST API endpoints:
- POST /api/handovers (create)
- GET /api/handovers (list)
- GET /api/handovers/:id (get single)
- PATCH /api/handovers/:id (update status)
- DELETE /api/handovers/:id (delete)

Run with: pytest apps/backend/tests/test_handovers_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.db import create_handover, get_handover_by_id
import os

client = TestClient(app)

# Test employee IDs
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
RECIPIENT_USER_ID = "660e8400-e29b-41d4-a716-446655440001"


@pytest.fixture
def test_jwt():
    """Get test JWT token from environment"""
    token = os.getenv("TEST_JWT_TOKEN")
    if not token:
        pytest.skip("Set TEST_JWT_TOKEN environment variable to test API endpoints")
    return token


@pytest.fixture
def recipient_jwt():
    """Get recipient JWT token from environment"""
    token = os.getenv("RECIPIENT_JWT_TOKEN")
    if not token:
        pytest.skip("Set RECIPIENT_JWT_TOKEN environment variable to test API endpoints")
    return token


def test_create_handover_success(test_jwt):
    """Test POST /api/handovers - create handover successfully"""
    response = client.post(
        "/api/handovers",
        json={
            "to_employee_id": RECIPIENT_USER_ID,
            "title": "API Test Handover",
            "project_id": "Atlas",
            "context": "Testing via API",
            "current_status": "In progress",
            "next_steps": [{"task": "Test task", "done": False}]
        },
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Test Handover"
    assert data["status"] == "pending"
    assert "handover_id" in data


def test_create_handover_unauthorized():
    """Test POST /api/handovers - without auth token"""
    response = client.post(
        "/api/handovers",
        json={
            "to_employee_id": RECIPIENT_USER_ID,
            "title": "Should Fail"
        }
    )

    assert response.status_code == 401


def test_create_handover_to_self(test_jwt):
    """Test POST /api/handovers - cannot create handover to yourself"""
    response = client.post(
        "/api/handovers",
        json={
            "to_employee_id": TEST_USER_ID,  # Same as sender
            "title": "Handover to Self"
        },
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 400
    assert "Cannot create handover to yourself" in response.json()["detail"]


def test_list_handovers_success(test_jwt):
    """Test GET /api/handovers - list user's handovers"""
    response = client.get(
        "/api/handovers",
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "received" in data
    assert "sent" in data
    assert isinstance(data["received"], list)
    assert isinstance(data["sent"], list)


def test_list_handovers_unauthorized():
    """Test GET /api/handovers - without auth"""
    response = client.get("/api/handovers")

    assert response.status_code == 401


def test_get_handover_by_id_success(test_jwt):
    """Test GET /api/handovers/:id - get single handover"""
    response = client.get(
        "/api/handovers/1",
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["handover_id"] == 1
    assert "title" in data
    assert "status" in data


def test_get_handover_by_id_not_found(test_jwt):
    """Test GET /api/handovers/:id - non-existent handover"""
    response = client.get(
        "/api/handovers/99999",
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 404


def test_get_handover_by_id_unauthorized():
    """Test GET /api/handovers/:id - without auth"""
    response = client.get("/api/handovers/1")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_handover_status_acknowledge(recipient_jwt):
    """Test PATCH /api/handovers/:id - acknowledge handover"""
    # Create a handover first
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Status Update Test",
        project_id="Atlas"
    )

    # Recipient acknowledges
    response = client.patch(
        f"/api/handovers/{handover_id}",
        json={"status": "acknowledged"},
        headers={"Authorization": f"Bearer {recipient_jwt}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["acknowledged_at"] is not None


@pytest.mark.asyncio
async def test_update_handover_status_complete(recipient_jwt):
    """Test PATCH /api/handovers/:id - complete handover"""
    # Create a handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Complete Test",
        project_id="Phoenix"
    )

    # Recipient completes
    response = client.patch(
        f"/api/handovers/{handover_id}",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {recipient_jwt}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_update_handover_status_unauthorized(test_jwt):
    """Test PATCH /api/handovers/:id - sender cannot update status"""
    # Create a handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Unauthorized Update Test",
        project_id="Atlas"
    )

    # Sender tries to acknowledge (should fail, only recipient can)
    response = client.patch(
        f"/api/handovers/{handover_id}",
        json={"status": "acknowledged"},
        headers={"Authorization": f"Bearer {test_jwt}"}  # Sender's token
    )

    assert response.status_code == 403


def test_update_handover_status_invalid():
    """Test PATCH /api/handovers/:id - without auth"""
    response = client.patch(
        "/api/handovers/1",
        json={"status": "acknowledged"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_handover_success(test_jwt):
    """Test DELETE /api/handovers/:id - sender deletes handover"""
    # Create a handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Delete Test",
        project_id="Atlas"
    )

    # Sender deletes
    response = client.delete(
        f"/api/handovers/{handover_id}",
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 204

    # Verify it's deleted
    handover = await get_handover_by_id(handover_id, TEST_USER_ID)
    assert handover is None


@pytest.mark.asyncio
async def test_delete_handover_unauthorized(recipient_jwt):
    """Test DELETE /api/handovers/:id - recipient cannot delete"""
    # Create a handover
    handover_id = await create_handover(
        from_employee_id=TEST_USER_ID,
        to_employee_id=RECIPIENT_USER_ID,
        title="Unauthorized Delete Test",
        project_id="Phoenix"
    )

    # Recipient tries to delete (should fail, only sender can)
    response = client.delete(
        f"/api/handovers/{handover_id}",
        headers={"Authorization": f"Bearer {recipient_jwt}"}
    )

    assert response.status_code == 404  # Or 403


def test_delete_handover_no_auth():
    """Test DELETE /api/handovers/:id - without auth"""
    response = client.delete("/api/handovers/1")

    assert response.status_code == 401


def test_create_handover_with_all_fields(test_jwt):
    """Test POST /api/handovers - with all optional fields"""
    response = client.post(
        "/api/handovers",
        json={
            "to_employee_id": RECIPIENT_USER_ID,
            "title": "Complete Handover",
            "project_id": "Atlas",
            "context": "Full test with all fields",
            "current_status": "All systems go",
            "next_steps": [
                {"task": "Task 1", "done": True},
                {"task": "Task 2", "done": False}
            ],
            "resources": [
                {"type": "doc", "doc_id": 1, "title": "Guide"},
                {"type": "link", "url": "https://example.com", "title": "Link"}
            ],
            "contacts": [
                {"name": "Alice", "email": "alice@example.com", "role": "Manager"}
            ],
            "additional_notes": "Important notes here",
            "cc_employee_ids": [RECIPIENT_USER_ID]
        },
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete Handover"
    assert data["context"] == "Full test with all fields"
    assert len(data["next_steps"]) == 2
    assert len(data["resources"]) == 2
    assert len(data["contacts"]) == 1


def test_handover_response_structure(test_jwt):
    """Test that handover response has all expected fields"""
    response = client.get(
        "/api/handovers/1",
        headers={"Authorization": f"Bearer {test_jwt}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify required fields
    required_fields = [
        "handover_id", "title", "status", "created_at",
        "from_employee_id", "to_employee_id"
    ]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify optional fields exist (even if None)
    optional_fields = [
        "project_id", "context", "current_status", "next_steps",
        "resources", "contacts", "additional_notes",
        "acknowledged_at", "completed_at",
        "from_name", "to_name", "project_name"
    ]
    for field in optional_fields:
        assert field in data, f"Missing optional field: {field}"