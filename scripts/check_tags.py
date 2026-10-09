from esper.db import connect, init_schema
from esper.storage import import_file
import tempfile
from pathlib import Path
from esper.tags import normalize_tag, add_tag, get_document_tags
import sqlite3

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    conn = connect(":memory:")
    init_schema(conn)

    (tmp / "test.txt").write_text("Hello world!", encoding="utf-8")
    (tmp / "test2.md").write_text("Hello mondo!", encoding="utf-8")

    files_dir = tmp / "archive"

    id1, _ = import_file(conn, tmp / "test.txt", files_dir)
    id2, _ = import_file(conn, tmp / "test2.md", files_dir)


    print(normalize_tag("  Contratti   Casa"))
    try:
        print(normalize_tag("     ")) 
    except ValueError as e:
        print("Empty string is not valid: ", e)

    add_tag(conn, id1, "LAVORO")
    add_tag(conn, id1, "CONTRATTI CASA")
    add_tag(conn, id2, "LAVORO")

    add_tag(conn, id1, "LAVORO") # should not give error

    print(get_document_tags(conn, id1), get_document_tags(conn, id2))

    print("Total number of tags: ", conn.execute("SELECT COUNT (*) FROM tags").fetchone()[0])

    try:
        add_tag(conn, 999, "x")
        print("ERROR bad insert of tag on non existing document")
    except sqlite3.IntegrityError as e:
        print("OK impossible to insert a tag for a non ecisting document: ", e)
    
