"""
Search API Route

This is the MAIN endpoint of the entire RAG system.
Handles: POST /api/search
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional
# from app.models.schemas import SearchRequest, SearchResponse
# from app.services import auth, embeddings, retrieval, llm, audit

router = APIRouter()


@router.post("/search")
async def search(
    # request: SearchRequest,  # Uncomment when schemas.py is implemented
    authorization: Optional[str] = Header(None)
):
    """
    Main RAG search endpoint - the heart of the system.

    Request Body (SearchRequest):
        {
            "query": "How do I deploy the Atlas API?",
            "top_k": 12
        }

    Request Headers:
        Authorization: Bearer <jwt-token>

    Response (SearchResponse):
        {
            "answer": "To deploy the Atlas API, follow these steps: 1. Run `make deploy`...",
            "chunks": [
                {
                    "doc_id": 123,
                    "title": "Atlas Deploy Guide",
                    "snippet": "To deploy Atlas API, first ensure...",
                    "uri": "https://notion.so/abc123",
                    "score": 0.87
                },
                ...
            ],
            "used_doc_ids": [123, 456, 789]
        }

    What This Endpoint Does:
        1. Extract and verify JWT token from Authorization header
        2. Get user's project memberships
        3. Embed the user's query
        4. Search database with ACL filter (vector similarity)
        5. Rerank results with Cohere
        6. Generate answer with LLM
        7. Log query to audit table
        8. Return answer + citations

    Step-by-Step Flow:

        Step 1: Authentication
            - Extract JWT from "Authorization: Bearer <token>" header
            - Call auth.verify_jwt(token) → user_id
            - If invalid/expired → return 401 Unauthorized

        Step 2: Load User Permissions
            - Call auth.get_user_projects(user_id) → ["Atlas", "Phoenix"]
            - This determines which documents user can access

        Step 3: Embed Query
            - Call embeddings.embed_query(request.query) → [0.1, 0.2, ...]
            - Converts text to 1024-dim vector

        Step 4: Vector Search with ACL
            - Call retrieval.run_vector_search(
                  query_vector=embedding,
                  user_projects=projects,
                  top_k=200
              ) → 200 candidate chunks
            - Only returns chunks from Public docs or user's projects

        Step 5: Rerank
            - Call retrieval.rerank(
                  chunks=candidates,
                  query=request.query,
                  top_k=request.top_k or 12
              ) → 12 best chunks
            - Uses Cohere reranker for better relevance

        Step 6: Generate Answer
            - Extract text from chunks: [c["text"] for c in chunks]
            - Call llm.call_llm(
                  query=request.query,
                  context_chunks=texts
              ) → "To deploy Atlas API: 1. ..."
            - LLM synthesizes answer from chunks

        Step 7: Audit Log
            - Extract doc_ids: [c["doc_id"] for c in chunks]
            - Call audit.audit_log(
                  user_id=user_id,
                  query=request.query,
                  used_doc_ids=doc_ids
              )
            - Logs to database (non-blocking)

        Step 8: Return Response
            - Format chunks for frontend (strip internal fields)
            - Return SearchResponse with answer + chunks + doc_ids

    Example Request:
        POST /api/search
        Headers:
            Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        Body:
            {
                "query": "How do I deploy the Atlas API?",
                "top_k": 12
            }

    Example Response (Success):
        {
            "answer": "To deploy the Atlas API: 1. Ensure environment variables are configured...",
            "chunks": [
                {
                    "doc_id": 123,
                    "title": "Atlas Deploy Guide",
                    "snippet": "To deploy Atlas API, first ensure all environment variables...",
                    "uri": "https://notion.so/abc123",
                    "score": 0.87
                }
            ],
            "used_doc_ids": [123]
        }

    Error Responses:

        401 Unauthorized (missing/invalid JWT):
            {
                "detail": "Invalid or expired token"
            }

        400 Bad Request (empty query):
            {
                "detail": "Query cannot be empty"
            }

        500 Internal Server Error (service failure):
            {
                "detail": "Failed to process search request"
            }

    Error Handling:
        - Catch exceptions from each service
        - Return appropriate HTTP status codes
        - Log errors for debugging
        - Don't expose internal error details to client

    Performance:
        - Target latency: <2 seconds end-to-end
        - Breakdown:
          • JWT verify: <10ms
          • Get projects: <10ms
          • Embed query: ~100-200ms (Cohere API)
          • Vector search: ~10-50ms (pgvector with HNSW)
          • Rerank: ~100-300ms (Cohere API)
          • LLM: ~500-2000ms (Groq, depends on model)
          • Audit log: <5ms (async)

    Security Notes:
        - ALWAYS verify JWT on every request
        - NEVER skip ACL filtering
        - Don't log sensitive query content (audit table only)
        - Rate limit this endpoint (prevent abuse)

    Testing:
        - Mock all service calls
        - Test with valid JWT → should return results
        - Test with invalid JWT → should return 401
        - Test with empty query → should return 400
        - Test ACL: user should only see their projects' docs

    Dependencies:
        - All services (auth, embeddings, retrieval, llm, audit)
        - SearchRequest and SearchResponse models
        - FastAPI for routing and validation

    Implementation Hints:
        1. Extract token from authorization header:
           token = authorization.replace("Bearer ", "")

        2. Handle each step in try/except blocks

        3. Format chunks for response:
           response_chunks = [
               {
                   "doc_id": c["doc_id"],
                   "title": c["title"],
                   "snippet": c["text"][:200] + "...",
                   "uri": c["uri"],
                   "score": c.get("rerank_score", c.get("score"))
               }
               for c in chunks
           ]

        4. Return SearchResponse object (FastAPI auto-converts to JSON)
    """
    raise NotImplementedError("TODO: Implement search endpoint")