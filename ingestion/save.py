from __future__ import annotations
import base64
import os
import pathlib
from typing import Iterable

class IngestionError(Exception):
    ...

def decode_base64_bytes(b64_str: str) -> bytes:
    """
    Strictly decode base64; raises IngestionError if invalid.
    """
    try:
        return base64.b64decode(b64_str, validate=True)
    except Exception as e:
        raise IngestionError(f"Invalid base64 content: {e}") from e

def validate_filename(file_name: str, allowed_extensions: Iterable[str]) -> None:
    """
    Validate non-empty filename, extension membership (case-insensitive),
    and prevent path traversal.
    """
    if not file_name or not isinstance(file_name, str):
        raise IngestionError("file_name must be a non-empty string")
    # prevent path traversal
    if os.path.basename(file_name) != file_name:
        raise IngestionError("file_name must not contain directory separators")
    lower = file_name.lower().strip()
    if "." not in lower:
        raise IngestionError(f"File extension missing. Allowed: {sorted(set(e.lower() for e in allowed_extensions))}")
    ext = lower.rsplit(".", 1)[-1]
    allowed = {e.lower().lstrip(".") for e in allowed_extensions}
    if ext not in allowed:
        raise IngestionError(f"Unsupported file type '.{ext}'. Allowed: {sorted(allowed)}")

def save_bytes(storage_dir: str, file_name: str, content: bytes) -> str:
    """
    Persist bytes to storage_dir and return absolute path.
    """
    pathlib.Path(storage_dir).mkdir(parents=True, exist_ok=True)
    abs_path = os.path.abspath(os.path.join(storage_dir, file_name))
    with open(abs_path, "wb") as f:
        f.write(content)
    return abs_path

# Backward-compat wrappers (if any other code still imports old names) 
def validate_csv_filename(file_name: str) -> None:  # pragma: no cover
    # Legacy helper kept to avoid breaking imports; restricts to CSV.
    return validate_filename(file_name, ["csv"])

def save_csv_bytes(storage_dir: str, file_name: str, content: bytes) -> str:  # pragma: no cover
    return save_bytes(storage_dir, file_name, content)
