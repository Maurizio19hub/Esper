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

def get_document_by_tag(conn: sqlite3.Connection, tag_names: list[str]) -> list[int]:
    """Filters documents by tag."""
    tag_names = sorted({normalize_tag(tag) for tag in tag_names})
    placeholders = ", ".join("?" * len(tag_names))
    if not tag_names:
        rows = conn.execute("SELECT id FROM documents ORDER BY id").fetchall()
        return [row["id"] for row in rows]
    rows = conn.execute("SELECT dt.document_id "
                        "FROM document_tags AS dt "
                        "JOIN tags AS t ON t.id = dt.tag_id "
                        f"WHERE t.name IN ({placeholders}) "
                        "GROUP BY dt.document_id "
                        "HAVING COUNT(*) = ? "
                        "ORDER BY dt.document_id", 
                        (*tag_names,len(tag_names),)
                        ).fetchall()
    return [row["document_id"] for row in rows]

def delete_unused_tags(conn: sqlite3.Connection) -> None:
    """Delete tags that are no longer attached to any document."""
    conn.execute("DELETE FROM tags WHERE id NOT IN (SELECT tag_id FROM document_tags)")

def remove_tag(conn: sqlite3.Connection, document_id: int, tag_name: str) -> None:
    """Detach a tag from a document and drop the tag if it is no longer used."""
    tag_name = normalize_tag(tag_name)
    with conn:
        conn.execute("DELETE FROM document_tags WHERE document_id = ? AND tag_id IN (SELECT id FROM tags WHERE name = ?)", (document_id, tag_name,))
        delete_unused_tags(conn)
