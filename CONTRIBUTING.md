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
- **The work is separate from the command line.** `convert.py` and the modules under it take
  text and options and return a deck: no printing, no files (images aside, read from
  `Options.base_dir`), no `sys.exit`. `cli.py` does the reading, printing and exit codes. The
  browser version calls `plan` and `convert` directly.
- **Reading and drawing are apart.** `blocks.py`, `inline.py` and `structure.py` turn Markdown into
  a `Deck` of plain data (`model.py`, no python-pptx); `render/` draws it. A Markdown feature
  touches the first, a layout change the second.
- **Errors users can cause raise `InputError`** with a message in their words; the command line
  prints it without a traceback. Anything else is a bug and may crash loudly.
- **User-visible changes** get a line under `[Unreleased]` in `CHANGELOG.md`.

## Code map

```
src/markdown2pptx/
  __init__.py       public API and __version__ (the only place the version is written)
  __main__.py       python -m markdown2pptx, and the executables' entry point
  cli.py            arguments, files, printing, exit codes
  windows.py        the Windows executable started from Explorer: file dialog, message boxes
  convert.py        plan() and convert(): Markdown text + Options -> Deck -> Presentation
  options.py        Options, environment variable names, slide sizes
  errors.py         InputError, TemplateError
  model.py          the Deck as plain data: slides, text blocks, runs, visuals
  blocks.py         Markdown lines -> blocks (headings, lists, tables, fences, notes, front matter)
  inline.py         inline Markdown -> styled runs
  structure.py      blocks -> Deck: title, slide level, chapters, one visual a slide, images
  render/
    deck.py         title, contents, chapter, text and visual slides
    template.py     the user's template: its layouts by type, its page grid
    text.py         text blocks in a text frame: runs, bullets, numbering, size that fits
    mermaid.py      a mermaid block: mermaid2pptx's group moved onto the slide, scaled
    table.py        native tables
    style.py        colours, page grid, text boxes, placeholders, footer
tests/              one file per module; helpers.py builds templates and checks layouts
web/index.html      the browser version (Pyodide installs the package's wheel)
examples/talk.md    the example: CI and the release smoke-test convert it, the web page loads it
install.py          a venv and a launcher, for people who get the folder as a zip
```

## Pull requests

Fork, branch, and open a pull request against `main`. The `tests` workflow (ruff, then pytest on
Windows, Linux and macOS) must be green before it can be merged.

By contributing, you agree that your work is released under the [MIT license](LICENSE), and to
follow the [Code of Conduct](CODE_OF_CONDUCT.md).
