"""Conversion options, shared by the command line, the Python API and the browser version."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

AUTHOR_ENV = "MARKDOWN2PPTX_AUTHOR"       # default document author, when --author is not given
TEMPLATE_ENV = "MARKDOWN2PPTX_TEMPLATE"   # default template deck, when --template is not given
SLIDE_SIZES = {"16:9": (12192000 / 914400, 7.5), "4:3": (10.0, 7.5)}      # inches; 16:9 as PowerPoint's own
MERMAID_COLORS = ("theme", "purple", "slate")                  # or #RRGGBB, as mermaid2pptx --color


@dataclass
class Options:
    title: str | None = None            # None: the document's own (front matter, its only # heading)
    subtitle: str | None = None
    author: str | None = None           # None: the front matter's, else $MARKDOWN2PPTX_AUTHOR, else empty
    aspect: str = "16:9"                # ignored with a template: its slide size wins
    contents: bool = True               # a contents slide when there are two chapters or more
    slide_level: int | None = None      # the heading level that starts a slide; None: found as pandoc does
    max_rows: int = 15                  # table rows on a slide; the footer says how many were cut
    max_columns: int = 8
    template: bytes | None = None       # a .pptx or .potx whose theme, layouts and slide size the deck takes
    mermaid_color: str = "theme"        # theme (the deck's colours), purple, slate or #RRGGBB
    mermaid_render: str = "mermaid"     # mermaid | bpmn (flowcharts read as a simplified BPMN process)
    base_dir: Path | None = None        # where image paths are read from: the Markdown file's folder
