"""Pytest configuration and fixtures for pycheckit tests."""

import tempfile
import os
from pathlib import Path
import pytest
import shutil


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
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def extended_path(monkeypatch):
    """Extend PATH to include ~/.local/bin for checkit compatibility tests.
    
    This fixture safely adds ~/.local/bin to PATH for tests that need to find
    the checkit command. If HOME environment variable is not set, PATH remains
    unchanged (tests will be skipped by the @pytest.mark.skipif decorator if
    checkit command cannot be found).
    """
    home = os.environ.get('HOME')
    if home:
        local_bin = os.path.join(home, '.local', 'bin')
        current_path = os.environ.get('PATH', '')
        new_path = os.pathsep.join([local_bin, current_path])
        monkeypatch.setenv('PATH', new_path)

