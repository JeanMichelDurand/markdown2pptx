"""The command line: arguments, reading files, printing results and errors, exit codes."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __doc__ as _doc, __version__
from .core import count
from .errors import InputError


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="markdown2pptx", description=_doc.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="text files to read, or - for standard input")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args(argv)
    ok = True
    for name in args.files:
        try:
            text = sys.stdin.read() if name == "-" else Path(name).read_text(encoding="utf-8-sig")
            print(f"{name}: {count(text).summary()}")
        except (OSError, UnicodeDecodeError, InputError) as e:
            print(f"{name}: error: {e}", file=sys.stderr)
            ok = False
    return 0 if ok else 1
