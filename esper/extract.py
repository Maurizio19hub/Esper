"""Extract plain text from archived files."""

import unicodedata
from pathlib import Path

TEXT_MIME_TYPES = ("text/plain", "text/markdown")

class UnsupportedFormatError(Exception):
    """Raised when there is no extractor for a file's MIME type."""

def decode_text(data: bytes) -> str:
    """Decode bytes as UTF-8 (with or without BOM), falling back to Windows-1252."""
    try:
        text = data.decode("utf-8-sig") # decode to remove the BOM in order not to let it finish in the first chunk of the embedding process
    except UnicodeDecodeError:
        text = data.decode("cp1252", errors="replace") # cp1252 contains 5 byte not defined, replacing them we can avoid exceptions
    return text 

def extract_text(path: Path, mime_type: str) -> str:
    """Return the text of a file, with normalized newlines and Unicode form."""
    if mime_type not in TEXT_MIME_TYPES:
        raise UnsupportedFormatError(mime_type)
    text = decode_text(path.read_bytes())
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", text) # NFC better for research with keywords

