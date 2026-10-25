import os
import re
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from app.config import settings

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and remove unsafe characters.
    """
    # Remove directory paths if provided
    base_name = os.path.basename(filename)
    # Strip dangerous characters
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', base_name).strip()
    if not cleaned or cleaned.startswith('.'):
        cleaned = f"doc_{uuid.uuid4().hex[:8]}{Path(base_name).suffix}"
    return cleaned

def validate_file_metadata(file: UploadFile) -> str:
    """
    Validates file extension and filename. Returns normalized extension.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename."
        )
    
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: '{ext}'. Allowed types: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}"
        )
    
    return ext

def validate_file_content(content: bytes, ext: str):
    """
    Validates file size and header magic bytes.
    """
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )
    
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    # Signature checks
    if ext == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file format. Missing PDF header."
            )
    elif ext == ".docx":
        # DOCX is a zip file, starts with PK\x03\x04
        if not content.startswith(b"PK\x03\x04"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid DOCX file format. File is not a valid OpenXML document."
            )
    elif ext == ".txt":
        # Verify it can be decoded as text
        try:
            content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content.decode('latin-1')
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid TXT file format. Content could not be decoded as text."
                )
