"""Tài khoản: tự đăng ký, admin duyệt, tự động từ chối quá hạn (UC-01..UC-04)."""
import re
from datetime import datetime, timedelta, timezone

from . import config, events
from .db import now
from .security import hash_password, verify_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def seed_admin(conn) -> None:
    """BR-019: tài khoản admin có sẵn khi vận hành."""
    email = config.ADMIN_EMAIL.lower()
    if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
        return
    conn.execute(
        "INSERT INTO users (email, display_name, password_hash, role, status, registered_at, decided_at) "
        "VALUES (?, 'Admin', ?, 'ADMIN', 'APPROVED', ?, ?)",
        (email, hash_password(config.ADMIN_PASSWORD), now(), now()),
    )


def register(conn, email: str, display_name: str, password: str) -> str:
    """Trả về: created | re_registered | exists | invalid."""
    email = email.strip().lower()
    display_name = display_name.strip()
    if not EMAIL_RE.match(email) or not display_name or len(password) < 6:
        return "invalid"
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if row:
        if row["status"] in ("REJECTED", "AUTO_REJECTED"):
            # BRU-010: đăng ký lại bằng cùng email
            conn.execute(
                "UPDATE users SET status='PENDING', registered_at=?, decided_at=NULL, "
                "display_name=?, password_hash=? WHERE id=?",
                (now(), display_name, hash_password(password), row["id"]),
            )
            events.log(conn, "REGISTER_SUBMITTED", row["id"], re_registered=True)
            return "re_registered"
        return "exists"
    cur = conn.execute(
        "INSERT INTO users (email, display_name, password_hash, registered_at) VALUES (?, ?, ?, ?)",
        (email, display_name, hash_password(password), now()),
    )
    events.log(conn, "REGISTER_SUBMITTED", cur.lastrowid)
    return "created"


def authenticate(conn, email: str, password: str):
    """Trả về (user, None) hoặc (None, lý do): bad_credentials | pending | rejected."""
    row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if not row or not verify_password(password, row["password_hash"]):
        events.log(conn, "LOGIN_FAILED", row["id"] if row else None)
        return None, "bad_credentials"
    if row["status"] == "PENDING":
        return None, "pending"
    if row["status"] in ("REJECTED", "AUTO_REJECTED"):
        return None, "rejected"
    events.log(conn, "LOGIN_SUCCESS", row["id"])
    return row, None


def _decide(conn, admin, user_id: int, new_status: str) -> bool:
    if admin["role"] != "ADMIN":
        return False
    row = conn.execute("SELECT * FROM users WHERE id=? AND status='PENDING'", (user_id,)).fetchone()
    if not row:
        return False
    conn.execute("UPDATE users SET status=?, decided_at=? WHERE id=?", (new_status, now(), user_id))
    if new_status == "APPROVED":
        waited = datetime.now(timezone.utc) - datetime.fromisoformat(row["registered_at"])
        # PRD EVT-002: thuộc tính `wait_time`, đơn vị giờ
        events.log(conn, "ACCOUNT_APPROVED", user_id, wait_time=round(waited.total_seconds() / 3600, 1))
    return True


def approve(conn, admin, user_id: int) -> bool:
    return _decide(conn, admin, user_id, "APPROVED")


def reject(conn, admin, user_id: int) -> bool:
    return _decide(conn, admin, user_id, "REJECTED")


def auto_reject_expired(conn, now_dt: datetime | None = None) -> int:
    """UC-04, BR-022: PENDING quá hạn thì chuyển AUTO_REJECTED."""
    now_dt = now_dt or datetime.now(timezone.utc)
    cutoff = (now_dt - timedelta(days=config.APPROVAL_EXPIRY_DAYS)).isoformat(timespec="seconds")
    rows = conn.execute("SELECT id FROM users WHERE status='PENDING' AND registered_at < ?", (cutoff,)).fetchall()
    for row in rows:
        conn.execute("UPDATE users SET status='AUTO_REJECTED', decided_at=? WHERE id=?", (now(), row["id"]))
        events.log(conn, "ACCOUNT_AUTO_REJECTED", row["id"])
    return len(rows)


def pending_users(conn):
    return conn.execute(
        "SELECT id, email, display_name, registered_at FROM users WHERE status='PENDING' ORDER BY registered_at"
    ).fetchall()
