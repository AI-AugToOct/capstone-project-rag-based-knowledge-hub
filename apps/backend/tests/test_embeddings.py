"""
Test embeddings service

Run with: pytest apps/backend/tests/test_embeddings.py -v
"""

import pytest
from app.services.embeddings import embed_query

def test_embed_query_basic():
    """Test embed_query() with real API call"""
    # Given
    query = "How do I deploy the Atlas API?"

    # When
    result = embed_query(query)

    # Then - Verify requirements from table:
    # 1. Returns 1024 dimensions
    assert len(result) == 1024, f"Expected 1024 dims, got {len(result)}"

    # 2. All elements are floats
    assert all(isinstance(x, float) for x in result), "Not all elements are floats"

    # 3. Not all zeros (actual embedding)
    assert result != [0.0] * 1024, "Embedding is all zeros"

    print(f"✅ embed_query() works! First 5 values: {result[:5]}")


def test_embed_query_empty_string():
    """Test that empty query raises error"""
    with pytest.raises(ValueError):
        embed_query("")


def test_embed_query_none():
    """Test that None query raises error"""
    with pytest.raises(ValueError):
        embed_query(None)


if __name__ == "__main__":
    # Can run directly: python tests/test_embeddings.py
    test_embed_query_basic()
    test_embed_query_empty_string()
    test_embed_query_none()
    print("All embeddings tests passed!")