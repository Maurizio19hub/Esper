"""Tests for esper.config."""

from esper.config import DATA_DIR, DB_PATH, FILES_DIR, PROJECT_ROOT


def test_paths_are_absolute():
    for path in (PROJECT_ROOT, DATA_DIR, DB_PATH, FILES_DIR):
        assert path.is_absolute()


def test_paths_live_inside_the_project():
    assert (PROJECT_ROOT / "esper" / "config.py").is_file()
    assert DATA_DIR == PROJECT_ROOT / "data"
    assert DB_PATH.parent == DATA_DIR
    assert FILES_DIR.parent == DATA_DIR
