"""File list management for pycheckit.

This module provides functionality to track lists of files during processing.
"""


class FileList:
    """Manages a list of files with their paths."""

    def __init__(self):
        """Initialize an empty file list."""
        self.files = []

    def append(self, basename: str, filename: str) -> None:
        """Add a file to the list.

        Args:
            basename: Directory path
            filename: Filename
        """
        if basename:
            full_path = f"{basename}{filename}"
        else:
            full_path = filename
        self.files.append(full_path)

    def get_list(self) -> str:
        """Get the list of files as a newline-separated string.

        Returns:
            String containing all files separated by newlines
        """
        return "\n".join(self.files)

    def clear(self) -> None:
        """Clear the file list."""
        self.files.clear()

    def __len__(self) -> int:
        """Return the number of files in the list."""
        return len(self.files)

