#!/usr/bin/env python3
"""
Simple command-line wrapper for pycheckit.
This can be used for testing without installing the package.
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from pycheckit import main

if __name__ == "__main__":
    sys.exit(main())

