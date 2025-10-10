from dotenv import load_dotenv
load_dotenv()

from lib import notion_client, normalizer
import json

# Test with your database
pages = notion_client.list_notion_pages("285c4a0c3a0c80cbbec5c3ab4cf38c18")

print(f"Found {len(pages)} pages\n")

# Check first page in detail
page = pages[0]
title = page["properties"]["Title"]["title"][0]["plain_text"]
page_id = page["id"]

print(f"=== Testing: {title} ===")
print(f"Page ID: {page_id}\n")

# Fetch blocks
blocks = notion_client.fetch_blocks(page_id)
print(f"Number of blocks: {len(blocks)}\n")

# Show first 3 blocks
for i, block in enumerate(blocks[:3]):
    print(f"Block {i+1}:")
    print(f"  Type: {block.get('type')}")
    print(f"  Content: {json.dumps(block, indent=2)[:300]}...\n")

# Try to normalize
markdown, sections = normalizer.normalize_to_markdown(blocks)
print(f"=== MARKDOWN OUTPUT ===")
print(f"Length: {len(markdown)} chars")
print(f"Content:\n{markdown[:500]}\n")

print(f"=== SECTIONS ===")
print(sections[:3] if sections else "None")
