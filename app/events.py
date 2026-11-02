import json

from .db import now

# Sự kiện đo lường (PRD 5.2). Không ghi nội dung câu hỏi hay câu trả lời.


def log(conn, type_: str, user_id: int | None = None, **props) -> None:
    conn.execute(
        "INSERT INTO usage_events (user_id, type, occurred_at, properties) VALUES (?, ?, ?, ?)",
        (user_id, type_, now(), json.dumps(props, ensure_ascii=False)),
    )
