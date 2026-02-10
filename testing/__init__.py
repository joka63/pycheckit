"""Test suite for pycheckit."""

import os

os.environ["PATH"] = os.pathsep.join([
    f"{os.environ.get('HOME')}/.local/bin",
    os.environ.get("PATH", "")])

