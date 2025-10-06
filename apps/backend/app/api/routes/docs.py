from fastapi import APIRouter, Header, HTTPException, Path
from typing import Optional, List
from app.services.db import fetch_document, fetch_documents_for_user

router = APIRouter()

@router.get("/docs/{doc_id}")
async def get_document(
    doc_id: int = Path(...),
    authorization: Optional[str] = Header(None)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    user_token = authorization.replace("Bearer ", "")
    is_manager = user_token == "manager_test_token"
    
    document = await fetch_document(doc_id, is_manager=is_manager, user_token=user_token)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
    
    return document

@router.get("/documents", response_model=List[dict])
async def list_documents(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    user_token = authorization.replace("Bearer ", "")
    is_manager = user_token == "manager_test_token"

    documents = await fetch_documents_for_user(is_manager, user_token)
    return documents
