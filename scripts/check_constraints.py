"""Check that the database constraints work as expected."""

import sqlite3

from esper.db import connect, init_schema

conn = connect(":memory:")
init_schema(conn)

def insert_document(conn, sha256, status="queued"):
    test = conn.execute("INSERT INTO documents (sha256, original_name, mime_type, size_bytes, stored_name, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (sha256, "test.txt", "text/plain", 10, f"{sha256}.txt", status),)

    return test.lastrowid

def insert_tag(conn, name):
    test = conn.execute("INSERT INTO tags (name) "
        "VALUES (?)",
        (name,))

    return test.lastrowid

def tag_document(conn, id_document, id_tag):
    test = conn.execute("INSERT INTO document_tags (document_id, tag_id) "
            "VALUES (?, ?)",
            (id_document, id_tag))
    
    return test.lastrowid


insert_document(conn, "thatsasha256")
try:
    insert_document(conn, "thatsasha256")
    print("FAIL duplicate accepted")
except sqlite3.IntegrityError as e:
    print("OK duplicate rejected: ", e)

try:
    insert_document(conn, "anothersha256", status="notexistentstatus")
    print("FAIL nonexistent status accepted")
except sqlite3.IntegrityError as e:
    print("OK nonexistent status rejected: ", e)

id_document= insert_document(conn, "thirdsha256")
id_tag = insert_tag(conn, "firsttag")

tag_document(conn, id_document, id_tag)

print("Number of connections between documents and tags: ", conn.execute("SELECT COUNT(*) FROM document_tags").fetchone()[0])

conn.execute("DELETE FROM documents WHERE id = ?", (id_document,))
print("Removed the document")

print("Number of connections between documents and tags: ", conn.execute("SELECT COUNT(*) FROM document_tags").fetchone()[0])

try:
    tag_document(conn, "notexistingid", id_tag)
    print("FAIL nonexistent document id accepted")
except sqlite3.IntegrityError as e:
    print("OK nonexistent document id rejected: ", e)