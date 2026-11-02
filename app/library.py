"""Kho tài liệu: upload, xử lý nền, xóa (UC-05..UC-07)."""
import io
import uuid

import numpy as np
from pypdf import PdfReader

from . import config, db, events
from .llm import get_provider
from .textutil import chunk_page, detect_language

REJECT_MESSAGES = {
    "QUOTA_EXCEEDED": "Đã đạt hạn mức số tệp được upload (tính cả tệp đã xóa).",
    "TOO_LARGE": "Tệp vượt dung lượng tối đa cho phép.",
    "NOT_PDF": "Tệp không phải PDF.",
    "CORRUPTED": "Tệp PDF bị hỏng hoặc không đọc được.",
}


def can_delete(user, doc) -> bool:
    """BRU-004: người upload xóa tài liệu của mình, admin xóa mọi tài liệu."""
    return user["role"] == "ADMIN" or doc["owner_id"] == user["id"]


def validate_upload(user, filename: str, data: bytes) -> str | None:
    """UploadPolicy.validate: trả về mã lý do từ chối hoặc None nếu hợp lệ."""
    if user["total_uploaded"] >= config.MAX_FILES_PER_USER:
        return "QUOTA_EXCEEDED"
    if len(data) > config.MAX_FILE_MB * 1024 * 1024:
        return "TOO_LARGE"
    if not filename.lower().endswith(".pdf") or not data.startswith(b"%PDF"):
        return "NOT_PDF"
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted or len(reader.pages) == 0:
            return "CORRUPTED"
    except Exception:
        return "CORRUPTED"
    return None


def add_document(conn, user, filename: str, data: bytes) -> int:
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}.pdf"
    (config.UPLOAD_DIR / stored).write_bytes(data)
    pages = len(PdfReader(io.BytesIO(data)).pages)
    cur = conn.execute(
        "INSERT INTO documents (owner_id, file_name, stored_name, size_mb, page_count, status, uploaded_at) "
        "VALUES (?, ?, ?, ?, ?, 'PROCESSING', ?)",
        (user["id"], filename, stored, round(len(data) / 1024 / 1024, 2), pages, db.now()),
    )
    conn.execute("UPDATE users SET total_uploaded = total_uploaded + 1 WHERE id=?", (user["id"],))
    events.log(conn, "DOCUMENT_UPLOAD_STARTED", user["id"], size_mb=round(len(data) / 1024 / 1024, 2))
    conn.commit()
    return cur.lastrowid


def process_document(doc_id: int) -> None:
    """Chạy nền: trích văn bản theo trang, nhận diện ngôn ngữ, tách đoạn, embedding."""
    with db.session() as conn:
        doc = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        if not doc:
            return
        try:
            reader = PdfReader(str(config.UPLOAD_DIR / doc["stored_name"]))
            pages = [(page.extract_text() or "") for page in reader.pages]
            if not "".join(pages).strip():
                conn.execute("UPDATE documents SET status='UNREADABLE' WHERE id=?", (doc_id,))
                return
            language = detect_language(" ".join(pages))
            pieces = [(n, c) for n, text in enumerate(pages, start=1)
                      for c in chunk_page(text, config.CHUNK_CHARS, config.CHUNK_OVERLAP)]
            provider = get_provider()
            vectors: list[list[float]] = []
            for i in range(0, len(pieces), 16):
                vectors.extend(provider.embed([c for _, c in pieces[i:i + 16]]))
            conn.executemany(
                "INSERT INTO chunks (document_id, page_number, text, embedding) VALUES (?, ?, ?, ?)",
                [(doc_id, n, c, np.asarray(v, dtype=np.float32).tobytes()) for (n, c), v in zip(pieces, vectors)],
            )
            conn.execute("UPDATE documents SET status='READY', language=? WHERE id=?", (language, doc_id))
            events.log(conn, "DOCUMENT_READY", doc["owner_id"], language=language, chunks=len(pieces))
        except Exception as exc:  # noqa: BLE001 - mọi lỗi xử lý đều thành FAILED (SAD mục 5.1)
            conn.rollback()
            conn.execute("UPDATE documents SET status='FAILED' WHERE id=?", (doc_id,))
            events.log(conn, "DOCUMENT_FAILED", doc["owner_id"], error=type(exc).__name__)


def delete_document(conn, user, doc_id: int) -> str:
    """Trả về: ok | not_found | forbidden. Xóa vĩnh viễn tệp và mọi đoạn văn, vector (BRU-003)."""
    doc = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not doc:
        return "not_found"
    if not can_delete(user, doc):
        return "forbidden"
    (config.UPLOAD_DIR / doc["stored_name"]).unlink(missing_ok=True)
    conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))  # chunks xóa theo (ON DELETE CASCADE)
    events.log(conn, "DOCUMENT_DELETED", user["id"], deleted_by="admin" if user["role"] == "ADMIN" and doc["owner_id"] != user["id"] else "owner")
    return "ok"


def list_documents(conn):
    return conn.execute(
        "SELECT d.id, d.file_name, d.size_mb, d.page_count, d.language, d.status, d.uploaded_at, d.owner_id, "
        "u.display_name AS uploader FROM documents d JOIN users u ON u.id = d.owner_id ORDER BY d.id DESC"
    ).fetchall()
