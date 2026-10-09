"""Tag management for documents."""
import sqlite3

def normalize_tag(name: str) -> str:
    """Lowercase a tag name and replace runs of whitespace with a single hyphen."""
    normalized = "-".join(name.lower().split())
    if not normalized:
        raise ValueError("Tag name cannot be empty")
    return normalized

def add_tag(conn: sqlite3.Connection, document_id: int, name: str) -> str:
    """Attach a tag to a document, creating the tag if needed; return the normalized name."""
    name = normalize_tag(name)
    with conn: # commands executed in a single transaction
        conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
        tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()["id"]
        conn.execute("INSERT OR IGNORE INTO document_tags (document_id, tag_id) VALUES (?, ?)", (document_id, tag_id,))
    return name

def get_document_tags(conn: sqlite3.Connection, document_id: int) -> list[str]:
    """Return the tag names of a document, sorted alphabetically."""
    rows = conn.execute("SELECT t.name FROM tags AS t "
                        "JOIN document_tags AS dt ON dt.tag_id = t.id "
                        "WHERE dt.document_id = ? "
                        "ORDER BY t.name ", 
                        (document_id,)).fetchall()
    return [row["name"] for row in rows]