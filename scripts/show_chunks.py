"""Show how Esper splits a file into chunks, with the token count of each chunk.

A developer tool to look at real chunks and try other sizes before changing config.py:

    uv run python scripts/show_chunks.py notes.md
    uv run python scripts/show_chunks.py notes.md --max-tokens 250 --overlap 30
"""

import argparse
import statistics
from pathlib import Path

from esper.chunking import chunk_text
from esper.config import CHUNK_MAX_TOKENS, CHUNK_OVERLAP_TOKENS
from esper.embedding import Embedder
from esper.extract import UnsupportedFormatError, extract_text
from esper.storage import guess_mime_type


def main() -> None:
    parser = argparse.ArgumentParser(description="Show the chunks Esper would create for a file.")
    parser.add_argument("path", type=Path, help="a .txt or .md file")
    parser.add_argument("--max-tokens", type=int, default=CHUNK_MAX_TOKENS, help=f"default: {CHUNK_MAX_TOKENS}")
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP_TOKENS, help=f"default: {CHUNK_OVERLAP_TOKENS}")
    args = parser.parse_args()

    if not args.path.is_file():
        parser.error(f"{args.path} is not a file")
    try:
        text = extract_text(args.path, guess_mime_type(args.path))
    except UnsupportedFormatError as exc:
        parser.error(f"unsupported file type: {exc}")

    # Only the tokenizer is needed here, but it comes with the model (a few seconds to load)
    embedder = Embedder()
    chunks = chunk_text(text, args.max_tokens, args.overlap, embedder.count_tokens)
    sizes = [embedder.count_tokens(chunk) for chunk in chunks]

    for number, (chunk, size) in enumerate(zip(chunks, sizes), start=1):
        print(f"\n─── chunk {number}/{len(chunks)} · {size} tokens " + "─" * 30)
        print(chunk)

    print(f"\n{args.path.name}: {len(text)} characters → {len(chunks)} chunks "
          f"(max {args.max_tokens} tokens, overlap {args.overlap})")
    if sizes:
        print(f"tokens per chunk: min {min(sizes)}, mean {statistics.mean(sizes):.0f}, max {max(sizes)}")


if __name__ == "__main__":
    main()
