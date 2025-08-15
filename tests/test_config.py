import os
import tempfile
import yaml
from config.settings import load_settings, AppSettings, dump_settings_yaml

def test_load_settings_valid_tmp_dir(tmp_path):
    cfg = {
        "app_name": "loonar-demo",
        "storage_dir": str(tmp_path / "uploads"),
        "allowed_extensions": ["pdf", "txt", "doc", "docx"],  # UPDATED
        "max_upload_size_mb": 5,
    }
    cfg_path = tmp_path / "settings.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    s = load_settings(str(cfg_path))
    assert set(s.allowed_extensions) == {"pdf", "txt", "doc", "docx"}


def test_load_settings_invalid_exts(tmp_path):
    bad_cfg = {
        "storage_dir": str(tmp_path / "uploads"),
        "allowed_extensions": [""],  # invalid
    }
    cfg_path = tmp_path / "settings.yaml"
    cfg_path.write_text(yaml.safe_dump(bad_cfg), encoding="utf-8")

    try:
        load_settings(str(cfg_path))
        assert False, "Expected ValueError for invalid extensions"
    except ValueError as e:
        assert "Invalid settings file" in str(e)

def test_dump_settings_roundtrip(tmp_path):
    s = AppSettings(app_name="x", storage_dir=str(tmp_path), allowed_extensions=["csv"], max_upload_size_mb=3)
    y = dump_settings_yaml(s)
    assert "storage_dir" in y and "allowed_extensions" in y
