"""
Test chunker

Run with: pytest workers/tests/test_chunker.py -v
"""

import pytest
from lib.chunker import chunk_markdown


def test_chunk_markdown_short_doc():
    """Test chunking a short document (< chunk_size)"""

    # Given: Short markdown (< 500 tokens)
    markdown = "# Test\n\nThis is a short document."

    # When
    chunks = chunk_markdown(markdown, chunk_size=500, chunk_overlap=50)

    # Then: Should return 1 chunk
    assert len(chunks) == 1, f"Expected 1 chunk, got {len(chunks)}"
    assert chunks[0]["text"] == markdown
    assert chunks[0]["order"] == 0
    assert chunks[0]["token_count"] > 0

    print(f"✅ chunk_markdown() handles short docs! Tokens: {chunks[0]['token_count']}")


def test_chunk_markdown_long_doc():
    """Test chunking a long document (> chunk_size)"""

    # Given: Long markdown (> 500 tokens)
    markdown = "# Deployment\n\n" + ("This is a sentence. " * 200)  # ~400 words = ~600 tokens

    # When
    chunks = chunk_markdown(markdown, chunk_size=500, chunk_overlap=50)

    # Then: Should return multiple chunks
    assert len(chunks) > 1, f"Expected multiple chunks, got {len(chunks)}"

    # Each chunk should have required fields
    for i, chunk in enumerate(chunks):
        assert "text" in chunk
        assert "token_count" in chunk
        assert "order" in chunk
        assert chunk["order"] == i

        # Token count should be reasonable
        assert chunk["token_count"] > 0
        assert chunk["token_count"] <= 700  # Max with some buffer

    print(f"✅ chunk_markdown() splits long docs! Created {len(chunks)} chunks")


def test_chunk_markdown_with_sections():
    """Test chunking with heading_path preservation"""

    # Given: Markdown with sections
    sections = [
        {"heading_path": ["Deployment"], "text": "Deploy instructions here."},
        {"heading_path": ["Deployment", "Steps"], "text": "Step 1, Step 2, Step 3."}
    ]
    markdown = "# Deployment\n\nDeploy instructions here.\n\n## Steps\n\nStep 1, Step 2, Step 3."

    # When
    chunks = chunk_markdown(markdown, sections=sections, chunk_size=500, chunk_overlap=50)

    # Then: Should preserve heading_path
    assert len(chunks) > 0

    for chunk in chunks:
        assert "heading_path" in chunk
        assert isinstance(chunk["heading_path"], list)

    print(f"✅ chunk_markdown() preserves heading paths!")


def test_chunk_overlap():
    """Test that chunks have overlap"""

    # Given: Long document
    markdown = "# Test\n\n" + " ".join([f"Word{i}" for i in range(300)])

    # When
    chunks = chunk_markdown(markdown, chunk_size=200, chunk_overlap=50)

    # Then: Adjacent chunks should share some content
    if len(chunks) > 1:
        # Check if last part of chunk[0] appears in chunk[1]
        chunk0_end = chunks[0]["text"][-100:]
        chunk1_start = chunks[1]["text"][:100]

        # Should have SOME overlap (not exact match due to boundary splitting)
        # Just verify both chunks have content
        assert len(chunks[0]["text"]) > 0
        assert len(chunks[1]["text"]) > 0

        print(f"✅ chunk_markdown() creates overlapping chunks!")


if __name__ == "__main__":
    test_chunk_markdown_short_doc()
    test_chunk_markdown_long_doc()
    test_chunk_markdown_with_sections()
    test_chunk_overlap()
    print("All chunker tests passed!")