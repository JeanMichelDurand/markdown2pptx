"""Inline Markdown (emphasis, code, links) as styled runs.

Covers what slides use: **bold**, *italic*, ***both***, ~~strike~~, `code`, [links](url),
<autolinks>, backslash escapes and HTML entities. Inline images keep their alt text; other inline
HTML is dropped, its text kept. A bare * or _ is content (2 * 3, snake_case).
"""
from __future__ import annotations

import html
import re
from dataclasses import replace

from .model import Run

_TOKEN = re.compile(r"""
    (?P<code>(?P<ticks>`+)(?P<code_text>.+?)(?P=ticks))
  | (?P<escape>\\(?P<escaped>[\\`*_{}\[\]()#+\-.!|~<>]))
  | (?P<image>!\[(?P<alt>[^\]]*)\]\([^)]*\))
  | (?P<link>\[(?P<link_text>(?:[^\[\]]|\[[^\]]*\])+)\]\((?P<url><[^>]*>|[^)\s]+)(?:\s+"[^"]*")?\))
  | (?P<auto><(?P<auto_url>(?:https?|mailto):[^>\s]+)>)
  | (?P<strong_em>(?P<se>\*\*\*|___)(?=\S)(?P<se_text>.+?)(?<=\S)(?P=se)(?!\w))
  | (?P<strong>(?P<s>\*\*|__)(?=\S)(?P<s_text>.+?)(?<=\S)(?P=s))
  | (?P<strike>~~(?=\S)(?P<strike_text>.+?)(?<=\S)~~)
  | (?P<em>(?<![\w*])\*(?=[^\s*])(?P<em_text>.+?)(?<=[^\s*])\*(?![\w*])
         |(?<![\w_])_(?=[^\s_])(?P<u_text>.+?)(?<=[^\s_])_(?![\w_]))
  | (?P<br><br\s*/?>)
  | (?P<tag></?[A-Za-z][^<>]*>)
""", re.X | re.S)


def runs(text: str, base: Run = Run("")) -> list[Run]:
    """The runs of one paragraph's text; line breaks inside it become spaces."""
    text = re.sub(r"[ \t]*\n[ \t]*", " ", text.strip())
    return _merge(_parse(text, base))


def _parse(text: str, base: Run) -> list[Run]:
    out: list[Run] = []
    pos = 0
    for m in _TOKEN.finditer(text):
        if m.start() > pos:
            out.append(replace(base, text=html.unescape(text[pos:m.start()])))
        pos = m.end()
        g = m.lastgroup
        if g == "code":
            out.append(replace(base, text=m.group("code_text").strip() or m.group("code_text"), code=True))
        elif g == "escape":
            out.append(replace(base, text=m.group("escaped")))
        elif g == "image":
            out.append(replace(base, text=m.group("alt")))
        elif g == "link":
            out += _parse(m.group("link_text"), replace(base, link=m.group("url").strip("<>")))
        elif g == "auto":
            out.append(replace(base, text=m.group("auto_url"), link=m.group("auto_url")))
        elif g == "strong_em":
            out += _parse(m.group("se_text"), replace(base, bold=True, italic=True))
        elif g == "strong":
            out += _parse(m.group("s_text"), replace(base, bold=True))
        elif g == "strike":
            out += _parse(m.group("strike_text"), replace(base, strike=True))
        elif g == "em":
            out += _parse(m.group("em_text") or m.group("u_text"), replace(base, italic=True))
        elif g == "br":
            out.append(replace(base, text=" "))
        # tag: dropped, its text is outside it
    if pos < len(text):
        out.append(replace(base, text=html.unescape(text[pos:])))
    return out


def _merge(rs: list[Run]) -> list[Run]:
    """Neighbouring runs of the same style as one; no empty run."""
    out: list[Run] = []
    for r in rs:
        if not r.text:
            continue
        if out and replace(out[-1], text="") == replace(r, text=""):
            out[-1] = replace(r, text=out[-1].text + r.text)
        else:
            out.append(r)
    return out


def plain_text(text: str) -> str:
    """Inline Markdown as plain text: a heading, a table cell, a title."""
    return " ".join("".join(r.text for r in runs(text)).split())
