"""Backend: data access / business logic for study sessions."""
from datetime import datetime

import pandas as pd

from focuslab.database import get_conn

COLUMNS = ["id", "user", "subject", "planned_min", "actual_min", "completed", "notes", "started_at"]


def add_session(user, subject, planned_min, actual_min, completed, notes="", started_at=None):
    user, subject = (user or "").strip(), (subject or "").strip()
    if not user or not subject:
        raise ValueError("User and subject are required.")
    if planned_min <= 0 or actual_min < 0:
        raise ValueError("Invalid duration.")
    started_at = started_at or datetime.now()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO sessions (user, subject, planned_min, actual_min, completed, notes, started_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (user, subject, float(planned_min), float(actual_min), int(bool(completed)),
             (notes or "").strip(), started_at.strftime("%Y-%m-%d %H:%M:%S")),
        )
        return cur.lastrowid


def fetch_sessions(user) -> pd.DataFrame:
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM sessions WHERE user = ? ORDER BY started_at DESC",
            conn, params=(user,), parse_dates=["started_at"],
        )
    if df.empty:
        df = pd.DataFrame(columns=COLUMNS)
        df["started_at"] = pd.to_datetime(df["started_at"])
    df["completed"] = df["completed"].astype(bool)
    return df


def delete_session(user, session_id) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM sessions WHERE id = ? AND user = ?", (int(session_id), user))
        return cur.rowcount > 0


def list_subjects(user) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT subject FROM sessions WHERE user = ? GROUP BY subject ORDER BY MAX(started_at) DESC",
            (user,),
        ).fetchall()
    return [r["subject"] for r in rows]
