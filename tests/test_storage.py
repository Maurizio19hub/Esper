"""Tests for esper.storage: hashing, MIME types, import and deletion."""

from pathlib import Path

import pytest

from esper.storage import delete_document, file_sha256, guess_mime_type, import_file
from esper.tags import add_tag

# SHA-256 of "Hello world!" (well-known value, also given by `sha256sum`)
HELLO_SHA256 = "c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a"


# --- Hashing -------------------------------------------------------------------


def test_sha256_known_value(make_file):
    assert file_sha256(make_file("a.txt", "Hello world!")) == HELLO_SHA256


def test_sha256_ignores_file_name(make_file):
    assert file_sha256(make_file("a.txt", "Hello world!")) == file_sha256(make_file("b.md", "Hello world!"))


def test_sha256_changes_with_content(make_file):
    assert file_sha256(make_file("a.txt", "Hello world!")) != file_sha256(make_file("b.txt", "Hello world"))


def test_sha256_of_file_larger_than_one_block(tmp_path):
    # 3 MiB + 1 byte spans several CHUNK_SIZE blocks
    path = tmp_path / "big.bin"
    data = b"x" * (3 * 1024 * 1024 + 1)
    path.write_bytes(data)
    import hashlib

    assert file_sha256(path) == hashlib.sha256(data).hexdigest()


# --- MIME types ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("nota.txt", "text/plain"),
        ("nota.md", "text/markdown"),
        ("CONTRATTO.PDF", "application/pdf"),
        ("foto.jpg", "image/jpeg"),
        ("foto.png", "image/png"),
        ("senza_estensione", "application/octet-stream"),
    ],
)
def test_guess_mime_type(name, expected):
    assert guess_mime_type(Path(name)) == expected


# --- Import ----------------------------------------------------------------------


def test_import_new_file(conn, files_dir, make_file):
    src = make_file("test.txt", "Hello world!")

    doc_id, created = import_file(conn, src, files_dir)

    assert created is True
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    assert row["sha256"] == HELLO_SHA256
    assert row["original_name"] == "test.txt"
    assert row["mime_type"] == "text/plain"
    assert row["size_bytes"] == 12
    assert row["stored_name"] == f"{HELLO_SHA256}.txt"
    assert row["status"] == "queued"
    assert (files_dir / row["stored_name"]).read_text(encoding="utf-8") == "Hello world!"


def test_import_duplicate_returns_existing_document(conn, files_dir, make_file):
    first_id, _ = import_file(conn, make_file("test.txt", "Hello world!"), files_dir)

    doc_id, created = import_file(conn, make_file("copy.md", "Hello world!"), files_dir)

    assert (doc_id, created) == (first_id, False)
    assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
    assert len(list(files_dir.iterdir())) == 1


def test_import_different_files(conn, files_dir, make_file):
    id1, _ = import_file(conn, make_file("a.txt", "Hello world!"), files_dir)
    id2, created = import_file(conn, make_file("b.md", "Hello world"), files_dir)

    assert created is True
    assert id2 != id1
    assert len(list(files_dir.iterdir())) == 2


def test_import_lowercases_extension(conn, files_dir, make_file):
    doc_id, _ = import_file(conn, make_file("NOTE.TXT", "Hello world!"), files_dir)
    stored_name = conn.execute("SELECT stored_name FROM documents WHERE id = ?", (doc_id,)).fetchone()[0]
    assert stored_name == f"{HELLO_SHA256}.txt"


def test_import_missing_file_rejected(conn, files_dir, tmp_path):
    with pytest.raises(FileNotFoundError):
        import_file(conn, tmp_path / "nonexistent.txt", files_dir)


def test_import_folder_rejected(conn, files_dir, tmp_path):
    with pytest.raises(FileNotFoundError):
        import_file(conn, tmp_path, files_dir)


# --- Deletion --------------------------------------------------------------------


def test_delete_document_removes_row_and_file(conn, files_dir, make_file):
    doc_id, _ = import_file(conn, make_file("test.txt", "Hello world!"), files_dir)

    assert delete_document(conn, doc_id, files_dir) is True

    assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
    assert list(files_dir.iterdir()) == []


def test_delete_missing_document_returns_false(conn, files_dir):
    assert delete_document(conn, 999, files_dir) is False


def test_delete_document_twice(conn, files_dir, make_file):
    doc_id, _ = import_file(conn, make_file("test.txt", "Hello world!"), files_dir)
    delete_document(conn, doc_id, files_dir)
    assert delete_document(conn, doc_id, files_dir) is False


def test_delete_document_with_file_already_gone(conn, files_dir, make_file):
    doc_id, _ = import_file(conn, make_file("test.txt", "Hello world!"), files_dir)
    for path in files_dir.iterdir():
        path.unlink()

    assert delete_document(conn, doc_id, files_dir) is True


def test_delete_document_cleans_up_tags(conn, files_dir, make_file):
    id1, _ = import_file(conn, make_file("a.txt", "one"), files_dir)
    id2, _ = import_file(conn, make_file("b.txt", "two"), files_dir)
    add_tag(conn, id1, "lavoro")
    add_tag(conn, id1, "contratti")
    add_tag(conn, id2, "lavoro")

    delete_document(conn, id1, files_dir)

    tags = [row["name"] for row in conn.execute("SELECT name FROM tags ORDER BY name")]
    assert tags == ["lavoro"]  # "contratti" was orphaned, "lavoro" is still used
    assert conn.execute("SELECT COUNT(*) FROM document_tags").fetchone()[0] == 1
