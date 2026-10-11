"""Tests for esper.db: connection settings, schema and constraints."""

import sqlite3

import pytest

from esper.db import connect, init_schema


def insert_document(conn, sha256, status="queued"):
    """Insert a minimal document row and return its id."""
    cur = conn.execute(
        "INSERT INTO documents (sha256, original_name, mime_type, size_bytes, stored_name, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (sha256, "test.txt", "text/plain", 10, f"{sha256}.txt", status),
    )
    return cur.lastrowid


def insert_tag(conn, name):
    """Insert a tag row and return its id."""
    return conn.execute("INSERT INTO tags (name) VALUES (?)", (name,)).lastrowid


# --- Connection settings ---------------------------------------------------


def test_connect_creates_missing_folder(tmp_path):
    db_path = tmp_path / "nested" / "esper.db"
    conn = connect(db_path)
    conn.close()
    assert db_path.is_file()


def test_pragmas(tmp_path):
    # WAL only applies to on-disk databases, so use a real file here
    conn = connect(tmp_path / "esper.db")
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    conn.close()


def test_rows_are_accessible_by_name(conn):
    row = conn.execute("SELECT 1 AS answer").fetchone()
    assert row["answer"] == 1


# --- Schema ------------------------------------------------------------------


def test_init_schema_is_idempotent(conn):
    # The fixture already called it once
    init_schema(conn)
    init_schema(conn)


def test_tables_exist(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    assert {row["name"] for row in rows} == {"documents", "tags", "document_tags"}


def test_tag_index_exists(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'").fetchall()
    assert "idx_document_tags_tag" in {row["name"] for row in rows}


def test_document_defaults(conn):
    doc_id = conn.execute(
        "INSERT INTO documents (sha256, original_name, mime_type, size_bytes, stored_name) "
        "VALUES ('abc', 'a.txt', 'text/plain', 1, 'abc.txt')"
    ).lastrowid
    row = conn.execute("SELECT status, error, created_at FROM documents WHERE id = ?", (doc_id,)).fetchone()
    assert row["status"] == "queued"
    assert row["error"] is None
    # ISO 8601 UTC, e.g. 2026-10-11T14:32:05.123Z
    assert row["created_at"].endswith("Z") and "T" in row["created_at"]


# --- Constraints ---------------------------------------------------------------


def test_duplicate_sha256_rejected(conn):
    insert_document(conn, "aaa")
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        insert_document(conn, "aaa")


def test_invalid_status_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        insert_document(conn, "bbb", status="notexistentstatus")


def test_duplicate_tag_name_rejected(conn):
    insert_tag(conn, "lavoro")
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        insert_tag(conn, "lavoro")


def test_tag_link_to_missing_document_rejected(conn):
    tag_id = insert_tag(conn, "lavoro")
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        conn.execute("INSERT INTO document_tags (document_id, tag_id) VALUES (?, ?)", (999, tag_id))


def test_deleting_document_cascades_to_tag_links(conn):
    doc_id = insert_document(conn, "ccc")
    tag_id = insert_tag(conn, "lavoro")
    conn.execute("INSERT INTO document_tags (document_id, tag_id) VALUES (?, ?)", (doc_id, tag_id))

    conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

    assert conn.execute("SELECT COUNT(*) FROM document_tags").fetchone()[0] == 0
