"""The deck's starting file: python-pptx's built-in template, or the user's, and its three layouts.

A user's template is found by PowerPoint's layout type, which a layout keeps when it is renamed or
translated ("Titre de section" is still a section header), not by its name. The first layout of
each type wins, so moving a layout first in the Slide Master view chooses it. Its sample slides are
dropped; its theme, fonts, master decoration and slide size are kept.
"""
from __future__ import annotations

import io
import zipfile

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER as P
from pptx.util import Inches

from ..errors import TemplateError
from .style import THEME, Page

BUILT_IN = {"title": 0, "chapter": 2, "slide": 5, "text": 1}         # python-pptx's own template's layouts
TYPES = {"title": "title", "chapter": "secHead", "slide": "titleOnly", "text": "obj"}
FURNITURE = (P.DATE, P.FOOTER, P.SLIDE_NUMBER)
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
_POTX = b"presentationml.template.main+xml"
_PPTX = b"presentationml.presentation.main+xml"


def open_template(blob: bytes | None):
    """(presentation, {kind: layout}, branded)."""
    if blob is None:
        prs = Presentation()
        return prs, {k: prs.slide_layouts[i] for k, i in BUILT_IN.items()}, False
    try:
        prs = Presentation(io.BytesIO(_as_pptx(blob)))
    except Exception as exc:                          # not a zip, or a zip that is not a deck
        raise TemplateError("not a PowerPoint .pptx or .potx file") from exc
    if not len(prs.slide_layouts):
        raise TemplateError("the template has no slide layouts")
    ids = prs.slides._sldIdLst                       # the sample slides go, with their parts
    for sid in list(ids):
        prs.part.drop_rel(sid.rId)
        ids.remove(sid)
    for sections in prs.part._element.findall(f".//{{{P14}}}sectionLst"):
        ext = sections.getparent()                   # its sections listed the slides just dropped
        ext.getparent().remove(ext)
    return prs, layouts(prs), True


def _as_pptx(blob: bytes) -> bytes:
    """A .potx read as a .pptx: python-pptx refuses its main part's content type, the only difference."""
    try:
        src = zipfile.ZipFile(io.BytesIO(blob))
        types = src.read("[Content_Types].xml")
    except (zipfile.BadZipFile, KeyError):
        return blob
    if _POTX not in types:
        return blob
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item)
            dst.writestr(item, data.replace(_POTX, _PPTX) if item.filename == "[Content_Types].xml" else data)
    return buf.getvalue()


def _kinds(layout) -> list:
    return [ph.placeholder_format.type for ph in layout.placeholders
            if ph.placeholder_format.type not in FURNITURE]


def layouts(prs) -> dict:
    """{title, chapter, slide, text: layout}: by layout type, else by the placeholders a layout has.
    `slide` holds a title only (visuals are placed on it); `text` a title and a body, for text slides."""
    all_ = list(prs.slide_layouts)
    by_type = {}
    for lay in all_:
        by_type.setdefault(lay._element.get("type"), lay)
    title = by_type.get(TYPES["title"]) or next((la for la in all_ if P.CENTER_TITLE in _kinds(la)), all_[0])
    titled = [la for la in all_ if P.TITLE in _kinds(la)]
    slide = by_type.get(TYPES["slide"]) or min(titled, key=lambda la: len(_kinds(la)), default=all_[-1])
    chapter = by_type.get(TYPES["chapter"]) or title
    bodied = [la for la in titled if any(k in (P.BODY, P.OBJECT) for k in _kinds(la))]
    text = by_type.get(TYPES["text"]) or min(bodied, key=lambda la: len(_kinds(la)), default=slide)
    return {"title": title, "chapter": chapter, "slide": slide, "text": text}


def page(prs, slide_layout) -> Page:
    """The content slides' grid, from the content layout: its title's place, its side margins, and
    the top of its footer placeholders."""
    w, h = prs.slide_width, prs.slide_height
    ph = next((p for p in slide_layout.placeholders if p.placeholder_format.type == P.TITLE), None)
    if ph is None or ph.width is None:
        base = Page.of((w / 914400, h / 914400))
        return Page(w, h, base.margin, base.inner, base.title, base.top, base.bottom, THEME, True)
    x, y, tw, th = ph.left, ph.top, ph.width, min(ph.height, Inches(1.0))
    feet = [p.top for p in slide_layout.placeholders
            if p.placeholder_format.type in FURNITURE and p.top is not None and h // 2 < p.top < h]
    bottom = min(min(feet) if feet else h, h - Inches(0.45)) - Inches(0.1)
    return Page(w, h, x, min(tw, w - 2 * x), (x, y, tw, th), y + th + Inches(0.42), bottom, THEME, True)
