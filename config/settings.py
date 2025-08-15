from __future__ import annotations
import os
import pathlib
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field, field_validator, ValidationError

DEFAULT_SETTINGS_PATH = os.getenv("SETTINGS_YAML", "config/settings.yaml")

class AppSettings(BaseModel):
    app_name: str = Field(default="loonar-demo")
    storage_dir: str = Field(default="data/uploads")
    allowed_extensions: List[str] = Field(
        default_factory=lambda: ["pdf", "txt", "docx", "doc"]
    )
    max_upload_size_mb: int = Field(default=10, ge=1, le=1024)

    @field_validator("allowed_extensions")
    @classmethod
    def normalize_exts(cls, exts: List[str]) -> List[str]:
        """
        Ensure extensions are lowercase, stripped, and without a leading dot.
        """
        normed = []
        for e in exts:
            e = e.strip().lower()
            if not e:
                raise ValueError("Empty extension not allowed")
            normed.append(e.lstrip("."))
        return normed

    def ensure_storage_dir(self) -> None:
        """
        Create the storage directory if it doesn't exist.
        """
        p = pathlib.Path(self.storage_dir)
        p.mkdir(parents=True, exist_ok=True)

    def is_allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed (case-insensitive).
        """
        ext = os.path.splitext(filename)[1][1:].lower()  # remove leading dot
        return ext in self.allowed_extensions

def load_settings(path: Optional[str] = None) -> AppSettings:
    """
    Load settings from YAML, allow env override for storage_dir via LOONAR_STORAGE_DIR.
    """
    path = path or DEFAULT_SETTINGS_PATH
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Environment override
    env_dir = os.getenv("LOONAR_STORAGE_DIR")
    if env_dir:
        data["storage_dir"] = env_dir

    try:
        settings = AppSettings(**data)
    except ValidationError as ve:
        raise ValueError(f"Invalid settings file '{path}': {ve}") from ve

    settings.ensure_storage_dir()
    return settings

def dump_settings_yaml(settings: AppSettings) -> str:
    """
    Dump settings object back to YAML string.
    """
    data = settings.model_dump()
    return yaml.safe_dump(data, sort_keys=False)
