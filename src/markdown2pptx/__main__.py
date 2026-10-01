"""`python -m markdown2pptx`, and the entry point of the one-file executables."""
import sys

from markdown2pptx.cli import main       # absolute: PyInstaller runs this file as a script
from markdown2pptx.windows import explorer_ui, started_from_explorer

if __name__ == "__main__":
    sys.exit(explorer_ui(sys.argv[1:]) if started_from_explorer() else main())
