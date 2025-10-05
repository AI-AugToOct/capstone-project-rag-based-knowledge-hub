"""
Test normalizer

Run with: pytest workers/tests/test_normalizer.py -v
"""

import pytest
from lib.normalizer import normalize_to_markdown


def test_normalize_heading_1():
    """Test converting heading_1 blocks"""

    # Given: Notion blocks with heading_1
    blocks = [
        {
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"plain_text": "Deployment Guide"}]
            }
        }
    ]

    # When
    markdown, sections = normalize_to_markdown(blocks)

    # Then
    assert "# Deployment Guide" in markdown
    assert len(sections) == 0  # No content yet, just heading

    print("✅ normalize_to_markdown() converts heading_1")


def test_normalize_paragraphs():
    """Test converting paragraph blocks"""

    # Given
    blocks = [
        {
            "type": "heading_1",
            "heading_1": {"rich_text": [{"plain_text": "Deploy"}]}
        },
        {
            "type": "paragraph",
            "paragraph": {"rich_text": [{"plain_text": "To deploy, run make deploy."}]}
        }
    ]

    # When
    markdown, sections = normalize_to_markdown(blocks)

    # Then
    assert "# Deploy" in markdown
    assert "To deploy, run make deploy." in markdown
    assert len(sections) == 1
    assert sections[0]["heading_path"] == ["Deploy"]
    assert "make deploy" in sections[0]["text"]

    print("✅ normalize_to_markdown() converts paragraphs with heading_path")


def test_normalize_lists():
    """Test converting list blocks"""

    # Given
    blocks = [
        {
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"plain_text": "First item"}]}
        },
        {
            "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": [{"plain_text": "Second item"}]}
        }
    ]

    # When
    markdown, sections = normalize_to_markdown(blocks)

    # Then
    assert "- First item" in markdown
    assert "1. Second item" in markdown

    print("✅ normalize_to_markdown() converts lists")


def test_normalize_code_blocks():
    """Test converting code blocks"""

    # Given
    blocks = [
        {
            "type": "code",
            "code": {
                "rich_text": [{"plain_text": "print('hello')"}],
                "language": "python"
            }
        }
    ]

    # When
    markdown, sections = normalize_to_markdown(blocks)

    # Then
    assert "python" in markdown
    assert "print('hello')" in markdown

    print("✅ normalize_to_markdown() converts code blocks")


def test_normalize_nested_headings():
    """Test heading hierarchy (heading_path tracking)"""

    # Given: Nested headings
    blocks = [
        {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "H1"}]}},
        {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Text under H1"}]}},
        {"type": "heading_2", "heading_2": {"rich_text": [{"plain_text": "H2"}]}},
        {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Text under H2"}]}},
    ]

    # When
    markdown, sections = normalize_to_markdown(blocks)

    # Then
    assert len(sections) == 2
    assert sections[0]["heading_path"] == ["H1"]
    assert sections[1]["heading_path"] == ["H1", "H2"]

    print("✅ normalize_to_markdown() tracks heading hierarchy!")


def test_normalize_empty_blocks():
    """Test with empty blocks"""

    # Given
    blocks = []

    # When
    markdown, sections = normalize_to_markdown(blocks)

    # Then
    assert markdown == ""
    assert sections == []

    print("✅ normalize_to_markdown() handles empty input")


if __name__ == "__main__":
    test_normalize_heading_1()
    test_normalize_paragraphs()
    test_normalize_lists()
    test_normalize_code_blocks()
    test_normalize_nested_headings()
    test_normalize_empty_blocks()
    print("All normalizer tests passed!")