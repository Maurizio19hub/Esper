from esper.db import connect, init_schema
from esper.storage import delete_document, import_file
import tempfile
from pathlib import Path
from esper.tags import add_tag, get_document_by_tag, get_document_tags, normalize_tag, remove_tag
import sqlite3


def check(label, actual, expected):
    """Print OK or FAIL depending on whether actual matches expected."""
    status = "OK  " if actual == expected else "FAIL"
    print(f"{status} {label}: got {actual!r}, expected {expected!r}")


def count_tags(conn):
    """Return the number of rows in the tags table."""
    return conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]

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
        print("OK impossible to insert a tag for a non existing document: ", e)

    # Filtering: document 1 has [contratti-casa, lavoro], document 2 has [lavoro]
    print("\n--- Filtering by tags ---")
    check("one tag", get_document_by_tag(conn, ["lavoro"]), [id1, id2])
    check("two tags (AND, normalized)", get_document_by_tag(conn, ["lavoro", "Contratti Casa"]), [id1])
    check("duplicate tags after normalization", get_document_by_tag(conn, ["lavoro", "LAVORO"]), [id1, id2])
    check("no tags returns every document", get_document_by_tag(conn, []), [id1, id2])
    check("unknown tag", get_document_by_tag(conn, ["inesistente"]), [])

    # Removing a tag: contratti-casa was used only by document 1, so it becomes orphan
    print("\n--- Removing tags ---")
    remove_tag(conn, id1, "contratti casa")
    check("document 1 tags after removal", get_document_tags(conn, id1), ["lavoro"])
    check("orphan tag deleted", count_tags(conn), 1)
    remove_tag(conn, id1, "never-added")  # removing a missing tag must not fail
    check("removing a missing tag changes nothing", get_document_tags(conn, id1), ["lavoro"])

    # Deleting documents: rows, tag links, orphan tags and files must all go away
    print("\n--- Deleting documents ---")
    check("delete document 1", delete_document(conn, id1, files_dir), True)
    check("files left in the archive", len(list(files_dir.iterdir())), 1)
    check("filter after deletion", get_document_by_tag(conn, ["lavoro"]), [id2])
    check("lavoro still used by document 2", count_tags(conn), 1)
    check("delete document 1 again", delete_document(conn, id1, files_dir), False)
    check("delete document 2", delete_document(conn, id2, files_dir), True)
    check("no tags left", count_tags(conn), 0)
    check("no files left", list(files_dir.iterdir()), [])
    check("no tag links left", conn.execute("SELECT COUNT(*) FROM document_tags").fetchone()[0], 0)
    
