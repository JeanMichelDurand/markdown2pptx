"""The work itself, as pure functions: text in, result out. No printing, no files."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import InputError


@dataclass(frozen=True)
class Stats:
    lines: int
    words: int

    def summary(self) -> str:
        return f"{_count(self.lines, 'line')}, {_count(self.words, 'word')}"


def count(text: str) -> Stats:
    """Lines and words of `text`; raises InputError on empty input."""
    if not text.strip():
        raise InputError("the input is empty")
    return Stats(len(text.splitlines()), len(text.split()))


def _count(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"
