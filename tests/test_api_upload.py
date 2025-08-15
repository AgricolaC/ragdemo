import os
import base64
import yaml
from fastapi.testclient import TestClient

def make_app(tmp_path):
    cfg = {
        "app_name": "loonar-demo",
        "storage_dir": str(tmp_path / "uploads"),
        "allowed_extensions": ["pdf", "txt", "doc", "docx"],  # UPDATED
        "max_upload_size_mb": 2,
    }
    cfg_path = tmp_path / "settings.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    os.environ["SETTINGS_YAML"] = str(cfg_path)

    from api.upload import app
    return app

def test_upload_success_pdf(tmp_path):
    app = make_app(tmp_path)
    client = TestClient(app)

    content = b"%PDF-1.4\n%fake-pdf\n"
    payload = {
        "file_name": "sample.pdf",
        "file_content": base64.b64encode(content).decode("ascii"),
    }

    r = client.post("/upload", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["size_bytes"] == len(content)
    assert data["file_path"].endswith("sample.pdf")
    assert "pdf" in data["allowed_extensions"]

def test_upload_invalid_extension(tmp_path):
    app = make_app(tmp_path)
    client = TestClient(app)

    content = b"a,b\n1,2\n"  # CSV should now be invalid by default config
    payload = {
        "file_name": "notes.csv",
        "file_content": base64.b64encode(content).decode("ascii"),
    }
    r = client.post("/upload", json=payload)
    assert r.status_code == 400
    err = r.json()["detail"]
    assert "Unsupported file type '.csv'" in " ".join(err.get("errors", []))

def test_upload_invalid_base64(tmp_path):
    app = make_app(tmp_path)
    client = TestClient(app)

    payload = {"file_name": "bad.pdf", "file_content": "!!not_base64!!"}
    r = client.post("/upload", json=payload)
    assert r.status_code == 400
    err = r.json()["detail"]
    assert "Invalid base64 content" in " ".join(err.get("errors", []))

def test_upload_too_large(tmp_path):
    app = make_app(tmp_path)
    client = TestClient(app)

    big = b"a" * (3 * 1024 * 1024)  # 3MB > max_upload_size_mb=2
    payload = {"file_name": "big.txt", "file_content": base64.b64encode(big).decode("ascii")}
    r = client.post("/upload", json=payload)
    assert r.status_code == 400
    err = r.json()["detail"]
    assert "exceeds max_upload_size_mb" in " ".join(err.get("errors", []))
