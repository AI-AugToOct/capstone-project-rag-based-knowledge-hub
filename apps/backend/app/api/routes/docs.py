"""
Documents API Route

Handles: GET /api/docs/:doc_id
Returns metadata for a specific document (with ACL check)
"""

from fastapi import APIRouter, Header, HTTPException, Path
from typing import Optional
# from app.models.schemas import DocMetadata
# from app.services import auth

router = APIRouter()


@router.get("/docs/{doc_id}")
async def get_document(
    doc_id: int = Path(..., description="Document ID"),
    authorization: Optional[str] = Header(None)
):
    """
    Retrieves metadata for a specific document (with permission check).

    Path Parameters:
        doc_id (int): The document ID to retrieve
            Example: 123

    Request Headers:
        Authorization: Bearer <jwt-token>

    Response (DocMetadata):
        {
            "doc_id": 123,
            "title": "Atlas Deploy Guide",
            "project_id": "Atlas",
            "visibility": "Private",
            "uri": "https://notion.so/abc123",
            "updated_at": "2025-01-15T10:30:00Z",
            "language": "en"
        }

    What This Endpoint Does:
        1. Verify JWT token
        2. Get user's projects
        3. Query database for document metadata
        4. Check if user has permission to access this document
        5. Return metadata OR 403 Forbidden

    Step-by-Step Flow:

        Step 1: Authentication
            - Extract JWT from Authorization header
            - Call auth.verify_jwt(token) → user_id
            - If invalid → return 401 Unauthorized

        Step 2: Load User Permissions
            - Call auth.get_user_projects(user_id) → ["Atlas", "Phoenix"]

        Step 3: Query Document
            - Query database:
              SELECT doc_id, title, project_id, visibility, uri, updated_at, language
              FROM documents
              WHERE doc_id = %s AND deleted_at IS NULL

            - If not found → return 404 Not Found

        Step 4: Access Control Check
            - Check if user can access this document:
              • IF visibility = 'Public' → ✅ ALLOW
              • ELSE IF project_id IN user_projects → ✅ ALLOW
              • ELSE → ❌ DENY (return 403 Forbidden)

        Step 5: Return Metadata
            - Format as DocMetadata
            - Return to client

    Example Request:
        GET /api/docs/123
        Headers:
            Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (Success):
        {
            "doc_id": 123,
            "title": "Atlas Deploy Guide",
            "project_id": "Atlas",
            "visibility": "Private",
            "uri": "https://notion.so/abc123",
            "updated_at": "2025-01-15T10:30:00Z",
            "language": "en"
        }

    Error Responses:

        401 Unauthorized (missing/invalid JWT):
            {
                "detail": "Invalid or expired token"
            }

        403 Forbidden (user doesn't have access):
            {
                "detail": "You do not have permission to access this document"
            }

        404 Not Found (document doesn't exist):
            {
                "detail": "Document not found"
            }

    Why We Need This Endpoint:
        - Frontend might want to show document details
        - User clicks on a citation → fetch full metadata
        - Useful for "document viewer" feature
        - Also enforces ACL (can't just guess doc_id and access it)

    Access Control Examples:

        Example 1: User CAN access
            - User belongs to ["Atlas", "Phoenix"]
            - Document: project_id="Atlas", visibility="Private"
            - Result: ✅ Return metadata (user is in Atlas)

        Example 2: User CANNOT access
            - User belongs to ["Atlas", "Phoenix"]
            - Document: project_id="Bolt", visibility="Private"
            - Result: ❌ 403 Forbidden (user not in Bolt)

        Example 3: Public document
            - User belongs to []  (no projects)
            - Document: visibility="Public"
            - Result: ✅ Return metadata (public to everyone)

    Security Notes:
        - ALWAYS re-check ACL (don't trust client)
        - Don't reveal document existence for 403 errors
          (both 403 and 404 mean "you can't access this")
        - Log access attempts for security monitoring

    Performance:
        - Target latency: <50ms
        - Simple single-row query
        - Use prepared statements (cached query plan)

    Database Query:
        SELECT
            doc_id,
            title,
            project_id,
            visibility,
            uri,
            updated_at,
            language
        FROM documents
        WHERE doc_id = %s
          AND deleted_at IS NULL

    ACL Logic (in code):
        if document['visibility'] == 'Public':
            return document  # Anyone can access
        elif document['project_id'] in user_projects:
            return document  # User is in project
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    Use Cases:
        1. User clicks citation in search results
           → Frontend calls GET /api/docs/123
           → Shows document metadata in side panel

        2. Document viewer feature
           → Frontend displays full doc info
           → Links to original Notion page

        3. Breadcrumb navigation
           → Show document hierarchy
           → Project → Document → Chunks

    Optional Enhancements (future):
        - Return chunk count for document
        - Return related documents
        - Return document statistics (views, last accessed)
        - Return full content (not just metadata)

    Testing:
        - Test with valid JWT + accessible doc → 200
        - Test with valid JWT + inaccessible doc → 403
        - Test with invalid JWT → 401
        - Test with non-existent doc_id → 404
        - Test with deleted document → 404

    Dependencies:
        - auth service (verify_jwt, get_user_projects)
        - Database connection
        - DocMetadata model

    Implementation Hints:
        1. Extract token: token = authorization.replace("Bearer ", "")
        2. Verify JWT and get user_id
        3. Get user's projects
        4. Query database for document
        5. Check ACL: visibility='Public' OR project_id IN user_projects
        6. Return DocMetadata or raise HTTPException
    """
    raise NotImplementedError("TODO: Implement get document metadata endpoint")