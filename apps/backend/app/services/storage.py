"""
Supabase Storage Service

Handles file uploads to Supabase Storage bucket.
"""

import os
from typing import Optional
try:
    from supabase import create_client, Client
except ImportError:
    from supabase.client import Client, create_client

# Storage bucket name
BUCKET_NAME = "documents"

# Lazy initialization
_supabase_client = None


def _get_supabase_client() -> Client:
    """
    Get or create Supabase client (lazy initialization).

    Returns:
        Supabase client instance

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set
    """
    global _supabase_client

    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment. "
                "Get your service role key from: https://app.supabase.com/project/brczyipagixshsnqhfhq/settings/api"
            )

        if supabase_key == "your-service-role-key-here":
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is still a placeholder. "
                "Get your actual service role key from: https://app.supabase.com/project/brczyipagixshsnqhfhq/settings/api"
            )

        # Create client with just URL and key (no options to avoid compatibility issues)
        _supabase_client = create_client(supabase_url, supabase_key)

    return _supabase_client


def upload_file_to_storage(
    file_bytes: bytes,
    filename: str,
    project_id: Optional[str] = None
) -> str:
    """
    Upload a file to Supabase Storage and return the public URL.

    Args:
        file_bytes: File content as bytes
        filename: Original filename
        project_id: Optional project ID to organize files

    Returns:
        Public URL of the uploaded file

    Example:
        url = upload_file_to_storage(file_bytes, "report.pdf", "atlas-api")
        # Returns: "https://brczyipagixshsnqhfhq.supabase.co/storage/v1/object/public/documents/atlas-api/report.pdf"
    """
    # Generate storage path
    if project_id:
        storage_path = f"{project_id}/{filename}"
    else:
        storage_path = f"public/{filename}"

    # Get Supabase client
    supabase = _get_supabase_client()

    # Upload to Supabase Storage
    try:
        result = supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": _get_content_type(filename)}
        )

        # Get public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)

        return public_url
    except Exception as e:
        # If file already exists, try to update it
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            # Update existing file
            supabase.storage.from_(BUCKET_NAME).update(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": _get_content_type(filename)}
            )
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
            return public_url
        else:
            raise Exception(f"Failed to upload file to storage: {e}")


def _get_content_type(filename: str) -> str:
    """
    Determine content type based on file extension.

    Args:
        filename: File name with extension

    Returns:
        MIME type string
    """
    ext = filename.lower().split('.')[-1]

    content_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain',
        'md': 'text/markdown',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
    }

    return content_types.get(ext, 'application/octet-stream')