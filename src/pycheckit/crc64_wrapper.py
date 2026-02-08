"""CRC64 wrapper module.

This module tries to import the fast Cython implementation of CRC64.
If that fails (e.g., extension not compiled), it falls back to the pure Python version.
"""

try:
    # Try to import the compiled Cython extension
    from pycheckit.crc64 import crc64
    _IMPLEMENTATION = "cython"
except ImportError:
    # Fall back to pure Python implementation
    from pycheckit.crc64_pure import crc64
    _IMPLEMENTATION = "python"


__all__ = ['crc64']


def get_implementation():
    """Return the current CRC64 implementation being used."""
    return _IMPLEMENTATION

