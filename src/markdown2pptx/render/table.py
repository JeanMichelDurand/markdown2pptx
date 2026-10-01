"""A Table as a native PowerPoint table, in the theme's table style (it follows the deck's colours).

Columns keep the Markdown's alignment (`:--`, `:-:`, `--:`); without one, numbers are right-aligned."""
from __future__ import annotations

import re

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from ..model import Table
from .style import clip

NUMBER = re.compile(r"^[-+−]?[$€£¥]?\s?[\d.,\s]+%?\s?[kMBK]?$|^(nan|NaN|None|NaT|<NA>|…|\.\.\.)?$")
CELL_CHARS = 40
ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}


def _numeric(col: list[str]) -> bool:
    return any(c.strip() and c.strip() not in ("...", "…") for c in col) and all(NUMBER.match(c.strip()) for c in col)


def add_table(slide, t: Table, x, y, w, h, max_rows: int, max_columns: int) -> list[str]:
    """Draw the table at the top of the box; returns what was cut, for the footer."""
    extra: list[str] = []
    width = max(1, len(t.header), *(len(r) for r in t.rows))
    header = (t.header + [""] * width)[:width]
    rows = [(r + [""] * width)[:width] for r in t.rows]
    if len(rows) > max_rows:
        extra.append(f"first {max_rows} of {len(rows)} rows shown")
        rows = rows[:max_rows]
    if width > max_columns:
        extra.append(f"first {max_columns} of {width} columns shown")
        header, rows, width = header[:max_columns], [r[:max_columns] for r in rows], max_columns

    has_header = any(header)
    grid = ([header] if has_header else []) + rows
    n = len(grid)
    size = 12 if n <= 8 else 11 if n <= 12 else 10
    row_h = min(Inches(0.42), int(h / n))
    shape = slide.shapes.add_table(n, width, x, y, w, row_h * n)
    shape.name = "deck:table"
    table = shape.table
    table.first_row = has_header
    table.horz_banding = True

    weights = [min(max(max(len(clip(r[j], CELL_CHARS)) for r in grid), 4), 30) for j in range(width)]
    total = sum(weights)
    used = 0
    for j, col in enumerate(table.columns):
        col.width = w - used if j == width - 1 else int(w * weights[j] / total)
        used += col.width
    align = (list(t.align) + [None] * width)[:width]
    numeric = [_numeric([r[j] for r in rows]) for j in range(width)]
    for i, row in enumerate(table.rows):
        row.height = row_h
        for j, cell in enumerate(row.cells):
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = ALIGN.get(align[j]) or (PP_ALIGN.RIGHT if numeric[j] else PP_ALIGN.LEFT)
            r = p.add_run()
            r.text = clip(grid[i][j], CELL_CHARS)
            r.font.size = Pt(size)
            r.font.bold = has_header and i == 0
    return extra
