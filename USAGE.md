# Using Esper

Esper is still a work in progress. This page lists what you can do **today** from the command line, and grows with the project.

| Available now | Coming next |
|---|---|
| Import files, list them, tag them, delete them | Text extraction and indexing, then `esper search "..."` |

## Requirements

- Linux or macOS
- [uv](https://docs.astral.sh/uv/), the Python package manager. It also downloads the right Python version (3.12) by itself.

Esper runs on the CPU: no GPU is needed.

## Installation

```bash
git clone https://github.com/Maurizio19hub/Esper.git
cd Esper
uv sync
```

`uv sync` creates the virtual environment in `.venv/`, installs the dependencies (PyTorch is the CPU-only build) and installs the `esper` command.

Every command below is run through `uv run`, which uses the project environment without activating it:

```bash
uv run esper --help
```

## Where your data lives

Everything Esper stores is in the `data/` folder of the project, which is never committed to git:

| Path | Content |
|---|---|
| `data/esper.db` | SQLite database: documents, tags and their links |
| `data/files/` | A copy of every imported file, named after the SHA-256 of its content |

Both are created automatically the first time you run a command. Importing a file **copies** it: the original stays where it is, and you can move or delete it afterwards.

## Commands

### `import`: add files to the archive

```bash
uv run esper import notes.md contract.txt
```
```
imported #1 notes.md
imported #2 contract.txt
```

- Accepts one or more files.
- **Duplicates are detected by content, not by name.** Importing the same content again, even under a different name, does not create a second copy:
  ```
  already present as #1 notes-copy.md
  ```
- A path that is not a file is reported as an error, and the other files are imported anyway.

### `list`: show the archive

```bash
uv run esper list
```
```
#   1 notes.md                            1.2 KiB queued      [home, work]
#   2 contract.txt                          833 B queued
```

The columns are the document number, the original name, the size, the processing status and the tags.

The status is one of:

| Status | Meaning |
|---|---|
| `queued` | imported, waiting to be indexed |
| `processing` | being indexed |
| `indexed` | ready to be searched |
| `error` | indexing failed |

Indexing is not implemented yet, so for now every document stays `queued`.

To show only the documents that have **all** the given tags, filter with `--tag`. The option can be repeated:

```bash
uv run esper list --tag work
uv run esper list --tag work --tag home
```

### `tag` / `untag`: organize with tags

```bash
uv run esper tag 1 work "house contract"
```
```
#1 [house-contract, work]
```
```bash
uv run esper untag 1 work
```
```
#1 [house-contract]
```

- The first argument is the document number shown by `list`, followed by one or more tags.
- **Tag names are normalized**: lowercase, with spaces replaced by hyphens. `Work`, `WORK` and `work` are the same tag, and `"house contract"` becomes `house-contract`. Use quotes for tags with spaces.
- After every change the command prints the current tags of the document.
- Removing a tag the document does not have is not an error.
- A tag that no document uses anymore is deleted automatically.

### `delete`: remove documents

```bash
uv run esper delete 2
```
```
delete document #2 [contract.txt]? [y/N] y
deleted document #2 [contract.txt]
```

- This removes the database entry, the tags that are no longer used and the copy in `data/files/`. **It cannot be undone**, but the original file you imported from is not touched.
- The default answer is **no**: anything other than `y`, including just pressing Enter, skips the document.
- Add `-y` (or `--yes`) to skip the confirmation, for example in scripts:
  ```bash
  uv run esper delete 2 3 -y
  ```
- Document numbers can be reused: after deleting the document with the highest number, the next import gets that number again. Always check with `list` before deleting.

### Exit codes

Every command follows the usual convention, so it can be used in scripts (`esper import x.md && echo done`):

| Code | Meaning |
|---|---|
| `0` | success |
| `1` | at least one operation failed (missing file, unknown document, empty tag name…) |
| `2` | wrong command line (unknown command, missing argument, a document number that is not a number) |

Error messages are printed on standard error, so `uv run esper list > archive.txt` writes only the list to the file.

## Starting over

To empty the archive completely, delete the whole data folder:

```bash
rm -rf data/
```

The next command creates an empty database. Always delete the database **and** the files together: deleting only one of them leaves the other out of sync.

## For developers

Run the test suite (it never touches `data/`):

```bash
uv run pytest
```

Check the environment:

```bash
uv run python scripts/check_sqlite.py     # SQLite version and the sqlite-vec extension
uv run python scripts/test_embedding.py   # loads the embedding model (bge-m3) and compares three sentences
```

`test_embedding.py` downloads the model the first time it runs, about 2.3 GB. After that the model is cached in `~/.cache/huggingface/` and Esper works offline.
