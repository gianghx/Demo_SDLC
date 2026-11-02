import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'MEMBER',        -- MEMBER | ADMIN
    status TEXT NOT NULL DEFAULT 'PENDING',     -- PENDING | APPROVED | REJECTED | AUTO_REJECTED
    registered_at TEXT NOT NULL,
    decided_at TEXT,
    total_uploaded INTEGER NOT NULL DEFAULT 0   -- chỉ tăng, không giảm khi xóa (BRU-007)
);
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    file_name TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    size_mb REAL NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    language TEXT,                              -- VI | EN
    status TEXT NOT NULL DEFAULT 'PROCESSING',  -- PROCESSING | READY | UNREADABLE | FAILED
    uploaded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding BLOB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(document_id);
CREATE TABLE IF NOT EXISTS usage_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                            -- có thể rỗng, ví dụ LOGIN_FAILED với email không tồn tại
    type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    properties TEXT NOT NULL DEFAULT '{}'       -- không chứa nội dung câu hỏi hay câu trả lời (OQ-024)
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def session():
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
