"""Paths and settings used by Esper."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = DATA_DIR / "esper.db"

FILES_DIR = DATA_DIR / "files"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_BATCH_SIZE = 8

CHUNK_MAX_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 50

EMBEDDING_DIMENSIONS = 1024

