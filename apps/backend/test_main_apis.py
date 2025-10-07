"""
Quick API Test Script - Main Features

Tests the core APIs that the frontend will use:
1. Health check
2. Search API (RAG)
3. Documents API

Run with: python test_main_apis.py
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
TOKEN = os.getenv("TEST_JWT_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_1_health_check():
    """Test GET /health"""
    print("\n[1] Testing GET /health")

    response = requests.get(f"{BASE_URL}/health")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy", f"Expected healthy, got {data}"

    print("   OK - Backend is healthy")
    return data


def test_2_root_endpoint():
    """Test GET / (root)"""
    print("\n[2] Testing GET / (root)")

    response = requests.get(f"{BASE_URL}/")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "message" in data, "Missing message"
    assert "version" in data, "Missing version"

    print(f"   OK - API version: {data['version']}")
    return data


def test_3_search_api():
    """Test POST /api/search (main RAG feature)"""
    print("\n[3] Testing POST /api/search (RAG)")

    payload = {
        "query": "How do I deploy the Atlas API?"
    }

    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    # Check response structure
    assert "answer" in data, "Missing answer"
    assert "chunks" in data, "Missing chunks"
    assert isinstance(data["chunks"], list), "chunks should be a list"

    print(f"   OK - Search returned answer with {len(data['chunks'])} chunks")
    print(f"   Answer preview: {data['answer'][:100]}...")
    return data


def test_4_search_no_results():
    """Test search with query that has no results"""
    print("\n[4] Testing POST /api/search (no results)")

    payload = {
        "query": "xyzabc123nonexistentquery999"
    }

    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()

    assert "answer" in data, "Missing answer"
    # Should still return an answer (LLM says "no info found")

    print(f"   OK - Search with no results handled gracefully")
    return data


def test_5_search_unauthorized():
    """Test search without auth"""
    print("\n[5] Testing POST /api/search (no auth)")

    payload = {"query": "test"}

    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload
    )

    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    print("   OK - Correctly rejected request without auth (401)")


def test_6_get_document():
    """Test GET /api/docs/:id"""
    print("\n[6] Testing GET /api/docs/:id")

    # Try to get document ID 1 (from seed data)
    response = requests.get(
        f"{BASE_URL}/api/docs/1",
        headers=headers
    )

    if response.status_code == 404:
        print("   OK - No documents in database (404 expected if seed data not loaded)")
        return None

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert "doc_id" in data, "Missing doc_id"
    assert "title" in data, "Missing title"

    print(f"   OK - Retrieved document: {data['title']}")
    return data


def test_7_get_document_not_found():
    """Test GET /api/docs/:id (non-existent)"""
    print("\n[7] Testing GET /api/docs/99999 (not found)")

    response = requests.get(
        f"{BASE_URL}/api/docs/99999",
        headers=headers
    )

    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    print("   OK - Correctly returned 404 for non-existent document")


def main():
    print("=" * 70)
    print("Main APIs Test Suite")
    print("=" * 70)

    if not TOKEN:
        print("ERROR: TEST_JWT_TOKEN not set in .env")
        print("   Run: python generate_test_jwt.py employee")
        return 1

    print(f"Testing against: {BASE_URL}")

    try:
        test_1_health_check()
        test_2_root_endpoint()
        test_3_search_api()
        test_4_search_no_results()
        test_5_search_unauthorized()
        test_6_get_document()
        test_7_get_document_not_found()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! Main APIs are working!")
        print("=" * 70)
        print("\nReady to connect frontend!")

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())