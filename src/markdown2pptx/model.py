"""What the Markdown says the deck holds, before any drawing: plain data, no python-pptx."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Run:
    """A piece of text with one style."""
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    strike: bool = False
    link: str | None = None


# ---- Text blocks: drawn together in the slide's text box ---------------------------------------

@dataclass
class Paragraph:
    runs: list[Run]


@dataclass
class Item:
    runs: list[Run]
    level: int = 0                      # 0 for a top-level item
    number: int | None = None           # an ordered list's number; None for a bullet
    checked: bool | None = None         # a task list's box


@dataclass
class ListBlock:
    items: list[Item]


@dataclass
class Subheading:
    """A heading below the slide level: bold text inside the slide."""
    runs: list[Run]


@dataclass
class Quote:
    runs: list[Run]


@dataclass
class Code:
    text: str
    lang: str = ""


# ---- Visuals: one a slide, beside or under the text ---------------------------------------------

@dataclass
class Table:
    header: list[str]
    rows: list[list[str]]
    align: list[str | None] = field(default_factory=list)      # left, center, right or None per column


@dataclass
class Picture:
    blob: bytes
    alt: str = ""


@dataclass
class Mermaid:
    src: str


TEXT = (Paragraph, ListBlock, Subheading, Quote, Code)
VISUAL = (Table, Picture, Mermaid)


@dataclass
class Slide:
    """One content slide: text blocks, at most one visual, the speaker notes."""
    title: str
    chapter: str | None = None
    blocks: list = field(default_factory=list)              # TEXT blocks, in order
    visual: Table | Picture | Mermaid | None = None
    notes: str = ""
    line: int = 0                                            # 1-based line of the Markdown it starts at

    @property
    def kind(self) -> str:
        return {Table: "table", Picture: "picture", Mermaid: "diagram"}.get(type(self.visual), "text")


@dataclass
class Deck:
    title: str
    subtitle: str = ""
    author: str | None = None
    slides: list[Slide] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def chapters(self) -> list[str]:
        """Chapter titles in order, as the chapter slides will show them."""
        out: list[str] = []
        for s in self.slides:
            if s.chapter and (not out or out[-1] != s.chapter):
                out.append(s.chapter)
        return out

    def summary(self) -> str:
        counts: dict[str, int] = {}
        for s in self.slides:
            counts[s.kind] = counts.get(s.kind, 0) + 1
        parts = [count(counts[k], k) for k in ("diagram", "table", "picture", "text") if counts.get(k)]
        n = len(self.chapters())
        return f"{count(len(self.slides), 'content slide')} ({', '.join(parts) or 'none'}), {count(n, 'chapter')}"


def count(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def plain(runs: list[Run]) -> str:
    return "".join(r.text for r in runs)
