"""Báo cáo pilot đơn giản (UC-10). MET-001 không có ở đây: đo bằng nghiên cứu tác vụ mẫu (PRD 5.2)."""
import json
import math
from datetime import datetime, timedelta, timezone

TARGET_USERS = 30  # BRD: khoảng 30 người


def pilot_report(conn, now_dt: datetime | None = None) -> dict:
    now_dt = now_dt or datetime.now(timezone.utc)
    since = (now_dt - timedelta(days=7)).isoformat(timespec="seconds")

    status_counts = {r["status"]: r["n"] for r in conn.execute(
        "SELECT status, COUNT(*) AS n FROM users WHERE role='MEMBER' GROUP BY status")}
    approved = status_counts.get("APPROVED", 0)
    active = conn.execute(
        "SELECT COUNT(DISTINCT user_id) AS n FROM usage_events WHERE type='QUESTION_SUBMITTED' AND occurred_at >= ?",
        (since,)).fetchone()["n"]
    doc_counts = {r["status"]: r["n"] for r in conn.execute(
        "SELECT status, COUNT(*) AS n FROM documents GROUP BY status")}

    answers = [json.loads(r["properties"]) for r in conn.execute(
        "SELECT properties FROM usage_events WHERE type='ANSWER_RETURNED'")]
    latencies = sorted(a.get("latency_ms", 0) for a in answers)
    p90 = latencies[max(math.ceil(0.9 * len(latencies)) - 1, 0)] if latencies else None
    return {
        "users": status_counts,
        "approved_members": approved,
        "active_last_7_days": active,
        "active_rate": round(active / approved, 2) if approved else None,
        "target_users": TARGET_USERS,
        "documents": doc_counts,
        "answers_total": len(answers),
        "p90_latency_ms": p90,
        "with_citation": sum(1 for a in answers if a.get("has_citation")),
        "not_found": sum(1 for a in answers if a.get("not_found")),
    }
