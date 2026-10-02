"""`python -m markdown2pptx`, and the entry point of the one-file executables."""
import os
import sys

from markdown2pptx.cli import main       # absolute: PyInstaller runs this file as a script
from markdown2pptx.windows import explorer_ui, started_from_explorer

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        # python-pptx reads its notes master from pptx/oxml/../templates; in the one-file bundle the
        # modules are archived, so pptx/oxml is no folder and macOS and Linux cannot resolve the `..`
        os.makedirs(os.path.join(sys._MEIPASS, "pptx", "oxml"), exist_ok=True)
    sys.exit(explorer_ui(sys.argv[1:]) if started_from_explorer() else main())
