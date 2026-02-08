"""Allow running pycheckit as a module: python -m pycheckit"""

import sys

from pycheckit.cli import main

if __name__ == "__main__":
    sys.exit(main())

