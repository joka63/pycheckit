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

from pycheckit.cli import main

__all__ = ["main"]

