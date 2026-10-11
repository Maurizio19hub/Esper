"""Shared pytest fixtures."""

import pytest

from esper.db import connect, init_schema


@pytest.fixture
def conn():
    """Fresh in-memory database with the schema, for each test."""
    conn = connect(":memory:")
    init_schema(conn)
    yield conn
    conn.close()


@pytest.fixture
def files_dir(tmp_path):
    """Temporary archive folder, so tests never touch data/files/."""
    return tmp_path / "archive"


@pytest.fixture
def make_file(tmp_path):
    """Return a function that writes a text file in a temporary folder and returns its path."""

    def _make_file(name, content):
        path = tmp_path / "source" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    return _make_file
