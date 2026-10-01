"""Markdown text -> a flat list of blocks, each with the line it starts at.

A small CommonMark-flavoured reader for what slides hold: ATX and setext headings, paragraphs,
bullet, numbered and task lists (nested by indentation), block quotes and GitHub callouts, fenced
code, GitHub tables, images on their own line, thematic breaks (`---`, the slide break), YAML
front matter, and speaker notes (`::: notes` blocks and HTML comments, as pandoc and Marp read them).
Indented code blocks are not read: a four-space indent continues a list item.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
BREAK = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
FENCE = re.compile(r"^( {0,3})(`{3,}|~{3,})[ \t]*([^`]*?)[ \t]*$")
ITEM = re.compile(r"^([ \t]*)([-+*]|\d{1,9}[.)])(?:[ \t]+(.*)|[ \t]*$)")
TASK = re.compile(r"^\[([ xX])\][ \t]+")
QUOTE = re.compile(r"^ {0,3}>[ \t]?(.*)$")
CALLOUT = re.compile(r"^\[!(\w+)\][ \t]*")
TABLE_RULE = re.compile(r"^ {0,3}\|?[ \t]*:?-+:?[ \t]*(\|[ \t]*:?-+:?[ \t]*)*\|?[ \t]*$")
IMAGE = re.compile(r"^ {0,3}!\[(?P<alt>[^\]]*)\]\((?P<url><[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\)[ \t]*$")
HTML_IMAGE = re.compile(r"^ {0,3}<img\s[^>]*?src=[\"'](?P<url>[^\"']+)[\"'][^>]*?(?:alt=[\"'](?P<alt>[^\"']*)[\"'])?"
                        r"[^>]*>[ \t]*$", re.I)
NOTES_OPEN = re.compile(r"^ {0,3}:::+[ \t]*\{?\.?notes\}?[ \t]*$")
NOTES_CLOSE = re.compile(r"^ {0,3}:::+[ \t]*$")


@dataclass
class Block:
    kind: str                     # heading, break, para, list, quote, code, table, image, notes
    line: int                     # 1-based
    text: str = ""                # heading, para, quote, code, notes; an image's alt
    level: int = 0                # heading level
    lang: str = ""                # code: the fence's info word; image: the url
    items: list = field(default_factory=list)       # list: (indent, marker, text, checked)
    rows: list = field(default_factory=list)        # table: header first
    align: list = field(default_factory=list)       # table: left, center, right or None


def front_matter(lines: list[str]) -> tuple[dict[str, str], int]:
    """The YAML front matter's simple `key: value` pairs, and the line after it (0 when none)."""
    if not lines or lines[0].strip() != "---":
        return {}, 0
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
    if end is None:
        return {}, 0
    meta = {}
    for ln in lines[1:end]:
        m = re.match(r"^([A-Za-z_][\w-]*)[ \t]*:[ \t]*(.*?)[ \t]*$", ln)
        if m and m.group(2):
            meta[m.group(1).lower()] = m.group(2).strip("'\"")
    return meta, end + 1


def parse(src: str) -> tuple[dict[str, str], list[Block]]:
    lines = src.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ").split("\n")
    meta, i = front_matter(lines)
    blocks: list[Block] = []
    para: list[str] = []
    para_line = 0

    def flush():
        nonlocal para
        if para:
            blocks.append(Block("para", para_line, "\n".join(para)))
            para = []

    while i < len(lines):
        ln, n = lines[i], i + 1
        if not ln.strip():
            flush()
            i += 1
            continue
        if para and SETEXT.match(ln):                    # `===` or `---` under a paragraph: a heading
            blocks.append(Block("heading", para_line, " ".join(para), level=1 if "=" in ln else 2))
            para = []
            i += 1
            continue
        if (m := FENCE.match(ln)):
            flush()
            i = _fence(lines, i, m, blocks)
            continue
        if NOTES_OPEN.match(ln):
            flush()
            end = next((k for k in range(i + 1, len(lines)) if NOTES_CLOSE.match(lines[k])), len(lines))
            blocks.append(Block("notes", n, "\n".join(lines[i + 1:end]).strip()))
            i = end + 1
            continue
        if ln.lstrip().startswith("<!--"):
            flush()
            end = next((k for k in range(i, len(lines)) if "-->" in lines[k]), len(lines) - 1)
            body = "\n".join(lines[i:end + 1]).strip()
            body = body[body.index("<!--") + 4:].rsplit("-->", 1)[0].strip()
            if body:
                blocks.append(Block("notes", n, body))
            i = end + 1
            continue
        if (m := HEADING.match(ln)):
            flush()
            blocks.append(Block("heading", n, m.group(2) or "", level=len(m.group(1))))
            i += 1
            continue
        if BREAK.match(ln):
            flush()
            blocks.append(Block("break", n))
            i += 1
            continue
        if not para and (m := IMAGE.match(ln) or HTML_IMAGE.match(ln)):
            blocks.append(Block("image", n, m.group("alt") or "", lang=m.group("url").strip("<>")))
            i += 1
            continue
        if QUOTE.match(ln):
            flush()
            i = _quote(lines, i, blocks)
            continue
        if (m := ITEM.match(ln)) and (not para or m.group(3)):
            flush()
            i = _list(lines, i, blocks)
            continue
        if "|" in ln and i + 1 < len(lines) and TABLE_RULE.match(lines[i + 1]) and "|" in lines[i] + lines[i + 1]:
            flush()
            i = _table(lines, i, blocks)
            continue
        if not para:
            para_line = n
        para.append(ln.strip())
        i += 1
    flush()
    return meta, blocks


def _fence(lines, i, m, blocks) -> int:
    indent, mark, info = len(m.group(1)), m.group(2), m.group(3)
    body = []
    k = i + 1
    while k < len(lines):
        close = re.match(r"^ {0,3}(`{3,}|~{3,})[ \t]*$", lines[k])
        if close and close.group(1)[0] == mark[0] and len(close.group(1)) >= len(mark):
            break
        body.append(re.sub(rf"^ {{0,{indent}}}", "", lines[k]))      # the fence's own indent, no more
        k += 1
    lang = info.split()[0].strip("{}.").lower() if info.split() else ""
    blocks.append(Block("code", i + 1, "\n".join(body), lang=lang))
    return k + 1


def _quote(lines, i, blocks) -> int:
    start, body = i, []
    while i < len(lines) and (m := QUOTE.match(lines[i])):
        body.append(m.group(1))
        i += 1
    text = "\n".join(body).strip()
    if (c := CALLOUT.match(text)):                       # > [!NOTE]: GitHub's callouts
        text = f"**{c.group(1).capitalize()}:** " + text[c.end():].lstrip()
    blocks.append(Block("quote", start + 1, re.sub(r"\n\s*\n", "\n\n", text)))
    return i


def _list(lines, i, blocks) -> int:
    start, items = i, []
    while i < len(lines):
        ln = lines[i]
        m = ITEM.match(ln)
        if m:
            text = m.group(3) or ""
            checked = None
            if (t := TASK.match(text)):
                checked, text = t.group(1) != " ", text[t.end():]
            items.append([len(m.group(1)), m.group(2), text, checked])
            i += 1
            continue
        if not ln.strip():                               # a blank line: the list goes on if an item
            k = i + 1                                    # or an indented line follows
            while k < len(lines) and not lines[k].strip():
                k += 1
            if k < len(lines) and (ITEM.match(lines[k]) or lines[k].startswith("  ")) and \
                    not FENCE.match(lines[k]):
                i = k
                continue
            break
        if ln.startswith("  ") and items and not FENCE.match(ln):     # continues the item above
            items[-1][2] += "\n" + ln.strip()
            i += 1
            continue
        if any(p.match(ln) for p in (HEADING, BREAK, QUOTE, FENCE)) or not items:
            break
        items[-1][2] += "\n" + ln.strip()                # a lazy continuation line
        i += 1
    blocks.append(Block("list", start + 1, items=[tuple(it) for it in items]))
    return i


def cells(line: str) -> list[str]:
    """A table row's cells: `|` splits, `\\|` does not."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def _table(lines, i, blocks) -> int:
    start = i
    header = cells(lines[i])
    align = []
    for c in cells(lines[i + 1]):
        left, right = c.startswith(":"), c.endswith(":")
        align.append("center" if left and right else "right" if right else "left" if left else None)
    rows = [header]
    i += 2
    while i < len(lines) and lines[i].strip() and "|" in lines[i] and not HEADING.match(lines[i]):
        rows.append(cells(lines[i]))
        i += 1
    blocks.append(Block("table", start + 1, rows=rows, align=align))
    return i
