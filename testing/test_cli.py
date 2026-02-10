"""Tests for CLI functionality."""
import pytest
import sys
import os
import subprocess
import shutil
from pycheckit.cli import main
from pycheckit.core import present_crc64, AttributeType, get_crc, ErrorType


class TestCLI:
    """Test command-line interface."""
    def test_cli_store(self, temp_file, monkeypatch):
        """Test storing checksum via CLI."""
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-s', temp_file])
        result = main()
        assert result == 0
    def test_cli_check(self, temp_file, monkeypatch):
        """Test checking checksum via CLI."""
        # First store a checksum
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-s', temp_file])
        main()
        # Then check it
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-c', temp_file])
        result = main()
        assert result == 0
    def test_cli_remove(self, temp_file, monkeypatch):
        """Test removing checksum via CLI."""
        # First store a checksum
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-s', temp_file])
        main()
        # Then remove it
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-x', temp_file])
        result = main()
        assert result == 0
        # Verify it's gone
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.NO_ATTR
    def test_cli_workflow(self, temp_file, monkeypatch):
        """Test complete CLI workflow: store, check, remove."""
        # Store
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-s', temp_file])
        result = main()
        assert result == 0
        # Check
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-c', temp_file])
        result = main()
        assert result == 0
        # Remove
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-x', temp_file])
        result = main()
        assert result == 0
        # Verify removal
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.NO_ATTR
    def test_cli_export_import(self, temp_file, monkeypatch):
        """Test export and import via CLI."""
        # Store
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-s', temp_file])
        main()
        # Export
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-e', temp_file])
        result = main()
        assert result == 0
        # Import
        monkeypatch.setattr(sys, 'argv', ['pycheckit', '-i', temp_file])
        result = main()
        assert result == 0


class TestCheckitCompatibility:
    """Test compatibility with the original checkit command."""
    
    # marks @pytest.mark.skipif(not shutil.which("checkit"), reason="checkit command not available in PATH")  for all tests in this class
    pytestmark = pytest.mark.skipif(not shutil.which("checkit"), reason="checkit command not available in PATH")

    def test_store_compatibility(self, temp_file):
        """Test that both checkit and pycheckit store the same CRC value."""
        # Store with original checkit
        result = subprocess.run(['checkit', '-s', temp_file], capture_output=True, text=True)
        assert result.returncode == 0, f"checkit failed: {result.stderr}"

        # Get the CRC stored by checkit
        status_checkit, crc_checkit = get_crc(temp_file)
        assert status_checkit == ErrorType.SUCCESS

        # Remove the CRC
        subprocess.run(['checkit', '-x', temp_file], check=True)

        # Store with pycheckit
        result = subprocess.run(['pycheckit', '-s', temp_file], capture_output=True, text=True)
        assert result.returncode == 0, f"pycheckit failed: {result.stderr}"

        # Get the CRC stored by pycheckit
        status_pycheckit, crc_pycheckit = get_crc(temp_file)
        assert status_pycheckit == ErrorType.SUCCESS

        # Compare CRC values
        assert crc_checkit == crc_pycheckit, \
            f"CRC mismatch: checkit={crc_checkit:016x}, pycheckit={crc_pycheckit:016x}"

    def test_check_compatibility_pycheckit_store(self, temp_file):
        """Test that checkit can verify CRC stored by pycheckit."""
        # Store with pycheckit
        result = subprocess.run(['pycheckit', '-s', temp_file], capture_output=True, text=True)
        assert result.returncode == 0

        # Check with original checkit
        result = subprocess.run(['checkit', '-c', temp_file], capture_output=True, text=True)
        assert result.returncode == 0, f"checkit check failed: {result.stderr}"
        assert "OK" in result.stdout or "OK" in result.stderr

    def test_check_compatibility_checkit_store(self, temp_file):
        """Test that pycheckit can verify CRC stored by checkit."""
        # Store with original checkit
        result = subprocess.run(['checkit', '-s', temp_file], capture_output=True, text=True)
        assert result.returncode == 0

        # Check with pycheckit
        result = subprocess.run(['pycheckit', '-c', temp_file], capture_output=True, text=True)
        assert result.returncode == 0, f"pycheckit check failed: {result.stderr}"
        assert "OK" in result.stdout or "OK" in result.stderr

    def test_display_compatibility(self, temp_file):
        """Test that both tools display the same CRC value."""
        # Store with pycheckit
        subprocess.run(['pycheckit', '-s', temp_file], check=True, capture_output=True)

        # Display with checkit
        result_checkit = subprocess.run(['checkit', '-p', temp_file],
                                       capture_output=True, text=True)

        # Display with pycheckit
        result_pycheckit = subprocess.run(['pycheckit', '-p', temp_file],
                                         capture_output=True, text=True)

        # Get the actual CRC value
        status, crc_value = get_crc(temp_file)
        assert status == ErrorType.SUCCESS
        crc_hex = f"{crc_value:016x}"

        # Check that both outputs contain the same CRC value
        assert crc_hex in result_checkit.stdout or crc_hex in result_checkit.stderr, \
            f"checkit output doesn't contain CRC {crc_hex}: {result_checkit.stdout} {result_checkit.stderr}"
        assert crc_hex in result_pycheckit.stdout or crc_hex in result_pycheckit.stderr, \
            f"pycheckit output doesn't contain CRC {crc_hex}: {result_pycheckit.stdout} {result_pycheckit.stderr}"

    def test_remove_compatibility(self, temp_file):
        """Test that both tools can remove CRC attributes."""
        # Store with pycheckit
        subprocess.run(['pycheckit', '-s', temp_file], check=True, capture_output=True)

        # Remove with checkit
        result = subprocess.run(['checkit', '-x', temp_file], capture_output=True, text=True)
        assert result.returncode == 0

        # Verify it's gone
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.NO_ATTR

        # Store again with checkit
        subprocess.run(['checkit', '-s', temp_file], check=True, capture_output=True)

        # Remove with pycheckit
        result = subprocess.run(['pycheckit', '-x', temp_file], capture_output=True, text=True)
        assert result.returncode == 0

        # Verify it's gone
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.NO_ATTR

    def test_export_import_compatibility(self, temp_file):
        """Test that export/import works between checkit and pycheckit."""
        import tempfile

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test 1: pycheckit stores and exports, checkit imports
            test_file1 = os.path.join(tmpdir, "test1.txt")
            shutil.copy2(temp_file, test_file1)

            # Store with pycheckit
            subprocess.run(['pycheckit', '-s', test_file1], check=True, capture_output=True)

            # Get the stored CRC value
            status1, crc1 = get_crc(test_file1)
            assert status1 == ErrorType.SUCCESS

            # Export with pycheckit (this removes xattr and creates hidden file)
            subprocess.run(['pycheckit', '-e', test_file1], check=True, capture_output=True)

            # Verify hidden file exists and xattr is gone
            hidden_file1 = os.path.join(tmpdir, ".test1.txt.crc64")
            assert os.path.exists(hidden_file1), "Hidden file should exist after export"
            attr_type = present_crc64(test_file1)
            assert attr_type == AttributeType.HIDDEN_ATTR, "Should only have hidden file after export"

            # Import with checkit
            result = subprocess.run(['checkit', '-i', test_file1],
                                   capture_output=True, text=True, cwd=tmpdir)
            assert result.returncode == 0, f"checkit import failed: {result.stderr}"

            # Verify CRC was restored as xattr and matches original
            status2, crc2 = get_crc(test_file1)
            assert status2 == ErrorType.SUCCESS
            assert crc1 == crc2, "CRC should match after import"
            attr_type = present_crc64(test_file1)
            assert attr_type == AttributeType.XATTR, "Should have xattr after import"

            # Test 2: checkit stores and exports, pycheckit imports
            test_file2 = os.path.join(tmpdir, "test2.txt")
            shutil.copy2(temp_file, test_file2)

            # Store with checkit
            subprocess.run(['checkit', '-s', test_file2], check=True, capture_output=True)

            # Export with checkit (this moves xattr to hidden file)
            subprocess.run(['checkit', '-e', test_file2], check=True, capture_output=True, cwd=tmpdir)

            # Get the CRC value from the hidden file by importing and reading
            hidden_file2 = os.path.join(tmpdir, ".test2.txt.crc64")
            assert os.path.exists(hidden_file2), "Hidden file should exist after export"

            # Read CRC from hidden file
            with open(hidden_file2, 'rb') as f:
                import struct
                crc3 = struct.unpack('<Q', f.read(8))[0]

            # Verify only hidden file remains
            attr_type = present_crc64(test_file2)
            assert attr_type == AttributeType.HIDDEN_ATTR, "Should only have hidden file after export"

            # Import with pycheckit
            result = subprocess.run(['pycheckit', '-i', test_file2],
                                   capture_output=True, text=True, cwd=tmpdir)
            assert result.returncode == 0, f"pycheckit import failed: {result.stderr}"

            # Verify CRC was restored as xattr and matches original
            status4, crc4 = get_crc(test_file2)
            assert status4 == ErrorType.SUCCESS
            assert crc3 == crc4, f"CRC should match after import: {crc3:016x} != {crc4:016x}"
            attr_type = present_crc64(test_file2)
            assert attr_type == AttributeType.XATTR, "Should have xattr after import"

    def test_output_format_compatibility(self, temp_file):
        """Test that check output format is similar between tools."""
        # Store with pycheckit
        subprocess.run(['pycheckit', '-s', temp_file], check=True, capture_output=True)

        # Check with both tools in monochrome mode
        result_checkit = subprocess.run(['checkit', '-c', '-m', temp_file],
                                       capture_output=True, text=True)
        result_pycheckit = subprocess.run(['pycheckit', '-c', '-m', temp_file],
                                         capture_output=True, text=True)

        # Both should report OK
        combined_checkit = result_checkit.stdout + result_checkit.stderr
        combined_pycheckit = result_pycheckit.stdout + result_pycheckit.stderr

        assert "OK" in combined_checkit, f"checkit didn't report OK: {combined_checkit}"
        assert "OK" in combined_pycheckit, f"pycheckit didn't report OK: {combined_pycheckit}"

    def test_nonexistent_file_error_message(self):
        """Test that both tools show an error message for nonexistent files."""
        nonexistent_file = "/tmp/pycheckit_test_nonexistent_file_xyz123456789.txt"

        # Ensure the file doesn't exist
        if os.path.exists(nonexistent_file):
            os.remove(nonexistent_file)

        # Test checkit behavior
        result_checkit = subprocess.run(['checkit', '-s', nonexistent_file],
                                       capture_output=True, text=True)
        combined_checkit = result_checkit.stdout + result_checkit.stderr

        # checkit should show an error message
        assert "open" in combined_checkit.lower() or "error" in combined_checkit.lower() or \
               "not" in combined_checkit.lower(), \
               f"checkit should show error message, got: '{combined_checkit}'"

        # Test pycheckit behavior
        result_pycheckit = subprocess.run(['pycheckit', '-s', nonexistent_file],
                                         capture_output=True, text=True)
        combined_pycheckit = result_pycheckit.stdout + result_pycheckit.stderr

        # pycheckit should also show an error message
        assert "open" in combined_pycheckit.lower() or "error" in combined_pycheckit.lower() or \
               "not" in combined_pycheckit.lower(), \
               f"pycheckit should show error message for nonexistent file, got: '{combined_pycheckit}'"

        # Both should show similar error messages
        # Note: checkit returns exit code 0 even for nonexistent files, so we don't check exit codes
        assert "could not open file" in combined_checkit.lower(), \
               f"checkit should show 'Could not open file', got: '{combined_checkit}'"
        assert "could not open file" in combined_pycheckit.lower(), \
               f"pycheckit should show 'Could not open file', got: '{combined_pycheckit}'"
