"""One Markdown text in, one deck out: the whole conversion, without files or printing."""
from __future__ import annotations

import mermaid2pptx
from pptx import Presentation

from .model import Deck
from .options import SLIDE_SIZES, Options
from .render.deck import build
from .structure import to_deck


def plan(source: str, opts: Options | None = None, name: str = "Presentation") -> Deck:
    """What the deck will hold (slides, chapters, warnings), without drawing it. `name` is the title
    of last resort (the file's stem)."""
    opts = opts or Options()
    if opts.aspect not in SLIDE_SIZES:
        raise ValueError(f"aspect {opts.aspect!r}: use {' or '.join(SLIDE_SIZES)}")
    if opts.slide_level is not None and not 1 <= opts.slide_level <= 6:
        raise ValueError(f"slide level {opts.slide_level}: use 1 to 6")
    mermaid2pptx.palette(opts.mermaid_color)              # ValueError on a colour it does not know
    if opts.mermaid_render not in ("mermaid", "bpmn"):
        raise ValueError(f"mermaid render {opts.mermaid_render!r}: use mermaid or bpmn")
    return to_deck(source.lstrip("﻿"), opts, name)


def convert(source: str, opts: Options | None = None, name: str = "Presentation") -> tuple[Presentation, Deck]:
    """The Presentation (save it with .save(path)) and the Deck it was drawn from. Drawing may add
    warnings to the Deck (a diagram that could not be drawn, text that does not fit)."""
    opts = opts or Options()
    deck = plan(source, opts, name)
    return build(deck, opts), deck
