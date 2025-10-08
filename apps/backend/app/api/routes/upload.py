"""
File Upload API Route

Handles manager file uploads (PDF, DOCX) and ingests them into the knowledge base.
Endpoint: POST /api/upload
"""

from fastapi import APIRouter, File, UploadFile, Header, HTTPException, Form
from typing import Optional
from app.services import auth, extraction
from app.services.embeddings import embed_document
from app.services.db import insert_document, insert_chunk
from app.services.chunker import chunk_markdown
from app.services.storage import upload_file_to_storage
from app.core.constants import CHUNK_SIZE, CHUNK_OVERLAP, VALID_VISIBILITIES
import uuid

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    visibility: str = Form("Public"),
    authorization: Optional[str] = Header(None)
):
    """
    Upload and ingest a document (PDF/DOCX) into the knowledge base.

    Args:
        file: Uploaded file (PDF, DOCX, TXT, MD)
        project_id: Optional project ID to assign document to
        visibility: "Public" or "Private" (default: Public)
        authorization: JWT token in header

    Returns:
        {
            "doc_id": 123,
            "title": "uploaded_file.pdf",
            "chunks_created": 15,
            "message": "Document uploaded and indexed successfully"
        }

    Flow:
        1. Authenticate user
        2. Validate file type
        3. Extract text to Markdown
        4. Create document record in DB
        5. Chunk markdown
        6. Embed each chunk
        7. Insert chunks into DB
        8. Return success
    """

    # --------- Step 1: Authentication ---------
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")

    token = authorization.replace("Bearer ", "")
    try:
        user_id = auth.verify_jwt(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    # Check if user is a manager
    is_manager = await auth.check_user_is_manager(user_id, project_id)
    if not is_manager:
        raise HTTPException(status_code=403, detail="Only managers can upload documents")

    # --------- Step 2: Validate Inputs ---------
    if visibility not in VALID_VISIBILITIES:
        raise HTTPException(status_code=400, detail=f"Invalid visibility. Must be one of: {VALID_VISIBILITIES}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")

    # --------- Step 3: Read File ---------
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
    # This also ensures file_bytes is not empty ..

    # --------- Step 4: Extract Text ---------
    try:
        markdown, sections = extraction.extract_text_from_file(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")

    if not markdown.strip():
        raise HTTPException(status_code=400, detail="Extracted document is empty")

    # --------- Step 5: Upload File to Storage ---------
    try:
        file_url = upload_file_to_storage(
            file_bytes=file_bytes,
            filename=file.filename,
            project_id=project_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to storage: {e}")

    # --------- Step 6: Create Document Record ---------
    try:
        doc_id = await insert_document(
            title=file.filename,
            project_id=project_id,
            visibility=visibility,
            uri=file_url,  # Use storage URL instead of fake URI
            language="en"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document record: {e}")

    # --------- Step 6: Chunk Markdown ---------
    try:
        chunks = chunk_markdown(markdown, sections, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to chunk document: {e}")

    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks created from document")

    # --------- Step 7: Embed and Insert Chunks ---------
    chunks_created = 0
    errors = []

    for idx, chunk in enumerate(chunks):
        try:
            # Embed chunk
            embedding = embed_document(chunk["text"])

            # Insert into database
            await insert_chunk(
                doc_id=doc_id,
                text=chunk["text"],
                heading_path=chunk["heading_path"],
                embedding=embedding,
                order_in_doc=idx
            )

            chunks_created += 1
        except Exception as e:
            errors.append(f"Chunk {idx + 1}: {str(e)}")
            # Continue processing other chunks even if one fails

    # --------- Step 8: Return Response ---------
    if chunks_created == 0:
        raise HTTPException(status_code=500, detail=f"Failed to create any chunks. Errors: {errors}")

    return {
        "doc_id": doc_id,
        "title": file.filename,
        "chunks_created": chunks_created,
        "total_chunks": len(chunks),
        "message": "Document uploaded and indexed successfully",
        "errors": errors if errors else None
    }


@router.get("/documents")
async def list_documents(
    authorization: Optional[str] = Header(None)
):
    """
    List all documents (for manager interface).

    Returns:
        [
            {
                "doc_id": 123,
                "title": "file.pdf",
                "visibility": "Public",
                "created_at": "2024-01-15T10:30:00Z"
            },
            ...
        ]
    """

    # --------- Step 1: Authentication ---------
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")

    token = authorization.replace("Bearer ", "")
    try:
        user_id = auth.verify_jwt(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    # --------- Step 2: Query Documents ---------
    # For now, return all documents (TODO: implement proper filtering)
    try:
        from app.db.client import get_db_pool
        pool = get_db_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT doc_id, title, visibility, project_id, updated_at, uri
                FROM documents
                WHERE deleted_at IS NULL
                ORDER BY updated_at DESC
                LIMIT 100
            """)

        documents = [
            {
                "doc_id": row["doc_id"],
                "title": row["title"],
                "visibility": row["visibility"],
                "project_id": row["project_id"],
                "created_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                "uri": row["uri"]
            }
            for row in rows
        ]

        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {e}")