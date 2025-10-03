import requests
import os

NOTION_API_KEY = os.getenv(
    "NOTION_API_KEY",
    "XXXXXXXXXXXXXXXXX"
)
NOTION_DATABASE_ID = os.getenv(
    "NOTION_DATABASE_ID",
    "XXXXXXXXXXXXXXXXX"
)


def fetch_tasks():
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("❌ Missing Notion API credentials. Set NOTION_API_KEY and NOTION_DATABASE_ID.")

    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch tasks: {response.status_code}, {response.text}")

    data = response.json()
    tasks = []

    for result in data.get("results", []):
        props = result.get("properties", {})

        # Task Name (title type)
        title_prop = props.get("Task Name", {}).get("title", [])
        task_name = title_prop[0]["plain_text"] if title_prop else "Untitled"

        # Status (status type)
        status_prop = props.get("Status", {}).get("status")
        task_status = status_prop["name"] if status_prop else "No Status"

        # Start Date (date type)
        start_prop = props.get("Start", {}).get("date")
        task_start = start_prop["start"] if start_prop else None

        # Due Date (date type)
        due_prop = props.get("Due", {}).get("date")
        task_due = due_prop["start"] if due_prop else None

        # Milestone (select type)
        milestone_prop = props.get("Milestone", {}).get("select")
        task_milestone = milestone_prop["name"] if milestone_prop else None

        tasks.append({
            "name": task_name,
            "status": task_status,
            "start": task_start,
            "due": task_due,
            "milestone": task_milestone,
        })

    return tasks
