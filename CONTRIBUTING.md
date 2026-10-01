# Contributing

Thanks for helping. A bug report with the smallest input that fails is the most useful
contribution of all: use the [bug report form](https://github.com/JeanMichelDurand/markdown2pptx/issues/new/choose).

## Set up

```sh
python3 install.py dev          # Windows: py install.py dev
.venv/bin/python -m pytest      # Windows: .venv\Scripts\python.exe -m pytest
.venv/bin/ruff check .
```

## Conventions

- **Few dependencies, short files.** Please open an issue before adding a dependency. No Python
  file goes over 500 lines (`tests/test_code_size.py` fails if one does): when a file grows, split
  it by responsibility, following the map below.
- **The work is separate from the command line.** `core.py` (and the modules it grows into) takes
  text or data and returns results: no printing, no files, no `sys.exit`. `cli.py` does the
  reading, printing and exit codes. The browser version calls the core directly.
- **Errors users can cause raise `InputError`** with a message in their words; the command line
  prints it without a traceback. Anything else is a bug and may crash loudly.
- **User-visible changes** get a line under `[Unreleased]` in `CHANGELOG.md`.

## Code map

```
src/markdown2pptx/
  __init__.py     public API and __version__ (the only place the version is written)
  __main__.py     python -m markdown2pptx, and the executables' entry point
  cli.py          arguments, files, printing, exit codes
  core.py         the work itself
  errors.py       InputError
tests/            one file per module
web/index.html    the browser version (Pyodide installs the package's wheel)
install.py        a venv and a launcher, for people who get the folder as a zip
```

## Pull requests

Fork, branch, and open a pull request against `main`. The `tests` workflow (ruff, then pytest on
Windows, Linux and macOS) must be green before it can be merged.

By contributing, you agree that your work is released under the [MIT license](LICENSE), and to
follow the [Code of Conduct](CODE_OF_CONDUCT.md).
