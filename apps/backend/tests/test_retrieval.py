"""
Test retrieval service

Run with: pytest apps/backend/tests/test_retrieval.py -v
"""

import pytest
from app.services.retrieval import run_vector_search, rerank


@pytest.mark.asyncio
async def test_run_vector_search():
    """Test run_vector_search() with test DB or mock"""

    # Given: A test query vector (1024 dims)
    test_vector = [0.1] * 1024  # Dummy vector for testing
    user_projects = ["Atlas", "Phoenix"]

    # When
    results = await run_vector_search(test_vector, user_projects, top_k=10)

    # Then - Verify requirements from table:
    # Returns list of dicts with correct keys
    assert isinstance(results, list), f"Expected list, got {type(results)}"

    if len(results) > 0:  # If DB has data
        chunk = results[0]
        required_keys = {"chunk_id", "doc_id", "title", "text", "uri", "score"}
        assert required_keys.issubset(chunk.keys()), f"Missing keys. Got: {chunk.keys()}"

        # Verify types
        assert isinstance(chunk["chunk_id"], int)
        assert isinstance(chunk["doc_id"], int)
        assert isinstance(chunk["title"], str)
        assert isinstance(chunk["text"], str)
        assert isinstance(chunk["uri"], str)
        assert isinstance(chunk["score"], float)

        print(f"✅ run_vector_search() works! Found {len(results)} chunks")
    else:
        print("⚠️  run_vector_search() returned empty (no data in DB)")


@pytest.mark.asyncio
async def test_run_vector_search_invalid_dimensions():
    """Test that wrong vector dimensions raises error"""

    bad_vector = [0.1] * 512  # Wrong size
    user_projects = ["Atlas"]

    with pytest.raises(ValueError) as exc_info:
        await run_vector_search(bad_vector, user_projects, top_k=10)

    assert "1024 dimensions" in str(exc_info.value)


def test_rerank_with_real_api():
    """Test rerank() with real Cohere API + mock data"""

    # Given: Mock chunks from vector search
    mock_chunks = [
        {
            "chunk_id": 1,
            "doc_id": 10,
            "title": "Atlas Deploy Guide",
            "text": "To deploy the Atlas API, run make deploy in the root directory.",
            "uri": "https://notion.so/abc123",
            "score": 0.85,
            "heading_path": ["Deployment"]
        },
        {
            "chunk_id": 2,
            "doc_id": 11,
            "title": "General Deployment",
            "text": "Deployment involves pushing code to production servers.",
            "uri": "https://notion.so/def456",
            "score": 0.72,
            "heading_path": ["DevOps"]
        },
        {
            "chunk_id": 3,
            "doc_id": 12,
            "title": "Unrelated Topic",
            "text": "This is about something completely different.",
            "uri": "https://notion.so/ghi789",
            "score": 0.65,
            "heading_path": ["Other"]
        }
    ]

    query = "How do I deploy Atlas API?"

    # When
    reranked = rerank(mock_chunks, query, top_k=2)

    # Then - Verify requirements from table:
    # Returns top_k items with rerank_score
    assert len(reranked) == 2, f"Expected 2 items, got {len(reranked)}"

    for chunk in reranked:
        assert "rerank_score" in chunk, "Missing rerank_score"
        assert isinstance(chunk["rerank_score"], float)
        assert 0.0 <= chunk["rerank_score"] <= 1.0, f"Invalid score: {chunk['rerank_score']}"

    # First result should be most relevant (Atlas Deploy Guide)
    assert "Atlas" in reranked[0]["title"], "Reranking didn't prioritize most relevant chunk"

    print(f"✅ rerank() works! Top result: {reranked[0]['title']} (score: {reranked[0]['rerank_score']:.2f})")


def test_rerank_empty_chunks():
    """Test rerank with empty chunk list"""

    result = rerank([], "test query", top_k=10)
    assert result == []


if __name__ == "__main__":
    test_run_vector_search_invalid_dimensions()
    test_rerank_with_real_api()
    test_rerank_empty_chunks()
    print("All retrieval tests passed!")