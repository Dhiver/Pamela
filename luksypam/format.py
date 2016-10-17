#!/usr/bin/env python3

import subprocess

def formatDeviceInExt4(path):
    p = subprocess.Popen("mkfs.ext4 {}".format(path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    return p.returncode, err
