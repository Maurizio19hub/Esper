# Creating esper CLI command
import argparse
import sys
from pathlib import Path
import sqlite3

from esper.config import DB_PATH
from esper.db import connect, init_schema
from esper.storage import import_file, get_document
from esper.tags import get_document_by_tag, get_document_tags


def build_parser() -> argparse.ArgumentParser:
    """Define the commands and their arguments."""
    parser = argparse.ArgumentParser(prog="esper", description="Personal document archive.")
    commands = parser.add_subparsers(dest="command", required=True)

    import_cmd = commands.add_parser("import", help="import one or more files")
    import_cmd.add_argument("paths", nargs="+", type=Path, help="files to import")

    list_cmd = commands.add_parser("list", help="list archived documents")
    list_cmd.add_argument("--tag", dest="tags", action="append", default=[], help="only documents with this tag (repeatable)")

    return parser

def main(argv: list[str] | None = None) -> int:
    """Entry point of the `esper` command; return the process exit code."""
    args = build_parser().parse_args(argv)
    conn = connect(DB_PATH)
    init_schema(conn)

    try:
        if args.command == "import":
            return cmd_import(conn, args.paths)
        if args.command == "list":
            return cmd_list(conn, args.tags)
    finally:
        conn.close()

    return 0

def cmd_import(conn: sqlite3.Connection, paths: list[Path]) -> int:
    """Import each path and report what happened; return 1 if any import failed."""
    exit_code = 0
    for path in paths:
        try:
            doc_id, created = import_file(conn, path)
        except FileNotFoundError:
            print(f"error: {path} is not a file", file=sys.stderr)
            exit_code = 1 # at least one file not imported
            continue
        if created:
            print(f"imported #{doc_id} {path.name}")
        else:
            print(f"already present as #{doc_id} {path.name}")
    return exit_code

def format_size(size: int) -> str:
    """Return a human-readable size, e.g. 833 B, 1.5 KiB, 2.1 GiB."""
    for unit in ("B", "KiB", "MiB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GiB"

def cmd_list(conn: sqlite3.Connection, tags: list[str]) -> int:
    """Print one line per document, optionally filtered by tags."""
    documents_ids = get_document_by_tag(conn, tags)
    if not documents_ids:
        print("no documents")
        return 0
    for doc_id in documents_ids:
        doc = get_document(conn, doc_id)
        doc_tags = get_document_tags(conn, doc_id)
        size = format_size(doc["size_bytes"])
        tag_text = f"  [{', '.join(doc_tags)}]" if doc_tags else ""
        print(
            f"#{doc['id']:>4} {doc['original_name']:<30} "
            f"{size:>10} {doc['status']:<10}{tag_text}"
        )
    return 0