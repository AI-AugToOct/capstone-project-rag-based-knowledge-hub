# LULUH

"""
Pydantic Models for API Request/Response Validation

These models define the shape of data coming in and going out of the API.
FastAPI uses these for:
- Automatic validation
- Auto-generated API documentation
- Type hints
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# For Enum for document visibility types in DocMetadata
class Visibility(str, Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"

# Class for search request and response models
class SearchRequest(BaseModel):
    """Request body for POST /api/search"""
    query: str = Field(
        ...,
        description="User's search question",
        min_length=1,
        max_length=1000,
        example="How do I deploy the Atlas API?"
    )

    top_k: Optional[int] = Field(
        default=12,
        description="Number of chunks to return (after reranking)",
        ge=1,
        le=50,
        example=12
    ) # Limit to max 50 to avoid excessive load

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I deploy the Atlas API?",
                "top_k": 12
            }
        }

# Chunk will take BaseModel for search response
class Chunk(BaseModel):
    """A single chunk in the search response (citation/source)"""
    doc_id: int = Field(..., description="Document ID this chunk belongs to", example=123)
    title: str = Field(..., description="Document title", example="Atlas Deploy Guide")
    snippet: str = Field(..., description="Relevant text excerpt from the document", example="To deploy Atlas API...")
    uri: str = Field(..., description="Deep link to the source document (Notion page)", example="https://notion.so/abc123")
    score: float = Field(..., description="Relevance score (0-1, higher is better)", ge=0.0, le=1.0, example=0.87)

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": 123,
                "title": "Atlas Deploy Guide",
                "snippet": "To deploy Atlas API, first ensure all environment variables are configured...",
                "uri": "https://notion.so/abc123",
                "score": 0.87
            }
        }


class SearchResponse(BaseModel):
    """Response body for POST /api/search"""
    answer: str = Field(..., description="LLM-generated answer to the user's query")
    chunks: List[Chunk] = Field(..., description="List of source chunks (citations) used to generate the answer")
    used_doc_ids: List[int] = Field(..., description="List of document IDs that contributed to the answer (for audit logging)")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To deploy the Atlas API, follow these steps: 1. Ensure environment variables are configured. 2. Run `make deploy`...",
                "chunks": [
                    {
                        "doc_id": 123,
                        "title": "Atlas Deploy Guide",
                        "snippet": "To deploy Atlas API, first ensure all environment variables are configured correctly...",
                        "uri": "https://notion.so/abc123",
                        "score": 0.87
                    }
                ],
                "used_doc_ids": [123, 456]
            }
        }


class DocMetadata(BaseModel):
    """Document metadata response for GET /api/docs/:doc_id"""
    doc_id: int = Field(..., description="Unique document ID", example=123)
    title: str = Field(..., description="Document title", example="Atlas Deploy Guide")
    project_id: Optional[str] = Field(None, description="Project this document belongs to (null for public docs)", example="Atlas")
    visibility: Visibility = Field(..., description="Document visibility (Public or Private)", example="Private")
    uri: str = Field(..., description="Deep link to source document", example="https://notion.so/abc123")
    updated_at: datetime = Field(..., description="Last update timestamp", example="2025-01-15T10:30:00Z")
    language: Optional[str] = Field(None, description="Document language code", example="en")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "doc_id": 123,
                "title": "Atlas Deploy Guide",
                "project_id": "Atlas",
                "visibility": "Private",
                "uri": "https://notion.so/abc123",
                "updated_at": "2025-01-15T10:30:00Z",
                "language": "en"
            }
        }


# ============================================================================
# Handover Models
# ============================================================================

class HandoverStatus(str, Enum):
    """Handover status enum"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    COMPLETED = "completed"


class CreateHandoverRequest(BaseModel):
    """Request body for POST /api/handovers"""
    to_employee_id: str = Field(..., description="Recipient's employee ID (UUID)", example="550e8400-e29b-41d4-a716-446655440000")
    title: str = Field(..., description="Handover title", min_length=1, max_length=500, example="Project Atlas Handover")
    project_id: Optional[str] = Field(None, description="Optional project ID", example="Atlas")
    context: Optional[str] = Field(None, description="Why this handover exists", example="Moving to new team")
    current_status: Optional[str] = Field(None, description="What's been done so far", example="Completed initial setup")
    next_steps: Optional[List[dict]] = Field(None, description="List of next steps", example=[{"task": "Deploy to prod", "done": False}])
    resources: Optional[List[dict]] = Field(None, description="Related resources/documents", example=[{"type": "doc", "doc_id": 123, "title": "Setup Guide"}])
    contacts: Optional[List[dict]] = Field(None, description="Key contacts", example=[{"name": "Sarah", "email": "sarah@example.com", "role": "Lead"}])
    additional_notes: Optional[str] = Field(None, description="Additional free-form notes", example="Please review the deployment checklist")
    cc_employee_ids: Optional[List[str]] = Field(None, description="List of employee IDs to CC", example=["123e4567-e89b-12d3-a456-426614174000"])

    class Config:
        json_schema_extra = {
            "example": {
                "to_employee_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Project Atlas Handover",
                "project_id": "Atlas",
                "context": "Moving to new team, need to transfer knowledge",
                "current_status": "API is deployed, documentation is up to date",
                "next_steps": [
                    {"task": "Review deployment checklist", "done": False},
                    {"task": "Schedule knowledge transfer meeting", "done": False}
                ],
                "resources": [
                    {"type": "doc", "doc_id": 123, "title": "Atlas Setup Guide"},
                    {"type": "link", "url": "https://notion.so/runbook", "title": "Runbook"}
                ],
                "contacts": [
                    {"name": "Sarah Khan", "email": "sarah@example.com", "role": "Team Lead"}
                ],
                "additional_notes": "Please prioritize the deployment checklist review",
                "cc_employee_ids": ["123e4567-e89b-12d3-a456-426614174000"]
            }
        }


class HandoverResponse(BaseModel):
    """Response model for handover details"""
    handover_id: int = Field(..., description="Handover ID")
    title: str = Field(..., description="Handover title")
    project_id: Optional[str] = Field(None, description="Project ID")
    project_name: Optional[str] = Field(None, description="Project name")
    from_employee_id: str = Field(..., description="Sender's employee ID")
    to_employee_id: str = Field(..., description="Recipient's employee ID")
    from_name: Optional[str] = Field(None, description="Sender's display name")
    from_email: Optional[str] = Field(None, description="Sender's email")
    to_name: Optional[str] = Field(None, description="Recipient's display name")
    to_email: Optional[str] = Field(None, description="Recipient's email")
    context: Optional[str] = Field(None, description="Handover context")
    current_status: Optional[str] = Field(None, description="Current status description")
    next_steps: Optional[List[dict]] = Field(None, description="Next steps")
    resources: Optional[List[dict]] = Field(None, description="Resources")
    contacts: Optional[List[dict]] = Field(None, description="Contacts")
    additional_notes: Optional[str] = Field(None, description="Additional notes")
    status: HandoverStatus = Field(..., description="Handover status")
    created_at: datetime = Field(..., description="Creation timestamp")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgement timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HandoversListResponse(BaseModel):
    """Response for GET /api/handovers - lists received and sent handovers"""
    received: List[HandoverResponse] = Field(..., description="Handovers received by the user")
    sent: List[HandoverResponse] = Field(..., description="Handovers sent by the user")


class UpdateHandoverStatusRequest(BaseModel):
    """Request body for PATCH /api/handovers/:id"""
    status: HandoverStatus = Field(..., description="New status (acknowledged or completed)")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "acknowledged"
            }
        }