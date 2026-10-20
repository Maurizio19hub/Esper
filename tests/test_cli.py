"""Tests for esper.cli: argument parsing, commands, output and exit codes."""

from functools import partial

import pytest

from esper import cli
from esper.db import connect
from esper.storage import delete_document, import_file


@pytest.fixture
def db_path(tmp_path, files_dir, monkeypatch):
    """Point the CLI at a temporary database and archive, so tests never touch data/."""
    db_path = tmp_path / "esper.db"
    monkeypatch.setattr(cli, "DB_PATH", db_path)
    # files_dir defaults are bound when storage.py is loaded, so patch the functions the CLI calls
    monkeypatch.setattr(cli, "import_file", partial(import_file, files_dir=files_dir))
    monkeypatch.setattr(cli, "delete_document", partial(delete_document, files_dir=files_dir))
    return db_path


@pytest.fixture
def run(db_path, capsys):
    """Return a function that runs the CLI and returns (exit code, stdout, stderr)."""

    def _run(*argv):
        exit_code = cli.main(list(argv))
        out, err = capsys.readouterr()
        return exit_code, out, err

    return _run


@pytest.fixture
def two_docs(run, make_file):
    """Import a.txt as #1 and b.md as #2."""
    run("import", str(make_file("a.txt", "Hello world!")), str(make_file("b.md", "Hello mondo!")))


def answer(monkeypatch, text):
    """Make input() return the given text, as if the user had typed it."""
    monkeypatch.setattr("builtins.input", lambda prompt: text)


def count_documents(db_path):
    """Return the number of documents in the database."""
    conn = connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    finally:
        conn.close()


# --- Argument parsing --------------------------------------------------------------


def test_missing_command_is_an_error(run):
    with pytest.raises(SystemExit) as exc:
        run()
    assert exc.value.code == 2


def test_unknown_command_is_an_error(run):
    with pytest.raises(SystemExit) as exc:
        run("explode")
    assert exc.value.code == 2


@pytest.mark.parametrize("command", ["tag", "untag", "delete"])
def test_document_id_must_be_an_integer(run, command):
    with pytest.raises(SystemExit) as exc:
        run(command, "abc", "x")
    assert exc.value.code == 2


def test_first_run_creates_the_database(run, db_path):
    run("list")
    assert db_path.is_file()


# --- import ------------------------------------------------------------------------


def test_import_new_file(run, make_file, files_dir):
    exit_code, out, _ = run("import", str(make_file("a.txt", "Hello world!")))
    assert exit_code == 0
    assert out == "imported #1 a.txt\n"
    assert len(list(files_dir.iterdir())) == 1


def test_import_duplicate(run, make_file, db_path):
    run("import", str(make_file("a.txt", "Hello world!")))
    exit_code, out, _ = run("import", str(make_file("copy.md", "Hello world!")))
    assert exit_code == 0
    assert out == "already present as #1 copy.md\n"
    assert count_documents(db_path) == 1


def test_import_missing_file_does_not_stop_the_others(run, make_file, tmp_path, db_path):
    missing = tmp_path / "missing.txt"
    exit_code, out, err = run("import", str(missing), str(make_file("a.txt", "Hello world!")))
    assert exit_code == 1
    assert err == f"error: {missing} is not a file\n"
    assert out == "imported #1 a.txt\n"
    assert count_documents(db_path) == 1


# --- list --------------------------------------------------------------------------


def test_list_empty_archive(run):
    assert run("list") == (0, "no documents\n", "")


def test_list_shows_name_size_status_and_tags(run, two_docs):
    run("tag", "1", "lavoro", "casa")
    exit_code, out, _ = run("list")
    assert exit_code == 0
    first, second = out.splitlines()
    assert first.split() == ["#", "1", "a.txt", "12", "B", "queued", "[casa,", "lavoro]"]
    assert second.split() == ["#", "2", "b.md", "12", "B", "queued"]


def test_list_filters_by_tag(run, two_docs):
    run("tag", "1", "lavoro", "casa")
    run("tag", "2", "lavoro")
    _, out, _ = run("list", "--tag", "LAVORO")
    assert len(out.splitlines()) == 2
    _, out, _ = run("list", "--tag", "lavoro", "--tag", "casa")
    assert len(out.splitlines()) == 1 and "a.txt" in out


def test_list_unknown_tag(run, two_docs):
    assert run("list", "--tag", "nonexistent") == (0, "no documents\n", "")


def test_list_empty_tag_is_an_error(run):
    assert run("list", "--tag", "  ") == (1, "", "error: Tag name cannot be empty\n")


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (0, "0 B"),
        (833, "833 B"),
        (1023, "1023 B"),
        (1024, "1.0 KiB"),
        (1536, "1.5 KiB"),
        (1024**2, "1.0 MiB"),
        (int(2.5 * 1024**3), "2.5 GiB"),
        (3 * 1024**4, "3072.0 GiB"),
    ],
)
def test_format_size(size, expected):
    assert cli.format_size(size) == expected


# --- tag / untag -------------------------------------------------------------------


def test_tag_normalizes_and_prints_current_tags(run, two_docs):
    assert run("tag", "1", "Lavoro", "contratti casa") == (0, "#1 [contratti-casa, lavoro]\n", "")


def test_tag_missing_document(run):
    assert run("tag", "99", "x") == (1, "", "error: no document #99\n")


def test_tag_with_an_empty_name_adds_nothing(run, two_docs):
    exit_code, _, err = run("tag", "1", "ok", "  ")
    assert exit_code == 1
    assert err == "error: Tag name cannot be empty\n"
    assert run("untag", "1", "never-added")[1] == "#1 no tags\n"


def test_untag_removes_and_ignores_missing_tags(run, two_docs):
    run("tag", "1", "lavoro", "casa")
    assert run("untag", "1", "LAVORO", "never-added") == (0, "#1 [casa]\n", "")


def test_untag_last_tag(run, two_docs):
    run("tag", "1", "lavoro")
    assert run("untag", "1", "lavoro") == (0, "#1 no tags\n", "")


def test_untag_missing_document(run):
    assert run("untag", "99", "x") == (1, "", "error: no document #99\n")


def test_untag_with_an_empty_name_removes_nothing(run, two_docs):
    run("tag", "1", "lavoro")
    assert run("untag", "1", "lavoro", "  ")[0] == 1
    assert run("tag", "1", "lavoro")[1] == "#1 [lavoro]\n"


# --- delete ------------------------------------------------------------------------


def test_delete_with_yes_flag(run, two_docs, files_dir, db_path, monkeypatch):
    # -y must never ask: a call to input() would fail the test
    monkeypatch.setattr("builtins.input", lambda prompt: pytest.fail("input() was called"))
    exit_code, out, err = run("delete", "1", "-y")
    assert (exit_code, out, err) == (0, "deleted document #1 [a.txt]\n", "")
    assert count_documents(db_path) == 1
    assert len(list(files_dir.iterdir())) == 1


@pytest.mark.parametrize("text", ["y", "Y", " y "])
def test_delete_confirmed(run, two_docs, db_path, monkeypatch, text):
    answer(monkeypatch, text)
    exit_code, out, _ = run("delete", "1")
    assert exit_code == 0
    assert "deleted document #1 [a.txt]" in out
    assert count_documents(db_path) == 1


@pytest.mark.parametrize("text", ["", "n", "yes", "no"])
def test_delete_not_confirmed(run, two_docs, db_path, monkeypatch, text):
    answer(monkeypatch, text)
    assert run("delete", "1") == (0, "skipped\n", "")
    assert count_documents(db_path) == 2


def test_delete_prompt_shows_the_document_name(run, two_docs, monkeypatch):
    prompts = []
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "n")
    run("delete", "2")
    assert prompts == ["delete document #2 [b.md]? [y/N] "]


def test_delete_missing_document_does_not_stop_the_others(run, two_docs, db_path):
    exit_code, out, err = run("delete", "99", "1", "-y")
    assert exit_code == 1
    assert err == "error: no document #99\n"
    assert out == "deleted document #1 [a.txt]\n"
    assert count_documents(db_path) == 1
