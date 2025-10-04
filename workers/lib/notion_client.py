#LULUH

from typing import List, Dict, Any
import os
import requests

# This function interacts with Notion API
def list_notion_pages(database_id: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise ValueError("NOTION_API_KEY not set in environment")

    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    all_pages = []
    next_cursor = None

    while True:
        payload = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Notion API error: {response.status_code} - {response.text}")

        data = response.json()
        all_pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        next_cursor = data.get("next_cursor")

    return all_pages

# for fetching blocks of a Notion page point
def fetch_blocks(page_id: str) -> List[Dict[str, Any]]:
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise ValueError("NOTION_API_KEY not set in environment")

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
    }

    all_blocks = []
    next_cursor = None

    while True:
        params = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Notion API error: {response.status_code} - {response.text}")

        data = response.json()
        all_blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        next_cursor = data.get("next_cursor")

    return all_blocks # End of fetch_blocks
