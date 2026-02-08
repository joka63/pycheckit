# PyCheckit

A Python port of the checkit file checksummer and integrity tester.

PyCheckit stores CRC64 checksums as extended file attributes, allowing you to easily detect file corruption or changes.

Read also the original README of the C version: [doc/ABOUT.md](doc/ABOUT.md)

## Features

- Calculate and store CRC64 checksums for files
- Store checksums as extended attributes (with fallback to hidden files)
- Check files against stored checksums
- Recursive directory processing
- Import/export checksums between extended attributes and hidden files
- Mark files as updateable or static

## Installation

Using uv:

```bash
uv pip install pycheckit
```

Or from source:

```bash
git clone <repository>
cd pycheckit
uv pip install -e .
```

## Usage

### Store checksum for a file

```bash
pycheckit -s file.txt
```

### Check file against stored checksum

```bash
pycheckit -c file.txt
```

### Display checksum

```bash
pycheckit -p file.txt
```

### Recursive operation

```bash
pycheckit -s -r /path/to/directory
```

### Remove stored checksum

```bash
pycheckit -x file.txt
```

### Export checksum to hidden file

```bash
pycheckit -e file.txt
```

### Import checksum from hidden file

```bash
pycheckit -i file.txt
```

### Mark file as read-only (static)

```bash
pycheckit -d file.txt
```

### Mark file as updateable

```bash
pycheckit -u file.txt
```

## Command Line Options

- `-s, --store` - Calculate and store checksum
- `-c, --check` - Check file against stored checksum
- `-v, --verbose` - Verbose output
- `-p, --display` - Display CRC64 checksum and status
- `-x, --remove` - Remove stored CRC64 checksum
- `-o, --overwrite` - Overwrite existing checksum
- `-r, --recurse` - Recurse through directories
- `-i, --import-crc` - Import CRC from hidden file
- `-e, --export` - Export CRC to hidden file
- `-f, --from-stdin` - Read list of files from stdin
- `-u, --allow-update` - Allow CRC updates on this file
- `-d, --disallow-update` - Disallow CRC updates on this file
- `-V, --license` - Print license
- `-m, --monochrome` - No colors

## Examples

### Check all files in a directory

```bash
pycheckit -c -r /path/to/directory
```

### Store checksums for multiple files

```bash
pycheckit -s file1.txt file2.txt file3.txt
```

### Check files from a list

```bash
find /path -type f | pycheckit -c -f
```

### Store checksums with overwrite

```bash
pycheckit -s -o file.txt
```

## Technical Details

### CRC64 Algorithm

PyCheckit uses the CRC64 variant with "Jones" coefficients:

- Name: crc-64-jones
- Width: 64 bits
- Poly: 0xad93d23594c935a9
- Reflected In: True
- Xor_In: 0xffffffffffffffff
- Reflected_Out: True
- Xor_Out: 0x0
- Check("123456789"): 0xe9c6d914c4b8d9ca

### Storage Methods

1. **Extended Attributes** (primary): Stored as `user.crc64` attribute
2. **Hidden Files** (fallback): Stored as `.filename.crc64` for filesystems that don't support extended attributes

### File Options

Files can be marked with additional attributes:

- **Updateable**: Checksums can be updated automatically
- **Static**: Checksums are protected from automatic updates

## Development

### Running Tests

```bash
# Basic tests
uv run python test_basic.py

# Integration tests
uv run python test_integration.py
```

### Project Structure

```
pycheckit/
├── pycheckit.py      # Main module
├── crc64.py          # CRC64 implementation
├── file_list.py      # File list management
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

### Credits

- Original C version: Copyright (C) 2014 Dennis Katsonis
- CRC64 algorithm: Copyright (c) 2012, Salvatore Sanfilippo <antirez at gmail dot com>
- Python port: 2026

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Changelog

### Version 0.1 (Python Port)

- Complete Python rewrite of the original C version
- Uses CPython for performance critical tasks (calculating checksums)
- Uses argparse for command-line argument parsing
- Improved error handling
- Modern Python packaging with pyproject.toml
- Type hints throughout the codebase

