"""Cấu hình lấy từ biến môi trường. Các module khác đọc `config.X` lúc gọi (không `from config import X`)
để test có thể monkeypatch."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = Path(os.getenv("APP_DATA_DIR", BASE_DIR / "app_data"))
DB_PATH = DATA_DIR / "app.db"
UPLOAD_DIR = DATA_DIR / "uploads"

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

# Tài khoản admin có sẵn (BR-019). Mặc định chỉ dành cho demo local.
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@demo.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Giới hạn theo BRD
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "100"))              # BR-002
MAX_FILES_PER_USER = int(os.getenv("MAX_FILES_PER_USER", "100"))  # BR-016, BRU-007 (tính tổng đã upload)
APPROVAL_EXPIRY_DAYS = int(os.getenv("APPROVAL_EXPIRY_DAYS", "7"))  # BRU-006
MAX_QUESTION_CHARS = int(os.getenv("MAX_QUESTION_CHARS", "1000"))   # PRD 4.2

# Mô hình: "ollama" (chạy local) hoặc "stub" (không cần cài gì, chất lượng thấp)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")

TOP_K = int(os.getenv("TOP_K", "5"))
# Ngưỡng "không tìm thấy". Cần hiệu chỉnh bằng bộ câu hỏi chuẩn (SAD mục 5.2).
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.2" if LLM_PROVIDER == "stub" else "0.4"))

CHUNK_CHARS = int(os.getenv("CHUNK_CHARS", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
