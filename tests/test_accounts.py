"""Ca test UC-01..UC-04. Mã ca (tcNNN) nằm trong tên hàm để ánh xạ về docs/testing/test-cases.md."""
from datetime import datetime, timedelta, timezone

from app import auth_service, config, db

from .conftest import admin_client, login, make_member, new_client, upload


def _uid(email):
    with db.session() as conn:
        return conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]


def _set(email, **fields):
    cols = ", ".join(f"{k}=?" for k in fields)
    with db.session() as conn:
        conn.execute(f"UPDATE users SET {cols} WHERE email=?", (*fields.values(), email))


def _row(email):
    with db.session() as conn:
        return conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()


def _register(client, email, name="N", password="secret1"):
    return client.post("/register", data={"email": email, "display_name": name, "password": password})


def _old(days, minutes=0):
    return (datetime.now(timezone.utc) - timedelta(days=days, minutes=minutes)).isoformat(timespec="seconds")


def test_tc001_register_creates_pending(env):
    r = _register(new_client(), "a@x.com", "A")
    assert r.status_code == 200 and "chờ admin duyệt" in r.text
    row = _row("a@x.com")
    assert (row["status"], row["role"]) == ("PENDING", "MEMBER")
    with db.session() as conn:
        assert conn.execute("SELECT COUNT(*) n FROM usage_events WHERE type='REGISTER_SUBMITTED'").fetchone()["n"] == 1


def test_tc002_invalid_data_shows_error_and_keeps_input(env):
    r = _register(new_client(), "bad-email", "Tên Tôi", "secret1")
    assert r.status_code == 400 and "không hợp lệ" in r.text
    assert 'value="bad-email"' in r.text and 'value="Tên Tôi"' in r.text  # giữ dữ liệu đã nhập
    assert _register(new_client(), "ok@x.com", "A", "123").status_code == 400  # mật khẩu quá ngắn
    assert _row("ok@x.com") is None


def test_tc003_duplicate_email_pending_and_approved(env):
    admin = admin_client()
    _register(new_client(), "a@x.com")
    assert "đã có tài khoản" in _register(new_client(), "a@x.com").text           # PENDING
    admin.post(f"/admin/users/{_uid('a@x.com')}/approve", follow_redirects=False)
    r = _register(new_client(), "a@x.com")                                         # APPROVED
    assert r.status_code == 400 and "đã có tài khoản" in r.text


def test_tc004_reregister_after_rejected_and_auto_rejected(env):
    admin = admin_client()
    for email, final in (("r@x.com", "REJECTED"), ("t@x.com", "AUTO_REJECTED")):
        _register(new_client(), email)
        if final == "REJECTED":
            admin.post(f"/admin/users/{_uid(email)}/reject", follow_redirects=False)
        else:
            _set(email, status="AUTO_REJECTED")
        old = _old(10)
        _set(email, registered_at=old)
        assert _register(new_client(), email, "Mới", "secret2").status_code == 200
        row = _row(email)
        assert row["status"] == "PENDING" and row["decided_at"] is None and row["registered_at"] > old


def test_tc005_login_approved_logs_event(env):
    admin = admin_client()
    member = make_member(admin, "u@x.com")
    assert member.get("/api/documents").status_code == 200
    with db.session() as conn:
        n = conn.execute("SELECT COUNT(*) n FROM usage_events WHERE type='LOGIN_SUCCESS' AND user_id=?",
                         (_uid("u@x.com"),)).fetchone()["n"]
    assert n == 1


def test_tc006_wrong_credentials(env):
    c = new_client()
    r = login(c, "nobody@x.com", "whatever1")
    assert r.status_code == 401
    assert "Sai email hoặc mật khẩu" in c.post("/login", data={"email": "nobody@x.com", "password": "x"}).text
    _register(new_client(), "k@x.com")
    login(new_client(), "k@x.com", "wrong-password")
    with db.session() as conn:
        ids = [r["user_id"] for r in conn.execute("SELECT user_id FROM usage_events WHERE type='LOGIN_FAILED'")]
    assert None in ids and _uid("k@x.com") in ids  # email không tồn tại thì không gắn User


def test_tc007_pending_cannot_login(env):
    _register(new_client(), "b@x.com")
    c = new_client()
    r = c.post("/login", data={"email": "b@x.com", "password": "secret1"})
    assert r.status_code == 401 and "chờ admin duyệt" in r.text
    assert c.get("/api/documents").status_code == 401


def test_tc008_rejected_and_auto_rejected_cannot_login(env):
    for email, status in (("r@x.com", "REJECTED"), ("t@x.com", "AUTO_REJECTED")):
        _register(new_client(), email)
        _set(email, status=status)
        r = new_client().post("/login", data={"email": email, "password": "secret1"})
        assert r.status_code == 401 and "bị từ chối" in r.text and "đăng ký lại" in r.text


def test_tc009_unauthenticated_cannot_access(env):
    c = new_client()
    assert c.get("/", follow_redirects=False).status_code == 303
    assert c.get("/admin", follow_redirects=False).status_code == 303
    assert c.get("/api/documents").status_code == 401
    assert c.post("/api/ask", json={"question": "hi"}).status_code == 401
    assert c.get("/documents/1/file").status_code == 401


def test_tc010_admin_approves(env):
    admin = admin_client()
    _register(new_client(), "a@x.com")
    r = admin.post(f"/admin/users/{_uid('a@x.com')}/approve", follow_redirects=False)
    assert r.status_code == 303
    row = _row("a@x.com")
    assert row["status"] == "APPROVED" and row["decided_at"]
    with db.session() as conn:
        assert conn.execute("SELECT COUNT(*) n FROM usage_events WHERE type='ACCOUNT_APPROVED'").fetchone()["n"] == 1
    assert login(new_client(), "a@x.com", "secret1").status_code == 303


def test_tc011_admin_rejects(env):
    admin = admin_client()
    _register(new_client(), "c@x.com")
    admin.post(f"/admin/users/{_uid('c@x.com')}/reject", follow_redirects=False)
    assert _row("c@x.com")["status"] == "REJECTED"
    assert login(new_client(), "c@x.com", "secret1").status_code == 401


def test_tc012_admin_page_with_no_pending(env):
    assert "Không có tài khoản nào chờ duyệt" in admin_client().get("/admin").text


def test_tc013_member_cannot_use_admin_endpoints(env):
    admin = admin_client()
    member = make_member(admin, "m@x.com")
    assert member.get("/admin", follow_redirects=False).status_code == 403
    assert member.post("/admin/users/1/approve", follow_redirects=False).status_code == 403
    assert member.post("/admin/users/1/reject", follow_redirects=False).status_code == 403
    assert "Quản trị" not in member.get("/").text  # không thấy mục quản trị


def test_tc014_tc015_tc016_auto_reject_after_7_days(env):
    admin = admin_client()
    _register(new_client(), "old@x.com")
    _register(new_client(), "new@x.com")
    make_member(admin, "approved@x.com")
    _set("old@x.com", registered_at=_old(config.APPROVAL_EXPIRY_DAYS, minutes=1))  # quá hạn 1 phút
    _set("new@x.com", registered_at=_old(config.APPROVAL_EXPIRY_DAYS, minutes=-1))  # còn 1 phút nữa mới hết hạn
    _set("approved@x.com", registered_at=_old(30))                           # đã được duyệt từ lâu
    with db.session() as conn:
        assert auth_service.auto_reject_expired(conn) == 1
    assert _row("old@x.com")["status"] == "AUTO_REJECTED"
    assert _row("new@x.com")["status"] == "PENDING"
    assert _row("approved@x.com")["status"] == "APPROVED"
    assert login(new_client(), "old@x.com", "secret1").status_code == 401
    with db.session() as conn:
        n = conn.execute("SELECT COUNT(*) n FROM usage_events WHERE type='ACCOUNT_AUTO_REJECTED'").fetchone()["n"]
    assert n == 1
    with db.session() as conn:
        assert auth_service.auto_reject_expired(conn) == 0  # chạy lại không xử lý lần hai


def test_tc017_seeded_admin_can_approve_and_delete(env):
    admin = admin_client()
    member = make_member(admin, "u@x.com")
    assert admin.get("/admin").status_code == 200
    upload(member, ["Content for the seeded admin deletion check."])
    with db.session() as conn:
        doc_id = conn.execute("SELECT id FROM documents").fetchone()["id"]
    assert admin.post(f"/api/documents/{doc_id}/delete").status_code == 200
