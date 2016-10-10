#!/usr/bin/python3

from pathlib import Path
import hashlib

def get_abs_path(filename):
    return str(Path(filename).resolve())

def get_sha256_hexdigest(string):
    return hashlib.sha256(string.encode()).hexdigest()
