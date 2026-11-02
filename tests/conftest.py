import os

# Chạy test bằng chế độ stub, không cần Ollama. Phải đặt trước khi import app.
os.environ["LLM_PROVIDER"] = "stub"

import pytest
from fastapi.testclient import TestClient

from app import config, db
from app.main import app


def make_pdf(pages: list[str]) -> bytes:
    """Tạo PDF tối thiểu hợp lệ, mỗi phần tử là văn bản của một trang (ASCII)."""
    n = len(pages)
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(n))
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode(),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, text in enumerate(pages):
        objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {5 + 2 * i} 0 R "
            f"/Resources << /Font << /F1 3 0 R >> >> >>".encode())
        safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 12 Tf 50 700 Td ({safe}) Tj ET".encode("latin-1", "replace")
        objs.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n".encode() + b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return bytes(out)


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "app.db")
    monkeypatch.setattr(config, "UPLOAD_DIR", tmp_path / "uploads")
    with TestClient(app):  # chạy lifespan: tạo DB và admin có sẵn
        yield


def new_client() -> TestClient:
    return TestClient(app)


def login(client: TestClient, email: str, password: str):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=False)


def admin_client() -> TestClient:
    c = new_client()
    assert login(c, config.ADMIN_EMAIL, config.ADMIN_PASSWORD).status_code == 303
    return c


def make_member(admin: TestClient, email: str, password: str = "secret1") -> TestClient:
    """Đăng ký, admin duyệt, đăng nhập. Trả về client đã đăng nhập."""
    c = new_client()
    assert c.post("/register", data={"email": email, "display_name": email.split("@")[0],
                                     "password": password}).status_code == 200
    with db.session() as conn:
        uid = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]
    assert admin.post(f"/admin/users/{uid}/approve", follow_redirects=False).status_code == 303
    assert login(c, email, password).status_code == 303
    return c


def upload(client: TestClient, pages: list[str], name: str = "doc.pdf"):
    return client.post("/api/documents", files={"file": (name, make_pdf(pages), "application/pdf")})
