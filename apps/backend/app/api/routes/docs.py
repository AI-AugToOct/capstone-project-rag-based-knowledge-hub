# LULUH

from fastapi import APIRouter, Header, HTTPException, Path
from typing import Optional
from app.models.schemas import DocMetadata
from app.services import auth
from app.services.db import fetch_document

router = APIRouter()


@router.get("/docs/{doc_id}")
async def get_document(
    doc_id: int = Path(..., description="Document ID"),
    authorization: Optional[str] = Header(None)
):
    """Retrieve document metadata with access control checks."""

    # Here it's for Authentication and Authorization checks
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        user_id = await auth.verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # here for make sure loading user permissions
    user_projects = await auth.get_user_projects(user_id)

    #  Querying document from our database
    document = await fetch_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # About Access control point
    if document["visibility"] == "Public" or document["project_id"] in user_projects:
        return DocMetadata(**document)

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access this document"
    )
