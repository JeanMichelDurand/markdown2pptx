"""Convert a Markdown file into a PowerPoint deck on your own template, with Mermaid diagrams as native shapes.

    markdown2pptx notes.txt report.md
    cat notes.txt | markdown2pptx -

The example feature counts lines and words: replace core.py with the real work, keep the shape
(cli.py reads files and prints, core.py computes and never prints). See README.md.
"""
from .core import Stats, count
from .errors import InputError

__version__ = "0.1.0"
__all__ = ["InputError", "Stats", "count", "__version__"]
