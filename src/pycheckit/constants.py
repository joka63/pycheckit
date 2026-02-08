"""Constants for pycheckit."""

from enum import IntEnum, Flag, auto

from pycheckit.version import __version__

VERSION = __version__
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

