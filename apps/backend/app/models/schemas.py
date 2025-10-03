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


class SearchRequest(BaseModel):
    """
    Request body for POST /api/search

    Example:
        {
            "query": "How do I deploy the Atlas API?",
            "top_k": 12
        }
    """
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
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I deploy the Atlas API?",
                "top_k": 12
            }
        }


class Chunk(BaseModel):
    """
    A single chunk in the search response (citation/source)

    Example:
        {
            "doc_id": 123,
            "title": "Atlas Deploy Guide",
            "snippet": "To deploy Atlas API, first ensure...",
            "uri": "https://notion.so/abc123",
            "score": 0.87
        }
    """
    doc_id: int = Field(
        ...,
        description="Document ID this chunk belongs to",
        example=123
    )

    title: str = Field(
        ...,
        description="Document title",
        example="Atlas Deploy Guide"
    )

    snippet: str = Field(
        ...,
        description="Relevant text excerpt from the document",
        example="To deploy Atlas API, first ensure all environment variables..."
    )

    uri: str = Field(
        ...,
        description="Deep link to the source document (Notion page)",
        example="https://notion.so/abc123"
    )

    score: float = Field(
        ...,
        description="Relevance score (0-1, higher is better)",
        ge=0.0,
        le=1.0,
        example=0.87
    )

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
    """
    Response body for POST /api/search

    Example:
        {
            "answer": "To deploy the Atlas API, follow these steps: 1. ...",
            "chunks": [
                {
                    "doc_id": 123,
                    "title": "Atlas Deploy Guide",
                    "snippet": "To deploy Atlas API...",
                    "uri": "https://notion.so/abc123",
                    "score": 0.87
                }
            ],
            "used_doc_ids": [123, 456]
        }
    """
    answer: str = Field(
        ...,
        description="LLM-generated answer to the user's query",
        example="To deploy the Atlas API, follow these steps: 1. Run `make deploy`..."
    )

    chunks: List[Chunk] = Field(
        ...,
        description="List of source chunks (citations) used to generate the answer",
        example=[
            {
                "doc_id": 123,
                "title": "Atlas Deploy Guide",
                "snippet": "To deploy Atlas API...",
                "uri": "https://notion.so/abc123",
                "score": 0.87
            }
        ]
    )

    used_doc_ids: List[int] = Field(
        ...,
        description="List of document IDs that contributed to the answer (for audit logging)",
        example=[123, 456, 789]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To deploy the Atlas API, follow these steps: 1. Ensure environment variables are configured. 2. Run `make deploy` from the atlas/ directory...",
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
    """
    Document metadata response for GET /api/docs/:doc_id

    Example:
        {
            "doc_id": 123,
            "title": "Atlas Deploy Guide",
            "project_id": "Atlas",
            "visibility": "Private",
            "uri": "https://notion.so/abc123",
            "updated_at": "2025-01-15T10:30:00Z",
            "language": "en"
        }
    """
    doc_id: int = Field(
        ...,
        description="Unique document ID",
        example=123
    )

    title: str = Field(
        ...,
        description="Document title",
        example="Atlas Deploy Guide"
    )

    project_id: Optional[str] = Field(
        None,
        description="Project this document belongs to (null for public docs)",
        example="Atlas"
    )

    visibility: str = Field(
        ...,
        description="Document visibility (Public or Private)",
        example="Private"
    )

    uri: str = Field(
        ...,
        description="Deep link to source document",
        example="https://notion.so/abc123"
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp",
        example="2025-01-15T10:30:00Z"
    )

    language: Optional[str] = Field(
        None,
        description="Document language code",
        example="en"
    )

    class Config:
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


# Why We Use Pydantic Models:
#
# 1. Automatic Validation:
#    - FastAPI validates incoming requests automatically
#    - If query is too long → returns 422 Unprocessable Entity
#    - If top_k is negative → returns 422
#
# 2. Type Safety:
#    - Python type hints improve code quality
#    - IDEs provide autocomplete
#    - Catch bugs before runtime
#
# 3. Auto-Generated API Docs:
#    - FastAPI generates OpenAPI/Swagger docs automatically
#    - Examples and descriptions appear in docs
#    - Try it: http://localhost:8000/docs
#
# 4. Serialization:
#    - Pydantic handles JSON → Python object conversion
#    - And Python object → JSON conversion
#    - Automatic datetime formatting
#
# 5. Documentation:
#    - Field descriptions serve as inline documentation
#    - Examples show developers how to use the API
#
# Example Validation:
#
#   Bad Request:
#     {"query": ""}  ← Empty string
#
#   FastAPI Response:
#     422 Unprocessable Entity
#     {
#       "detail": [
#         {
#           "loc": ["body", "query"],
#           "msg": "ensure this value has at least 1 characters",
#           "type": "value_error.any_str.min_length"
#         }
#       ]
#     }