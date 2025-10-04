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