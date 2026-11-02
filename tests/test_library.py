"""Ca test UC-05..UC-07. Mã ca (tcNNN) nằm trong tên hàm."""
from app import config, db
from app.textutil import chunk_page, detect_language

from .conftest import admin_client, login, make_member, make_pdf, new_client, upload

MB = 1024 * 1024


def _doc_ids():
    with db.session() as conn:
        return [r["id"] for r in conn.execute("SELECT id FROM documents ORDER BY id")]


def _events(type_):
    with db.session() as conn:
        return [r["properties"] for r in conn.execute("SELECT properties FROM usage_events WHERE type=?", (type_,))]


def _padded_pdf(size: int) -> bytes:
    base = make_pdf(["boundary test page content"])
    return base + b"\n" * (size - len(base))


def test_tc018_upload_valid_pdf_becomes_ready_and_others_can_ask(env):
    admin = admin_client()
    a, b = make_member(admin, "a@x.com"), make_member(admin, "b@x.com")
    r = upload(a, ["Refund policy is thirty days for all products."])
    assert r.status_code == 200 and r.json()["ok"]
    docs = a.get("/api/documents").json()
    assert len(docs) == 1 and docs[0]["status"] == "READY" and docs[0]["language"] == "EN"
    with db.session() as conn:
        assert conn.execute("SELECT COUNT(*) n FROM chunks").fetchone()["n"] >= 1
        assert conn.execute("SELECT total_uploaded FROM users WHERE email='a@x.com'").fetchone()[0] == 1
    assert b.post("/api/ask", json={"question": "refund policy products"}).status_code == 200  # người khác hỏi được


def test_tc019_file_of_exactly_100mb_accepted(env):
    assert config.MAX_FILE_MB == 100
    member = make_member(admin_client(), "u@x.com")
    r = member.post("/api/documents", files={"file": ("big.pdf", _padded_pdf(100 * MB), "application/pdf")})
    assert r.status_code == 200 and r.json()["ok"]
    assert member.get("/api/documents").json()[0]["status"] == "READY"


def test_tc020_file_over_100mb_rejected(env):
    member = make_member(admin_client(), "u@x.com")
    r = member.post("/api/documents", files={"file": ("big.pdf", _padded_pdf(100 * MB + 1), "application/pdf")})
    body = r.json()
    assert r.status_code == 400 and body["reason"] == "TOO_LARGE" and body["message"]
    assert _doc_ids() == [] and len(_events("DOCUMENT_REJECTED")) == 1


def test_tc021_tc022_not_pdf_and_corrupted_with_reason(env):
    member = make_member(admin_client(), "u@x.com")
    r = member.post("/api/documents", files={"file": ("a.txt", b"plain text", "text/plain")})
    assert r.json()["reason"] == "NOT_PDF" and r.json()["message"]
    r = member.post("/api/documents", files={"file": ("a.pdf", b"%PDF-1.4 broken", "application/pdf")})
    assert r.json()["reason"] == "CORRUPTED" and r.json()["message"]
    assert _doc_ids() == [] and len(_events("DOCUMENT_REJECTED")) == 2


def test_tc023_tc024_tc025_quota_of_100_counts_total_uploaded(env):
    assert config.MAX_FILES_PER_USER == 100
    member = make_member(admin_client(), "u@x.com")
    with db.session() as conn:  # đã upload 99 tệp trước đó
        conn.execute("UPDATE users SET total_uploaded=99 WHERE email='u@x.com'")
    assert upload(member, ["the hundredth file"]).json()["ok"]                       # TC-023: tệp thứ 100
    r = upload(member, ["the hundred and first file"])
    assert r.status_code == 400 and r.json()["reason"] == "QUOTA_EXCEEDED" and r.json()["message"]  # TC-024
    member.post(f"/api/documents/{_doc_ids()[0]}/delete")
    assert upload(member, ["after deleting one"]).json()["reason"] == "QUOTA_EXCEEDED"             # TC-025


def test_tc026_unreadable_scan_not_used_for_queries(env):
    member = make_member(admin_client(), "u@x.com")
    assert upload(member, [""]).json()["ok"]
    assert member.get("/api/documents").json()[0]["status"] == "UNREADABLE"
    assert member.post("/api/ask", json={"question": "anything at all"}).status_code == 409


def test_tc029_documents_persist_across_logout_login_and_shared(env):
    admin = admin_client()
    a, b = make_member(admin, "a@x.com"), make_member(admin, "b@x.com")
    upload(a, ["Shared knowledge base content here."])
    a.post("/logout")
    assert a.get("/api/documents").status_code == 401
    assert login(a, "a@x.com", "secret1").status_code == 303
    assert len(a.get("/api/documents").json()) == 1
    assert len(b.get("/api/documents").json()) == 1  # kho chung (BRU-001)


def test_tc032_tc033_tc034_delete_permissions(env):
    admin = admin_client()
    a, b = make_member(admin, "a@x.com"), make_member(admin, "b@x.com")
    upload(a, ["Content of document one."])
    upload(a, ["Content of document two."])
    d1, d2 = _doc_ids()
    assert not any(d["can_delete"] for d in b.get("/api/documents").json())     # không có hành động xóa
    assert b.post(f"/api/documents/{d1}/delete").status_code == 403             # TC-033
    assert a.post(f"/api/documents/{d1}/delete").status_code == 200             # TC-032
    assert admin.post(f"/api/documents/{d2}/delete").status_code == 200         # TC-034
    assert _doc_ids() == []
    with db.session() as conn:
        assert conn.execute("SELECT COUNT(*) n FROM chunks").fetchone()["n"] == 0
    assert a.post(f"/api/documents/{d1}/delete").status_code == 404
    assert not list(config.UPLOAD_DIR.glob("*.pdf"))
    deleted_by = sorted(__import__("json").loads(p)["deleted_by"] for p in _events("DOCUMENT_DELETED"))
    assert deleted_by == ["admin", "owner"]
    assert a.post("/api/ask", json={"question": "document one content"}).status_code == 409  # không còn trong truy vấn


def test_unit_language_detection_rules():
    vi = "Chính sách hoàn tiền áp dụng trong vòng ba mươi ngày kể từ ngày mua hàng của khách."
    en = "The refund policy is that customers can return products within thirty days of the purchase."
    assert detect_language(vi) == "VI"
    assert detect_language(en) == "EN"
    assert detect_language(vi + " " + en) == "EN"  # BRU-008


def test_unit_chunking_keeps_text_and_overlap():
    chunks = chunk_page("word " * 400, size=300, overlap=50)
    assert len(chunks) > 1 and all(len(c) <= 300 for c in chunks)
    assert chunk_page("   ", 300, 50) == []
