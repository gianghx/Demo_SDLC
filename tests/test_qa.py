"""Ca test UC-08..UC-10. Mã ca (tcNNN) nằm trong tên hàm.
Các test `test_stub_*` kiểm tra logic truy xuất và Citation bằng chế độ stub. Chúng KHÔNG chứng minh chất lượng
câu trả lời (TC-036..TC-044, TC-057, TC-058), việc đó cần mô hình thật."""
import json

from app import config, db, report

from .conftest import admin_client, make_member, new_client, upload


def _ask(client, q):
    return client.post("/api/ask", json={"question": q})


def _events(type_):
    with db.session() as conn:
        return [json.loads(r["properties"]) for r in
                conn.execute("SELECT properties FROM usage_events WHERE type=?", (type_,))]


def test_tc045_empty_question_rejected(env):
    member = make_member(admin_client(), "u@x.com")
    upload(member, ["Some content to make the library non-empty."])
    r = _ask(member, "   ")
    assert r.status_code == 400 and r.json()["error"] == "empty" and r.json()["message"]


def test_tc046_question_length_boundary(env):
    member = make_member(admin_client(), "u@x.com")
    upload(member, ["Some content to make the library non-empty."])
    assert config.MAX_QUESTION_CHARS == 1000
    assert _ask(member, "c" * 1000).status_code == 200
    r = _ask(member, "c" * 1001)
    assert r.status_code == 400 and r.json()["error"] == "too_long" and "1000" in r.json()["message"]


def test_tc047_no_ready_documents_guides_upload(env):
    member = make_member(admin_client(), "u@x.com")
    r = _ask(member, "What is the refund policy?")
    assert r.status_code == 409 and r.json()["error"] == "no_documents" and "upload" in r.json()["message"].lower()


def test_stub_answer_cites_correct_page(env):
    member = make_member(admin_client(), "u@x.com")
    upload(member, ["Introduction to our company history and mission.",
                    "The refund policy allows returns within thirty days of purchase."], name="policy.pdf")
    data = _ask(member, "What is the refund policy for returns?").json()
    assert data["not_found"] is False and data["language"] == "EN"
    assert data["citations"][0]["document_name"] == "policy.pdf" and data["citations"][0]["page"] == 2


def test_stub_not_found_when_nothing_relevant(env):
    member = make_member(admin_client(), "u@x.com")
    upload(member, ["The refund policy allows returns within thirty days of purchase."])
    data = _ask(member, "Explain quantum entanglement of spaceship engines").json()
    assert data["not_found"] is True and data["citations"] == []


def test_stub_retrieval_spans_all_documents(env):
    member = make_member(admin_client(), "u@x.com")
    upload(member, ["Shipping takes five business days within the country."], name="ship.pdf")
    upload(member, ["Warranty covers manufacturing defects for twelve months."], name="warranty.pdf")
    names = set()
    for q in ("How long does shipping take?", "What does the warranty cover for defects?"):
        names |= {c["document_name"] for c in _ask(member, q).json()["citations"]}
    assert names == {"ship.pdf", "warranty.pdf"}


def test_deleted_document_file_returns_404(env):
    member = make_member(admin_client(), "u@x.com")
    upload(member, ["The refund policy allows returns within thirty days."])
    with db.session() as conn:
        doc_id = conn.execute("SELECT id FROM documents").fetchone()["id"]
    assert member.head(f"/documents/{doc_id}/file").status_code == 200
    member.post(f"/api/documents/{doc_id}/delete")
    assert member.head(f"/documents/{doc_id}/file").status_code == 404


def test_tc054_report_shows_active_users_metric(env):
    admin = admin_client()
    member = make_member(admin, "u@x.com")
    make_member(admin, "idle@x.com")
    upload(member, ["The refund policy allows returns within thirty days."])
    _ask(member, "What is the refund policy?")
    with db.session() as conn:
        rep = report.pilot_report(conn)
    assert rep["approved_members"] == 2 and rep["active_last_7_days"] == 1 and rep["active_rate"] == 0.5
    page = admin.get("/admin").text
    assert "MET-002" in page and "50%" in page


def test_tc056_report_with_no_data(env):
    page = admin_client().get("/admin").text
    assert "chưa có dữ liệu" in page and "MET-002" in page


def test_tc059_events_recorded_with_properties_and_no_content(env):
    admin = admin_client()
    member = make_member(admin, "u@x.com")
    new_client().post("/login", data={"email": "ghost@x.com", "password": "x"})            # LOGIN_FAILED
    member.post("/api/documents", files={"file": ("a.txt", b"text", "text/plain")})        # DOCUMENT_REJECTED
    upload(member, ["The refund policy allows returns within thirty days."])
    _ask(member, "What is the refund policy?")                                             # QUESTION/ANSWER
    with db.session() as conn:
        doc_id = conn.execute("SELECT id FROM documents").fetchone()["id"]
    member.head(f"/documents/{doc_id}/file")                                               # CITATION_OPENED
    member.post(f"/api/documents/{doc_id}/delete")                                         # DOCUMENT_DELETED
    with db.session() as conn:
        types = {r["type"] for r in conn.execute("SELECT DISTINCT type FROM usage_events")}
    expected = {"REGISTER_SUBMITTED", "ACCOUNT_APPROVED", "LOGIN_SUCCESS", "LOGIN_FAILED",
                "DOCUMENT_UPLOAD_STARTED", "DOCUMENT_READY", "DOCUMENT_REJECTED", "DOCUMENT_DELETED",
                "QUESTION_SUBMITTED", "ANSWER_RETURNED", "CITATION_OPENED"}
    assert expected <= types
    assert "wait_time" in _events("ACCOUNT_APPROVED")[-1]                    # PRD EVT-002
    assert "size_mb" in _events("DOCUMENT_UPLOAD_STARTED")[0]                 # EVT-004
    assert "reject_reason" in _events("DOCUMENT_REJECTED")[0]                 # EVT-004
    assert _events("DOCUMENT_DELETED")[0]["deleted_by"] == "owner"            # EVT-005
    assert _events("QUESTION_SUBMITTED")[0]["language"] in ("VI", "EN")       # EVT-006
    a = _events("ANSWER_RETURNED")[0]                                         # EVT-007
    assert {"latency_ms", "has_citation", "not_found"} <= set(a)
    with db.session() as conn:
        props = " ".join(r["properties"] for r in conn.execute("SELECT properties FROM usage_events"))
    assert "refund" not in props.lower()                                      # OQ-024: không ghi nội dung
