#!/usr/bin/env python3
"""Basic test script for pycheckit."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing CRC64...")
from crc64 import crc64

# Test CRC64
test_data = b"123456789"
result = crc64(0, test_data)
expected = 0xe9c6d914c4b8d9ca
assert result == expected, f"CRC64 test failed: {result:016x} != {expected:016x}"
print(f"✓ CRC64 test passed: {result:016x}")

print("\nTesting file_list...")
from file_list import FileList

fl = FileList()
fl.append("/path/", "file1.txt")
fl.append("/path/", "file2.txt")
assert len(fl) == 2
print(f"✓ FileList test passed: {len(fl)} files")

print("\nTesting pycheckit module import...")
try:
    from pycheckit import (
        ErrorType, AttributeType, get_crc, file_crc64,
        present_crc64, hidden_crc_file
    )
    print("✓ Pycheckit module imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

print("\nAll basic tests passed!")

