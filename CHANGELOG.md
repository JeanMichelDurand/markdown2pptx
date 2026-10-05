# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] - 2026-10-02

### Added

- Four more examples (post-incident review, project kick-off, architecture review, training), and
  a menu on the web page that loads any of them, with its images. A README example with slides.

### Fixed

- The macOS and Linux executables failed on the first slide with speaker notes.
- A large picture was drawn a few pixels wide: it now fills its area, and a small one grows to
  twice its size at most.
- Table cells were cut at 40 characters: they now wrap, the row grows, and a short table's text
  starts at 16 pt.

## [0.1.0] - 2026-10-01

### Added

- First version: a Markdown file becomes a deck with a title slide, a linked contents slide, a
  section-header slide per chapter and a slide per heading at the slide level (pandoc's rule,
  or `--slide-level`); `---` starts a new slide.
- `--template DECK` (`.pptx` or `.potx`, or `$MARKDOWN2PPTX_TEMPLATE`): the deck takes the
  template's theme, fonts, slide size and layouts, found by layout type; text slides write into its
  body placeholder with its bullets; footer and slide number in its placeholders.
- Mermaid flowcharts, sequence diagrams and Gantt charts as native, editable shapes through
  mermaid2pptx, scaled into the slide, in the template's theme colours (`--mermaid-color`,
  `--mermaid-render bpmn`); other diagram types shown as source, with a warning.
- GitHub tables as native tables with their column alignment; images as pictures with alt text;
  bullet, numbered and task lists; bold, italic, code, strike and links as styled runs; block
  quotes and callouts; fenced code; speaker notes from `::: notes` and HTML comments; YAML front
  matter (title, subtitle, author).
- Text sized to fit its box, with a warning when it cannot.
- Command line, Python API (`plan`, `convert`), Windows executable with a file dialog, and a
  browser version with a live outline, image upload and a template picker.

[Unreleased]: ../../compare/v0.1.1...HEAD
[0.1.1]: ../../compare/v0.1.0...v0.1.1
[0.1.0]: ../../releases/tag/v0.1.0
