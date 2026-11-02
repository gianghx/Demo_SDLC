import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from . import auth_service, config, db, events, library, qa, report
from .llm import ProviderError

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


async def _auto_reject_loop():
    """UC-04: mỗi giờ tự động từ chối các đăng ký quá hạn."""
    while True:
        try:
            with db.session() as conn:
                auth_service.auto_reject_expired(conn)
        except Exception:  # noqa: BLE001 - tác vụ nền không được làm sập ứng dụng
            pass
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    db.init_db()
    with db.session() as conn:
        auth_service.seed_admin(conn)
    task = asyncio.create_task(_auto_reject_loop())
    yield
    task.cancel()


app = FastAPI(title="Chat với tài liệu (demo)", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY, same_site="lax", max_age=8 * 3600)


def get_db():
    conn = db.connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def current_user(request: Request, conn=Depends(get_db)):
    uid = request.session.get("uid")
    if not uid:
        return None
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not row or row["status"] != "APPROVED":
        request.session.clear()
        return None
    return row


def require_user(user=Depends(current_user)):
    if not user:
        raise HTTPException(401, "Chưa đăng nhập")
    return user


def require_admin(user=Depends(require_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(403, "Chỉ admin")
    return user


# ---------- Trang HTML ----------

@app.get("/")
def home(request: Request, user=Depends(current_user)):
    if not user:
        return RedirectResponse("/login", 303)
    me = {"id": user["id"], "name": user["display_name"], "admin": user["role"] == "ADMIN",
          "max_file_mb": config.MAX_FILE_MB, "max_question": config.MAX_QUESTION_CHARS}
    return templates.TemplateResponse(request, "home.html", {"me": me})


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"message": None})


LOGIN_MESSAGES = {
    "bad_credentials": "Sai email hoặc mật khẩu.",
    "pending": "Tài khoản đang chờ admin duyệt (tối đa 7 ngày).",
    "rejected": "Tài khoản đã bị từ chối. Bạn có thể đăng ký lại bằng cùng email.",
}


@app.post("/login")
async def login(request: Request, conn=Depends(get_db)):
    form = await request.form()
    user, reason = auth_service.authenticate(conn, str(form.get("email", "")), str(form.get("password", "")))
    if not user:
        conn.commit()  # giữ lại sự kiện LOGIN_FAILED
        return templates.TemplateResponse(request, "login.html", {"message": LOGIN_MESSAGES[reason]}, status_code=401)
    request.session["uid"] = user["id"]
    return RedirectResponse("/", 303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", 303)


REGISTER_MESSAGES = {
    "created": "Đã ghi nhận. Tài khoản đang chờ admin duyệt (tối đa 7 ngày).",
    "re_registered": "Đã đăng ký lại. Tài khoản đang chờ admin duyệt (tối đa 7 ngày).",
    "exists": "Email này đã có tài khoản.",
    "invalid": "Dữ liệu không hợp lệ: kiểm tra email, tên hiển thị và mật khẩu (tối thiểu 6 ký tự).",
}


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"message": None, "ok": False, "form": {}})


@app.post("/register")
async def register(request: Request, conn=Depends(get_db)):
    form = await request.form()
    result = auth_service.register(conn, str(form.get("email", "")), str(form.get("display_name", "")),
                                   str(form.get("password", "")))
    ok = result in ("created", "re_registered")
    # Giữ lại email và tên khi báo lỗi (PRD 4.2); không bao giờ gửi lại mật khẩu
    kept = {} if ok else {"email": str(form.get("email", "")), "display_name": str(form.get("display_name", ""))}
    return templates.TemplateResponse(
        request, "register.html", {"message": REGISTER_MESSAGES[result], "ok": ok, "form": kept},
        status_code=200 if ok else 400)


@app.get("/admin")
def admin_page(request: Request, admin=Depends(current_user), conn=Depends(get_db)):
    if not admin:
        return RedirectResponse("/login", 303)
    if admin["role"] != "ADMIN":
        raise HTTPException(403, "Chỉ admin")
    auth_service.auto_reject_expired(conn)
    return templates.TemplateResponse(request, "admin.html", {
        "pending": auth_service.pending_users(conn),
        "report": report.pilot_report(conn),
        "name": admin["display_name"],
    })


@app.post("/admin/users/{user_id}/approve")
def admin_approve(user_id: int, admin=Depends(require_admin), conn=Depends(get_db)):
    auth_service.approve(conn, admin, user_id)
    return RedirectResponse("/admin", 303)


@app.post("/admin/users/{user_id}/reject")
def admin_reject(user_id: int, admin=Depends(require_admin), conn=Depends(get_db)):
    auth_service.reject(conn, admin, user_id)
    return RedirectResponse("/admin", 303)


# ---------- API ----------

@app.get("/api/documents")
def api_list_documents(user=Depends(require_user), conn=Depends(get_db)):
    return [{**dict(r), "can_delete": user["role"] == "ADMIN" or r["owner_id"] == user["id"]}
            for r in library.list_documents(conn)]


@app.post("/api/documents")
async def api_upload(file: UploadFile, background: BackgroundTasks,
                     user=Depends(require_user), conn=Depends(get_db)):
    data = await file.read()
    reason = library.validate_upload(user, file.filename or "", data)
    if reason:
        events.log(conn, "DOCUMENT_REJECTED", user["id"], reject_reason=reason)
        conn.commit()
        return JSONResponse({"ok": False, "reason": reason, "message": library.REJECT_MESSAGES[reason]},
                            status_code=400)
    doc_id = library.add_document(conn, user, file.filename, data)
    background.add_task(library.process_document, doc_id)
    return {"ok": True, "id": doc_id}


@app.post("/api/documents/{doc_id}/delete")
def api_delete(doc_id: int, user=Depends(require_user), conn=Depends(get_db)):
    result = library.delete_document(conn, user, doc_id)
    if result == "not_found":
        raise HTTPException(404, "Không tìm thấy tài liệu")
    if result == "forbidden":
        raise HTTPException(403, "Bạn không có quyền xóa tài liệu này")
    return {"ok": True}


@app.api_route("/documents/{doc_id}/file", methods=["GET", "HEAD"])
def document_file(doc_id: int, user=Depends(require_user), conn=Depends(get_db)):
    doc = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not doc:
        raise HTTPException(404, "Tài liệu đã bị xóa")
    path = config.UPLOAD_DIR / doc["stored_name"]
    events.log(conn, "CITATION_OPENED", user["id"])
    return FileResponse(path, media_type="application/pdf", filename=doc["file_name"],
                        content_disposition_type="inline")


class AskIn(BaseModel):
    question: str


@app.post("/api/ask")
def api_ask(body: AskIn, user=Depends(require_user), conn=Depends(get_db)):
    try:
        result = qa.ask(conn, user, body.question)
    except qa.QuestionError as exc:
        messages = {"empty": "Câu hỏi đang trống.",
                    "too_long": f"Câu hỏi tối đa {config.MAX_QUESTION_CHARS} ký tự."}
        return JSONResponse({"error": exc.code, "message": messages[exc.code]}, status_code=400)
    except qa.NoDocumentsError:
        return JSONResponse({"error": "no_documents",
                             "message": "Kho chưa có tài liệu sẵn sàng. Hãy upload PDF trước."}, status_code=409)
    except ProviderError as exc:
        conn.commit()
        return JSONResponse({"error": "provider", "message": f"Dịch vụ mô hình lỗi: {exc}"}, status_code=502)
    return result


@app.get("/healthz")
def healthz():
    return {"ok": True, "provider": config.LLM_PROVIDER}
