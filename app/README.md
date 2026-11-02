# Chat với tài liệu — demo local

Demo chạy local theo hồ sơ demo ở `docs/design/SAD.md` mục 14. Python 3.12, FastAPI, SQLite, Ollama (miễn phí).

## Chạy nhanh (không cần cài gì thêm, chế độ stub)

```powershell
cd "D:\SDLC AI\Demo_SDLC"
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:LLM_PROVIDER = "stub"
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Mở http://localhost:8000. Tài khoản admin có sẵn: `admin@demo.local` / `admin123` (chỉ dành cho demo local, đổi bằng biến `ADMIN_EMAIL`, `ADMIN_PASSWORD`).

Chế độ stub chỉ khớp từ khóa nên chất lượng thấp, không hỏi chéo ngôn ngữ Việt và Anh được. Dùng để xem luồng và giao diện.

## Chạy với mô hình thật (Ollama, miễn phí, chạy trên máy)

1. Cài Ollama: https://ollama.com/download
2. Tải mô hình (một lần):
   ```powershell
   ollama pull bge-m3
   ollama pull qwen2.5:3b
   ```
3. Chạy ứng dụng, **không** đặt `LLM_PROVIDER` (mặc định là `ollama`):
   ```powershell
   .venv\Scripts\python -m uvicorn app.main:app --reload
   ```

Muốn chất lượng cao hơn: `ollama pull qwen2.5:7b` rồi đặt `$env:CHAT_MODEL = "qwen2.5:7b"` (vừa với GPU 8 GB).

## Luồng dùng thử

1. Mở `/register`, đăng ký một tài khoản thường.
2. Đăng nhập bằng admin, vào `/admin`, duyệt tài khoản đó.
3. Đăng nhập tài khoản thường, upload PDF (có văn bản, không phải bản scan).
4. Chờ trạng thái "Sẵn sàng", rồi hỏi. Bấm vào nguồn để mở đúng trang PDF.

## Biến môi trường chính

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` hoặc `stub` |
| `CHAT_MODEL` / `EMBED_MODEL` | `qwen2.5:3b` / `bge-m3` | Mô hình Ollama |
| `MIN_SCORE` | 0.4 (ollama), 0.2 (stub) | Ngưỡng "không tìm thấy". Cần chỉnh bằng bộ câu hỏi chuẩn |
| `MAX_FILE_MB` / `MAX_FILES_PER_USER` | 100 / 100 | Giới hạn upload (BR-002, BR-016) |
| `APP_DATA_DIR` | `app_data/` | Nơi lưu cơ sở dữ liệu SQLite và PDF |

## Test

```powershell
.venv\Scripts\python -m pytest -q
```

Test chạy ở chế độ stub, không cần Ollama.

## Giới hạn của demo

Không có OCR (PDF scan thành "Không đọc được"), không gửi email, không sao lưu, không Docker. Hội thoại không được lưu. Chưa đo được độ chính xác (G2) và thời gian trả lời (G4) cho tới khi chạy mô hình thật với bộ câu hỏi chuẩn.
