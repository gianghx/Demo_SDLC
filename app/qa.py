"""Hỏi đáp (UC-08). Truy xuất đoạn văn, ràng buộc câu trả lời vào nguồn, gắn Citation từ đoạn đã dùng."""
import re
import time

import numpy as np

from . import config, events
from .llm import get_provider
from .textutil import detect_language

NOT_FOUND_TOKEN = "KHONG_TIM_THAY"


class QuestionError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class NoDocumentsError(Exception):
    pass


def _load_chunks(conn):
    rows = conn.execute(
        "SELECT c.id, c.document_id, c.page_number, c.text, c.embedding, d.file_name, d.language "
        "FROM chunks c JOIN documents d ON d.id = c.document_id WHERE d.status = 'READY'"
    ).fetchall()
    return rows


def ask(conn, user, question: str) -> dict:
    question = question.strip()
    if not question:
        raise QuestionError("empty")
    if len(question) > config.MAX_QUESTION_CHARS:
        raise QuestionError("too_long")

    rows = _load_chunks(conn)
    if not rows:
        raise NoDocumentsError()

    started = time.perf_counter()
    events.log(conn, "QUESTION_SUBMITTED", user["id"], language=detect_language(question))  # PRD EVT-006
    provider = get_provider()

    q = np.asarray(provider.embed([question])[0], dtype=np.float32)
    q = q / (np.linalg.norm(q) or 1.0)
    matrix = np.vstack([np.frombuffer(r["embedding"], dtype=np.float32) for r in rows])
    norms = np.linalg.norm(matrix, axis=1)
    norms[norms == 0] = 1.0
    scores = (matrix / norms[:, None]) @ q
    order = [i for i in np.argsort(-scores)[: config.TOP_K] if scores[i] >= config.MIN_SCORE]

    result = {"answer": "", "not_found": True, "language": None, "citations": []}
    if order:
        used = [rows[i] for i in order]
        # BR-021, BRU-009: theo ngôn ngữ tài liệu nguồn; có cả VI và EN thì EN
        language = "EN" if any(r["language"] == "EN" for r in used) else "VI"
        lang_name = "English" if language == "EN" else "Vietnamese"
        context = "\n".join(f"[{n}] ({r['file_name']}, page {r['page_number']}) {r['text']}"
                            for n, r in enumerate(used, start=1))
        system = (
            "You answer questions using ONLY the numbered excerpts provided. "
            f"If the excerpts do not contain the answer, reply with exactly {NOT_FOUND_TOKEN} and nothing else. "
            f"Write the answer in {lang_name}. Be concise. Cite the excerpts you used as [n]."
        )
        text = provider.chat(system, f"Excerpts:\n{context}\n\nQuestion: {question}")
        if NOT_FOUND_TOKEN not in text:
            cited = {int(n) for n in re.findall(r"\[(\d+)\]", text) if 1 <= int(n) <= len(used)} or {1}
            seen, citations = set(), []
            for n in sorted(cited):
                r = used[n - 1]
                key = (r["document_id"], r["page_number"])
                if key not in seen:  # Citation do hệ thống gắn từ đoạn đã dùng, không do mô hình tự nêu
                    seen.add(key)
                    citations.append({"document_id": r["document_id"], "document_name": r["file_name"],
                                      "page": r["page_number"]})
            result = {"answer": text, "not_found": False, "language": language, "citations": citations}

    latency_ms = int((time.perf_counter() - started) * 1000)
    events.log(conn, "ANSWER_RETURNED", user["id"], latency_ms=latency_ms,
               has_citation=bool(result["citations"]), not_found=result["not_found"])
    result["latency_ms"] = latency_ms
    return result
