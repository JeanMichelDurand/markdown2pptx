# markdown2pptx

Convert a Markdown file into a PowerPoint deck on your own template, with Mermaid diagrams as native shapes.

```sh
markdown2pptx notes.txt report.md
cat notes.txt | markdown2pptx -
```

```text
notes.txt: 2 lines, 9 words
```

## Install

Pick one:

- **No install at all:** the [browser version](https://jeanmicheldurand.github.io/markdown2pptx/)
  runs in the page; your files never leave your computer.
- **A single executable**, no Python needed: download it from the
  [latest release](https://github.com/JeanMichelDurand/markdown2pptx/releases/latest)
  (Windows, Linux, macOS).
- **With Python 3.10 or later:** `pipx install markdown2pptx` (or `uv tool install markdown2pptx`).
- **From a copy of this folder:** `python3 install.py` (Windows: `py install.py`), then `./markdown2pptx`
  (Windows: `markdown2pptx.bat`).

## Usage

```text
markdown2pptx FILE [FILE ...]
```

| Option | Meaning |
|---|---|
| `FILE` | text files to read, or `-` for standard input |
| `--version` | print the version |

Exit code 0 when every file worked, 1 otherwise; errors go to standard error, one line per file.

## Development

```sh
python3 install.py dev          # Windows: py install.py dev
.venv/bin/python -m pytest      # Windows: .venv\Scripts\python.exe -m pytest
.venv/bin/ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the conventions and the code map.

## Releasing

1. Record the changes under a new version heading in [CHANGELOG.md](CHANGELOG.md).
2. Bump `__version__` in `src/markdown2pptx/__init__.py`, open a pull request and merge it into `main`.
3. Tag the merged commit, not your branch:
   `git switch main && git pull && git tag v1.2.3 && git push origin v1.2.3`.

The `release` workflow stops at once if the tag and `__version__` differ; otherwise it runs the
tests, builds and smoke-tests one executable per system, attaches them to a GitHub release and
publishes the package to PyPI. The `pages` workflow deploys the browser version from the same tag.

## Licence

[MIT](LICENSE), provided as is, without warranty.
