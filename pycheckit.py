#!/usr/bin/env python3
"""PYCHECKIT - A file checksummer and integrity tester

A Python port of checkit that stores checksums (CRC64) as extended attributes.
Using this program you can easily calculate and store a checksum as
a file attribute, and check the file data against the checksum
at any time, to determine if there have been any changes to the file.

Copyright (C) 2014 Dennis Katsonis (original C version)
Copyright (C) 2026 (Python port)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import argparse
import struct
from pathlib import Path
from typing import Optional, Tuple
from enum import IntEnum, Flag, auto
import xattr

from crc64 import crc64
from file_list import FileList


VERSION = "0.5.2"
ATTRIBUTE_NAME = "user.crc64"
CHECKIT_OPTIONS_NAME = "user.checkit"
MAX_BUF_LEN = 65536


class ErrorType(IntEnum):
    """Error types for checkit operations."""
    SUCCESS = 0
    ERROR_CRC_CALC = 1
    ERROR_REMOVE_XATTR = 2
    ERROR_STORE_CRC = 3
    ERROR_OPEN_DIR = 4
    ERROR_OPEN_FILE = 5
    ERROR_READ_FILE = 6
    ERROR_SET_CRC = 7
    ERROR_REMOVE_HIDDEN = 8
    ERROR_NO_XATTR = 9
    ERROR_NO_OVERWRITE = 10
    ERROR_WRITE_FILE = 11
    ERROR_FILENAME_OVERFLOW = 12
    ERROR_NO_MEM = 13


class Validity(IntEnum):
    """Validity status."""
    VALID = 0
    INVALID = 1


class AttributeType(IntEnum):
    """Extended attribute types."""
    NO_ATTR = 0
    XATTR = 1
    HIDDEN_ATTR = 2


class CheckitOptions(IntEnum):
    """Checkit option flags."""
    UPDATEABLE = 0x01
    STATIC = 0x02
    OPT_ERROR = 0x04
    NO_XATTR_SUPPORT = 0x08


class Flags(Flag):
    """Command line flags."""
    VERBOSE = auto()
    STORE = auto()
    CHECK = auto()
    DISPLAY = auto()
    REMOVE = auto()
    RECURSE = auto()
    OVERWRITE = auto()
    PRINT = auto()
    EXPORT = auto()
    IMPORT = auto()
    PIPEDFILES = auto()
    SETCRCRO = auto()
    SETCRCRW = auto()
    MONOCHROME = auto()


class Color(IntEnum):
    """Terminal colors."""
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6


class Attribute(IntEnum):
    """Character attributes."""
    RESET = 0
    BRIGHT = 1
    DIM = 2
    UNDERLINE = 3
    BLINK = 4
    REVERSE = 7
    HIDDEN = 8


# Filesystem type constants
FS_VFAT = 0x4d44
FS_NTFS = 0x5346544e
FS_UDF = 0x15013346
FS_XFS = 0x58465342
FS_JFS = 0x3153464a
FS_NFS = 0x6969
FS_SMB = 0x517b
FS_CIFS = 0xff534d42
FS_BTRFS = 0x9123683e


ERROR_MESSAGES = {
    ErrorType.SUCCESS: "Success",
    ErrorType.ERROR_CRC_CALC: "Failed to calculate CRC from file.",
    ErrorType.ERROR_REMOVE_XATTR: "Failed to remove extended attribute.",
    ErrorType.ERROR_STORE_CRC: "Could not store CRC.",
    ErrorType.ERROR_OPEN_DIR: "Could not open directory.",
    ErrorType.ERROR_OPEN_FILE: "Could not open file.",
    ErrorType.ERROR_READ_FILE: "Could not read file.",
    ErrorType.ERROR_SET_CRC: "Setting CRC failed. Could not write attribute.",
    ErrorType.ERROR_REMOVE_HIDDEN: "Could not remove hidden checksum file.",
    ErrorType.ERROR_NO_XATTR: "No extended attribute to export.",
    ErrorType.ERROR_NO_OVERWRITE: "Can not overwrite existing checksum.",
    ErrorType.ERROR_WRITE_FILE: "Could not write to file.",
    ErrorType.ERROR_FILENAME_OVERFLOW: "Filename too long.",
}


class Stats:
    """Global statistics for file processing."""
    processed = 0
    failed = 0
    nocrc = 0


def error_message(error: ErrorType) -> str:
    """Get error message for error code."""
    return ERROR_MESSAGES.get(error, "Unknown error")


def textcolor(attr: int, fg: int, bg: int) -> None:
    """Change text color."""
    print(f"\033[{attr};{fg + 30};{bg + 40}m", end="")


def reset_text() -> None:
    """Reset text formatting."""
    print("\033[0;0m", end="")


def hidden_crc_file(filepath: str) -> str:
    """Return the filename of the hidden CRC file.

    Args:
        filepath: Path to the file

    Returns:
        Path to the hidden CRC file
    """
    path = Path(filepath)
    return str(path.parent / f".{path.name}.crc64")


def file_exists(filepath: str) -> bool:
    """Check if file exists."""
    return Path(filepath).exists()


def present_crc64(filepath: str) -> AttributeType:
    """Check if CRC64 attribute is present.

    Args:
        filepath: Path to the file

    Returns:
        XATTR if xattr present, HIDDEN_ATTR if hidden file exists, NO_ATTR otherwise
    """
    try:
        attrs = xattr.listxattr(filepath)
        if ATTRIBUTE_NAME in attrs:
            return AttributeType.XATTR
    except (OSError, IOError):
        pass

    # Check for hidden CRC file
    if file_exists(hidden_crc_file(filepath)):
        return AttributeType.HIDDEN_ATTR

    return AttributeType.NO_ATTR


def get_crc(filepath: str) -> Tuple[ErrorType, Optional[int]]:
    """Retrieve the stored CRC64 checksum.

    Args:
        filepath: Path to the file

    Returns:
        Tuple of (error_code, crc64_value)
    """
    attr_format = present_crc64(filepath)

    if attr_format == AttributeType.NO_ATTR:
        return ErrorType.ERROR_NO_XATTR, None

    if attr_format == AttributeType.XATTR:
        try:
            data = xattr.getxattr(filepath, ATTRIBUTE_NAME)
            crc_value = struct.unpack('<Q', data)[0]
            return ErrorType.SUCCESS, crc_value
        except (OSError, IOError, struct.error):
            return ErrorType.ERROR_CRC_CALC, None

    if attr_format == AttributeType.HIDDEN_ATTR:
        try:
            with open(hidden_crc_file(filepath), 'rb') as f:
                data = f.read(8)
                crc_value = struct.unpack('<Q', data)[0]
                return ErrorType.SUCCESS, crc_value
        except (OSError, IOError, struct.error):
            return ErrorType.ERROR_READ_FILE, None

    return ErrorType.ERROR_CRC_CALC, None


def file_crc64(filepath: str) -> Tuple[ErrorType, Optional[int]]:
    """Calculate CRC64 checksum for a file.

    Args:
        filepath: Path to the file

    Returns:
        Tuple of (error_code, crc64_value)
    """
    try:
        crc = 0
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(MAX_BUF_LEN)
                if not data:
                    break
                crc = crc64(crc, data)
        return ErrorType.SUCCESS, crc
    except (OSError, IOError):
        return ErrorType.ERROR_CRC_CALC, None


def get_fs_type(filepath: str) -> Optional[int]:
    """Get filesystem type for a file.

    Args:
        filepath: Path to the file

    Returns:
        Filesystem type constant or None
    """
    try:
        stat_result = os.statvfs(filepath)
        # Python's statvfs doesn't provide f_type, so we'll just return None
        # and assume extended attributes are supported
        return None
    except (OSError, IOError):
        return None


def put_crc(filepath: str, flags: Flags) -> ErrorType:
    """Calculate and store CRC64 checksum.

    Args:
        filepath: Path to the file
        flags: Command line flags

    Returns:
        Error code
    """
    # Get old CRC if exists
    old_status, old_crc = get_crc(filepath)

    # If there's an error other than NO_XATTR, return it
    if old_status != ErrorType.SUCCESS and old_status != ErrorType.ERROR_NO_XATTR:
        return old_status

    # If CRC exists and we're not overwriting, bail out
    if old_status == ErrorType.SUCCESS and not (flags & Flags.OVERWRITE):
        return ErrorType.ERROR_NO_OVERWRITE

    # Calculate new checksum
    status, new_crc = file_crc64(filepath)
    if status != ErrorType.SUCCESS:
        return status

    # Notify if checksum changed
    if old_status == ErrorType.SUCCESS and old_crc != new_crc:
        print(f"File {filepath} has been changed since checksum last computed!")

    # Try to store in extended attribute
    fs_type = get_fs_type(filepath)

    try:
        crc_bytes = struct.pack('<Q', new_crc)
        if flags & Flags.OVERWRITE:
            xattr.setxattr(filepath, ATTRIBUTE_NAME, crc_bytes)
        else:
            xattr.setxattr(filepath, ATTRIBUTE_NAME, crc_bytes, xattr.XATTR_CREATE)
        return ErrorType.SUCCESS
    except (OSError, IOError):
        # Fall back to hidden file
        try:
            with open(hidden_crc_file(filepath), 'wb') as f:
                f.write(struct.pack('<Q', new_crc))
            return ErrorType.SUCCESS
        except (OSError, IOError):
            return ErrorType.ERROR_SET_CRC


def remove_crc(filepath: str) -> ErrorType:
    """Remove stored CRC64 checksum.

    Args:
        filepath: Path to the file

    Returns:
        Error code
    """
    attr_type = present_crc64(filepath)

    if attr_type == AttributeType.XATTR:
        try:
            xattr.removexattr(filepath, ATTRIBUTE_NAME)
        except (OSError, IOError):
            return ErrorType.ERROR_REMOVE_XATTR

    if attr_type == AttributeType.HIDDEN_ATTR:
        try:
            os.unlink(hidden_crc_file(filepath))
        except (OSError, IOError):
            return ErrorType.ERROR_REMOVE_HIDDEN

    return ErrorType.SUCCESS


def export_crc(filepath: str, flags: Flags) -> ErrorType:
    """Export CRC from extended attribute to hidden file.

    Args:
        filepath: Path to the file
        flags: Command line flags

    Returns:
        Error code
    """
    if present_crc64(filepath) != AttributeType.XATTR:
        return ErrorType.ERROR_NO_XATTR

    hidden_file = hidden_crc_file(filepath)
    if file_exists(hidden_file) and not (flags & Flags.OVERWRITE):
        return ErrorType.ERROR_NO_OVERWRITE

    status, crc_value = get_crc(filepath)
    if status != ErrorType.SUCCESS:
        return ErrorType.ERROR_READ_FILE

    try:
        with open(hidden_file, 'wb') as f:
            f.write(struct.pack('<Q', crc_value))
        xattr.removexattr(filepath, ATTRIBUTE_NAME)
        return ErrorType.SUCCESS
    except (OSError, IOError):
        return ErrorType.ERROR_WRITE_FILE


def import_crc(filepath: str, flags: Flags) -> ErrorType:
    """Import CRC from hidden file to extended attribute.

    Args:
        filepath: Path to the file
        flags: Command line flags

    Returns:
        Error code
    """
    if present_crc64(filepath) != AttributeType.HIDDEN_ATTR:
        return ErrorType.ERROR_NO_OVERWRITE

    hidden_file = hidden_crc_file(filepath)

    try:
        with open(hidden_file, 'rb') as f:
            data = f.read(8)
            crc_value = struct.unpack('<Q', data)[0]

        crc_bytes = struct.pack('<Q', crc_value)
        if flags & Flags.OVERWRITE:
            xattr.setxattr(filepath, ATTRIBUTE_NAME, crc_bytes)
        else:
            xattr.setxattr(filepath, ATTRIBUTE_NAME, crc_bytes, xattr.XATTR_CREATE)

        os.unlink(hidden_file)
        return ErrorType.SUCCESS
    except (OSError, IOError):
        return ErrorType.ERROR_SET_CRC


def get_checkit_options(filepath: str) -> CheckitOptions:
    """Get checkit options for a file.

    Args:
        filepath: Path to the file

    Returns:
        Checkit options
    """
    try:
        attrs = xattr.listxattr(filepath)
        if CHECKIT_OPTIONS_NAME in attrs:
            data = xattr.getxattr(filepath, CHECKIT_OPTIONS_NAME)
            return CheckitOptions(ord(data))
    except (OSError, IOError):
        pass

    return CheckitOptions.OPT_ERROR


def set_checkit_options(filepath: str, options: CheckitOptions) -> ErrorType:
    """Set checkit options for a file.

    Args:
        filepath: Path to the file
        options: Options to set

    Returns:
        Error code
    """
    try:
        xattr.setxattr(filepath, CHECKIT_OPTIONS_NAME, bytes([options]))
        return ErrorType.SUCCESS
    except (OSError, IOError):
        return ErrorType.ERROR_SET_CRC


def remove_checkit_options(filepath: str) -> ErrorType:
    """Remove checkit options from a file.

    Args:
        filepath: Path to the file

    Returns:
        Error code
    """
    try:
        attrs = xattr.listxattr(filepath)
        if CHECKIT_OPTIONS_NAME in attrs:
            xattr.removexattr(filepath, CHECKIT_OPTIONS_NAME)
        return ErrorType.SUCCESS
    except (OSError, IOError):
        return ErrorType.ERROR_REMOVE_XATTR


def cprintf(msg: str, directory: str, base_filename: str, mono: bool, color: Color) -> None:
    """Print colored output.

    Args:
        msg: Message to print
        directory: Directory path
        base_filename: Filename
        mono: Whether to use monochrome output
        color: Color to use
    """
    print(f"{directory}{base_filename:<20}\t", end="")
    if not mono:
        print("[", end="")
        textcolor(Attribute.BRIGHT, color, Color.BLACK)
    print(msg, end="")
    if not mono:
        reset_text()


def print_error_message(result: ErrorType, filename: str) -> None:
    """Print error message."""
    print(f"For file {filename}: {error_message(result)}", file=sys.stderr)


def process_file(filepath: str, flags: Flags, no_crc_files: FileList, bad_crc_files: FileList) -> ErrorType:
    """Process a single file.

    Args:
        filepath: Path to the file
        flags: Command line flags
        no_crc_files: List to store files without CRC
        bad_crc_files: List to store files with bad CRC

    Returns:
        Error code
    """
    path = Path(filepath)

    # Skip hidden files
    if path.name.startswith('.'):
        return ErrorType.SUCCESS

    # Check if it's a directory
    if path.is_dir():
        if flags & Flags.RECURSE:
            return process_dir(filepath, flags, no_crc_files, bad_crc_files)
        return ErrorType.SUCCESS

    # Only process regular files
    if not path.is_file():
        return ErrorType.SUCCESS

    directory = str(path.parent / "")
    base_filename = path.name

    checkit_attrs = get_checkit_options(filepath)

    # Display CRC
    if flags & Flags.DISPLAY:
        status, crc_value = get_crc(filepath)
        if status != ErrorType.SUCCESS:
            print_error_message(status, filepath)
            return status
        print(f"Checksum for {filepath}: {crc_value:016x}")
        if checkit_attrs == CheckitOptions.UPDATEABLE:
            print("R/W Checksum: Checkit can update this checksum.", file=sys.stderr)
        elif checkit_attrs == CheckitOptions.STATIC:
            print("R/O Checksum: Checkit will not update this checksum.", file=sys.stderr)

    # Set CRC to read-only
    if flags & Flags.SETCRCRO:
        if flags & Flags.VERBOSE:
            print(f"Setting CRC for {filepath} to remain static/read only.", file=sys.stderr)
        result = set_checkit_options(filepath, CheckitOptions.STATIC)
        if result != ErrorType.SUCCESS:
            print_error_message(result, filepath)
            return result

    # Set CRC to read-write
    if flags & Flags.SETCRCRW:
        if flags & Flags.VERBOSE:
            print(f"Setting CRC for {filepath} to allow updates/read-write.", file=sys.stderr)
        result = set_checkit_options(filepath, CheckitOptions.UPDATEABLE)
        if result != ErrorType.SUCCESS:
            print_error_message(result, filepath)
            return result

    # Export CRC
    if flags & Flags.EXPORT:
        if flags & Flags.VERBOSE:
            print(f"Exporting attribute for {filepath} to {hidden_crc_file(base_filename)}")
        result = export_crc(filepath, flags)
        if result != ErrorType.SUCCESS:
            print_error_message(result, filepath)
            return result

    # Import CRC
    if flags & Flags.IMPORT:
        result = import_crc(filepath, flags)
        if result != ErrorType.SUCCESS:
            print_error_message(result, filepath)
            return result

    # Store CRC
    if flags & Flags.STORE:
        print(f"Storing checksum for file {filepath}", file=sys.stderr)

        if checkit_attrs == CheckitOptions.STATIC:
            print_error_message(ErrorType.ERROR_NO_OVERWRITE, filepath)
            return ErrorType.ERROR_NO_OVERWRITE
        elif checkit_attrs == CheckitOptions.UPDATEABLE:
            flags |= Flags.OVERWRITE

        result = put_crc(filepath, flags)
        if result != ErrorType.SUCCESS:
            print_error_message(result, filepath)
            return result

    # Check CRC
    if flags & Flags.CHECK:
        stored_status, stored_crc = get_crc(filepath)
        calc_crc = None

        if stored_status != ErrorType.ERROR_NO_XATTR:
            if stored_status != ErrorType.SUCCESS:
                print_error_message(ErrorType.ERROR_READ_FILE, filepath)
                return stored_status

            calc_status, calc_crc = file_crc64(filepath)
            if calc_status != ErrorType.SUCCESS:
                print_error_message(ErrorType.ERROR_CRC_CALC, filepath)
                return calc_status

        mono = bool(flags & Flags.MONOCHROME)

        if stored_status != ErrorType.ERROR_NO_XATTR and calc_crc is not None and calc_crc == stored_crc:
            cprintf("  OK  ", directory, base_filename, mono, Color.GREEN)
        elif stored_status == ErrorType.ERROR_NO_XATTR:
            cprintf("NO CRC", directory, base_filename, mono, Color.YELLOW)
            Stats.nocrc += 1
            if flags & Flags.VERBOSE:
                no_crc_files.append(directory, base_filename)
        else:
            cprintf("FAILED", directory, base_filename, mono, Color.RED)
            Stats.failed += 1
            if flags & Flags.VERBOSE:
                bad_crc_files.append(directory, base_filename)

        if not mono:
            print("]")
        else:
            print()

    # Remove CRC
    if flags & Flags.REMOVE:
        if flags & Flags.VERBOSE:
            print("Removing checksum.", file=sys.stderr)

        result = remove_crc(filepath)
        if result == ErrorType.SUCCESS:
            result = remove_checkit_options(filepath)

        if result != ErrorType.SUCCESS:
            print_error_message(result, filepath)
            return result

    Stats.processed += 1
    return ErrorType.SUCCESS


def process_dir(dirpath: str, flags: Flags, no_crc_files: FileList, bad_crc_files: FileList) -> ErrorType:
    """Process a directory recursively.

    Args:
        dirpath: Path to the directory
        flags: Command line flags
        no_crc_files: List to store files without CRC
        bad_crc_files: List to store files with bad CRC

    Returns:
        Error code
    """
    try:
        for entry in sorted(Path(dirpath).iterdir()):
            if entry.name in ('.', '..'):
                continue

            if entry.is_dir() and (flags & Flags.RECURSE):
                process_dir(str(entry), flags, no_crc_files, bad_crc_files)
            else:
                process_file(str(entry), flags, no_crc_files, bad_crc_files)
                if flags & Flags.VERBOSE:
                    print(f"Processing file {entry}.")

        return ErrorType.SUCCESS
    except (OSError, IOError):
        return ErrorType.ERROR_OPEN_DIR


def print_header() -> None:
    """Print program header."""
    print(f"PYCHECKIT: A file checksum utility.\tVersion : {VERSION}")
    print("(C) Dennis Katsonis (2014)")
    print()
    print("CRC64 Copyright (c) 2012, Salvatore Sanfilippo <antirez at gmail dot com>")
    print("All rights reserved.")
    print()


def print_license() -> None:
    """Print license information."""
    license_text = """License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""
    print(license_text)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="A file checksummer and integrity tester using CRC64 checksums.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Options:
  -s  Calculate and store checksum        -c   Check file against stored checksum
  -v  Verbose. Print more information     -p   Display CRC64 checksum and status
  -x  Remove stored CRC64 checksum        -o   Overwrite existing checksum
  -r  Recurse through directories         -i   Import CRC from hidden file
  -e  Export CRC to hidden file           -f   Read list of files from stdin
  -u  Allow CRC on this file to be updated (for files you intend to change)
  -d  Disallow updating of CRC on this file (for files you do not intend to change)
  -V  Print license                       -m  No colours.
"""
    )

    parser.add_argument('-s', '--store', action='store_true', help='Calculate and store checksum')
    parser.add_argument('-c', '--check', action='store_true', help='Check file against stored checksum')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-p', '--display', action='store_true', help='Display CRC64 checksum and status')
    parser.add_argument('-x', '--remove', action='store_true', help='Remove stored CRC64 checksum')
    parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite existing checksum')
    parser.add_argument('-r', '--recurse', action='store_true', help='Recurse through directories')
    parser.add_argument('-i', '--import-crc', action='store_true', dest='import_crc', help='Import CRC from hidden file')
    parser.add_argument('-e', '--export', action='store_true', help='Export CRC to hidden file')
    parser.add_argument('-f', '--from-stdin', action='store_true', dest='from_stdin', help='Read list of files from stdin')
    parser.add_argument('-u', '--allow-update', action='store_true', dest='allow_update', help='Allow CRC updates')
    parser.add_argument('-d', '--disallow-update', action='store_true', dest='disallow_update', help='Disallow CRC updates')
    parser.add_argument('-V', '--license', action='store_true', help='Print license')
    parser.add_argument('-m', '--monochrome', action='store_true', help='No colors')
    parser.add_argument('files', nargs='*', help='Files to process')

    args = parser.parse_args()

    # Check for conflicting options
    if args.check and args.store:
        print("Cannot store and check CRC at same time.", file=sys.stderr)
        return 1

    if args.check and args.remove:
        print("Cannot remove and check CRC at same time.", file=sys.stderr)
        return 1

    if args.store and args.remove:
        print("Cannot remove and store CRC at same time.", file=sys.stderr)
        return 1

    if args.allow_update and args.disallow_update:
        print("Cannot disallow and allow changes to CRC at the same time!", file=sys.stderr)
        return 1

    if args.export and args.import_crc:
        print("Cannot import and export at the same time.", file=sys.stderr)
        return 1

    # Print license if requested
    if args.license:
        print_header()
        print_license()
        return 0

    # Print header and help if no arguments
    if len(sys.argv) == 1:
        print_header()
        parser.print_help()
        return 0

    # Build flags
    flags = Flags(0)
    if args.verbose:
        flags |= Flags.VERBOSE
    if args.store:
        flags |= Flags.STORE
    if args.check:
        flags |= Flags.CHECK
    if args.display:
        flags |= Flags.DISPLAY
    if args.remove:
        flags |= Flags.REMOVE
    if args.recurse:
        flags |= Flags.RECURSE
    if args.overwrite:
        flags |= Flags.OVERWRITE
    if args.export:
        flags |= Flags.EXPORT
    if args.import_crc:
        flags |= Flags.IMPORT
    if args.from_stdin:
        flags |= Flags.PIPEDFILES
    if args.allow_update:
        flags |= Flags.SETCRCRW
    if args.disallow_update:
        flags |= Flags.SETCRCRO
    if args.monochrome:
        flags |= Flags.MONOCHROME

    # Check for NO_COLOR environment variable or non-tty
    if not sys.stdout.isatty() or os.environ.get('NO_COLOR'):
        flags |= Flags.MONOCHROME

    # Initialize file lists if verbose
    no_crc_files = FileList()
    bad_crc_files = FileList()

    # Process files from stdin
    if args.from_stdin:
        for line in sys.stdin:
            filepath = line.strip()
            if filepath:
                process_file(filepath, flags, no_crc_files, bad_crc_files)

    # Process files from command line
    for filepath in args.files:
        process_file(filepath, flags, no_crc_files, bad_crc_files)

    # Print summary
    if not args.files and not args.from_stdin:
        print("No files specified.", file=sys.stderr)
        return 0

    print(f"Total of {Stats.processed} file(s) processed.", file=sys.stderr)

    if Stats.nocrc and Stats.processed:
        print(f"\nWARNING: **** {Stats.nocrc} file(s) without a checksum ****", file=sys.stderr)
        if flags & Flags.VERBOSE:
            print(no_crc_files.get_list(), file=sys.stderr)

    if Stats.failed and Stats.processed:
        print(f"\nERROR: **** {Stats.failed} file(s) failed ****", file=sys.stderr)
        if flags & Flags.VERBOSE:
            print(bad_crc_files.get_list(), file=sys.stderr)
        return Stats.failed

    if Stats.processed and (flags & Flags.CHECK) and not Stats.nocrc:
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

