"""Setup configuration for pycheckit with Cython extension."""

from setuptools import setup
from Cython.Build import cythonize
import os

# Determine the path to the .pyx file
pyx_file = os.path.join("src", "pycheckit", "crc64.pyx")

setup(
    ext_modules=cythonize(
        [pyx_file],
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
        },
    ),
)

