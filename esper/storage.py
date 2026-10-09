"""Import files into the Esper archive."""

import hashlib
from pathlib import Path
import mimetypes
import sqlite3
from esper.config import FILES_DIR
import shutil

CHUNK_SIZE = 1024 * 1024 # 1 MiB

def file_sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's content"""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(CHUNK_SIZE):
            digest.update(block)
    return digest.hexdigest()

def guess_mime_type(path: Path) -> str:
    """Return the mime type of the file"""
    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream" # unknown data-type if mime not recognized


def import_file(conn: sqlite3.Connection, src: Path, files_dir: Path = FILES_DIR) -> tuple[int, bool]:
    """Copy a file into the archive and register it; return (document id, created)."""
    if not src.is_file():
        raise FileNotFoundError(src)
    
    sha256 = file_sha256(src)
    
    row = conn.execute("SELECT id FROM documents WHERE sha256 = ?", (sha256,)).fetchone()
    
    if row is not None:
        return row["id"], False # if the file already exists, then return False and the id of the file

    stored_name = sha256 + src.suffix.lower()
    files_dir.mkdir(parents=True, exist_ok=True)
    dest = files_dir / stored_name

    shutil.copyfile(src, dest)

    try:
        with conn:
            cur = conn.execute("INSERT INTO documents (sha256, original_name, mime_type, size_bytes, stored_name) VALUES (?, ?, ?, ?, ?)", (sha256, src.name, guess_mime_type(src), src.stat().st_size, stored_name,))
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    return cur.lastrowid, True
    
