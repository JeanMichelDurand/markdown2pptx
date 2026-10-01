"""Convert a Markdown file into a PowerPoint deck on your own template, with Mermaid diagrams as native shapes.

    markdown2pptx talk.md                          # -> talk.pptx
    markdown2pptx talk.md --template brand.pptx    # on your template's layouts, fonts and colours

Headings make the structure (a chapter slide per chapter, a slide per heading at the slide
level), `---` starts a new slide. ```mermaid blocks become native, editable PowerPoint shapes
(through mermaid2pptx), tables native tables, images pictures, lists real bullets. See README.md.

    from markdown2pptx import convert
    prs, deck = convert(open("talk.md", encoding="utf-8").read())
    prs.save("talk.pptx")
"""
from .convert import convert, plan
from .errors import InputError, TemplateError
from .model import Deck, Mermaid, Picture, Slide, Table
from .options import AUTHOR_ENV, TEMPLATE_ENV, Options

__version__ = "0.1.0"
__all__ = ["AUTHOR_ENV", "Deck", "InputError", "Mermaid", "Options", "Picture", "Slide", "Table", "TEMPLATE_ENV",
           "TemplateError", "convert", "plan", "__version__"]
