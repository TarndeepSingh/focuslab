"""SQLite persistence layer."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL,
    subject     TEXT    NOT NULL,
    started_at  TEXT    NOT NULL,           -- UTC ISO-8601
    planned_min REAL    NOT NULL CHECK (planned_min > 0),
    actual_min  REAL    NOT NULL CHECK (actual_min >= 0),
    completed   INTEGER NOT NULL CHECK (completed IN (0, 1)),
    notes       TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_start ON sessions (username, started_at);
"""

COLUMNS = ["id", "subject", "started_at", "planned_min", "actual_min", "completed", "notes"]


@contextmanager
def connect(db_path=None):
    path = Path(db_path or config.DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def add_session(username, subject, started_at: datetime, planned_min, actual_min,
                completed, notes="", db_path=None) -> int:
    subject = (subject or "").strip()
    if not username or not subject:
        raise ValueError("username and subject are required")
    if planned_min <= 0 or actual_min < 0:
        raise ValueError("durations must be positive")
    with connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO sessions (username, subject, started_at, planned_min, actual_min, completed, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, subject[:60], started_at.isoformat(), float(planned_min),
             float(actual_min), int(bool(completed)), (notes or "").strip()[:500]),
        )
        return cur.lastrowid


def fetch_sessions(username, db_path=None) -> list[dict]:
    with connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT {', '.join(COLUMNS)} FROM sessions WHERE username = ? ORDER BY started_at DESC",
            (username,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_session(username, session_id, db_path=None) -> bool:
    with connect(db_path) as conn:
        cur = conn.execute("DELETE FROM sessions WHERE id = ? AND username = ?", (session_id, username))
        return cur.rowcount > 0


def get_subjects(username, db_path=None) -> list[str]:
    """Subjects the user has used (most frequent first)."""
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT subject FROM sessions WHERE username = ? GROUP BY subject ORDER BY COUNT(*) DESC",
            (username,),
        ).fetchall()
    return [r["subject"] for r in rows]
