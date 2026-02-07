"""Tests for CLI functionality."""
import pytest
import sys
import os
from pycheckit.cli import main
from pycheckit.core import present_crc64, AttributeType
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
