import tempfile
from pathlib import Path
from esper.storage import file_sha256, guess_mime_type, import_file
from esper.db import connect, init_schema



with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp / "test.txt").write_text("Hello world!", encoding="utf-8")
    (tmp / "test2.md").write_text("Hello world!", encoding="utf-8")
    (tmp / "test3.md").write_text("Hello world", encoding="utf-8")

    # testing storage
    print("Hash of test.txt: ", file_sha256(tmp / "test.txt"))
    print("Mime type of test.txt: ", guess_mime_type(tmp / "test.txt"))

    print("Hash of test2.md: ", file_sha256(tmp / "test2.md"))
    print("Mime type of test2.md: ", guess_mime_type(tmp / "test2.md"))

    print("Hash of test3.md: ", file_sha256(tmp / "test3.md"))
    print("Mime type of test3.md: ", guess_mime_type(tmp / "test3.md"))

    conn = connect(":memory:")
    init_schema(conn)
    files_dir = tmp / "archive"

    print("test.txt:", import_file(conn, tmp / "test.txt", files_dir))   # expected: (1, True)
    print("test2.md:", import_file(conn, tmp / "test2.md", files_dir))   # expected: (1, False)
    print("test3.md:", import_file(conn, tmp / "test3.md", files_dir))   # expected: (2, True)

    print(sorted(p.name for p in files_dir.iterdir())) # expect to have 2 files

    documents_rows = conn.execute("SELECT id, original_name, mime_type, size_bytes, status FROM documents").fetchall()

    for row in documents_rows:
        print(dict(row))

    try:
        import_file(conn, tmp / "nonexistent.txt", files_dir)
        print("FAIL: missing file accepted")
    except FileNotFoundError as e:
        print("OK missing file rejected")
