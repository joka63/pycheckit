"""Pytest configuration and fixtures for pycheckit tests."""

import tempfile
import os
from pathlib import Path
import pytest


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Test content for pycheckit\n")

    yield test_file

    # Cleanup
    if os.path.exists(test_file):
        os.unlink(test_file)
    # Also cleanup hidden CRC file if it exists
    hidden_file = os.path.join(os.path.dirname(test_file), f".{os.path.basename(test_file)}.crc64")
    if os.path.exists(hidden_file):
        os.unlink(hidden_file)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

