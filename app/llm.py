"""Nhà cung cấp mô hình: Ollama (local, miễn phí) hoặc stub (không cần cài gì)."""
import hashlib
import re

import httpx
import numpy as np

from . import config


class ProviderError(Exception):
    pass


class OllamaProvider:
    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            r = httpx.post(f"{config.OLLAMA_URL}/api/embed",
                           json={"model": config.EMBED_MODEL, "input": texts}, timeout=300)
            r.raise_for_status()
            return r.json()["embeddings"]
        except (httpx.HTTPError, KeyError) as exc:
            raise ProviderError(f"Ollama embed lỗi: {exc}") from exc

    def chat(self, system: str, user: str) -> str:
        try:
            r = httpx.post(
                f"{config.OLLAMA_URL}/api/chat",
                json={"model": config.CHAT_MODEL, "stream": False, "options": {"temperature": 0.1},
                      "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
                timeout=300,
            )
            r.raise_for_status()
            return r.json()["message"]["content"].strip()
        except (httpx.HTTPError, KeyError) as exc:
            raise ProviderError(f"Ollama chat lỗi: {exc}") from exc


_STOP = {"the", "and", "for", "are", "was", "what", "which", "who", "how", "with", "that", "this", "from",
         "have", "has", "does", "did", "you", "your", "about", "into", "than", "then", "them", "their",
         "là", "và", "của", "có", "cho", "các", "một", "được", "trong", "với", "không", "những", "này"}


class StubProvider:
    """Embedding băm từ khóa (256 chiều) và câu trả lời lấy thẳng đoạn trích. Chỉ để chạy thử và test."""
    DIM = 256

    def embed(self, texts: list[str]) -> list[list[float]]:
        out = []
        for text in texts:
            vec = np.zeros(self.DIM, dtype=np.float32)
            for tok in re.findall(r"\w+", text.lower()):
                if len(tok) > 2 and tok not in _STOP:
                    vec[int(hashlib.md5(tok.encode()).hexdigest(), 16) % self.DIM] += 1.0
            norm = np.linalg.norm(vec)
            out.append((vec / norm if norm else vec).tolist())
        return out

    def chat(self, system: str, user: str) -> str:
        m = re.search(r"\[1\]\s*(.+?)(?:\n\[|\n\nQuestion:)", user, re.S)
        snippet = (m.group(1).strip() if m else user)[:300]
        return f"[1] {snippet}"


_override = None


def set_provider(provider) -> None:
    """Dùng trong test để thay nhà cung cấp."""
    global _override
    _override = provider


def get_provider():
    if _override is not None:
        return _override
    return StubProvider() if config.LLM_PROVIDER == "stub" else OllamaProvider()
