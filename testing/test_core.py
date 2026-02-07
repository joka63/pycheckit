"""Integration tests for core pycheckit functionality."""
import pytest
import os
from pycheckit.core import (
    file_crc64, put_crc, get_crc, remove_crc,
    export_crc, import_crc, present_crc64,
    ErrorType, AttributeType
)
from pycheckit.constants import Flags
class TestCoreOperations:
    """Test basic CRC operations."""
    def test_file_crc64_calculation(self, temp_file):
        """Test CRC64 calculation for a file."""
        status, crc = file_crc64(temp_file)
        assert status == ErrorType.SUCCESS
        assert crc > 0
    def test_put_crc(self, temp_file):
        """Test storing CRC."""
        result = put_crc(temp_file, Flags(0))
        assert result == ErrorType.SUCCESS
    def test_get_crc(self, temp_file):
        """Test retrieving CRC."""
        # First store a CRC
        put_crc(temp_file, Flags(0))
        # Then retrieve it
        status, crc = get_crc(temp_file)
        assert status == ErrorType.SUCCESS
        assert crc > 0
    def test_crc_roundtrip(self, temp_file):
        """Test storing and retrieving CRC."""
        # Calculate original CRC
        status1, crc1 = file_crc64(temp_file)
        assert status1 == ErrorType.SUCCESS
        # Store CRC
        result = put_crc(temp_file, Flags(0))
        assert result == ErrorType.SUCCESS
        # Retrieve CRC
        status2, crc2 = get_crc(temp_file)
        assert status2 == ErrorType.SUCCESS
        # They should match
        assert crc1 == crc2
    def test_present_crc64(self, temp_file):
        """Test checking CRC presence."""
        # Initially no CRC
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.NO_ATTR
        # Store CRC
        put_crc(temp_file, Flags(0))
        # Now should have CRC
        attr_type = present_crc64(temp_file)
        assert attr_type in [AttributeType.XATTR, AttributeType.HIDDEN_ATTR]
    def test_remove_crc(self, temp_file):
        """Test removing CRC."""
        # Store CRC
        put_crc(temp_file, Flags(0))
        # Verify it's there
        attr_type = present_crc64(temp_file)
        assert attr_type != AttributeType.NO_ATTR
        # Remove it
        result = remove_crc(temp_file)
        assert result == ErrorType.SUCCESS
        # Verify it's gone
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.NO_ATTR
class TestExportImport:
    """Test export/import functionality."""
    def test_export_crc(self, temp_file):
        """Test exporting CRC to hidden file."""
        # Store CRC first
        put_crc(temp_file, Flags(0))
        # Export to hidden file
        result = export_crc(temp_file, Flags.OVERWRITE)
        assert result == ErrorType.SUCCESS
        # Should now be in hidden file
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.HIDDEN_ATTR
    def test_import_crc(self, temp_file):
        """Test importing CRC from hidden file."""
        # Store and export CRC
        put_crc(temp_file, Flags(0))
        status1, crc1 = get_crc(temp_file)
        export_crc(temp_file, Flags.OVERWRITE)
        # Import back
        result = import_crc(temp_file, Flags.OVERWRITE)
        assert result == ErrorType.SUCCESS
        # Should be back in xattr
        attr_type = present_crc64(temp_file)
        assert attr_type == AttributeType.XATTR
        # CRC should match
        status2, crc2 = get_crc(temp_file)
        assert crc1 == crc2
    def test_export_import_roundtrip(self, temp_file):
        """Test full export/import roundtrip."""
        # Store original CRC
        put_crc(temp_file, Flags(0))
        status1, crc1 = get_crc(temp_file)
        # Export
        export_crc(temp_file, Flags.OVERWRITE)
        # Import back
        import_crc(temp_file, Flags.OVERWRITE)
        # Verify CRC matches
        status2, crc2 = get_crc(temp_file)
        assert crc1 == crc2
