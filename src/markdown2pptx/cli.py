"""The command line: `markdown2pptx FILE.md`, and the batch conversion behind the Windows dialog."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __doc__ as _doc, __version__
from .convert import convert
from .errors import InputError, TemplateError
from .options import AUTHOR_ENV, MERMAID_COLORS, SLIDE_SIZES, TEMPLATE_ENV, Options


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="markdown2pptx", description=_doc.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Markdown file (.md); '-' = stdin")
    ap.add_argument("-o", "--output", help="output .pptx (default: the input's name with .pptx)")
    ap.add_argument("--template", metavar="DECK", help="a PowerPoint deck or template (.pptx or .potx): its theme, "
                                                       f"fonts, layouts and slide size (default: ${TEMPLATE_ENV})")
    ap.add_argument("--title", help="title slide (default: the front matter's, else the only # heading)")
    ap.add_argument("--subtitle", help="line under the title")
    ap.add_argument("--author", help=f"document author (default: the front matter's, else ${AUTHOR_ENV})")
    ap.add_argument("--aspect", choices=sorted(SLIDE_SIZES), help="slide shape (16:9; with --template, the template's)")
    ap.add_argument("--slide-level", type=int, metavar="N", help="the heading level that starts a slide "
                                                                 "(default: the highest one followed by content)")
    ap.add_argument("--no-contents", action="store_true", help="no contents slide")
    ap.add_argument("--max-rows", type=int, default=15, help="table rows on a slide (15)")
    ap.add_argument("--max-columns", type=int, default=8, help="table columns on a slide (8)")
    ap.add_argument("--mermaid-color", default="theme", metavar="COLOR",
                    help=f"diagram colours: {', '.join(MERMAID_COLORS)} or #RRGGBB (theme: the deck's)")
    ap.add_argument("--mermaid-render", choices=["mermaid", "bpmn"], default="mermaid",
                    help="flowcharts with their Mermaid shapes, or read as a simplified BPMN process")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args(argv)
    if args.max_rows < 1 or args.max_columns < 1:
        ap.error("--max-rows and --max-columns must be 1 or more")
    if args.slide_level is not None and not 1 <= args.slide_level <= 6:
        ap.error("--slide-level must be 1 to 6")

    try:
        if args.input == "-":
            sys.stdin.reconfigure(encoding="utf-8-sig")      # the Windows console code page is not UTF-8
            src = sys.stdin.read()
        else:
            src = Path(args.input).read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(f"error: cannot read {args.input}: {exc.strerror}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"error: {args.input} is not UTF-8 text: is it really a Markdown file?", file=sys.stderr)
        return 1
    template_path = args.template if args.template is not None else os.environ.get(TEMPLATE_ENV, "")
    template = None
    if template_path:
        try:
            template = Path(template_path).read_bytes()
        except OSError as exc:
            print(f"error: cannot read template {template_path}: {exc.strerror}", file=sys.stderr)
            return 1
    stdin = args.input == "-"
    out = Path(args.output) if args.output else Path("slides.pptx" if stdin else Path(args.input).with_suffix(".pptx"))
    opts = Options(title=args.title, subtitle=args.subtitle, author=args.author, aspect=args.aspect or "16:9",
                   contents=not args.no_contents, slide_level=args.slide_level, max_rows=args.max_rows,
                   max_columns=args.max_columns, template=template, mermaid_color=args.mermaid_color,
                   mermaid_render=args.mermaid_render, base_dir=Path.cwd() if stdin else Path(args.input).parent)
    try:
        prs, deck = convert(src, opts, name="slides" if stdin else Path(args.input).stem)
    except InputError as exc:
        print(f"error: {template_path if isinstance(exc, TemplateError) else args.input}: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:                                # an option mermaid2pptx refuses: --mermaid-color
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if template is not None and args.aspect:
        deck.warnings.insert(0, "--aspect is ignored with --template: the slides take the template's size")
    try:
        prs.save(out)
    except OSError as exc:
        hint = " (is it open in PowerPoint?)" if isinstance(exc, PermissionError) else ""
        print(f"error: cannot write {out}: {exc.strerror}{hint}", file=sys.stderr)
        return 1
    for w in deck.warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(f"{out}: {deck.summary()}")
    return 0


def convert_files(paths: list[str]) -> tuple[bool, str]:
    """Convert each file with the default options, as `markdown2pptx FILE` would.

    Returns whether every file converted, and everything the conversions printed (results,
    warnings, errors), for a message box.
    """
    import contextlib
    import io
    ok, report = True, io.StringIO()
    for path in paths:
        with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
            try:
                code = main([path])
            except SystemExit as exc:                    # argparse errors
                code = exc.code
            except Exception as exc:                     # a bug: say so rather than vanish
                print(f"error: {path}: unexpected {exc!r}. Please report it with the Markdown file.")
                code = 1
        ok = ok and code == 0
    return ok, report.getvalue().strip()
