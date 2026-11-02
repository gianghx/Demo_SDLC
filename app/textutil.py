import re

_VI_CHARS = set(
    "ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ"
    "ĂÂĐÊÔƠƯÀÁẠẢÃẰẮẶẲẴẦẤẬẨẪÈÉẸẺẼỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕỒỐỘỔỖỜỚỢỞỠÙÚỤỦŨỪỨỰỬỮỲÝỴỶỸ"
)
_EN_WORDS = {"the", "and", "of", "to", "is", "in", "that", "for", "with", "are", "on", "this", "be", "as", "by"}


def detect_language(text: str) -> str:
    """BRU-008: tài liệu có cả tiếng Việt lẫn tiếng Anh được coi là tiếng Anh. Không rõ thì mặc định EN."""
    sample = text[:20000]
    letters = [c for c in sample if c.isalpha()]
    if not letters:
        return "EN"
    vi_ratio = sum(1 for c in letters if c in _VI_CHARS) / len(letters)
    words = re.findall(r"[A-Za-z]+", sample.lower())
    en_ratio = sum(1 for w in words if w in _EN_WORDS) / max(len(words), 1)
    has_vi = vi_ratio > 0.03
    has_en = en_ratio > 0.08
    if has_vi and not has_en:
        return "VI"
    return "EN"


def chunk_page(text: str, size: int, overlap: int) -> list[str]:
    """Tách một trang thành các đoạn. Số trang được giữ bởi người gọi (BR-008)."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    step = max(size - overlap, 1)
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]
