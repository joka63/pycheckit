"""Allow running pycheckit as a module: python -m pycheckit"""

from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())

