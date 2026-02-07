#!/usr/bin/env python3
"""Integration test for pycheckit."""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from pycheckit import (
    file_crc64, put_crc, get_crc, remove_crc,
    ErrorType, Flags, present_crc64, AttributeType
)

def test_crc_operations():
    """Test basic CRC operations."""

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Test content for pycheckit integration test\n")

    try:
        print(f"Testing with file: {test_file}")

        # Test 1: Calculate CRC
        print("\n1. Calculating CRC64...")
        status, crc = file_crc64(test_file)
        assert status == ErrorType.SUCCESS, f"CRC calculation failed: {status}"
        print(f"   ✓ CRC64: {crc:016x}")

        # Test 2: Store CRC
        print("\n2. Storing CRC...")
        result = put_crc(test_file, Flags(0))
        assert result == ErrorType.SUCCESS, f"Store CRC failed: {result}"
        print(f"   ✓ CRC stored successfully")

        # Test 3: Check if CRC is present
        print("\n3. Checking CRC presence...")
        attr_type = present_crc64(test_file)
        print(f"   Attribute type: {attr_type}")
        assert attr_type in [AttributeType.XATTR, AttributeType.HIDDEN_ATTR], \
            f"CRC not found: {attr_type}"
        print(f"   ✓ CRC is present (type: {attr_type.name})")

        # Test 4: Retrieve CRC
        print("\n4. Retrieving CRC...")
        status, stored_crc = get_crc(test_file)
        assert status == ErrorType.SUCCESS, f"Get CRC failed: {status}"
        assert stored_crc == crc, f"CRC mismatch: {stored_crc:016x} != {crc:016x}"
        print(f"   ✓ Retrieved CRC: {stored_crc:016x}")

        # Test 5: Verify CRC matches
        print("\n5. Verifying CRC...")
        status2, crc2 = file_crc64(test_file)
        assert status2 == ErrorType.SUCCESS
        assert crc2 == stored_crc, f"CRC verification failed"
        print(f"   ✓ CRC verification passed")

        # Test 6: Remove CRC
        print("\n6. Removing CRC...")
        result = remove_crc(test_file)
        assert result == ErrorType.SUCCESS, f"Remove CRC failed: {result}"
        print(f"   ✓ CRC removed successfully")

        # Test 7: Verify CRC is gone
        print("\n7. Verifying CRC removal...")
        attr_type = present_crc64(test_file)
        assert attr_type == AttributeType.NO_ATTR, f"CRC still present: {attr_type}"
        print(f"   ✓ CRC is no longer present")

        print("\n" + "="*50)
        print("All integration tests passed!")
        print("="*50)

    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)
        print(f"\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    test_crc_operations()

