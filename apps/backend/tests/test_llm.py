"""
Test LLM service

Run with: pytest apps/backend/tests/test_llm.py -v
"""

import pytest
from app.services.llm import call_llm


def test_call_llm_with_real_api():
    """Test call_llm() with real Groq API + fake chunks"""

    # Given: Fake context chunks
    fake_chunks = [
        "To deploy the Atlas API, run 'make deploy' in the root directory.",
        "Ensure all environment variables are configured before deployment.",
        "The deployment process takes approximately 5 minutes."
    ]

    query = "How do I deploy the Atlas API?"

    # When
    answer = call_llm(query, fake_chunks)

    # Then - Verify requirements from table:
    # Returns non-empty string
    assert isinstance(answer, str), f"Expected string, got {type(answer)}"
    assert len(answer) > 0, "Answer is empty"
    assert len(answer) > 20, f"Answer too short ({len(answer)} chars), might be error message"

    # Answer should mention deployment (context-aware)
    assert any(word in answer.lower() for word in ["deploy", "make", "run"]), \
        "Answer doesn't seem to use the provided context"

    print(f"✅ call_llm() works! Answer preview: {answer[:100]}...")


def test_call_llm_with_empty_context():
    """Test LLM with no context chunks"""

    query = "How do I deploy?"
    empty_chunks = []

    # When
    answer = call_llm(query, empty_chunks)

    # Then: Should still return a string (might say "insufficient context")
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_call_llm_long_context():
    """Test LLM with many chunks"""

    # Given: 12 chunks (typical rerank output)
    chunks = [f"This is chunk {i} with some deployment information." for i in range(12)]
    query = "How do I deploy?"

    # When
    answer = call_llm(query, chunks)

    # Then
    assert isinstance(answer, str)
    assert len(answer) > 0

    print(f"✅ call_llm() handles 12 chunks! Answer length: {len(answer)} chars")


if __name__ == "__main__":
    test_call_llm_with_real_api()
    test_call_llm_with_empty_context()
    test_call_llm_long_context()
    print("All LLM tests passed!")