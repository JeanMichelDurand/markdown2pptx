"""Blocks -> a Deck: which headings are chapters, which start slides, what each slide holds.

    ---                              front matter: title, subtitle, author
    # Title                          the deck's title: first, alone at its level, no front-matter title
    ## Chapter                       above the slide level: a chapter slide
    ### Slide                        at the slide level: a new slide with this title
    #### Detail                      below it: bold text on the slide
    ---                              a new slide, with the same title
    ```mermaid                       a native diagram (mermaid2pptx)
    | a | b |                        a native table
    ![alt](img.png)                  a picture
    ::: notes / <!-- … -->           the speaker notes

The slide level is pandoc's: the highest heading level followed directly by content, so a
document with only `##` headings gets a slide per `##`. A slide holds one visual (diagram, table,
picture); a second one starts a new slide under the same title.
"""
from __future__ import annotations

import base64
import binascii
import re
from pathlib import Path
from urllib.parse import unquote

from .blocks import Block, parse
from .errors import InputError
from .inline import plain_text, runs
from .model import Code, Deck, Item, ListBlock, Mermaid, Paragraph, Picture, Quote, Slide, Subheading, Table
from .options import Options

SUBTITLE_CHARS = 200


def slide_level(blocks: list[Block]) -> int:
    """The highest heading level directly followed by content; the lowest level present when none is."""
    found = [b.level for b, nxt in zip(blocks, blocks[1:] + [None])
             if b.kind == "heading" and nxt is not None and nxt.kind not in ("heading", "break")]
    levels = [b.level for b in blocks if b.kind == "heading"]
    return min(found) if found else max(levels, default=1)


def to_deck(src: str, opts: Options, name: str = "Presentation") -> Deck:
    meta, blocks = parse(src)
    if not any(b.kind != "notes" for b in blocks) and not meta.get("title"):
        raise InputError("the document is empty")
    title, subtitle = opts.title or meta.get("title"), opts.subtitle or meta.get("subtitle")
    author = opts.author if opts.author is not None else meta.get("author")

    content = [b for b in blocks if b.kind != "notes"]
    lead = content[0] if content else None
    if not meta.get("title") and lead is not None and lead.kind == "heading" and lead.level == 1 and \
            sum(b.kind == "heading" and b.level == 1 for b in content) == 1:
        title = title or plain_text(lead.text)               # a lone leading # heading is the deck's title
        k = blocks.index(lead)
        del blocks[k]
        after = blocks[k + 1] if k + 1 < len(blocks) else None
        if k < len(blocks) and blocks[k].kind == "para" and len(blocks[k].text) <= SUBTITLE_CHARS and \
                (after is None or after.kind in ("heading", "break")):
            sub = blocks.pop(k)                              # with a short line under it: the subtitle
            subtitle = subtitle or plain_text(sub.text)
    deck = Deck(title or name, subtitle or "", author)
    _Builder(deck, opts, title or name).run(blocks, opts.slide_level or slide_level(blocks))
    return deck


class _Builder:
    def __init__(self, deck: Deck, opts: Options, title: str):
        self.deck, self.opts, self.title = deck, opts, title
        self.chapter: str | None = None
        self.cur: Slide | None = None
        self.notes: list[str] = []                           # read before the slide they belong to

    def run(self, blocks: list[Block], level: int):
        for b in blocks:
            if b.kind == "heading":
                text = plain_text(b.text)
                if b.level < level:
                    self.chapter, self.cur = text or None, None
                elif b.level == level:
                    self._new(text or (self.cur.title if self.cur else self.chapter or self.title), b.line)
                else:
                    self._slide(b).blocks.append(Subheading(runs(b.text)))
            elif b.kind == "break":
                if self.cur is not None and (self.cur.blocks or self.cur.visual):
                    self._new(self.cur.title, b.line)
            elif b.kind == "notes":
                if self.cur is None:
                    self.notes.append(b.text)
                else:
                    self.cur.notes = "\n\n".join(t for t in (self.cur.notes, b.text) if t)
            else:
                self._content(b)

    def _new(self, title: str, line: int) -> Slide:
        self.cur = Slide(title, self.chapter, line=line, notes="\n\n".join(self.notes))
        self.notes = []
        self.deck.slides.append(self.cur)
        return self.cur

    def _slide(self, b: Block) -> Slide:
        """The slide content goes on: one titled with the chapter (or the deck) when no heading started one."""
        return self.cur if self.cur is not None else self._new(self.chapter or self.title, b.line)

    def _visual(self, b: Block, visual):
        s = self._slide(b)
        if s.visual is not None:                             # one visual a slide: the next goes on its own
            s = self._new(s.title, b.line)
        s.visual = visual

    def _content(self, b: Block):
        if b.kind == "para":
            self._slide(b).blocks.append(Paragraph(runs(b.text)))
        elif b.kind == "list":
            self._slide(b).blocks.append(ListBlock(list_items(b.items)))
        elif b.kind == "quote":
            self._slide(b).blocks.append(Quote(runs(b.text)))
        elif b.kind == "code" and b.lang == "mermaid":
            self._visual(b, Mermaid(b.text))
        elif b.kind == "code":
            self._slide(b).blocks.append(Code(b.text, b.lang))
        elif b.kind == "table":
            header, *rows = [[plain_text(c) for c in r] for r in b.rows]
            self._visual(b, Table(header, rows, b.align))
        elif b.kind == "image":
            blob = self._image(b)
            if blob is not None:
                self._visual(b, Picture(blob, plain_text(b.text)))
            elif b.text:
                self._slide(b).blocks.append(Paragraph(runs(f"[{b.text}]")))

    def _image(self, b: Block) -> bytes | None:
        url, where = b.lang, f"line {b.line}"
        if url.startswith("data:"):
            try:
                blob = base64.b64decode(url.split(",", 1)[1])
            except (IndexError, binascii.Error):
                return self._warn(f"{where}: the image's data: URL is not base64")
        elif re.match(r"^[a-z][a-z0-9+.-]*://", url, re.I):
            return self._warn(f"{where}: {url} is not downloaded: save the image next to the Markdown file")
        else:
            base = self.opts.base_dir or Path(".")
            path = Path(unquote(url.split("#")[0].split("?")[0]))
            found = next((p for p in (base / path, base / path.name) if p.is_file()), None)
            if found is None:
                return self._warn(f"{where}: image {url} not found")
            blob = found.read_bytes()
        if blob.lstrip()[:5] in (b"<?xml", b"<svg ") or url.lower().endswith(".svg"):
            return self._warn(f"{where}: {url} is an SVG, which PowerPoint pictures here cannot hold: use a PNG")
        try:
            from pptx.parts.image import Image
            Image.from_blob(blob).size
        except Exception:
            return self._warn(f"{where}: {url} is not an image PowerPoint reads (PNG, JPEG, GIF, BMP, TIFF)")
        return blob

    def _warn(self, message: str) -> None:
        self.deck.warnings.append(message)
        return None


def list_items(raw: list[tuple]) -> list[Item]:
    """(indent, marker, text, checked) -> Items with their nesting level and their number."""
    items, indents, counters = [], [], {}
    for indent, marker, text, checked in raw:
        while indents and indent < indents[-1]:
            indents.pop()
        if not indents or indent > indents[-1]:
            indents.append(indent)
            counters.pop(len(indents) - 1, None)             # a new sub-list counts from its own start
        level = len(indents) - 1
        for deeper in [k for k in counters if k > level]:
            del counters[deeper]
        number = None
        if marker[0].isdigit():
            number = counters[level] + 1 if level in counters else int(marker[:-1])
            counters[level] = number
        items.append(Item(runs(text), level, number, checked))
    return items

