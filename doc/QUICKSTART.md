# PyCheckit Quick Start Guide

## What is PyCheckit?

PyCheckit is a Python port of the checkit file checksummer. It calculates CRC64 checksums and stores them as extended file attributes, allowing you to detect file corruption or changes.

## Installation

The project is already set up with uv. Dependencies are installed automatically.

## Quick Start

### 1. Run Tests (Verify Everything Works)

```bash
cd /home/joachim/Projekte/pycheckit
uv run python test_e2e.py
```

You should see:
```
🎉 All tests passed!
```

### 2. Basic Usage Examples

#### Store a checksum for a file
```bash
uv run python pycheckit_cli.py -s myfile.txt
```

#### Check a file against its stored checksum
```bash
uv run python pycheckit_cli.py -c myfile.txt
```

#### Display the checksum
```bash
uv run python pycheckit_cli.py -p myfile.txt
```

#### Check multiple files
```bash
uv run python pycheckit_cli.py -c file1.txt file2.txt file3.txt
```

#### Check all files in a directory (recursively)
```bash
uv run python pycheckit_cli.py -c -r /path/to/directory
```

### 3. Common Workflows

#### Protect important files

```bash
# Store checksums for all files
uv run python pycheckit_cli.py -s -r ~/Documents

# Later, verify nothing changed
uv run python pycheckit_cli.py -c -r ~/Documents
```

#### Mark files as read-only (protected from updates)

```bash
uv run python pycheckit_cli.py -d important_file.txt
```

#### Allow updates on specific files

```bash
uv run python pycheckit_cli.py -u editable_file.txt
```

## Command Reference

| Option | Description |
|--------|-------------|
| `-s` | Store checksum |
| `-c` | Check file against stored checksum |
| `-p` | Display checksum |
| `-x` | Remove checksum |
| `-r` | Recurse through directories |
| `-v` | Verbose output |
| `-o` | Overwrite existing checksum |
| `-e` | Export CRC to hidden file |
| `-i` | Import CRC from hidden file |
| `-d` | Mark file as read-only (no auto-updates) |
| `-u` | Mark file as updateable |
| `-m` | Monochrome (no colors) |

## How It Works

1. **Calculate**: PyCheckit calculates a CRC64 checksum of the file content
2. **Store**: The checksum is stored as an extended attribute (`user.crc64`)
3. **Verify**: Later, the file is read again and the checksum is recalculated
4. **Compare**: The new checksum is compared with the stored one
5. **Report**: Files that match show "OK", changed files show "FAILED"

## Extended Attributes vs Hidden Files

- **Primary method**: Extended attributes (user.crc64)
  - Fast, efficient, doesn't create extra files
  - Works on most modern Linux filesystems (ext4, xfs, btrfs, etc.)

- **Fallback method**: Hidden files (.filename.crc64)
  - Used when extended attributes aren't supported
  - Works on FAT32, NTFS, network shares, etc.

## Examples

### Example 1: Verify Downloaded Files

```bash
# After downloading important files
cd ~/Downloads
uv run python pycheckit_cli.py -s *.iso

# Before using them, verify integrity
uv run python pycheckit_cli.py -c *.iso
```

### Example 2: Monitor Photo Collection

```bash
# Store checksums for all photos
uv run python pycheckit_cli.py -s -r ~/Photos

# Monthly verification
uv run python pycheckit_cli.py -c -r -v ~/Photos
```

### Example 3: Protect System Configuration

```bash
# Store checksums (mark as read-only)
uv run python pycheckit_cli.py -s -d /etc/important.conf

# Later, check if config was modified
uv run python pycheckit_cli.py -c /etc/important.conf
```

## Troubleshooting

### "No extended attribute to export"
The file doesn't have a stored checksum yet. Use `-s` to store one first.

### "Can not overwrite existing checksum"
The file already has a checksum. Use `-o` to overwrite:
```bash
uv run python pycheckit_cli.py -s -o myfile.txt
```

### Permission denied
You need write permission to set extended attributes. Try with sudo or check file permissions.

## More Information

- See `README.md` for complete documentation
- See `CONVERSION_SUMMARY.md` for technical details
- See `FILES.md` for project structure

## Development

### Run all tests:
```bash
uv run python test_e2e.py
```

### Install for system-wide use:
```bash
uv pip install -e .
```

Then you can use:
```bash
pycheckit -c myfile.txt
```

---

**That's it!** You now have a working Python version of checkit. Enjoy protecting your files! 🎉

