"""Test imports and module structure."""
import pytest
class TestImports:
    """Test that all required modules can be imported."""
    def test_import_core(self):
        """Test importing core module."""
        from pycheckit import core
        assert core is not None
    def test_import_enums(self):
        """Test importing enums."""
        from pycheckit.core import ErrorType, AttributeType
        assert ErrorType is not None
        assert AttributeType is not None
    def test_import_functions(self):
        """Test importing main functions."""
        from pycheckit.core import (
            get_crc, put_crc, remove_crc,
            file_crc64, present_crc64
        )
        assert get_crc is not None
        assert put_crc is not None
        assert remove_crc is not None
        assert file_crc64 is not None
        assert present_crc64 is not None
    def test_import_cli(self):
        """Test importing CLI module."""
        from pycheckit import cli
        assert cli is not None
    def test_import_main(self):
        """Test importing main function."""
        from pycheckit.cli import main
        assert main is not None
    def test_import_crc64(self):
        """Test importing CRC64 wrapper."""
        from pycheckit.crc64_wrapper import crc64
        assert crc64 is not None
    def test_import_file_list(self):
        """Test importing FileList."""
        from pycheckit.file_list import FileList
        assert FileList is not None
