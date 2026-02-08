"""Core functionality for pycheckit."""

import os
import struct
from pathlib import Path
from typing import Optional, Tuple
import xattr

from pycheckit.crc64 import crc64
from pycheckit.constants import (
    ATTRIBUTE_NAME,
    CHECKIT_OPTIONS_NAME,
    MAX_BUF_LEN,
    ERROR_MESSAGES,
    ErrorType,
    AttributeType,
    CheckitOptions,
    Flags
)


class Stats:
    """Global statistics for file processing."""
    processed = 0
    failed = 0
    nocrc = 0


def error_message(error: ErrorType) -> str:
    """Get error message for error code."""
    return ERROR_MESSAGES.get(error, "Unknown error")


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


def put_crc(filepath: str, flags) -> ErrorType:
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

    # If CRC exists, and we're not overwriting, bail out
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


def export_crc(filepath: str, flags) -> ErrorType:
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


def import_crc(filepath: str, flags) -> ErrorType:
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

