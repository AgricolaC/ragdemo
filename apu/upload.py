from __future__ import annotations
import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from config.settings import load_settings
from ingestion.save import decode_base64_bytes, validate_filename, save_bytes

# Load settings (can be overridden in tests via env SETTINGS_YAML or LOONAR_STORAGE_DIR)
SETTINGS_PATH = os.getenv("SETTINGS_YAML")
settings = load_settings(SETTINGS_PATH)

app = FastAPI(title=settings.app_name)

class UploadRequest(BaseModel):
    file_name: str = Field(..., description="Uploaded file name (must end with one of allowed extensions)")
    file_content: str = Field(..., description="Base64-encoded file content")

    @field_validator("file_name")
    @classmethod
    def basic_check_name(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("file_name must be a non-empty string")
        return v

class UploadResponse(BaseModel):
    message: str
    file_path: str
    size_bytes: int
    allowed_extensions: list[str]

def _bad_request(errors: List[str]) -> None:
    raise HTTPException(status_code=400, detail={"message": "Validation failed", "errors": errors})

@app.post("/upload", response_model=UploadResponse)
def upload(req: UploadRequest):
    """
    POST /upload
    Validates JSON payload and saves a file decoded from base64.
    Allowed extensions are taken from settings.allowed_extensions (pdf, txt, doc, docx).
    On failure returns HTTP 400 with an error list.
    """
    errors: List[str] = []

    # filename + extension validation against config
    try:
        validate_filename(req.file_name, settings.allowed_extensions)
    except Exception as e:
        errors.append(str(e))

    # decode base64 content
    try:
        content_bytes = decode_base64_bytes(req.file_content)
    except Exception as e:
        errors.append(str(e))
        return _bad_request(errors)

    if len(content_bytes) == 0:
        errors.append("Decoded content is empty")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content_bytes) > max_bytes:
        errors.append(f"File exceeds max_upload_size_mb={settings.max_upload_size_mb}")

    if errors:
        return _bad_request(errors)

    file_path = save_bytes(settings.storage_dir, req.file_name, content_bytes)
    return UploadResponse(
        message="Upload successful",
        file_path=file_path,
        size_bytes=len(content_bytes),
        allowed_extensions=[e for e in settings.allowed_extensions],
    )
