"""Unit tests for CRC64 algorithm."""

import pytest


class TestCRC64:
    """Test CRC64 calculation."""

    def test_crc64_known_vector(self):
        """Test CRC64 with known test vector."""
        from pycheckit.crc64_wrapper import crc64

        test_data = b"123456789"
        result = crc64(0, test_data)
        expected = 0xe9c6d914c4b8d9ca

        assert result == expected, f"CRC64 mismatch: {result:016x} != {expected:016x}"

    def test_crc64_empty_data(self):
        """Test CRC64 with empty data."""
        from pycheckit.crc64_wrapper import crc64

        result = crc64(0, b"")
        assert result == 0

    def test_crc64_incremental(self):
        """Test incremental CRC64 calculation."""
        from pycheckit.crc64_wrapper import crc64

        # Calculate in one go
        data = b"123456789"
        result_full = crc64(0, data)

        # Calculate incrementally
        result_inc = crc64(0, data[:3])
        result_inc = crc64(result_inc, data[3:6])
        result_inc = crc64(result_inc, data[6:])

        assert result_full == result_inc, "Incremental CRC64 doesn't match"

