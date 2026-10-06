"""SQLite connection handling and schema."""
import sqlite3
from contextlib import contextmanager

from focuslab import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user        TEXT    NOT NULL,
    subject     TEXT    NOT NULL,
    planned_min REAL    NOT NULL CHECK (planned_min > 0),
    actual_min  REAL    NOT NULL CHECK (actual_min >= 0),
    completed   INTEGER NOT NULL CHECK (completed IN (0, 1)),
    notes       TEXT    DEFAULT '',
    started_at  TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_time ON sessions(user, started_at);
"""


@contextmanager
def get_conn():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)
