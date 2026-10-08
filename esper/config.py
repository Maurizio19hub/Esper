"""Filesystem paths used by Esper."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = DATA_DIR / "esper.db"

FILES_DIR = DATA_DIR / "files"

