from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os, shutil
from typing import Optional
from app.db.client import execute

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    visibility: str = Form(...),  # "Public" أو "Private"
    allowed_projects: Optional[str] = Form(None),  # CSV لمشاريع مسموح لها Private
    description: Optional[str] = Form(None),
    custom_name: Optional[str] = Form(None),  # <-- اسم الملف المخصص
):
    try:
        # استخدام الاسم المخصص إذا وُجد، وإلا الاسم الأصلي
        filename_to_save = custom_name.strip() if custom_name else file.filename

        # حفظ الملف
        file_location = os.path.join(UPLOAD_DIR, filename_to_save)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # حفظ بيانات الملف في DB
        project_id = allowed_projects if visibility == "Private" else None
        query = """
            INSERT INTO documents (title, uri, visibility, project_id, updated_at, deleted_at)
            VALUES ($1, $2, $3, $4, NOW(), NULL)
            RETURNING doc_id
        """
        doc = await execute(query, filename_to_save, file_location, visibility, project_id)

        return JSONResponse({
            "message": "File uploaded successfully",
            "title": filename_to_save,
            "uri": file_location,
            "visibility": visibility,
            "project_id": project_id,
            "description": description
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
