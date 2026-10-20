"""Split extracted text into chunks for embedding and keyword search."""

import re
from collections.abc import Callable

HEADING = re.compile(r"#{1,6}\s") # from 1 to 6 # followed by a space, in order to recognise titles and subtitles
PARAGRAPH_BREAK = re.compile(r"\n\s*\n") # empty line
SENTENCE_END = re.compile(r"(?<=[.!?])\s+") # point that follows one of the character i the []

def has_body(lines: list[str]) -> bool:
    """Return True if the lines contain text other than headings and blank lines."""
    return any(line.strip() and not HEADING.match(line) for line in lines)

def split_sections(text: str) -> list[str]:
    """Split Markdown text before each heading, ignoring headings inside code blocks."""
    sections: list[list[str]] = [[]] # list of sections, where every section is a list of lines
    in_code = False
    for line in text.split("\n"):
        if line.startswith("```"): # recognice the fact that we have a code section so the # means a comment maybe instead of beeing a title or subtitle
            in_code = not in_code
        elif not in_code and HEADING.match(line) and has_body(sections[-1]): # search the pattern onli at the beginning of the line
            sections.append([])
        sections[-1].append(line)
    
    result = []
    for lines in sections:
        section = "\n".join(lines).strip()
        if section:
            result.append(section)
    return result

def split_words(text: str, max_tokens: int, count_tokens: Callable[[str], int]) -> list[str]:
    """Split text into consecutive groups of words, each within max_tokens."""
    pieces: list[str] = []
    current: list[str] = []
    for word in text.split():
        if current and count_tokens(" ".join(current + [word])) > max_tokens:
            pieces.append(" ".join(current))
            current = []
        current.append(word)
    if current:
        pieces.append(" ".join(current))
    return pieces

def split_units(section: str, max_tokens: int, count_tokens: Callable[[str], int]) -> list[str]:
    """Split a section into paragraphs, breaking those above max_tokens into sentences or words."""
    units: list[str] = []
    for paragraph in PARAGRAPH_BREAK.split(section):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if count_tokens(paragraph) <= max_tokens:
            units.append(paragraph)
            continue
        for sentence in SENTENCE_END.split(paragraph):
            if count_tokens(sentence) <= max_tokens:
                units.append(sentence)
            else:
                units.extend(split_words(sentence, max_tokens, count_tokens))
    return units

def overlap_tail(chunk: str, overlap_tokens: int, count_tokens: Callable[[str], int]) -> str:
    """Return the last whole sentences of a chunk within overlap_tokens, or "" if none fits."""
    tail: list[str] = []
    for sentence in reversed(SENTENCE_END.split(chunk)):
        if count_tokens(" ".join([sentence] + tail)) > overlap_tokens:
            break
        tail.insert(0, sentence)
    return " ".join(tail)

def pack_units(units: list[str], max_tokens: int, overlap_tokens: int, count_tokens: Callable[[str], int]) -> list[str]:
    """Group consecutive units into chunks within max_tokens, each starting with the tail of the previous one."""
    chunks: list[str] = []
    current: list[str] = []
    for unit in units:
        if current and count_tokens("\n\n".join(current + [unit])) > max_tokens:
            chunk = "\n\n".join(current)
            chunks.append(chunk)
            tail = overlap_tail(chunk, overlap_tokens, count_tokens)
            current = [tail] if tail else []
            if current and count_tokens("\n\n".join(current + [unit])) > max_tokens:
                current = []
        current.append(unit)
    if current:
        chunks.append("\n\n".join(current))
    return chunks

def chunk_text(text: str, max_tokens: int, overlap_tokens: int, count_tokens: Callable[[str], int]) -> list[str]:
    """Split text into chunks: sections, then units, then packed chunks with overlap."""
    chunks: list[str] = []
    for section in split_sections(text):
        units = split_units(section, max_tokens, count_tokens)
        chunks.extend(pack_units(units, max_tokens, overlap_tokens, count_tokens))
    return chunks