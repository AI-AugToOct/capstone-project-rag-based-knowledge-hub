"""
Notion Ingestion Worker

Main script that orchestrates the ingestion pipeline:
Notion API → Normalize → Chunk → Embed → Database

Run this script manually or via cron/scheduler to sync Notion content.
"""

import argparse
import hashlib
from dotenv import load_dotenv
from lib import notion_client, normalizer, chunker, embeddings, db_operations
from lib.constants import CHUNK_SIZE, CHUNK_OVERLAP

# Load environment variables from .env file
load_dotenv()


def compute_content_hash(markdown: str) -> str:
    """
    Computes MD5 hash of content for change detection.

    Args:
        markdown (str): The Markdown content

    Returns:
        str: MD5 hash (hex string)

    Example:
        >>> hash1 = compute_content_hash("Hello world")
        >>> hash2 = compute_content_hash("Hello world")
        >>> hash3 = compute_content_hash("Different")
        >>> hash1 == hash2  # Same content → same hash
        True
        >>> hash1 == hash3  # Different content → different hash
        False
    """
    return hashlib.md5(markdown.encode()).hexdigest()


def detect_project_from_page(page: dict) -> str:
    """
    Extracts project ID from Notion page properties.

    Args:
        page (dict): Notion page object

    Returns:
        str: Project ID (e.g., "Atlas")

    Example:
        # Notion page has "Project" property with select field
        page["properties"]["Project"]["select"]["name"]  → "Atlas"
    """
    try:
        return page["properties"]["Project"]["select"]["name"]
    except (KeyError, TypeError):
        return "Uncategorized"  # Default if no project


def detect_visibility(page: dict) -> str:
    """
    Determines if document should be Public or Private.

    Args:
        page (dict): Notion page object

    Returns:
        str: "Public" or "Private"

    Example:
        # Notion page has "Visibility" status property
        page["properties"]["Visibility"]["status"]["name"]  → "Public"
    """
    try:
        visibility = page["properties"]["Visibility"]["status"]["name"]
        return visibility if visibility in ["Public", "Private"] else "Private"
    except (KeyError, TypeError):
        return "Private"  # Default to Private if not specified


def ingest_page(page: dict):
    """
    Ingests a single Notion page.

    What This Does:
        1. Fetch blocks from Notion
        2. Normalize to Markdown
        3. Compute content hash
        4. Upsert document (check if content changed)
        5. If changed: Delete old chunks, create new chunks
        6. Embed each chunk
        7. Insert chunks into database

    Args:
        page (dict): Notion page object from list_notion_pages()
    """
    page_id = page["id"]
    title = page["properties"]["Title"]["title"][0]["plain_text"]
    uri = page["url"]

    print(f"\n📄 Processing: {title}")

    # Step 1: Fetch blocks
    print("   ├─ Fetching blocks...")
    blocks = notion_client.fetch_blocks(page_id)
    print(f"   ├─ Found {len(blocks)} blocks")

    # Step 2: Normalize to Markdown
    print("   ├─ Converting to Markdown...")
    markdown, sections = normalizer.normalize_to_markdown(blocks)

    # Step 3: Compute content hash
    content_hash = compute_content_hash(markdown)

    # Step 4: Check if content changed (BEFORE upsert!)
    if not db_operations.check_content_changed(f"notion_{page_id}", content_hash):
        print("   └─ ✓ Content unchanged, skipping embedding")
        return

    # Step 5: Detect metadata
    project_id = detect_project_from_page(page)
    visibility = detect_visibility(page)

    print("   ├─ Content changed, re-embedding...")

    # Step 6: Upsert document
    print(f"   ├─ Upserting document (project={project_id}, visibility={visibility})...")
    doc_id = db_operations.upsert_document(
        source_external_id=f"notion_{page_id}",
        title=title,
        project_id=project_id,
        visibility=visibility,
        uri=uri,
        content_hash=content_hash
    )

    # Step 7: Chunk the document
    print("   ├─ Chunking document...")
    chunks = chunker.chunk_markdown(markdown, sections, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    print(f"   ├─ Created {len(chunks)} chunks")

    # Step 8: Embed and insert each chunk
    print("   ├─ Embedding chunks...")
    for i, chunk in enumerate(chunks):
        # Embed the chunk
        embedding = embeddings.embed_text(chunk["text"])

        # Insert into database
        db_operations.insert_chunk(
            doc_id=doc_id,
            text=chunk["text"],
            embedding=embedding,
            heading_path=chunk.get("heading_path", []),
            order_in_doc=i
        )

        if (i + 1) % 5 == 0:
            print(f"   ├─ Embedded {i + 1}/{len(chunks)} chunks")

    print(f"   └─ ✓ Completed ({len(chunks)} chunks embedded)")


def main(database_id: str):
    """
    Main ingestion pipeline.

    What This Does:
        1. Fetch all pages from Notion database
        2. Process each page (ingest_page)
        3. Print summary

    Args:
        database_id (str): Notion database ID
    """
    print("🚀 Starting Notion Ingestion")
    print(f"📊 Database ID: {database_id}\n")

    # Fetch all pages
    print("📡 Fetching pages from Notion...")
    pages = notion_client.list_notion_pages(database_id)
    print(f"✅ Found {len(pages)} pages\n")

    # Process each page
    for i, page in enumerate(pages, 1):
        print(f"[{i}/{len(pages)}]", end=" ")
        try:
            ingest_page(page)
        except Exception as e:
            title = page["properties"]["Title"]["title"][0]["plain_text"]
            print(f"   └─ ❌ Error processing {title}: {e}")
            continue

    print(f"\n✅ Ingestion complete! Processed {len(pages)} pages.")


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Ingest Notion pages into RAG knowledge hub")
    parser.add_argument(
        "--notion-db-id",
        required=True,
        help="Notion database ID (from database URL)"
    )

    args = parser.parse_args()

    # Run ingestion
    main(args.notion_db_id)


# Usage Examples:
#
# 1. Ingest pages from Notion database:
#    python ingest_notion.py --notion-db-id abc123def456
#
# 2. Run as cron job (every 6 hours):
#    0 */6 * * * cd /path/to/workers && python ingest_notion.py --notion-db-id abc123
#
# 3. Run in GitHub Actions:
#    - name: Ingest Notion
#      run: python workers/ingest_notion.py --notion-db-id ${{ secrets.NOTION_DB_ID }}
#
# 4. Run in AWS Lambda:
#    def lambda_handler(event, context):
#        main(os.getenv("NOTION_DB_ID"))


# Expected Output:
#
# 🚀 Starting Notion Ingestion
# 📊 Database ID: abc123def456
#
# 📡 Fetching pages from Notion...
# ✅ Found 42 pages
#
# [1/42] 📄 Processing: Atlas Deploy Guide
#    ├─ Fetching blocks...
#    ├─ Found 25 blocks
#    ├─ Converting to Markdown...
#    ├─ Upserting document (project=Atlas, visibility=Private)...
#    ├─ Content changed, re-embedding...
#    ├─ Chunking document...
#    ├─ Created 8 chunks
#    ├─ Embedding chunks...
#    ├─ Embedded 5/8 chunks
#    └─ ✓ Completed (8 chunks embedded)
#
# [2/42] 📄 Processing: Company Handbook
#    ├─ Fetching blocks...
#    ├─ Found 50 blocks
#    ├─ Converting to Markdown...
#    ├─ Upserting document (project=None, visibility=Public)...
#    └─ ✓ Content unchanged, skipping embedding
#
# ...
#
# ✅ Ingestion complete! Processed 42 pages.