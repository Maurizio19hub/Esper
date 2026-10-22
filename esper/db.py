"""Open a SQLite connection with the project's standard settings."""

import sqlite3
from pathlib import Path
import sqlite_vec
from esper.config import EMBEDDING_DIMENSIONS

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS documents (
    id            INTEGER PRIMARY KEY,
    sha256        TEXT    NOT NULL UNIQUE,
    original_name TEXT    NOT NULL,
    mime_type     TEXT    NOT NULL,
    size_bytes    INTEGER NOT NULL,
    stored_name   TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'queued'
                  CHECK (status IN ('queued', 'processing', 'indexed', 'error')),
    error         TEXT,
    created_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY,
    name TEXT    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS document_tags (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tags(id)      ON DELETE CASCADE,
    PRIMARY KEY (document_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_document_tags_tag ON document_tags(tag_id);

CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    position    INTEGER NOT NULL,
    text        TEXT    NOT NULL,
    UNIQUE (document_id, position)
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5 (
    text,
    tokenize = 'unicode61 remove_diacritics 2'
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0 (
    embedding float[{EMBEDDING_DIMENSIONS}] distance_metric=cosine
);

CREATE TRIGGER IF NOT EXISTS chunks_after_delete AFTER DELETE ON chunks
BEGIN 
    DELETE FROM chunks_fts WHERE rowid = old.id;
    DELETE FROM chunks_vec WHERE rowid = old.id;
END;
"""

def connect(db_path: Path | str) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.row_factory = sqlite3.Row

    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL') # changes are first written to a log file and later copied to the main file
    conn.execute('PRAGMA busy_timeout = 5000')


    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create tables and indexes if they do not exist."""
    conn.executescript(SCHEMA)