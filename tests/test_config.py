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
