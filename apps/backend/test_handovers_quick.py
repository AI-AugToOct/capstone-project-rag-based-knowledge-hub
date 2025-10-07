"""
Quick Handovers API Test Script

Tests all 5 handover endpoints with real HTTP calls.
Run with: python test_handovers_quick.py

This tests:
1. GET /api/handovers (list)
2. POST /api/handovers (create)
3. GET /api/handovers/:id (get single)
4. PATCH /api/handovers/:id (update status)
5. DELETE /api/handovers/:id (delete)
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = os.getenv("TEST_JWT_TOKEN")

# Test user IDs from seed data
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"  # John Employee
RECIPIENT_ID = "660e8400-e29b-41d4-a716-446655440001"  # Sarah Manager

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_1_list_handovers():
    """Test GET /api/handovers"""
    print("\n[1] Testing GET /api/handovers (list)")

    response = requests.get(f"{BASE_URL}/api/handovers", headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()

    assert "received" in data, "Missing 'received' key"
    assert "sent" in data, "Missing 'sent' key"
    assert isinstance(data["received"], list), "'received' should be a list"
    assert isinstance(data["sent"], list), "'sent' should be a list"

    print(f"   OK - List handovers: {len(data['received'])} received, {len(data['sent'])} sent")
    return data


def test_2_create_handover():
    """Test POST /api/handovers"""
    print("\n[2] Testing POST /api/handovers (create)")

    payload = {
        "to_employee_id": RECIPIENT_ID,
        "title": "Automated Test Handover",
        "project_id": "atlas-api",
        "context": "Testing handover creation via script",
        "current_status": "Ready for handover",
        "next_steps": [
            {"task": "Review documentation", "done": False},
            {"task": "Schedule meeting", "done": False}
        ],
        "resources": [
            {"type": "link", "url": "https://example.com", "title": "Documentation"}
        ],
        "contacts": [
            {"name": "Tech Lead", "email": "lead@example.com", "role": "Support"}
        ],
        "additional_notes": "This is a test handover created by automated script"
    }

    response = requests.post(f"{BASE_URL}/api/handovers", headers=headers, json=payload)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()

    assert "handover_id" in data, "Missing handover_id"
    assert data["title"] == payload["title"], "Title mismatch"
    assert data["status"] == "pending", f"Expected status 'pending', got {data['status']}"
    assert data["from_employee_id"] == TEST_USER_ID, "from_employee_id mismatch"
    assert data["to_employee_id"] == RECIPIENT_ID, "to_employee_id mismatch"

    print(f"   OK - Created handover ID: {data['handover_id']}")
    return data["handover_id"]


def test_3_get_single_handover(handover_id):
    """Test GET /api/handovers/:id"""
    print(f"\n[3] Testing GET /api/handovers/{handover_id} (get single)")

    response = requests.get(f"{BASE_URL}/api/handovers/{handover_id}", headers=headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["handover_id"] == handover_id, "handover_id mismatch"
    assert "title" in data, "Missing title"
    assert "status" in data, "Missing status"
    assert "next_steps" in data, "Missing next_steps"
    assert "resources" in data, "Missing resources"
    assert "contacts" in data, "Missing contacts"

    print(f"   OK - Retrieved handover: {data['title']}")
    return data


def test_4_update_status(handover_id):
    """Test PATCH /api/handovers/:id (update status)"""
    print(f"\n[4] Testing PATCH /api/handovers/{handover_id} (update status)")

    # Note: Only recipient can update status, so this will fail with 403
    # because we're using sender's token
    payload = {"status": "acknowledged"}

    response = requests.patch(f"{BASE_URL}/api/handovers/{handover_id}", headers=headers, json=payload)

    # We expect 403 because sender can't acknowledge their own handover
    assert response.status_code == 403, f"Expected 403 (sender can't update), got {response.status_code}"

    print(f"   OK - Correctly rejected sender's attempt to update status (403)")


def test_5_delete_handover(handover_id):
    """Test DELETE /api/handovers/:id"""
    print(f"\n[5] Testing DELETE /api/handovers/{handover_id} (delete)")

    response = requests.delete(f"{BASE_URL}/api/handovers/{handover_id}", headers=headers)

    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    print(f"   OK - Deleted handover ID: {handover_id}")

    # Verify it's gone
    verify_response = requests.get(f"{BASE_URL}/api/handovers/{handover_id}", headers=headers)
    assert verify_response.status_code == 404, f"Handover should be deleted (404), got {verify_response.status_code}"

    print(f"   OK - Verified handover is deleted (404)")


def test_6_error_cases():
    """Test error handling"""
    print("\n[6] Testing error cases")

    # Test without auth
    response = requests.get(f"{BASE_URL}/api/handovers")
    assert response.status_code == 401, f"Expected 401 (no auth), got {response.status_code}"
    print("   OK - Correctly rejected request without auth (401)")

    # Test invalid handover ID
    response = requests.get(f"{BASE_URL}/api/handovers/99999", headers=headers)
    assert response.status_code == 404, f"Expected 404 (not found), got {response.status_code}"
    print("   OK - Correctly returned 404 for non-existent handover")

    # Test creating handover to self
    payload = {
        "to_employee_id": TEST_USER_ID,  # Same as sender
        "title": "Handover to Self"
    }
    response = requests.post(f"{BASE_URL}/api/handovers", headers=headers, json=payload)
    assert response.status_code == 400, f"Expected 400 (bad request), got {response.status_code}"
    print("   OK - Correctly rejected handover to self (400)")


def main():
    print("=" * 70)
    print("Handovers API Comprehensive Test Suite")
    print("=" * 70)

    if not TOKEN:
        print("ERROR: TEST_JWT_TOKEN not set in .env")
        print("   Run: python generate_test_jwt.py employee")
        return

    print(f"Testing against: {BASE_URL}")
    print(f"Test user: {TEST_USER_ID}")

    try:
        # Run tests in sequence
        test_1_list_handovers()
        handover_id = test_2_create_handover()
        test_3_get_single_handover(handover_id)
        test_4_update_status(handover_id)
        test_5_delete_handover(handover_id)
        test_6_error_cases()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! Handovers API is working perfectly!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())