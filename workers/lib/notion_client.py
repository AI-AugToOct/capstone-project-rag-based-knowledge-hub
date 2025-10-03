"""
Notion API Client

This module handles all interactions with the Notion API.
Used to fetch pages and blocks from Notion databases.
"""

from typing import List, Dict, Any
import os


def list_notion_pages(database_id: str) -> List[Dict[str, Any]]:
    """
    Fetches all pages from a Notion database.

    Args:
        database_id (str): The Notion database ID
            Example: "abc123def456"
            How to get: From Notion database URL
                https://notion.so/workspace/abc123def456?v=...
                                          ^^^^^^^^^^^^

    Returns:
        List[Dict[str, Any]]: List of page objects
            Example: [
                {
                    "id": "page-uuid-1",
                    "properties": {
                        "Title": {"title": [{"plain_text": "Atlas Deploy Guide"}]},
                        "Project": {"select": {"name": "Atlas"}},
                        "Status": {"status": {"name": "Published"}}
                    },
                    "url": "https://notion.so/Atlas-Deploy-abc123",
                    "last_edited_time": "2025-01-15T10:30:00Z"
                },
                ...
            ]

    What This Does:
        1. Gets Notion API key from environment (NOTION_API_KEY)
        2. Calls Notion API: POST https://api.notion.com/v1/databases/{database_id}/query
        3. Paginates through all results (Notion returns max 100 per request)
        4. Returns list of all pages in the database

    Example Usage:
        >>> database_id = "abc123def456"
        >>> pages = list_notion_pages(database_id)
        >>> print(f"Found {len(pages)} pages")
        Found 42 pages
        >>> print(pages[0]["properties"]["Title"]["title"][0]["plain_text"])
        "Atlas Deploy Guide"

    Why We Need This:
        - Starting point for ingestion pipeline
        - Discovers all documents to process
        - Gets metadata (title, project, last_edited_time)

    Notion API Endpoint:
        POST https://api.notion.com/v1/databases/{database_id}/query

    Request Headers:
        Authorization: Bearer {NOTION_API_KEY}
        Notion-Version: 2022-06-28
        Content-Type: application/json

    Request Body (for pagination):
        {
            "start_cursor": "optional-cursor-from-previous-response"
        }

    Response Format:
        {
            "results": [
                { "id": "page-1", "properties": {...}, ... },
                { "id": "page-2", "properties": {...}, ... }
            ],
            "has_more": true,
            "next_cursor": "abc123"
        }

    Pagination:
        - Notion returns max 100 pages per request
        - If has_more=true, make another request with next_cursor
        - Keep fetching until has_more=false

    Extracting Page Properties:
        # Title property
        title = page["properties"]["Title"]["title"][0]["plain_text"]

        # Project property (select field)
        project = page["properties"]["Project"]["select"]["name"]

        # Last edited time
        updated_at = page["last_edited_time"]

    Common Notion Property Types:
        - title: {"title": [{"plain_text": "text"}]}
        - rich_text: {"rich_text": [{"plain_text": "text"}]}
        - select: {"select": {"name": "option"}}
        - multi_select: {"multi_select": [{"name": "tag1"}, ...]}
        - date: {"date": {"start": "2025-01-15"}}
        - status: {"status": {"name": "In Progress"}}

    Rate Limiting:
        - Notion API: 3 requests per second
        - Add delay between requests: time.sleep(0.4)
        - Handle 429 Too Many Requests error (retry with backoff)

    Error Handling:
        - 401 Unauthorized → Invalid API key
        - 404 Not Found → Database doesn't exist or not shared with integration
        - 429 Too Many Requests → Rate limit exceeded
        - Always check response.status_code

    Dependencies:
        - requests library: pip install requests
        - Environment variable: NOTION_API_KEY

    API Documentation:
        https://developers.notion.com/reference/post-database-query

    Implementation Hints:
        - import requests
        - headers = {
            "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
            "Notion-Version": "2022-06-28"
          }
        - url = f"https://api.notion.com/v1/databases/{database_id}/query"
        - Handle pagination in a loop
        - Collect all pages in a list

    Testing:
        - Create test Notion database with 2-3 pages
        - Share database with your integration
        - Run function and verify all pages are returned
    """
    raise NotImplementedError("TODO: Implement Notion pages fetching with pagination")


def fetch_blocks(page_id: str) -> List[Dict[str, Any]]:
    """
    Fetches all content blocks from a Notion page.

    Args:
        page_id (str): The Notion page ID (UUID)
            Example: "page-uuid-123abc"

    Returns:
        List[Dict[str, Any]]: List of block objects
            Example: [
                {
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"plain_text": "Deployment"}]}
                },
                {
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": "To deploy Atlas API..."}]}
                },
                {
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"plain_text": "Step 1: Configure environment"}]}
                }
            ]

    What This Does:
        1. Gets Notion API key from environment
        2. Calls Notion API: GET https://api.notion.com/v1/blocks/{page_id}/children
        3. Paginates through all blocks (Notion returns max 100 per request)
        4. Returns list of all blocks in the page

    Example Usage:
        >>> page_id = "page-uuid-123abc"
        >>> blocks = fetch_blocks(page_id)
        >>> print(f"Page has {len(blocks)} blocks")
        Page has 25 blocks
        >>> print(blocks[0]["type"])
        "heading_1"

    Why We Need This:
        - Notion pages are made of "blocks" (paragraphs, headings, lists, etc.)
        - We need the actual content, not just metadata
        - Blocks are converted to Markdown for processing

    Notion Block Types:
        - paragraph: Regular text
        - heading_1, heading_2, heading_3: Headings
        - bulleted_list_item: Bullet points
        - numbered_list_item: Numbered lists
        - code: Code blocks
        - quote: Blockquotes
        - callout: Highlighted boxes
        - toggle: Collapsible sections
        - table: Tables
        - divider: Horizontal rules

    Block Structure:
        {
            "id": "block-uuid",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"plain_text": "This is a paragraph."}
                ]
            },
            "has_children": false
        }

    Handling Nested Blocks:
        - Some blocks have children (toggle, callout, etc.)
        - If has_children=true, recursively fetch children:
          GET /v1/blocks/{block_id}/children
        - Build tree structure or flatten to list

    Notion API Endpoint:
        GET https://api.notion.com/v1/blocks/{page_id}/children

    Request Headers:
        Authorization: Bearer {NOTION_API_KEY}
        Notion-Version: 2022-06-28

    Response Format:
        {
            "results": [
                {"type": "heading_1", ...},
                {"type": "paragraph", ...}
            ],
            "has_more": true,
            "next_cursor": "abc123"
        }

    Pagination (same as list_notion_pages):
        - Max 100 blocks per request
        - Use next_cursor for pagination
        - Loop until has_more=false

    Rate Limiting:
        - Same as list_notion_pages (3 req/sec)
        - Add time.sleep(0.4) between requests

    Dependencies:
        - requests library
        - Environment variable: NOTION_API_KEY

    API Documentation:
        https://developers.notion.com/reference/get-block-children

    Implementation Hints:
        - Similar structure to list_notion_pages
        - Handle pagination
        - Optionally handle nested blocks (has_children=true)
        - For V1, flat list is sufficient

    Testing:
        - Create test page with various block types
        - Fetch blocks and verify all are returned
        - Check different block types are parsed correctly
    """
    raise NotImplementedError("TODO: Implement Notion blocks fetching with pagination")