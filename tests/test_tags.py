"""Tests for esper.tags: normalization, adding, removing and filtering."""

import sqlite3

import pytest

from esper.storage import import_file
from esper.tags import add_tag, get_document_by_tag, get_document_tags, normalize_tag, remove_tag


def count_tags(conn):
    """Return the number of rows in the tags table."""
    return conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]


@pytest.fixture
def two_docs(conn, files_dir, make_file):
    """Two documents: the first tagged [contratti-casa, lavoro], the second [lavoro]."""
    id1, _ = import_file(conn, make_file("a.txt", "Hello world!"), files_dir)
    id2, _ = import_file(conn, make_file("b.md", "Hello mondo!"), files_dir)
    add_tag(conn, id1, "Lavoro")
    add_tag(conn, id1, "contratti casa")
    add_tag(conn, id2, "lavoro")
    return id1, id2


# --- Normalization ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("lavoro", "lavoro"),
        ("LAVORO", "lavoro"),
        ("  Contratti   Casa ", "contratti-casa"),
        ("tab\tseparated", "tab-separated"),
    ],
)
def test_normalize_tag(raw, expected):
    assert normalize_tag(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "\t\n"])
def test_normalize_empty_tag_rejected(raw):
    with pytest.raises(ValueError):
        normalize_tag(raw)


# --- Adding and listing ------------------------------------------------------------


def test_add_tag_returns_normalized_name(conn, files_dir, make_file):
    doc_id, _ = import_file(conn, make_file("a.txt", "x"), files_dir)
    assert add_tag(conn, doc_id, "Contratti Casa") == "contratti-casa"


def test_document_tags_are_sorted(conn, two_docs):
    id1, id2 = two_docs
    assert get_document_tags(conn, id1) == ["contratti-casa", "lavoro"]
    assert get_document_tags(conn, id2) == ["lavoro"]


def test_shared_tag_is_stored_once(conn, two_docs):
    assert count_tags(conn) == 2


def test_adding_same_tag_twice_is_harmless(conn, two_docs):
    id1, _ = two_docs
    add_tag(conn, id1, "LAVORO")
    assert get_document_tags(conn, id1) == ["contratti-casa", "lavoro"]
    assert count_tags(conn) == 2


def test_tag_on_missing_document_rejected(conn, two_docs):
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        add_tag(conn, 999, "x")
    # The whole transaction is rolled back: tag "x" was not created either
    assert count_tags(conn) == 2


def test_document_without_tags(conn, files_dir, make_file):
    doc_id, _ = import_file(conn, make_file("a.txt", "x"), files_dir)
    assert get_document_tags(conn, doc_id) == []


# --- Filtering -------------------------------------------------------------------


def test_filter_one_tag(conn, two_docs):
    id1, id2 = two_docs
    assert get_document_by_tag(conn, ["lavoro"]) == [id1, id2]


def test_filter_two_tags_is_and(conn, two_docs):
    id1, _ = two_docs
    assert get_document_by_tag(conn, ["lavoro", "Contratti Casa"]) == [id1]


def test_filter_ignores_duplicates_after_normalization(conn, two_docs):
    id1, id2 = two_docs
    assert get_document_by_tag(conn, ["lavoro", "LAVORO"]) == [id1, id2]


def test_filter_without_tags_returns_every_document(conn, two_docs, files_dir, make_file):
    id1, id2 = two_docs
    id3, _ = import_file(conn, make_file("c.txt", "untagged"), files_dir)
    assert get_document_by_tag(conn, []) == [id1, id2, id3]


def test_filter_unknown_tag(conn, two_docs):
    assert get_document_by_tag(conn, ["inesistente"]) == []


# --- Removing --------------------------------------------------------------------


def test_remove_tag(conn, two_docs):
    id1, _ = two_docs
    remove_tag(conn, id1, "Contratti Casa")
    assert get_document_tags(conn, id1) == ["lavoro"]


def test_remove_tag_deletes_orphan(conn, two_docs):
    id1, _ = two_docs
    remove_tag(conn, id1, "contratti casa")
    assert count_tags(conn) == 1


def test_remove_shared_tag_keeps_it_for_other_documents(conn, two_docs):
    id1, id2 = two_docs
    remove_tag(conn, id1, "lavoro")
    assert get_document_tags(conn, id2) == ["lavoro"]
    assert count_tags(conn) == 2


def test_remove_missing_tag_is_harmless(conn, two_docs):
    id1, _ = two_docs
    remove_tag(conn, id1, "never-added")
    assert get_document_tags(conn, id1) == ["contratti-casa", "lavoro"]
