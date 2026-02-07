"""Unit tests for FileList class."""
import pytest
from pycheckit.file_list import FileList
class TestFileList:
    """Test FileList functionality."""
    def test_file_list_creation(self):
        """Test creating a new FileList."""
        fl = FileList()
        assert len(fl) == 0
    def test_file_list_append(self):
        """Test appending files to FileList."""
        fl = FileList()
        fl.append("/path/", "file1.txt")
        fl.append("/path/", "file2.txt")
        assert len(fl) == 2
    def test_file_list_append_no_path(self):
        """Test appending file without path."""
        fl = FileList()
        fl.append("", "file.txt")
        assert len(fl) == 1
    def test_file_list_get_list(self):
        """Test getting list output."""
        fl = FileList()
        fl.append("/path/", "file1.txt")
        fl.append("/path/", "file2.txt")
        fl.append("", "file3.txt")
        list_str = fl.get_list()
        assert "/path/file1.txt" in list_str
        assert "/path/file2.txt" in list_str
        assert "file3.txt" in list_str
    def test_file_list_empty_get_list(self):
        """Test getting list from empty FileList."""
        fl = FileList()
        list_str = fl.get_list()
        assert list_str == ""
