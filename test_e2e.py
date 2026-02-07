#!/usr/bin/env python3
"""
End-to-end test suite for pycheckit.
Tests the complete workflow.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def run_test(description, test_func):
    """Run a test and print results."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print('='*60)
    try:
        test_func()
        print(f"✅ PASSED: {description}")
        return True
    except AssertionError as e:
        print(f"❌ FAILED: {description}")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {description}")
        print(f"   Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crc64_algorithm():
    """Test CRC64 algorithm with known test vector."""
    from crc64 import crc64

    test_data = b"123456789"
    result = crc64(0, test_data)
    expected = 0xe9c6d914c4b8d9ca

    print(f"   Input: {test_data}")
    print(f"   Expected: {expected:016x}")
    print(f"   Got:      {result:016x}")

    assert result == expected, f"CRC64 mismatch: {result:016x} != {expected:016x}"

def test_file_list():
    """Test file list management."""
    from file_list import FileList

    fl = FileList()
    fl.append("/path/", "file1.txt")
    fl.append("/path/", "file2.txt")
    fl.append("", "file3.txt")

    print(f"   Files added: 3")
    print(f"   List length: {len(fl)}")

    assert len(fl) == 3, f"Expected 3 files, got {len(fl)}"

    list_str = fl.get_list()
    print(f"   List output:\n{list_str}")

    assert "/path/file1.txt" in list_str
    assert "/path/file2.txt" in list_str
    assert "file3.txt" in list_str

def test_basic_workflow():
    """Test basic store-check-remove workflow."""
    from pycheckit import (
        file_crc64, put_crc, get_crc, remove_crc,
        ErrorType, Flags, present_crc64, AttributeType
    )

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Test content for workflow\n")

    try:
        # Calculate CRC
        status1, crc1 = file_crc64(test_file)
        assert status1 == ErrorType.SUCCESS
        print(f"   Calculated CRC: {crc1:016x}")

        # Store CRC
        result = put_crc(test_file, Flags(0))
        assert result == ErrorType.SUCCESS
        print(f"   ✓ CRC stored")

        # Check presence
        attr_type = present_crc64(test_file)
        assert attr_type != AttributeType.NO_ATTR
        print(f"   ✓ CRC present (type: {attr_type.name})")

        # Retrieve CRC
        status2, crc2 = get_crc(test_file)
        assert status2 == ErrorType.SUCCESS
        assert crc2 == crc1
        print(f"   ✓ CRC retrieved and matches")

        # Remove CRC
        result = remove_crc(test_file)
        assert result == ErrorType.SUCCESS
        print(f"   ✓ CRC removed")

        # Verify removal
        attr_type = present_crc64(test_file)
        assert attr_type == AttributeType.NO_ATTR
        print(f"   ✓ CRC no longer present")

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_import_export():
    """Test import/export functionality."""
    from pycheckit import (
        put_crc, export_crc, import_crc, get_crc, remove_crc,
        ErrorType, Flags, present_crc64, AttributeType
    )

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Export/import test\n")

    try:
        # Store CRC
        put_crc(test_file, Flags(0))
        status1, crc1 = get_crc(test_file)
        print(f"   Original CRC: {crc1:016x}")

        # Export to hidden file
        result = export_crc(test_file, Flags.OVERWRITE)
        assert result == ErrorType.SUCCESS
        print(f"   ✓ Exported to hidden file")

        # Verify it's now in hidden file
        attr_type = present_crc64(test_file)
        assert attr_type == AttributeType.HIDDEN_ATTR
        print(f"   ✓ CRC in hidden file")

        # Import back
        result = import_crc(test_file, Flags.OVERWRITE)
        assert result == ErrorType.SUCCESS
        print(f"   ✓ Imported from hidden file")

        # Verify it's back in xattr
        attr_type = present_crc64(test_file)
        assert attr_type == AttributeType.XATTR

        # Verify CRC matches
        status2, crc2 = get_crc(test_file)
        assert crc2 == crc1
        print(f"   ✓ CRC matches after import")

        # Cleanup
        remove_crc(test_file)

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_cli_main():
    """Test the main CLI function."""
    from pycheckit import main

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("CLI test\n")

    try:
        # Store checksum
        original_argv = sys.argv
        sys.argv = ['pycheckit', '-s', test_file]

        result = main()
        assert result == 0, f"Store failed with code {result}"
        print(f"   ✓ Store via CLI: exit code {result}")

        # Check checksum
        sys.argv = ['pycheckit', '-c', test_file]
        result = main()
        assert result == 0, f"Check failed with code {result}"
        print(f"   ✓ Check via CLI: exit code {result}")

        # Remove checksum
        sys.argv = ['pycheckit', '-x', test_file]
        result = main()
        assert result == 0, f"Remove failed with code {result}"
        print(f"   ✓ Remove via CLI: exit code {result}")

        sys.argv = original_argv

    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)
        # Restore argv
        sys.argv = original_argv if 'original_argv' in locals() else sys.argv

def main_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("PyCheckit End-to-End Test Suite")
    print("="*60)

    tests = [
        ("CRC64 Algorithm", test_crc64_algorithm),
        ("File List Management", test_file_list),
        ("Basic Store-Check-Remove Workflow", test_basic_workflow),
        ("Import/Export Functionality", test_import_export),
        ("CLI Main Function", test_cli_main),
    ]

    results = []
    for description, test_func in tests:
        results.append(run_test(description, test_func))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main_tests())

