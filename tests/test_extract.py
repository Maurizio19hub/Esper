"""Tests for esper.extract: decoding, newline and Unicode normalization."""

import pytest

from esper.extract import UnsupportedFormatError, decode_text, extract_text

TEXT = "Perché il caffè costa 2 €?"


@pytest.fixture
def write_bytes(tmp_path):
    """Return a function that writes raw bytes to a temporary file and returns its path."""

    def _write_bytes(name, data):
        path = tmp_path / name
        path.write_bytes(data)
        return path

    return _write_bytes


# --- Decoding ----------------------------------------------------------------------


def test_decode_utf8():
    assert decode_text(TEXT.encode("utf-8")) == TEXT


def test_decode_utf8_strips_bom():
    data = TEXT.encode("utf-8-sig")
    assert data.startswith(b"\xef\xbb\xbf")
    assert decode_text(data) == TEXT


def test_decode_falls_back_to_cp1252():
    data = TEXT.encode("cp1252")
    assert data != TEXT.encode("utf-8")  # one byte per accented letter and for €
    assert decode_text(data) == TEXT


def test_decode_cp1252_undefined_byte_is_replaced():
    # 0x81 is undefined in cp1252 and invalid as a UTF-8 start byte
    assert decode_text(b"caff\xe8 \x81") == "caffè �"


def test_decode_ascii():
    assert decode_text(b"plain ascii") == "plain ascii"


def test_decode_empty():
    assert decode_text(b"") == ""


# --- Extraction --------------------------------------------------------------------


@pytest.mark.parametrize("mime_type", ["text/plain", "text/markdown"])
def test_extract_text_files(write_bytes, mime_type):
    path = write_bytes("note", TEXT.encode("utf-8"))
    assert extract_text(path, mime_type) == TEXT


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (b"one\r\ntwo", "one\ntwo"),  # Windows
        (b"one\rtwo", "one\ntwo"),  # old Mac
        (b"one\ntwo", "one\ntwo"),  # Unix, unchanged
        (b"one\r\n\r\ntwo", "one\n\ntwo"),  # a blank line stays one blank line
    ],
)
def test_extract_normalizes_newlines(write_bytes, raw, expected):
    assert extract_text(write_bytes("note.txt", raw), "text/plain") == expected


def test_extract_keeps_the_letter_r(write_bytes):
    text = "ricerca, carattere, errore"
    assert extract_text(write_bytes("note.txt", text.encode("utf-8")), "text/plain") == text


def test_extract_composes_accents(write_bytes):
    decomposed = "perché"  # "e" followed by a combining acute accent
    result = extract_text(write_bytes("note.txt", decomposed.encode("utf-8")), "text/plain")
    assert result == "perché"
    assert len(result) == 6


def test_extract_keeps_markdown_syntax(write_bytes):
    text = "# Title\n\nSome **bold** text.\n\n## Section\n\n- item"
    assert extract_text(write_bytes("note.md", text.encode("utf-8")), "text/markdown") == text


def test_extract_windows_file_end_to_end(write_bytes):
    # Old Notepad file: cp1252 and CRLF
    path = write_bytes("old.txt", "Caffè\r\n2 €".encode("cp1252"))
    assert extract_text(path, "text/plain") == "Caffè\n2 €"


@pytest.mark.parametrize("mime_type", ["application/pdf", "image/png", "application/octet-stream"])
def test_extract_unsupported_type(write_bytes, mime_type):
    path = write_bytes("file.bin", b"\x00\x01")
    with pytest.raises(UnsupportedFormatError, match=mime_type):
        extract_text(path, mime_type)
