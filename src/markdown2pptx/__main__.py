"""`python -m markdown2pptx`, and the entry point of the one-file executables."""
import sys

from markdown2pptx.cli import main       # absolute: PyInstaller runs this file as a script

if __name__ == "__main__":
    sys.exit(main())
