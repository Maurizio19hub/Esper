"""Tests for esper.chunking: sections, units, packing with overlap.

A word counter stands in for the model tokenizer, so the expected chunks are easy to work out by hand.
"""

import random

import pytest

from esper.chunking import chunk_text, overlap_tail, pack_units, split_sections, split_units, split_words


def words(text):
    """Count whitespace-separated words: a predictable stand-in for count_tokens."""
    return len(text.split())


# --- Sections ----------------------------------------------------------------------


def test_text_without_headings_is_one_section():
    assert split_sections("just text\n\nmore text") == ["just text\n\nmore text"]


def test_split_at_headings():
    text = "# A\none\n## B\ntwo\n### C\nthree"
    assert split_sections(text) == ["# A\none", "## B\ntwo", "### C\nthree"]


def test_text_before_first_heading_is_its_own_section():
    assert split_sections("Intro.\n# A\ntext") == ["Intro.", "# A\ntext"]


def test_consecutive_headings_stay_together():
    text = "# Casa\n\n## Affitto\n\n### Contratto\nScade nel 2027.\n\n## Bollette\nLuce e gas."
    assert split_sections(text) == [
        "# Casa\n\n## Affitto\n\n### Contratto\nScade nel 2027.",
        "## Bollette\nLuce e gas.",
    ]


def test_headings_inside_code_blocks_are_ignored():
    text = "# A\n```python\n# a comment\nx = 1\n```\nafter"
    assert split_sections(text) == [text]


def test_code_block_counts_as_body():
    assert split_sections("# A\n```\ncode\n```\n# B\ntext") == ["# A\n```\ncode\n```", "# B\ntext"]


@pytest.mark.parametrize("line", ["#hashtag", "####### seven", "  # indented", "text # not at start"])
def test_lines_that_are_not_headings(line):
    assert split_sections(f"# A\nbody\n{line}") == [f"# A\nbody\n{line}"]


@pytest.mark.parametrize("text", ["", "\n\n", "   \n\t\n"])
def test_empty_text_has_no_sections(text):
    assert split_sections(text) == []


# --- Units -------------------------------------------------------------------------


def test_short_paragraphs_stay_whole():
    assert split_units("one two\n\nthree four five", 5, words) == ["one two", "three four five"]


def test_blank_line_with_spaces_separates_paragraphs():
    assert split_units("one\n  \t\ntwo", 5, words) == ["one", "two"]


def test_paragraphs_are_stripped():
    assert split_units("   indented   \n\n  \nnext  ", 5, words) == ["indented", "next"]


def test_long_paragraph_is_split_into_sentences():
    units = split_units("Uno due tre. Quattro cinque! Sei sette otto?", 4, words)
    assert units == ["Uno due tre.", "Quattro cinque!", "Sei sette otto?"]


def test_long_sentence_is_split_into_words():
    assert split_units("a b c d e f g", 3, words) == ["a b c", "d e f", "g"]


def test_split_words_keeps_an_oversized_word_whole():
    assert split_words("supercalifragilistic", 0, words) == ["supercalifragilistic"]


# --- Overlap -----------------------------------------------------------------------


def test_overlap_takes_whole_sentences_from_the_end():
    assert overlap_tail("Uno due tre. Quattro. Cinque sei.", 3, words) == "Quattro. Cinque sei."


def test_overlap_crosses_paragraphs():
    assert overlap_tail("Uno due.\n\nTre.", 3, words) == "Uno due. Tre."


def test_no_overlap_when_last_sentence_is_too_long():
    assert overlap_tail("Uno. Due tre quattro cinque.", 3, words) == ""


# --- Packing -----------------------------------------------------------------------


def test_units_are_packed_up_to_the_limit():
    assert pack_units(["a b", "c d", "e f"], 4, 0, words) == ["a b\n\nc d", "e f"]


def test_next_chunk_starts_with_overlap():
    assert pack_units(["A b c.", "D e.", "F g h i."], 6, 3, words) == ["A b c.\n\nD e.", "D e.\n\nF g h i."]


def test_overlap_is_dropped_when_it_would_exceed_the_limit():
    assert pack_units(["A b c d.", "E f.", "G h i j k l."], 6, 3, words) == ["A b c d.\n\nE f.", "G h i j k l."]


def test_pack_no_units():
    assert pack_units([], 400, 50, words) == []


# --- chunk_text --------------------------------------------------------------------


def test_short_note_is_one_chunk():
    text = "# Caldaia\nSostituita a novembre.\n\nCosto 2.400 €."
    assert chunk_text(text, 400, 50, words) == [text]


def test_no_overlap_across_sections():
    text = "# A\nUno. Due.\n\nTre quattro.\n# B\nCinque sei."
    chunks = chunk_text(text, 4, 2, words)
    # "Due." is repeated inside section A, but nothing from A leaks into B
    assert chunks == ["# A\nUno. Due.", "Due.\n\nTre quattro.", "# B\nCinque sei."]


def test_empty_text_has_no_chunks():
    assert chunk_text("", 400, 50, words) == []


def random_document(rng):
    """Build a random Markdown document with headings, paragraphs and sentences of varied length."""
    vocab = "casa affitto caldaia costo rate garanzia tecnico bolletta luce gas".split()
    parts = []
    for _ in range(rng.randint(1, 5)):
        parts.append("#" * rng.randint(1, 3) + " Title")
        for _ in range(rng.randint(0, 6)):
            sentences = [
                " ".join(rng.choices(vocab, k=rng.randint(1, 30))).capitalize() + rng.choice(".!?")
                for _ in range(rng.randint(1, 6))
            ]
            parts.append(" ".join(sentences))
    return "\n\n".join(parts)


@pytest.mark.parametrize(("max_tokens", "overlap_tokens"), [(20, 5), (50, 10), (100, 15)])
def test_random_documents_respect_limit_and_lose_nothing(max_tokens, overlap_tokens):
    rng = random.Random(0)  # fixed seed: the same documents on every run
    for _ in range(200):
        text = random_document(rng)
        chunks = chunk_text(text, max_tokens, overlap_tokens, words)
        assert all(words(chunk) <= max_tokens for chunk in chunks)
        # Every word appears in the chunks, in order (overlap only adds repetitions)
        remaining = iter(" ".join(chunks).split())
        assert all(word in remaining for word in text.split())
