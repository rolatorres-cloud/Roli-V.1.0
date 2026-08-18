"""
Capa de base de datos para la cola de contenido.
Cada pieza de contenido pasa por estados:
  draft -> pending_approval -> approved -> scheduled -> published -> failed
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "data" / "content.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,       -- 'video' | 'post'
                platform TEXT NOT NULL,           -- 'instagram' | 'tiktok' | 'facebook' | etc
                topic TEXT,
                caption TEXT,
                script TEXT,
                hashtags TEXT,
                media_path TEXT,
                status TEXT DEFAULT 'draft',
                scheduled_for TEXT,
                created_at TEXT,
                updated_at TEXT,
                meta_json TEXT
            )
        """)


def create_content(content_type, platform, topic, caption, script="", hashtags="", meta=None):
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO content
            (content_type, platform, topic, caption, script, hashtags, status, created_at, updated_at, meta_json)
            VALUES (?, ?, ?, ?, ?, ?, 'draft', ?, ?, ?)
        """, (content_type, platform, topic, caption, script, hashtags, now, now, json.dumps(meta or {})))
        return cur.lastrowid


def update_status(content_id, status, **fields):
    now = datetime.utcnow().isoformat()
    sets = ["status = ?", "updated_at = ?"]
    values = [status, now]
    for k, v in fields.items():
        sets.append(f"{k} = ?")
        values.append(v)
    values.append(content_id)
    with get_conn() as conn:
        conn.execute(f"UPDATE content SET {', '.join(sets)} WHERE id = ?", values)


def get_by_status(status):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM content WHERE status = ? ORDER BY created_at", (status,)).fetchall()
        return [dict(r) for r in rows]


def get_by_id(content_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM content WHERE id = ?", (content_id,)).fetchone()
        return dict(row) if row else None
