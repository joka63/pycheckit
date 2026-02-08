"""Command-line interface for pycheckit."""

import os
import sys
import argparse
from pathlib import Path

from pycheckit.constants import (
    VERSION,
    ErrorType,
    Flags,
    CheckitOptions,
    Color,
    Attribute,
)
from pycheckit.core import (
    Stats,
    error_message,
    get_crc,
    file_crc64,
    put_crc,
    remove_crc,
    export_crc,
    import_crc,
    get_checkit_options,
    set_checkit_options,
    remove_checkit_options,
    hidden_crc_file,
)
from pycheckit.file_list import FileList


def textcolor(attr: int, fg: int, bg: int) -> None:
    """Change text color."""
    print(f"\033[{attr};{fg + 30};{bg + 40}m", end="")


def reset_text() -> None:
    """Reset text formatting."""
    print("\033[0;0m", end="")


def cprintf(msg: str, directory: str, base_filename: str, mono: bool, color: Color) -> None:
    """Print colored output.

    Args:
        msg: Message to print
        directory: Directory path
        base_filename: Filename
        mono: Whether to use monochrome output
        color: Color to use
    """
    print(f"{directory}{'/' if directory else ''}{base_filename:<20}\t", end="")
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
        epilog=f"""Version: pycheckit {VERSION}"""
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

