#!/usr/bin/python3

import ctypes
from ctypes.util import find_library
import os

def mount(source, target, fs):
    err_msg = ""
    ret = ctypes.CDLL(find_library('c'), use_errno=True).mount(
        ctypes.c_char_p(source.encode()), ctypes.c_char_p(target.encode()),
        ctypes.c_char_p(fs.encode()), 0, 0)
    if ret != 0:
        errno = ctypes.get_errno()
        err_msg = "Error mounting {} ({}) on {}: {}".format(
            source, fs, target, os.strerror(errno))
        return False, err_msg
    return True, err_msg

def umount(path):
    err_msg = ""
    ret = ctypes.CDLL(find_library('c'), use_errno=True).umount(
        ctypes.c_char_p(path.encode()))
    if ret != 0:
        errno = ctypes.get_errno()
        err_msg = "Error umounting {} : {}".format(path, os.strerror(errno))
        return False, err_msg
    return True, err_msg
