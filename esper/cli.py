# Creating esper CLI command
import argparse
import sys
from pathlib import Path
import sqlite3

from esper.config import DB_PATH
from esper.db import connect, init_schema
from esper.storage import import_file


def build_parser() -> argparse.ArgumentParser:
    """Define the commands and their arguments."""
    parser = argparse.ArgumentParser(prog="esper", description="Personal document archive.")
    commands = parser.add_subparsers(dest="command", required=True)

    import_cmd = commands.add_parser("import", help="import one or more files")
    import_cmd.add_argument("paths", nargs="+", type=Path, help="files to import")

    return parser

def main(argv: list[str] | None = None) -> int:
    """Entry point of the `esper` command; return the process exit code."""
    args = build_parser().parse_args(argv)
    conn = connect(DB_PATH)
    init_schema(conn)

    try:
        if args.command == "import":
            return cmd_import(conn, args.paths)
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

