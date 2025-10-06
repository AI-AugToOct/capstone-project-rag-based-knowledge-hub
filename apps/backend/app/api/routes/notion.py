"""
Notion Tasks API Route

Fetches tasks from Notion for display on home dashboard.
For MVP: Returns mock data.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/notion-tasks")
async def get_notion_tasks():
    """
    Fetch tasks from Notion for home dashboard.

    For MVP: Returns mock data.
    Later: Actually fetch from Notion API.

    Returns:
        List of tasks with name, status, start date, due date, milestone
    """
    # Mock data for now
    return [
        {
            "name": "Upload company documentation",
            "status": "In Progress",
            "start": "2024-10-01",
            "due": "2024-10-15",
            "milestone": "Knowledge Base Setup"
        },
        {
            "name": "Test document search functionality",
            "status": "Not Started",
            "start": "2024-10-10",
            "due": "2024-10-20",
            "milestone": "MVP Testing"
        },
        {
            "name": "Configure permission system",
            "status": "Completed",
            "start": "2024-09-20",
            "due": "2024-09-30",
            "milestone": "Security Setup"
        },
        {
            "name": "Deploy to production",
            "status": "Not Started",
            "start": "2024-10-25",
            "due": "2024-11-01",
            "milestone": "Launch"
        }
    ]