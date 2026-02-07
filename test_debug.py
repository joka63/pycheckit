#!/usr/bin/env python3
"""Debug script to test pycheckit main function."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("DEBUG: Starting test...")

# Simulate command line arguments
sys.argv = ['pycheckit.py', '-s', 'testfile.txt']

print(f"DEBUG: Args: {sys.argv}")

# Import and run
print("DEBUG: Importing main...")
from pycheckit import main

print("DEBUG: Calling main()...")
try:
    result = main()
    print(f"DEBUG: main() returned: {result}")
except Exception as e:
    print(f"DEBUG: Exception: {e}")
    import traceback
    traceback.print_exc()

